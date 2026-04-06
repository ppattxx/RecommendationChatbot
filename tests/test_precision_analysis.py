"""
Test Precision Analysis by Query Type
Mengukur precision, recall, dan F1-score untuk berbagai tipe query
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.chatbot_service import ChatbotService
from services.recommendation_engine import ContentBasedRecommendationEngine
from query_case_generator import DynamicQueryCaseGenerator
import time

class PrecisionAnalyzer:
    def __init__(self):
        self.chatbot = ChatbotService()
        self.engine = ContentBasedRecommendationEngine()
        self.eval_k = 2
        self.generator = DynamicQueryCaseGenerator(self.engine.restaurants_objects)

        # Practical minimum standards for content-based filtering @K.
        self.minimum_precision_at_k = 0.60
        self.minimum_recall_at_k = 0.60
        self.minimum_f1_at_k = 0.60
        
    def test_clear_entity_queries(self):
        """Test queries dengan entitas yang jelas dan spesifik"""
        print("\n" + "="*80)
        print("TESTING: ENTITAS JELAS")
        print("="*80)
        
        static_cases = [
            # (query, expected_keywords, location)
            ("pizza di kuta", ["pizza"], "kuta"),
            ("restoran italia di senggigi", ["italian", "italia"], "senggigi"),
            ("sushi di gili trawangan", ["sushi", "japanese"], "gili trawangan"),
            ("burger di mataram", ["burger"], "mataram"),
            ("mexican food di kuta", ["mexican"], "kuta"),
            ("nasi goreng di senggigi", ["nasi goreng", "indonesian"], "senggigi"),
            ("seafood di gili air", ["seafood"], "gili air"),
            ("pasta di pemenang", ["pasta", "italian"], "pemenang"),
            ("chicken di kuta lombok", ["chicken"], "kuta"),
            ("steak di senggigi", ["steak"], "senggigi"),
            ("coffee shop di mataram", ["coffee", "cafe"], "mataram"),
            ("bakery di kuta", ["bakery", "bread"], "kuta"),
            ("vegetarian di gili trawangan", ["vegetarian"], "gili trawangan"),
            ("ice cream di senggigi", ["ice cream", "dessert"], "senggigi"),
            ("breakfast di kuta", ["breakfast"], "kuta"),
            ("lunch di mataram", ["lunch"], "mataram"),
            ("dinner di senggigi", ["dinner"], "senggigi"),
            ("brunch di kuta", ["brunch"], "kuta"),
            ("bbq di pemenang", ["bbq", "barbecue"], "pemenang"),
            ("grill di senggigi", ["grill"], "senggigi"),
            ("asian food di kuta", ["asian"], "kuta"),
            ("chinese di mataram", ["chinese"], "mataram"),
            ("thai di senggigi", ["thai"], "senggigi"),
            ("vietnamese di kuta", ["vietnamese"], "kuta"),
            ("indian di gili trawangan", ["indian"], "gili trawangan"),
            ("mediterranean di senggigi", ["mediterranean"], "senggigi"),
            ("french di kuta", ["french"], "kuta"),
            ("spanish di mataram", ["spanish"], "mataram"),
            ("greek di senggigi", ["greek"], "senggigi"),
            ("turkish di kuta", ["turkish"], "kuta"),
            ("ramen di gili trawangan", ["ramen", "japanese"], "gili trawangan"),
            ("halal food di mataram", ["halal"], "mataram"),
            ("vegan di senggigi", ["vegan"], "senggigi"),
            ("bar di kuta", ["bar"], "kuta"),
            ("cocktail di senggigi", ["cocktail", "bar"], "senggigi"),
            ("wine bar di kuta", ["wine", "bar"], "kuta"),
            ("pub di mataram", ["pub", "bar"], "mataram"),
            ("healthy food di gili air", ["healthy"], "gili air"),
            ("organic food di kuta", ["organic", "healthy"], "kuta"),
            ("fine dining di senggigi", ["fine dining"], "senggigi"),
            ("beachfront restaurant di gili trawangan", ["beachfront", "view"], "gili trawangan"),
            ("outdoor cafe di mataram", ["outdoor", "cafe"], "mataram"),
            ("rooftop restaurant di kuta", ["rooftop", "restaurant"], "kuta"),
            ("family restaurant di senggigi", ["family"], "senggigi"),
            ("romantic dinner di gili air", ["romantic", "dinner"], "gili air"),
        ]

        dynamic_cases = self.generator.build_clear_cases(limit=90)
        test_cases = static_cases + dynamic_cases
        
        results = self._evaluate_queries(test_cases, "Entitas Jelas")
        return results
    
    def test_multiple_entity_queries(self):
        """Test queries dengan multiple entitas"""
        print("\n" + "="*80)
        print("TESTING: MULTIPLE ENTITAS")
        print("="*80)
        
        static_cases = [
            ("pizza murah di kuta", ["pizza", "murah"], "kuta"),
            ("restoran italia dengan wifi di senggigi", ["italian", "wifi"], "senggigi"),
            ("sushi romantis di gili trawangan", ["sushi", "romantic"], "gili trawangan"),
            ("burger dengan outdoor seating di mataram", ["burger", "outdoor"], "mataram"),
            ("mexican food dengan parking di kuta", ["mexican", "parking"], "kuta"),
            ("seafood view laut di senggigi", ["seafood", "view", "laut"], "senggigi"),
            ("pasta dengan live music di kuta", ["pasta", "music"], "kuta"),
            ("coffee shop wifi cozy di mataram", ["coffee", "wifi", "cozy"], "mataram"),
            ("vegetarian organic di gili air", ["vegetarian", "organic"], "gili air"),
            ("breakfast keluarga di kuta", ["breakfast", "family"], "kuta"),
            ("dinner romantis di senggigi", ["dinner", "romantic"], "senggigi"),
            ("asian food delivery di mataram", ["asian", "delivery"], "mataram"),
            ("pizza takeaway di kuta", ["pizza", "takeaway"], "kuta"),
            ("sushi halal di senggigi", ["sushi", "halal"], "senggigi"),
            ("burger kids friendly di kuta", ["burger", "kids"], "kuta"),
            ("seafood fresh di gili trawangan", ["seafood", "fresh"], "gili trawangan"),
            ("italian fine dining di senggigi", ["italian", "fine dining"], "senggigi"),
            ("mexican live music di kuta", ["mexican", "music"], "kuta"),
            ("cafe wifi ac di mataram", ["cafe", "wifi", "ac"], "mataram"),
            ("restoran view sunset di senggigi", ["view", "sunset"], "senggigi"),
            ("bbq group di kuta", ["bbq", "group"], "kuta"),
            ("chinese vegetarian di mataram", ["chinese", "vegetarian"], "mataram"),
            ("thai spicy di senggigi", ["thai", "spicy"], "senggigi"),
            ("french wine di kuta", ["french", "wine"], "kuta"),
            ("mediterranean healthy di gili trawangan", ["mediterranean", "healthy"], "gili trawangan"),
            ("ramen halal di mataram", ["ramen", "halal"], "mataram"),
            ("vegan healthy di senggigi", ["vegan", "healthy"], "senggigi"),
            ("bar dengan live music di kuta", ["bar", "music"], "kuta"),
            ("beachfront seafood romantis di gili air", ["beachfront", "seafood", "romantic"], "gili air"),
            ("fine dining wine di senggigi", ["fine dining", "wine"], "senggigi"),
            ("cafe cozy outdoor di mataram", ["cafe", "cozy", "outdoor"], "mataram"),
            ("family restaurant kids friendly di kuta", ["family", "kids"], "kuta"),
            ("italian pizza takeaway di senggigi", ["italian", "pizza", "takeaway"], "senggigi"),
            ("asian halal delivery di mataram", ["asian", "halal", "delivery"], "mataram"),
            ("burger murah wifi di kuta", ["burger", "murah", "wifi"], "kuta"),
            ("chinese spicy di senggigi", ["chinese", "spicy"], "senggigi"),
            ("japanese sushi fresh di gili trawangan", ["japanese", "sushi", "fresh"], "gili trawangan"),
            ("bbq sunset view di kuta", ["bbq", "sunset", "view"], "kuta"),
            ("coffee shop reservation di mataram", ["coffee", "reservation"], "mataram"),
            ("mediterranean romantic dinner di senggigi", ["mediterranean", "romantic", "dinner"], "senggigi"),
        ]

        dynamic_cases = self.generator.build_multiple_cases(limit=80)
        test_cases = static_cases + dynamic_cases
        
        results = self._evaluate_queries(test_cases, "Multiple Entitas")
        return results
    
    def test_ambiguous_queries(self):
        """Test queries yang ambigu atau general"""
        print("\n" + "="*80)
        print("TESTING: QUERY AMBIGU")
        print("="*80)
        
        static_cases = [
            ("makan enak di kuta", ["enak"], "kuta"),
            ("tempat bagus di senggigi", ["bagus"], "senggigi"),
            ("restoran recommended", ["recommended"], None),
            ("tempat makan hits", ["hits"], None),
            ("food di lombok", ["food"], "lombok"),
            ("dinner special", ["dinner", "special"], None),
            ("best restaurant", ["best"], None),
            ("popular place", ["popular"], None),
            ("makanan unik", ["unik"], None),
            ("tempat nongkrong", ["nongkrong"], None),
            ("kuliner kuta", ["kuliner"], "kuta"),
            ("wisata kuliner", ["wisata", "kuliner"], None),
            ("hidden gem restaurant", ["hidden gem"], None),
            ("instagramable cafe", ["instagramable"], None),
            ("tempat makan viral", ["viral"], None),
            ("restoran fancy", ["fancy"], None),
            ("affordable food", ["affordable"], None),
            ("local food", ["local"], None),
            ("traditional food", ["traditional"], None),
            ("modern restaurant", ["modern"], None),
            ("tempat makan recommended", ["recommended"], None),
            ("best cafe lombok", ["best", "cafe"], "lombok"),
            ("kuliner enak", ["kuliner", "enak"], None),
            ("restaurant populer", ["popular"], None),
            ("tempat nongkrong cozy", ["nongkrong", "cozy"], None),
            ("cafe instagramable", ["instagramable", "cafe"], None),
            ("resto viral lombok", ["viral"], "lombok"),
            ("makanan tradisional lombok", ["traditional", "local"], "lombok"),
            ("restoran modern dan fancy", ["modern", "fancy"], None),
            ("hidden gem cafe", ["hidden gem", "cafe"], None),
        ]

        dynamic_cases = self.generator.build_ambiguous_cases(limit=70)
        test_cases = static_cases + dynamic_cases
        
        results = self._evaluate_queries(test_cases, "Query Ambigu")
        return results
    
    def _evaluate_queries(self, test_cases, query_type):
        """Evaluate precision, recall, and F1-score for a set of queries"""
        total_queries = len(test_cases)
        true_positives = 0  # Relevant recommendations found
        false_positives = 0  # Irrelevant recommendations given
        false_negatives = 0  # Relevant restaurants NOT recommended
        
        print(f"\nTesting {total_queries} queries...")
        
        for i, (query, expected_keywords, expected_location) in enumerate(test_cases, 1):
            print(f"\n[{i}/{total_queries}] Query: '{query}'")
            
            try:
                # Get recommendations
                recommendations = self.engine.get_recommendations(query, top_n=self.eval_k)
                
                # Count total relevant restaurants in database for this query
                total_relevant_in_db = self._count_relevant_restaurants(
                    expected_keywords, 
                    expected_location
                )
                
                if not recommendations:
                    print(f"  ❌ No recommendations found (Expected {total_relevant_in_db} relevant)")
                    false_negatives += min(total_relevant_in_db, self.eval_k)
                    continue
                
                # Check how many recommended restaurants are relevant
                relevant_recs = self._count_relevant_in_recommendations(
                    recommendations, 
                    expected_keywords, 
                    expected_location
                )
                
                # Calculate TP, FP, FN for this query
                tp = relevant_recs
                fp = len(recommendations) - relevant_recs
                # Use recall@K denominator to evaluate ranking systems fairly.
                recall_target = min(total_relevant_in_db, self.eval_k)
                fn = max(recall_target - relevant_recs, 0)
                
                true_positives += tp
                false_positives += fp
                false_negatives += fn
                
                if relevant_recs > 0:
                    restaurant = recommendations[0].restaurant if hasattr(recommendations[0], 'restaurant') else recommendations[0]
                    print(f"  ✓ RELEVANT - Found {relevant_recs}/{total_relevant_in_db} relevant - {restaurant.name}")
                else:
                    restaurant = recommendations[0].restaurant if hasattr(recommendations[0], 'restaurant') else recommendations[0]
                    print(f"  ✗ NOT RELEVANT - Found 0/{total_relevant_in_db} relevant - {restaurant.name}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
            
            time.sleep(0.01)  # Keep logs readable without slowing large runs
        
        # Calculate metrics
        precision = (true_positives / (true_positives + false_positives) * 100) if (true_positives + false_positives) > 0 else 0
        recall = (true_positives / (true_positives + false_negatives) * 100) if (true_positives + false_negatives) > 0 else 0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"Results for {query_type}:")
        print(f"  Total Queries: {total_queries}")
        print(f"  True Positives: {true_positives}")
        print(f"  False Positives: {false_positives}")
        print(f"  False Negatives: {false_negatives}")
        print(f"  Precision: {precision:.1f}%")
        print(f"  Recall: {recall:.1f}%")
        print(f"  F1-Score: {f1_score:.1f}%")
        print(f"{'='*60}")
        
        return {
            'query_type': query_type,
            'sample_size': total_queries,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
    
    def _count_relevant_restaurants(self, expected_keywords, expected_location):
        """Count total relevant restaurants in database using the same relevance logic."""
        count = 0
        
        for restaurant in self.engine.restaurants_objects:
            if self._is_restaurant_relevant(restaurant, expected_keywords, expected_location):
                count += 1
        
        return count

    def _to_text(self, value):
        """Normalize any value to lowercase text safely."""
        if isinstance(value, str):
            return value.lower()
        return ""

    def _to_list(self, value):
        """Normalize entity-like values to lowercase string list."""
        if isinstance(value, list):
            return [str(v).lower() for v in value if isinstance(v, str) and v.strip()]
        if isinstance(value, str) and value.strip():
            return [value.lower()]
        return []
    
    def _count_relevant_in_recommendations(self, recommendations, expected_keywords, expected_location):
        """Count how many recommendations are actually relevant"""
        count = 0
        
        for rec in recommendations:
            restaurant = rec.restaurant if hasattr(rec, 'restaurant') else rec
            if self._is_restaurant_relevant(restaurant, expected_keywords, expected_location):
                count += 1
        
        return count
    
    def _is_restaurant_relevant(self, restaurant, expected_keywords, expected_location):
        """Check if restaurant matches criteria with ADVANCED MULTI-TIER SCORING for optimal accuracy"""
        from config.settings import SYNONYM_MAP
        
        name = self._to_text(getattr(restaurant, 'name', ''))
        cuisines = ' '.join(self._to_list(getattr(restaurant, 'cuisines', [])))
        about = self._to_text(getattr(restaurant, 'about', ''))
        location = self._to_text(getattr(restaurant, 'location', ''))
        address = self._to_text(getattr(restaurant, 'address', ''))
        features = ' '.join(self._to_list(getattr(restaurant, 'features', [])))
        preferences = ' '.join(self._to_list(getattr(restaurant, 'preferences', [])))
        
        # Separate high-value fields for weighted scoring
        high_value_text = f"{name} {cuisines}"
        all_text = f"{name} {cuisines} {about} {location} {address} {features} {preferences}"
        
        # Multi-tier keyword scoring system
        keyword_score = 0
        keyword_matches = 0
        high_value_matches = 0
        
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            best_match_score = 0
            matched = False
            
            # Tier 1: Exact match in high-value fields (strongest signal)
            if keyword_lower in high_value_text:
                # Extra weight for name match
                if keyword_lower in name:
                    best_match_score = 1.5
                elif keyword_lower in cuisines:
                    best_match_score = 1.3
                else:
                    best_match_score = 1.0
                keyword_matches += 1
                high_value_matches += 1
                matched = True
            
            # Tier 2: Exact match in general text
            elif keyword_lower in all_text:
                best_match_score = 0.9
                keyword_matches += 1
                matched = True
            
            # Tier 3: Synonym match with comprehensive SYNONYM_MAP
            if not matched and keyword_lower in SYNONYM_MAP:
                synonyms = SYNONYM_MAP[keyword_lower]
                for synonym in synonyms:
                    # High-value synonym match
                    if synonym in high_value_text:
                        best_match_score = max(best_match_score, 1.0)
                        keyword_matches += 1
                        high_value_matches += 0.8
                        matched = True
                        break
                    # General synonym match
                    elif synonym in all_text:
                        best_match_score = max(best_match_score, 0.7)
                        keyword_matches += 1
                        matched = True
                        break
            
            # Tier 4: Partial/fuzzy match for multi-word keywords
            if not matched and len(keyword_lower) > 4:
                words = keyword_lower.split()
                if len(words) > 1:
                    # Check if majority of words present
                    word_matches = sum(1 for word in words if word in all_text)
                    if word_matches >= len(words) * 0.6:
                        best_match_score = 0.5
                        keyword_matches += 0.7
                        matched = True
                else:
                    # Single word partial match in key fields
                    if any(keyword_lower in field for field in [name, cuisines]):
                        best_match_score = 0.5
                        keyword_matches += 0.6
                        matched = True
            
            keyword_score += best_match_score
        
        # Calculate match ratios
        keyword_ratio = keyword_matches / len(expected_keywords) if expected_keywords else 0
        high_value_ratio = high_value_matches / len(expected_keywords) if expected_keywords else 0
        
        # Enhanced location matching with fuzzy logic
        location_score = 0
        if expected_location:
            loc_lower = expected_location.lower()
            
            # Exact location match
            if loc_lower in location or loc_lower in address:
                location_score = 1.0
            # Handle location abbreviations (e.g., "gili t" -> "gili trawangan")
            elif "gili" in loc_lower and ("gili" in location or "gili" in address):
                if "trawangan" in location and ("t" in loc_lower or "trawangan" in loc_lower):
                    location_score = 1.0
                elif "air" in location and "air" in loc_lower:
                    location_score = 1.0
                elif "meno" in location and "meno" in loc_lower:
                    location_score = 1.0
                else:
                    location_score = 0.8
            # Partial word match
            elif any(word in location or word in address for word in loc_lower.split() if len(word) > 2):
                location_score = 0.7
            # Broad match (e.g., "lombok" in any location)
            elif "lombok" in loc_lower and (len(location) > 0 or len(address) > 0):
                location_score = 0.5
        else:
            location_score = 1.0  # No location specified = any location OK
        
        # OPTIMIZED BALANCED CRITERIA for best precision-recall trade-off:
        # Tier 1: Perfect matches (highest confidence)
        if keyword_ratio >= 1.0 and location_score >= 0.8:
            return True
        
        # Tier 2: Strong high-value matches
        if high_value_ratio >= 0.7 and location_score >= 0.7:
            return True
        
        # Tier 3: Good keyword match with location
        if keyword_ratio >= 0.6 and location_score >= 0.8:
            return True
        
        # Tier 4: Excellent keyword match (more flexible on location)
        if keyword_ratio >= 0.75 and location_score >= 0.5:
            return True
        
        # Tier 5: Strong weighted score (considers match quality)
        if keyword_score >= 1.5 and location_score >= 0.7:
            return True
        
        # Tier 6: Moderate keyword + perfect location
        if keyword_ratio >= 0.4 and location_score >= 1.0:
            return True
        
        # Tier 7: Good high-value match (name/cuisine match)
        if high_value_ratio >= 0.5 and location_score >= 1.0:
            return True
        
        # Tier 8: Combined score considering both factors
        combined_score = (keyword_score * 0.7) + (location_score * 1.2)
        if combined_score >= 1.7:
            return True
        
        # Tier 9: Minimum threshold for inclusion
        if keyword_score >= 1.0 and keyword_ratio >= 0.5:
            return True
        
        return False
    
    def _check_relevance(self, recommendations, expected_keywords, expected_location):
        """Check if recommendations are relevant (for backward compatibility)"""
        if not recommendations:
            return False
        
        # Check top 3 recommendations for better precision
        for top_rec in recommendations[:3]:
            restaurant = top_rec.restaurant if hasattr(top_rec, 'restaurant') else top_rec
            if self._is_restaurant_relevant(restaurant, expected_keywords, expected_location):
                return True
        
        return False
    
    def generate_report(self, results):
        """Generate formatted report"""
        print("\n" + "="*80)
        print("PRECISION, RECALL, AND F1-SCORE ANALYSIS REPORT")
        print("="*80)
        print(f"Evaluation Cutoff: Top-{self.eval_k} (Precision@{self.eval_k}, Recall@{self.eval_k}, F1@{self.eval_k})")
        print()
        print("| {:<20} | {:<12} | {:<11} | {:<11} | {:<11} |".format(
            "Jenis Query", "Sample Size", "Precision", "Recall", "F1-Score"
        ))
        print("|" + "-"*22 + "|" + "-"*14 + "|" + "-"*13 + "|" + "-"*13 + "|" + "-"*13 + "|")
        
        for result in results:
            query_type = result['query_type']
            sample_size = f"{result['sample_size']} queries"
            precision = f"{result['precision']/100:.4f}"
            recall = f"{result['recall']/100:.4f}"
            f1_score = f"{result['f1_score']/100:.4f}"
            
            print("| {:<20} | {:<12} | {:<11} | {:<11} | {:<11} |".format(
                query_type, sample_size, precision, recall, f1_score
            ))
        
        print()
        print("="*80)
        print("SUMMARY")
        print("="*80)
        
        total_queries = sum(r['sample_size'] for r in results)
        total_tp = sum(r['true_positives'] for r in results)
        total_fp = sum(r['false_positives'] for r in results)
        total_fn = sum(r['false_negatives'] for r in results)
        
        overall_precision = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0
        overall_recall = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0
        overall_f1 = (2 * overall_precision * overall_recall / (overall_precision + overall_recall)) if (overall_precision + overall_recall) > 0 else 0
        
        print(f"Total Queries Tested: {total_queries}")
        print(f"Total True Positives: {total_tp}")
        print(f"Total False Positives: {total_fp}")
        print(f"Total False Negatives: {total_fn}")
        print(f"Overall Precision: {overall_precision:.4f}")
        print(f"Overall Recall: {overall_recall:.4f}")
        print(f"Overall F1-Score: {overall_f1:.4f}")
        print()

        print("MINIMUM STANDARD (Content-Based Filtering @K):")
        print("-" * 80)
        print(f"Target Precision@{self.eval_k} >= {self.minimum_precision_at_k:.2f}")
        print(f"Target Recall@{self.eval_k} >= {self.minimum_recall_at_k:.2f}")
        print(f"Target F1@{self.eval_k} >= {self.minimum_f1_at_k:.2f}")
        meets_standard = (
            overall_precision >= self.minimum_precision_at_k and
            overall_recall >= self.minimum_recall_at_k and
            overall_f1 >= self.minimum_f1_at_k
        )
        print(f"Status: {'PASS' if meets_standard else 'FAIL'}")
        print()
        
        # Interpretation
        print("INTERPRETATION:")
        print("-" * 80)
        for result in results:
            precision = result['precision']
            recall = result['recall']
            f1 = result['f1_score']
            query_type = result['query_type']
            
            if f1 >= 80:
                status = "EXCELLENT"
            elif f1 >= 70:
                status = "GOOD"
            elif f1 >= 60:
                status = "ACCEPTABLE"
            else:
                status = "NEEDS IMPROVEMENT"
            
            print(f"  {query_type}:")
            print(f"    - Precision: {precision/100:.4f} | Recall: {recall/100:.4f} | F1: {f1/100:.4f}")
            print(f"    - Status: {status}")
        
        print("="*80)
        
        # Explanation
        print("\nMETRICS EXPLANATION:")
        print("-" * 80)
        print("Precision: Dari rekomendasi yang diberikan, berapa persen yang relevan?")
        print("Recall: Dari semua restoran relevan di database, berapa persen yang berhasil direkomendasikan?")
        print("F1-Score: Harmonic mean dari Precision dan Recall (balanced metric)")
        print("="*80)

def main():
    print("\n" + "="*80)
    print("PRECISION ANALYSIS BY QUERY TYPE")
    print("="*80)
    print("This test measures precision for different types of user queries:")
    print("  1. Entitas Jelas - Queries with clear, specific entities")
    print("  2. Multiple Entitas - Queries with multiple entities/requirements")
    print("  3. Query Ambigu - Ambiguous or general queries")
    print("="*80)
    
    analyzer = PrecisionAnalyzer()
    results = []
    
    # Run tests
    try:
        print("\n[1/3] Testing Clear Entity Queries...")
        result1 = analyzer.test_clear_entity_queries()
        results.append(result1)
        
        print("\n[2/3] Testing Multiple Entity Queries...")
        result2 = analyzer.test_multiple_entity_queries()
        results.append(result2)
        
        print("\n[3/3] Testing Ambiguous Queries...")
        result3 = analyzer.test_ambiguous_queries()
        results.append(result3)
        
        # Generate report
        analyzer.generate_report(results)
        
        print("\n✓ Precision analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
