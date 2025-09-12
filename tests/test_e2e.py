import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch
import tempfile
import json
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from main import main, check_requirements
from interfaces.cli_interface import ChatbotCLI
from interfaces.web_interface import app
from services.chatbot_service import ChatbotService
class TestSystemRequirements(unittest.TestCase):
    def test_check_requirements(self):
        try:
            missing = check_requirements()
            self.assertIsInstance(missing, list)
        except Exception as e:
            self.fail(f"check_requirements raised exception: {e}")
    def test_data_files_exist(self):
        data_dir = project_root / "data"
        required_files = [
            "restaurants.csv",
            "restaurants_processed.csv"
        ]
        self.assertTrue(data_dir.exists(), "Data directory should exist")
        for filename in required_files:
            file_path = data_dir / filename
            self.assertTrue(file_path.exists(), f"Required file {filename} should exist")
    def test_config_import(self):
        try:
            from config.settings import MODEL_CONFIG, CHATBOT_CONFIG, ENTITY_KEYWORDS
            self.assertIsInstance(MODEL_CONFIG, dict)
            self.assertIsInstance(CHATBOT_CONFIG, dict)
            self.assertIsInstance(ENTITY_KEYWORDS, dict)
            self.assertIn('tfidf_params', MODEL_CONFIG)
            self.assertIn('greeting_responses', CHATBOT_CONFIG)
            self.assertIn('location', ENTITY_KEYWORDS)
        except ImportError as e:
            self.fail(f"Cannot import configuration: {e}")
class TestCLIInterface(unittest.TestCase):
    def setUp(self):
        try:
            self.cli = ChatbotCLI()
        except Exception as e:
            self.skipTest(f"Cannot initialize CLI: {e}")
    @patch('builtins.input', side_effect=['halo', 'pizza di kuta', 'keluar'])
    @patch('builtins.print')
    def test_cli_conversation_flow(self, mock_print, mock_input):
        try:
            self.cli.chatbot_service = ChatbotService()
            session_id, greeting = self.cli.chatbot_service.start_conversation()
            response1 = self.cli.chatbot_service.process_message("halo", session_id)
            response2 = self.cli.chatbot_service.process_message("pizza di kuta", session_id)
            response3 = self.cli.chatbot_service.process_message("keluar", session_id)
            self.assertIsInstance(response1, str)
            self.assertIsInstance(response2, str)
            self.assertIsInstance(response3, str)
        except Exception as e:
            self.fail(f"CLI conversation flow failed: {e}")
    def test_cli_special_commands(self):
        help_response = self.cli.handle_special_commands('/help')
        self.assertTrue(help_response)
        stats_response = self.cli.handle_special_commands('/stats')
        self.assertTrue(stats_response)
        history_response = self.cli.handle_special_commands('/history')
        self.assertTrue(history_response)
        normal_response = self.cli.handle_special_commands('normal message')
        self.assertFalse(normal_response)
class TestWebInterface(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    def test_web_app_creation(self):
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Chatbot', response.data)
    def test_start_conversation_api(self):
        response = self.client.post('/api/start_conversation')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('session_id', data)
        self.assertIn('greeting', data)
        self.assertIsInstance(data['session_id'], str)
        self.assertIsInstance(data['greeting'], str)
    def test_send_message_api(self):
        start_response = self.client.post('/api/start_conversation')
        start_data = json.loads(start_response.data)
        session_id = start_data['session_id']
        message_response = self.client.post('/api/send_message', 
                                          json={
                                              'message': 'pizza di kuta',
                                              'session_id': session_id
                                          })
        self.assertEqual(message_response.status_code, 200)
        message_data = json.loads(message_response.data)
        self.assertIn('response', message_data)
        self.assertIsInstance(message_data['response'], str)
    def test_send_message_no_session(self):
        response = self.client.post('/api/send_message', 
                                  json={'message': 'test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
    def test_send_message_invalid_json(self):
        response = self.client.post('/api/send_message', 
                                  data='invalid json',
                                  content_type='application/json')
        self.assertIn(response.status_code, [400, 200])
class TestMainApplication(unittest.TestCase):
    def test_main_with_check_mode(self):
        test_args = ['main.py', '--check']
        with patch('sys.argv', test_args):
            with patch('builtins.print') as mock_print:
                try:
                    with patch('main.check_requirements', return_value=[]):
                        result = main()
                except SystemExit:
                    pass
    def test_main_with_invalid_mode(self):
        test_args = ['main.py', '--mode', 'invalid']
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit):
                main()
class TestEndToEndScenarios(unittest.TestCase):
    def setUp(self):
        try:
            self.chatbot = ChatbotService()
        except Exception as e:
            self.skipTest(f"Cannot initialize chatbot service: {e}")
    def test_tourist_scenario(self):
        session_id, greeting = self.chatbot.start_conversation("tourist")
        response1 = self.chatbot.process_message("hello", session_id)
        self.assertIsInstance(response1, str)
        response2 = self.chatbot.process_message("I want pizza in Kuta", session_id)
        self.assertIsInstance(response2, str)
        self.assertTrue(len(response2) > 50)
        response3 = self.chatbot.process_message("how about seafood?", session_id)
        self.assertIsInstance(response3, str)
        response4 = self.chatbot.process_message("thank you", session_id)
        self.assertIsInstance(response4, str)
        history = self.chatbot.get_conversation_history(session_id)
        self.assertGreaterEqual(len(history), 4)
    def test_local_user_scenario(self):
        session_id, greeting = self.chatbot.start_conversation("local_user")
        response1 = self.chatbot.process_message("halo", session_id)
        self.assertIsInstance(response1, str)
        response2 = self.chatbot.process_message("makanan halal yang enak di Ubud", session_id)
        self.assertIsInstance(response2, str)
        response3 = self.chatbot.process_message("yang harganya tidak terlalu mahal", session_id)
        self.assertIsInstance(response3, str)
        response4 = self.chatbot.process_message("bisa kasih detail alamat?", session_id)
        self.assertIsInstance(response4, str)
        history = self.chatbot.get_conversation_history(session_id)
        self.assertGreaterEqual(len(history), 4)
    def test_business_user_scenario(self):
        session_id, greeting = self.chatbot.start_conversation("business_user")
        response1 = self.chatbot.process_message("tempat makan untuk meeting bisnis", session_id)
        self.assertIsInstance(response1, str)
        response2 = self.chatbot.process_message("yang tenang dan profesional di Sanur", session_id)
        self.assertIsInstance(response2, str)
        response3 = self.chatbot.process_message("dengan wifi yang bagus", session_id)
        self.assertIsInstance(response3, str)
        self.assertTrue(len(response2) > 30)
    def test_family_scenario(self):
        session_id, greeting = self.chatbot.start_conversation("family")
        response1 = self.chatbot.process_message("restoran family friendly di Nusa Dua", session_id)
        self.assertIsInstance(response1, str)
        response2 = self.chatbot.process_message("yang ada menu untuk anak-anak", session_id)
        self.assertIsInstance(response2, str)
        self.assertIsInstance(response2, str)
        self.assertTrue(len(response2) > 20)
    def test_error_recovery_scenario(self):
        session_id, greeting = self.chatbot.start_conversation("error_test")
        response1 = self.chatbot.process_message("asdfghjkl", session_id)
        self.assertIsInstance(response1, str)
        response2 = self.chatbot.process_message("pizza di kuta", session_id)
        self.assertIsInstance(response2, str)
        self.assertTrue(len(response2) > 20)
        response3 = self.chatbot.process_message("terima kasih", session_id)
        self.assertIsInstance(response3, str)
class TestSystemPerformance(unittest.TestCase):
    def setUp(self):
        try:
            self.chatbot = ChatbotService()
        except Exception as e:
            self.skipTest(f"Cannot initialize chatbot service: {e}")
    def test_response_time(self):
        import time
        session_id, _ = self.chatbot.start_conversation()
        start_time = time.time()
        response = self.chatbot.process_message("pizza di kuta", session_id)
        end_time = time.time()
        response_time = end_time - start_time
        self.assertLess(response_time, 5.0, "Response should be within 5 seconds")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    def test_multiple_concurrent_sessions(self):
        import threading
        import time
        results = []
        def create_session_and_query():
            try:
                session_id, _ = self.chatbot.start_conversation()
                response = self.chatbot.process_message("seafood di gili", session_id)
                results.append({
                    'session_id': session_id,
                    'response': response,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'error': str(e),
                    'success': False
                })
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_session_and_query)
            threads.append(thread)
        start_time = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        end_time = time.time()
        self.assertEqual(len(results), 3, "All sessions should complete")
        successful_results = [r for r in results if r.get('success', False)]
        self.assertGreater(len(successful_results), 0, "At least one session should succeed")
        total_time = end_time - start_time
        self.assertLess(total_time, 15.0, "All sessions should complete within 15 seconds")
if __name__ == '__main__':
    unittest.main(verbosity=2)