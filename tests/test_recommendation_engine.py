import unittest
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from services.recommendation_engine import ContentBasedRecommendationEngine
from models.data_models import Restaurant
from utils.text_processing import EntityExtractor
class TestRecommendationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.engine = ContentBasedRecommendationEngine()
        except Exception as e:
            cls.skipTest(cls, f"Cannot initialize engine: {e}")
    def test_initialization(self):
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.restaurants_objects)
        self.assertIsNotNone(self.engine.tfidf_matrix)
        self.assertTrue(len(self.engine.restaurants_objects) > 0)
    def test_get_recommendations_basic(self):
        query = "pizza di kuta"
        recommendations = self.engine.get_recommendations(query, top_n=3)
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) <= 3)
        if recommendations:
            rec = recommendations[0]
            self.assertTrue(hasattr(rec, 'restaurant'))
            self.assertTrue(hasattr(rec, 'similarity_score'))
            self.assertIsInstance(rec.similarity_score, float)
            self.assertTrue(0 <= rec.similarity_score <= 1)
    def test_get_recommendations_various_queries(self):
        test_queries = [
            "seafood murah",
            "restoran romantis",
            "tempat makan keluarga",
            "italian food di senggigi",
            "sushi dengan pemandangan"
        ]
        for query in test_queries:
            with self.subTest(query=query):
                recommendations = self.engine.get_recommendations(query, top_n=2)
                self.assertIsInstance(recommendations, list)
    def test_get_similar_restaurants(self):
        if self.engine.restaurants_objects:
            restaurant_id = self.engine.restaurants_objects[0].id
            similar = self.engine.get_similar_restaurants(restaurant_id, top_n=3)
            self.assertIsInstance(similar, list)
            self.assertTrue(len(similar) <= 3)
            similar_ids = [rec.restaurant.id for rec in similar]
            self.assertNotIn(restaurant_id, similar_ids)
    def test_get_recommendations_by_category(self):
        categories = ["italian", "kuta", "romantis", "seafood"]
        for category in categories:
            with self.subTest(category=category):
                recommendations = self.engine.get_recommendations_by_category(category, top_n=2)
                self.assertIsInstance(recommendations, list)
    def test_get_restaurant_by_id(self):
        if self.engine.restaurants_objects:
            restaurant = self.engine.restaurants_objects[0]
            found_restaurant = self.engine.get_restaurant_by_id(restaurant.id)
            self.assertIsNotNone(found_restaurant)
            self.assertEqual(found_restaurant.id, restaurant.id)
            self.assertEqual(found_restaurant.name, restaurant.name)
    def test_get_statistics(self):
        stats = self.engine.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_restaurants', stats)
        self.assertIn('average_rating', stats)
        self.assertIn('unique_cuisines', stats)
        self.assertIn('unique_locations', stats)
        self.assertTrue(stats['total_restaurants'] > 0)
        self.assertTrue(0 <= stats['average_rating'] <= 5)
        self.assertTrue(stats['unique_cuisines'] >= 0)
    def test_empty_query(self):
        recommendations = self.engine.get_recommendations("", top_n=3)
        self.assertIsInstance(recommendations, list)
    def test_nonsense_query(self):
        nonsense_queries = [
            "xyzabc123",
            "qwerty asdfgh",
            "????????????"
        ]
        for query in nonsense_queries:
            with self.subTest(query=query):
                recommendations = self.engine.get_recommendations(query, top_n=3)
                self.assertIsInstance(recommendations, list)
class TestEntityExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = EntityExtractor()
    def test_extract_entities_location(self):
        queries_with_locations = [
            ("pizza di kuta", ["kuta"]),
            ("seafood gili trawangan", ["gili trawangan", "gili"]),
            ("restoran senggigi lombok", ["senggigi", "lombok"])
        ]
        for query, expected_locations in queries_with_locations:
            with self.subTest(query=query):
                entities = self.extractor.extract_entities(query)
                if 'lokasi' in entities:
                    found_locations = entities['lokasi']
                    self.assertTrue(any(loc in found_locations for loc in expected_locations))
    def test_extract_entities_cuisine(self):
        queries_with_cuisines = [
            ("pizza italian", ["italian"]),
            ("sushi japanese", ["japanese", "jepang"]),
            ("chinese food", ["chinese", "cina"])
        ]
        for query, expected_cuisines in queries_with_cuisines:
            with self.subTest(query=query):
                entities = self.extractor.extract_entities(query)
                if 'jenis_makanan' in entities:
                    found_cuisines = entities['jenis_makanan']
                    self.assertTrue(any(cuisine in found_cuisines for cuisine in expected_cuisines))
    def test_extract_entities_menu(self):
        queries_with_menus = [
            ("pizza margherita", ["pizza"]),
            ("fresh sushi", ["sushi"]),
            ("grilled seafood", ["seafood"])
        ]
        for query, expected_menus in queries_with_menus:
            with self.subTest(query=query):
                entities = self.extractor.extract_entities(query)
                if 'menu' in entities:
                    found_menus = entities['menu']
                    self.assertTrue(any(menu in found_menus for menu in expected_menus))
    def test_extract_entities_preferences(self):
        queries_with_preferences = [
            ("tempat romantis", ["romantis"]),
            ("suasana santai", ["santai"]),
            ("untuk keluarga", ["keluarga"])
        ]
        for query, expected_prefs in queries_with_preferences:
            with self.subTest(query=query):
                entities = self.extractor.extract_entities(query)
                if 'preferensi' in entities:
                    found_prefs = entities['preferensi']
                    self.assertTrue(any(pref in found_prefs for pref in expected_prefs))
    def test_extract_intent(self):
        queries_with_intents = [
            ("cari pizza", "cari_restoran"),
            ("rekomendasi tempat makan", "cari_restoran"),
            ("halo", "greeting"),
            ("terima kasih", "goodbye")
        ]
        for query, expected_intent in queries_with_intents:
            with self.subTest(query=query):
                intent = self.extractor.extract_intent(query)
                self.assertEqual(intent, expected_intent)
    def test_empty_query(self):
        entities = self.extractor.extract_entities("")
        self.assertIsInstance(entities, dict)
        intent = self.extractor.extract_intent("")
        self.assertIsInstance(intent, str)
if __name__ == '__main__':
    unittest.main(verbosity=2)