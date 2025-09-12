import unittest
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from services.chatbot_service import ChatbotService
class TestChatbotService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.chatbot = ChatbotService()
        except Exception as e:
            cls.skipTest(cls, f"Cannot initialize chatbot service: {e}")
    def test_start_conversation(self):
        session_id, greeting = self.chatbot.start_conversation()
        self.assertIsInstance(session_id, str)
        self.assertIsInstance(greeting, str)
        self.assertTrue(len(session_id) > 0)
        self.assertTrue(len(greeting) > 0)
    def test_process_message_basic(self):
        session_id, _ = self.chatbot.start_conversation()
        response = self.chatbot.process_message("pizza di kuta", session_id)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        self.assertNotIn("error", response.lower())
    def test_process_message_various_queries(self):
        session_id, _ = self.chatbot.start_conversation()
        test_queries = [
            "seafood murah di gili",
            "tempat romantis untuk dinner",
            "restoran keluarga yang santai", 
            "sushi terenak",
            "italian food dengan pemandangan"
        ]
        for query in test_queries:
            with self.subTest(query=query):
                response = self.chatbot.process_message(query, session_id)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)
    def test_greeting_detection(self):
        session_id, _ = self.chatbot.start_conversation()
        greetings = ["halo", "hai", "hello", "selamat pagi"]
        for greeting in greetings:
            with self.subTest(greeting=greeting):
                response = self.chatbot.process_message(greeting, session_id)
                self.assertIsInstance(response, str)
                self.assertTrue(any(word in response.lower() for word in ["halo", "hai", "selamat", "saya", "bantu"]))
    def test_exit_detection(self):
        session_id, _ = self.chatbot.start_conversation()
        exit_commands = ["keluar", "exit", "selesai", "bye"]
        for exit_cmd in exit_commands:
            with self.subTest(exit_cmd=exit_cmd):
                response = self.chatbot.process_message(exit_cmd, session_id)
                self.assertIsInstance(response, str)
                self.assertTrue(any(word in response.lower() for word in ["terima kasih", "sampai jumpa", "selamat"]))
    def test_get_restaurant_details(self):
        response = self.chatbot.get_restaurant_details("pizza")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    def test_get_recommendations_by_category(self):
        categories = ["italian", "seafood", "kuta", "romantis"]
        for category in categories:
            with self.subTest(category=category):
                response = self.chatbot.get_recommendations_by_category(category)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)
    def test_conversation_history(self):
        session_id, _ = self.chatbot.start_conversation()
        self.chatbot.process_message("pizza di kuta", session_id)
        self.chatbot.process_message("seafood murah", session_id)
        history = self.chatbot.get_conversation_history(session_id)
        self.assertIsInstance(history, list)
        self.assertTrue(len(history) > 0)
        if history:
            turn = history[0]
            self.assertIn('timestamp', turn)
            self.assertIn('user_query', turn)
            self.assertIn('bot_response', turn)
    def test_statistics(self):
        stats = self.chatbot.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('chatbot', stats)
        self.assertIn('recommendation_engine', stats)
        chatbot_stats = stats['chatbot']
        self.assertIn('current_session_turns', chatbot_stats)
        self.assertIn('user_profile_interactions', chatbot_stats)
        self.assertIn('active_sessions', chatbot_stats)
        engine_stats = stats['recommendation_engine']
        self.assertIn('total_restaurants', engine_stats)
        self.assertIn('average_rating', engine_stats)
    def test_empty_message(self):
        session_id, _ = self.chatbot.start_conversation()
        empty_messages = ["", "   ", "\n", "\t"]
        for empty_msg in empty_messages:
            with self.subTest(empty_msg=repr(empty_msg)):
                response = self.chatbot.process_message(empty_msg, session_id)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)
    def test_long_message(self):
        session_id, _ = self.chatbot.start_conversation()
        long_message = "Saya mencari restoran yang menyajikan pizza dengan suasana romantis di area Kuta dengan harga yang tidak terlalu mahal dan memiliki pemandangan yang bagus serta pelayanan yang ramah dan menu yang beragam"
        response = self.chatbot.process_message(long_message, session_id)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    def test_special_characters(self):
        session_id, _ = self.chatbot.start_conversation()
        special_queries = [
            "pizza??? di kuta!!!",
            "restoran @#$% murah",
            "tempat makan (yang bagus)"
        ]
        for query in special_queries:
            with self.subTest(query=query):
                response = self.chatbot.process_message(query, session_id)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)
class TestChatbotIntegration(unittest.TestCase):
    def setUp(self):
        try:
            self.chatbot = ChatbotService()
        except Exception as e:
            self.skipTest(f"Cannot initialize chatbot service: {e}")
    def test_full_conversation_flow(self):
        session_id, greeting = self.chatbot.start_conversation()
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(greeting)
        response1 = self.chatbot.process_message("halo", session_id)
        self.assertIsInstance(response1, str)
        response2 = self.chatbot.process_message("pizza romantis di kuta", session_id)
        self.assertIsInstance(response2, str)
        self.assertTrue(len(response2) > 50)
        response3 = self.chatbot.process_message("bagaimana dengan seafood?", session_id)
        self.assertIsInstance(response3, str)
        history = self.chatbot.get_conversation_history(session_id)
        self.assertGreaterEqual(len(history), 3)
        response4 = self.chatbot.process_message("terima kasih", session_id)
        self.assertIsInstance(response4, str)
        self.assertTrue(any(word in response4.lower() for word in ["terima kasih", "sampai jumpa"]))
    def test_recommendation_quality(self):
        session_id, _ = self.chatbot.start_conversation()
        response = self.chatbot.process_message("pizza italian di kuta", session_id)
        self.assertIn("pizza", response.lower())
        self.assertTrue(any(word in response.lower() for word in ["rating", "⭐", "kecocokan"]))
        self.assertTrue(any(symbol in response for symbol in ["🍽️", "💰", "📍", "✨"]))
    def test_multiple_sessions(self):
        session1_id, _ = self.chatbot.start_conversation("user1")
        session2_id, _ = self.chatbot.start_conversation("user2")
        self.assertNotEqual(session1_id, session2_id)
        response1 = self.chatbot.process_message("pizza di kuta", session1_id)
        response2 = self.chatbot.process_message("seafood di gili", session2_id)
        self.assertIsInstance(response1, str)
        self.assertIsInstance(response2, str)
        history1 = self.chatbot.get_conversation_history(session1_id)
        history2 = self.chatbot.get_conversation_history(session2_id)
        self.assertTrue(len(history1) > 0)
        self.assertTrue(len(history2) > 0)
        self.assertNotEqual(history1[0]['user_query'], history2[0]['user_query'])
if __name__ == '__main__':
    unittest.main(verbosity=2)