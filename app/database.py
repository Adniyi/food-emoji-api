
import json
import os
from typing import Dict, Any, List, Optional
from functools import lru_cache

REGIONAL_ALIASES = {
    "UK": {
        "aubergine": "eggplant",
        "courgette": "zucchini",
        "coriander": "cilantro",
        "rocket": "arugula",
        "spring_onion": "scallion",
        "swede": "rutabaga",
        "beetroot": "beet",
        "beef_mince": "ground_beef",
        "biscuit": "cookie",
        "jam": "jelly",
        "crisps": "potato_chips",
        "chips": "fries"
    },
    "US": {
        "eggplant": "eggplant",
        "zucchini": "zucchini",
        "cilantro": "cilantro",
        "arugula": "arugula",
        "scallion": "scallion",
        "beet": "beet",
        "ground_beef": "ground_beef",
        "cookie": "cookie",
        "jelly": "jelly",
        "potato_chips": "potato_chips",
        "fries": "fries"
    },
    "IN": {
        "brinjal": "eggplant",
        "lady_finger": "okra",
        "bindi": "okra",
        "capsicum": "bell_pepper"
    },
    "AU": {
        "capsicum": "bell_pepper",
        "coriander": "cilantro"
    }
}

class FoodDatabase:
    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'foods.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.alias_map: Dict[str, str] = {}
        self.ambiguous_terms: Dict[str, Any] = {}
        self._build_indexes()
    
    def _build_indexes(self):
        for canonical, item in self.data.items():
            # Map canonical name
            self.alias_map[canonical.lower()] = canonical
            
            # Map aliases
            for alias in item.get('aliases', []):
                self.alias_map[alias.lower()] = canonical
            
            # Track ambiguous terms
            if item.get('ambiguous', False):
                self.ambiguous_terms[canonical.lower()] = item
    
    def resolve(self, query: str, region: Optional[str] = None) -> Optional[Dict]:
        """Resolve query to canonical entry"""
        query_lower = query.lower().strip()
        
        # Check regional variant
        if region and region.upper() in REGIONAL_ALIASES:
            regional = REGIONAL_ALIASES[region.upper()]
            if query_lower in regional:
                query_lower = regional[query_lower]
        
        # Direct lookup
        if query_lower in self.alias_map:
            canonical = self.alias_map[query_lower]
            result = self.data[canonical].copy()
            result['canonical'] = canonical
            result['query'] = query
            return result
        
        return None
    
    def get(self, canonical: str) -> Optional[Dict]:
        """Get by canonical name"""
        return self.data.get(canonical.lower())
    
    def search_prefix(self, prefix: str) -> List[Dict]:
        """Find all items starting with prefix"""
        prefix_lower = prefix.lower()
        matches = []
        for alias, canonical in self.alias_map.items():
            if alias.startswith(prefix_lower):
                item = self.data[canonical].copy()
                item['canonical'] = canonical
                item['matched_alias'] = alias
                matches.append(item)
        return matches
    
    def get_by_category(self, category: str, subcategory: Optional[str] = None) -> List[Dict]:
        """Get items by category/subcategory"""
        results = []
        for canonical, item in self.data.items():
            if item.get('category') == category:
                if subcategory is None or item.get('subcategory') == subcategory:
                    result = item.copy()
                    result['canonical'] = canonical
                    results.append(result)
        return results
    
    def get_all(self) -> Dict[str, Any]:
        return self.data
    
    def get_random(self, category: Optional[str] = None) -> Optional[Dict]:
        """Get random item, optionally filtered by category"""
        import random
        pool = []
        for canonical, item in self.data.items():
            if not item.get('ambiguous', False):
                if category is None or item.get('category') == category:
                    result = item.copy()
                    result['canonical'] = canonical
                    pool.append(result)
        return random.choice(pool) if pool else None

@lru_cache()
def get_db():
    return FoodDatabase()
