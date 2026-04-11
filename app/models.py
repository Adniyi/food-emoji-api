from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class Category(str, Enum):
    FRUIT="fruit"
    VEGITABLE="vegitable"
    PROTINE="protine"
    GRAIN="grain"
    DAIRY="dairy"
    SEAFOOD="seafood"
    DESSERT="dessert"
    BEVERAGES="beverage"
    SPICE="spice"
    HERB="herb"
    FAST_FOOD="fast_food"
    ASIAN="asian"
    MEDITERRANEAN="mediterranean"
    LATINE_AMERICA="latine_america"
    AFRICA="africa"
    MIDDLE_EASTERN="middle_east"

class VariantInfo(BaseModel):
    emoji: str
    note: Optional[str] = None

class Metadata(BaseModel):
    added_in_unicode: Optional[str] = None
    has_skin_tone: bool = False
    display_consistency: Optional[str] = None

class EmojiSuccessResponse(BaseModel):
    query: str
    matched: bool = True
    canonical: str
    emoji: str
    unicode: str
    category: str
    subcategory: Optional[str] = None
    aliases: List[str]
    variants: Optional[Dict[str, VariantInfo]] = None
    metadata: Optional[Metadata] = None

class DisambiguationOption(BaseModel):
    canonical: str
    emoji: Optional[str] = None # null if ambiguous is empty
    context: str
    example_phrase: Optional[str] = None

class AmbiguousResponse(BaseModel):
    query: str
    matched: bool = False
    ambiguous: bool = True
    message: str = "Multiple matches found. Please specify."
    options: List[DisambiguationOption]

class NotFoundResponse(BaseModel):
    query: str
    matched: bool = False
    suggestion: Optional[str] = None
    similar: List[str]

class BatchOptions(BaseModel):
    include_metadata: bool = False
    fuzzy_match: bool = True
    fallback_emoji: str = "❓"


class BatchRequest(BaseModel):
    queries: List[str] = Field(..., min_items=1, max_items=100)
    options: Optional[BatchOptions] = BatchOptions()


class BatchItemSuccess(BaseModel):
    matched: bool = True
    emoji: str
    canonical: str
    alias_used: Optional[str] = None
    disambiguation_note: Optional[str] = None


class BatchItemFailure(BaseModel):
    matched: bool = False
    emoji: str
    suggestions: List[str]

class BatchResponse(BaseModel):
    processed: int
    found: int
    results: Dict[str, Union[BatchItemSuccess, BatchItemFailure]]

class SearchMatch(BaseModel):
    canonical: str
    emoji: Optional[str]
    match_type: str  # exact, prefix, substring, fuzzy
    confidence: float
    ambiguous: Optional[bool] = None
    variants: Optional[int] = None

class SearchResponse(BaseModel):
    query: str
    matches: List[SearchMatch]


class CategoryItem(BaseModel):
    canonical: str
    emoji: str
    unicode: str
    note: Optional[str] = None

class CategoryResponse(BaseModel):
    category: str
    subcategory: Optional[str] = None
    total: int
    items: List[CategoryItem]

class RandomResponse(BaseModel):
    canonical: str
    emoji: str
    unicode: str
    note: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None  # common, uncommon, exotic


class FoodRequest(BaseModel):
    food: str
    region: Optional[str] = None

class CategoryRequest(BaseModel):
    category: str
    subcategory: Optional[str] = None