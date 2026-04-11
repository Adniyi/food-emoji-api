from fastapi import APIRouter, Query
from typing import Optional

from app.database import get_db
from app.models import CategoryResponse, CategoryItem, Category

router = APIRouter()

@router.get("/category/{category}", response_model=CategoryResponse)
async def get_category(
    category: Category,
    body: Optional[CategoryRequest] = None,
    subcategory: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    if body:
        category = body.category
        subcategory = body.subcategory
    db = get_db()
    items = db.get_by_category(category.value, subcategory)
    
    # Limit results
    items = items[:limit]
    
    return {
        "category": category.value,
        "subcategory": subcategory,
        "total": len(items),
        "items": [
            CategoryItem(
                canonical=item['canonical'],
                emoji=item['emoji'],
                unicode=item['unicode'],
                note=item.get('note')
            )
            for item in items
        ]
    }
