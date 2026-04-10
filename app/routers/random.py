from fastapi import APIRouter, Query
from typing import Optional

from app.database import get_db
from app.models import RandomResponse, Category

router = APIRouter()

@router.get("/random", response_model=RandomResponse)
async def get_random(category: Optional[Category] = Query(None)):
    db = get_db()
    item = db.get_random(category.value if category else None)
    
    if not item:
        raise HTTPException(status_code=404, detail="No items found")
    
    return {
        "canonical": item['canonical'],
        "emoji": item['emoji'],
        "unicode": item['unicode'],
        "note": item.get('note'),
        "category": item.get('category'),
        "rarity": item.get('rarity', 'common')
    }
