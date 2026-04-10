from fastapi import APIRouter, Query
from typing import List

from app.database import get_db
from app.matcher import FuzzyMatcher
from app.utils import normalize_query
from app.models import SearchResponse, SearchMatch

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    query = normalize_query(q)
    db = get_db()
    matcher = FuzzyMatcher(db.get_all())
    
    matches = matcher.find_matches(query, threshold=0.4)
    
    results: List[SearchMatch] = []
    for m in matches[:limit]:
        item = m['item']
        match_data = {
            "canonical": m['canonical'],
            "emoji": item.get('emoji'),
            "match_type": m['match_type'],
            "confidence": round(m['confidence'], 2)
        }
        
        if m['is_ambiguous']:
            match_data['ambiguous'] = True
            match_data['variants'] = len(item.get('options', []))
        
        results.append(SearchMatch(**match_data))
    
    return {
        "query": query,
        "matches": results
    }
