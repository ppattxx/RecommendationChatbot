"""
Dynamic query-case generator for precision/recall/F1 evaluation.

Generates query sets from current dataset so evaluation scales when data grows.
"""

from collections import Counter
from typing import List, Tuple, Optional


class DynamicQueryCaseGenerator:
    """Generate dynamic test cases from restaurant objects."""

    def __init__(self, restaurants):
        self.restaurants = restaurants

    def _primary_location(self, location_value: Optional[str]) -> Optional[str]:
        if not isinstance(location_value, str) or not location_value.strip():
            return None

        # Location may contain multiple values separated by commas.
        parts = [p.strip().lower() for p in location_value.split(',') if p.strip()]
        if not parts:
            return None

        for p in parts:
            if len(p) >= 3:
                return p
        return parts[0]

    def _top_locations(self, limit: int = 8) -> List[str]:
        counter = Counter()
        for r in self.restaurants:
            loc = self._primary_location(getattr(r, 'location', None))
            if loc:
                counter[loc] += 1
        return [loc for loc, _ in counter.most_common(limit)]

    def _top_cuisines(self, limit: int = 16) -> List[str]:
        counter = Counter()
        blocked_terms = {
            'restaurant', 'restaurants', 'in', 'with', 'and', 'the', 'food', 'drinks'
        }
        for r in self.restaurants:
            cuisines = getattr(r, 'cuisines', [])
            if isinstance(cuisines, list):
                for c in cuisines:
                    if isinstance(c, str) and c.strip():
                        cuisine = c.strip().lower()
                        words = cuisine.split()

                        # Keep concise cuisine tags and avoid noisy sentence-like values.
                        if len(cuisine) < 3 or len(cuisine) > 28:
                            continue
                        if len(words) > 3:
                            continue
                        if any(w in blocked_terms for w in words):
                            continue
                        if any(ch.isdigit() for ch in cuisine):
                            continue

                        counter[cuisine] += 1
        return [c for c, _ in counter.most_common(limit)]

    def _top_features(self, limit: int = 12) -> List[str]:
        counter = Counter()
        for r in self.restaurants:
            features = getattr(r, 'features', [])
            if isinstance(features, list):
                for f in features:
                    if isinstance(f, str) and f.strip():
                        val = f.strip().lower()
                        if 2 <= len(val) <= 28 and len(val.split()) <= 4:
                            counter[val] += 1
        return [f for f, _ in counter.most_common(limit)]

    def _top_preferences(self, limit: int = 12) -> List[str]:
        counter = Counter()
        for r in self.restaurants:
            prefs = getattr(r, 'preferences', [])
            if isinstance(prefs, list):
                for p in prefs:
                    if isinstance(p, str) and p.strip():
                        val = p.strip().lower()
                        if 2 <= len(val) <= 28 and len(val.split()) <= 4:
                            counter[val] += 1
        return [p for p, _ in counter.most_common(limit)]

    def _restaurant_location(self, restaurant) -> Optional[str]:
        return self._primary_location(getattr(restaurant, 'location', None))

    def _restaurant_cuisines(self, restaurant) -> List[str]:
        vals = []
        cuisines = getattr(restaurant, 'cuisines', [])
        if not isinstance(cuisines, list):
            return vals
        blocked_terms = {'restaurant', 'restaurants', 'food', 'drinks'}
        for c in cuisines:
            if not isinstance(c, str) or not c.strip():
                continue
            v = c.strip().lower()
            if len(v) < 3 or len(v) > 28:
                continue
            if len(v.split()) > 3:
                continue
            if any(w in blocked_terms for w in v.split()):
                continue
            if any(ch.isdigit() for ch in v):
                continue
            vals.append(v)
        return vals

    def build_clear_cases(self, limit: int = 60) -> List[Tuple[str, List[str], Optional[str]]]:
        """Generate clear query cases from observed cuisine-location pairs."""
        cases = []
        seen = set()

        pair_counter = Counter()
        for r in self.restaurants:
            loc = self._restaurant_location(r)
            if not loc:
                continue
            for cuisine in self._restaurant_cuisines(r):
                pair_counter[(cuisine, loc)] += 1

        for (cuisine, loc), _ in pair_counter.most_common(limit * 2):
            query = f"{cuisine} di {loc}"
            if query in seen:
                continue
            seen.add(query)
            cases.append((query, [cuisine], loc))
            if len(cases) >= limit:
                break

        return cases

    def build_multiple_cases(self, limit: int = 60) -> List[Tuple[str, List[str], Optional[str]]]:
        """Generate multi-entity queries from observed triplets in data."""
        cases = []
        seen = set()

        cf_counter = Counter()
        cp_counter = Counter()

        for r in self.restaurants:
            loc = self._restaurant_location(r)
            cuisines = self._restaurant_cuisines(r)
            if not loc or not cuisines:
                continue

            features = getattr(r, 'features', []) if isinstance(getattr(r, 'features', []), list) else []
            prefs = getattr(r, 'preferences', []) if isinstance(getattr(r, 'preferences', []), list) else []

            clean_features = [f.strip().lower() for f in features if isinstance(f, str) and 2 <= len(f.strip()) <= 28]
            clean_prefs = [p.strip().lower() for p in prefs if isinstance(p, str) and 2 <= len(p.strip()) <= 28]

            for c in cuisines:
                for f in clean_features[:4]:
                    if len(f.split()) <= 4:
                        cf_counter[(c, f, loc)] += 1
                for p in clean_prefs[:4]:
                    if len(p.split()) <= 4:
                        cp_counter[(c, p, loc)] += 1

        # Prefer high-support triplets.
        for (cuisine, feature, loc), _ in cf_counter.most_common(limit * 2):
            query = f"{cuisine} dengan {feature} di {loc}"
            if query in seen:
                continue
            seen.add(query)
            cases.append((query, [cuisine, feature], loc))
            if len(cases) >= (limit // 2):
                break

        for (cuisine, pref, loc), _ in cp_counter.most_common(limit * 2):
            query = f"{cuisine} {pref} di {loc}"
            if query in seen:
                continue
            seen.add(query)
            cases.append((query, [cuisine, pref], loc))
            if len(cases) >= limit:
                break

        return cases

    def build_ambiguous_cases(self, limit: int = 40) -> List[Tuple[str, List[str], Optional[str]]]:
        """Generate ambiguous/general queries with broad intent terms."""
        seeds = [
            ("restoran recommended", ["recommended"], None),
            ("tempat makan hits", ["hits"], None),
            ("best restaurant", ["best"], None),
            ("popular place", ["popular"], None),
            ("kuliner enak", ["kuliner", "enak"], None),
            ("hidden gem cafe", ["hidden gem", "cafe"], None),
            ("cafe instagramable", ["instagramable", "cafe"], None),
            ("tempat nongkrong cozy", ["nongkrong", "cozy"], None),
            ("restoran modern", ["modern"], None),
            ("restoran fancy", ["fancy"], None),
        ]

        locations = self._top_locations(limit=14)
        for loc in locations:
            seeds.append((f"food di {loc}", ["food"], loc))
            seeds.append((f"kuliner {loc}", ["kuliner"], loc))
            seeds.append((f"best restaurant di {loc}", ["best"], loc))
            seeds.append((f"cafe di {loc}", ["cafe"], loc))
            seeds.append((f"tempat makan di {loc}", ["kuliner"], loc))

        # Deduplicate while preserving order.
        cases = []
        seen = set()
        for query, keywords, location in seeds:
            if query in seen:
                continue
            seen.add(query)
            cases.append((query, keywords, location))
            if len(cases) >= limit:
                break

        return cases
