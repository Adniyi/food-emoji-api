from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Union

from app.database import get_db, REGIONAL_ALIASES
from app.matcher import FuzzyMatcher
from app.utils import decode_url_param
from app.models import EmojiSuccessResponse, AmbiguousResponse, NotFoundResponse, FoodRequest

router = APIRouter()

@router.get(
    "/emoji/{food}",
    response_model=EmojiSuccessResponse,
    responses={
        300: {"model": AmbiguousResponse},
        404: {"model": NotFoundResponse}
    }
)
async def get_emoji(
    food: str,
    region: Optional[str] = Query(None, description="Region: UK, US, IN, AU"),
    body: Optional[FoodRequest] = None
):
    if body:
        query = decode_url_param(body.food)
        region = body.region
    else:
        query = decode_url_param(food)
    db = get_db()
    
    # Try direct resolution
    result = db.resolve(query, region=region)
    
    # If not found, try fuzzy matching
    if not result:
        matcher = FuzzyMatcher(db.get_all())
        matches = matcher.find_matches(query, threshold=0.7)
        if matches and not matches[0]['is_ambiguous']:
            canonical = matches[0]['canonical']
            result = db.get(canonical)
            result['canonical'] = canonical
            result['query'] = query
    
    # Handle not found
    if not result:
        matcher = FuzzyMatcher(db.get_all())
        suggestions = matcher.get_suggestions(query, n=3)
        suggestion_text = f"Did you mean: {suggestions[0]}?" if suggestions else None
        
        raise HTTPException(status_code=404, detail={
            "query": query,
            "matched": False,
            "suggestion": suggestion_text,
            "similar": suggestions
        })
    
    # Handle ambiguous
    if result.get('ambiguous'):
        options = []
        for opt in result.get('options', []):
            opt_data = {
                "canonical": opt['canonical'],
                "emoji": opt.get('emoji'),
                "context": opt['context']
            }
            if 'example_phrase' in opt:
                opt_data['example_phrase'] = opt['example_phrase']
            options.append(opt_data)
        
        return JSONResponse(status_code=300, content={
            "query": query,
            "matched": False,
            "ambiguous": True,
            "message": "Multiple matches found. Please specify.",
            "options": options
        })
    
    # Build success response
    response = {
        "query": query,
        "matched": True,
        "canonical": result['canonical'],
        "emoji": result['emoji'],
        "unicode": result['unicode'],
        "category": result['category'],
        "aliases": result.get('aliases', [])
    }
    
    if 'subcategory' in result:
        response['subcategory'] = result['subcategory']
    if 'plural' in result:
        response['plural'] = result['plural']
    if 'variants' in result:
        response['variants'] = result['variants']
    if 'metadata' in result:
        response['metadata'] = result['metadata']
    
    return response
