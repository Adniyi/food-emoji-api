from fastapi import APIRouter
from typing import Dict, Union
import asyncio

from app.database import get_db, REGIONAL_ALIASES
from app.matcher import FuzzyMatcher
from app.utils import normalize_query
from app.models import BatchRequest, BatchResponse, BatchItemSuccess, BatchItemFailure

router = APIRouter()

@router.post("/batch", response_model=BatchResponse)
async def batch_lookup(request: BatchRequest):
    db = get_db()
    matcher = FuzzyMatcher(db.get_all())
    results: Dict[str, Union[BatchItemSuccess, BatchItemFailure]] = {}
    
    async def process_one(query: str):
        normalized = normalize_query(query)
        result = db.resolve(normalized)
        
        # Fuzzy fallback
        if not result and request.options.fuzzy_match:
            matches = matcher.find_matches(normalized, threshold=0.7)
            if matches and not matches[0]['is_ambiguous']:
                canonical = matches[0]['canonical']
                result = db.get(canonical)
                result['canonical'] = canonical
        
        if not result:
            suggestions = matcher.get_suggestions(normalized, n=3)
            return query, BatchItemFailure(
                matched=False,
                emoji=request.options.fallback_emoji,
                suggestions=suggestions if suggestions else ["unknown"]
            )
        
        # Handle ambiguous
        if result.get('ambiguous'):
            first_opt = result['options'][0]
            first_canonical = first_opt['canonical']
            first_item = db.get(first_canonical)
            
            note = f"Ambiguous: could be {', '.join([o['canonical'] for o in result['options']])}"
            return query, BatchItemSuccess(
                matched=True,
                emoji=first_item['emoji'],
                canonical=first_canonical,
                disambiguation_note=note
            )
        
        # Check for regional alias
        alias_used = None
        for region, mapping in REGIONAL_ALIASES.items():
            if normalized in mapping:
                alias_used = f"{normalized} → {result['canonical']}"
                break
        
        # Check for notes (like UK/US differences)
        note = None
        if 'notes' in result:
            for region, msg in result['notes'].items():
                if alias_used and region in alias_used:
                    note = msg
                    break
        
        return query, BatchItemSuccess(
            matched=True,
            emoji=result['emoji'],
            canonical=result['canonical'],
            alias_used=alias_used,
            disambiguation_note=note
        )
    
    # Process all concurrently
    tasks = [process_one(q) for q in request.queries]
    processed = await asyncio.gather(*tasks)
    
    found_count = 0
    for query, item in processed:
        results[query] = item
        if item.matched:
            found_count += 1
    
    return {
        "processed": len(request.queries),
        "found": found_count,
        "results": results
    }
