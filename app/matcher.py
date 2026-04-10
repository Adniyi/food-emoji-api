from difflib import SequenceMatcher
from typing import List, Tuple, Dict, Any, Optional
# import jellyfish

class FuzzyMatcher:
    def __init__(self, database: Dict[str, Any]):
        self.db = database
        self.all_aliases = self._extract_all_aliases()
    
    def _extract_all_aliases(self) -> List[Tuple[str, str, bool]]:
        """Extract all (alias, canonical, is_ambiguous) tuples"""
        aliases = []
        for canonical, item in self.db.items():
            if item.get('ambiguous'):
                aliases.append((canonical, canonical, True))
            else:
                aliases.append((canonical, canonical, False))
                for a in item.get('aliases', []):
                    aliases.append((a, canonical, False))
        return aliases
    
    def find_matches(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """Find fuzzy matches"""
        query_lower = query.lower()
        matches = []
        seen_canonical = set()
        
        for alias, canonical, is_ambig in self.all_aliases:
            # Exact match
            if alias == query_lower:
                confidence = 1.0
                match_type = "exact"
            # Prefix match
            elif alias.startswith(query_lower):
                confidence = 0.95 - (len(alias) - len(query_lower)) * 0.02
                match_type = "prefix"
            # Substring match
            elif query_lower in alias:
                confidence = 0.8
                match_type = "substring"
            # Fuzzy match
            else:
                ratio = SequenceMatcher(None, query_lower, alias).ratio()
                if ratio >= threshold:
                    confidence = ratio
                    match_type = "fuzzy"
                else:
                    continue
            
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                item = self.db[canonical]
                matches.append({
                    'canonical': canonical,
                    'confidence': confidence,
                    'match_type': match_type,
                    'is_ambiguous': is_ambig,
                    'item': item
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches
    
    def get_suggestions(self, query: str, n: int = 3) -> List[str]:
        """Get suggestions for misspelled query"""
        matches = self.find_matches(query, threshold=0.5)
        return [m['canonical'] for m in matches[:n] if not m['is_ambiguous']]
