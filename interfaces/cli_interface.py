import sys
import os
from pathlib import Path
from typing import Optional
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from services.chatbot_service import ChatbotService
from utils.logger import get_logger
from config.settings import RESTAURANTS_ENTITAS_CSV
logger = get_logger("cli_interface")
class ChatbotCLI:
    def __init__(self, data_path: Optional[str] = None):
        try:
            self.chatbot = ChatbotService(data_path or str(RESTAURANTS_ENTITAS_CSV))
            self.session_id = None
            self.is_running = False
        except Exception as e:
            logger.error(f"Failed to initialize CLI: {e}")
            sys.exit(1)
    def display_welcome_message(self):
        welcome_text = "Selamat datang di Chatbot Rekomendasi Restoran!"
    def display_help(self):
        help_text = "Perintah yang tersedia:\n"
        help_text += "/help - Menampilkan bantuan ini\n"
        help_text += "/stats - Menampilkan statistik sistem\n"
        help_text += "/history - Menampilkan riwayat percakapan\n"
    def display_statistics(self):

    #         print("\nSTATISTIK SISTEM")

    #             print(f"Total Restoran: {engine_stats.get('total_restaurants', 0)}")
    #             print(f"Rating Rata-rata: {engine_stats.get('average_rating', 0)}")
    #             print(f"Jenis Masakan Unik: {engine_stats.get('unique_cuisines', 0)}")
    #             print(f"Lokasi Unik: {engine_stats.get('unique_locations', 0)}")
    #             print(f"Fitur TF-IDF: {engine_stats.get('tfidf_features', 0)}")

    #             print(f"\nPercakapan Sesi Ini: {chatbot_stats.get('current_session_turns', 0)}")
    #             print(f"Interaksi Pengguna: {chatbot_stats.get('user_profile_interactions', 0)}")
    #             print(f"Sesi Aktif: {chatbot_stats.get('active_sessions', 0)}")

    #         print(f"Error menampilkan statistik: {e}")
    #         logger.error(f"Error displaying statistics: {e}")

        try:
            history = self.chatbot.get_conversation_history(self.session_id)
            if not history:
                return
            for i, interaction in enumerate(history, 1):
                timestamp = interaction['timestamp'][:19].replace('T', ' ')
        except Exception as e:
            logger.error(f"Error displaying history: {e}")
    def handle_special_commands(self, user_input: str) -> bool:
        user_input = user_input.strip()
        if user_input == "/help":
            self.display_help()
            return True
        elif user_input == "/stats":
            self.display_statistics()
            return True
        elif user_input == "/history":
            self.display_history()
            return True
        elif user_input.startswith("/detail "):
            restaurant_name = user_input[8:].strip()
            response = self.chatbot.get_restaurant_details(restaurant_name)
            return True
        elif user_input.startswith("/category "):
            category = user_input[10:].strip()
            response = self.chatbot.get_recommendations_by_category(category)
            return True
        elif user_input in ["/exit", "/quit", "/keluar"]:
            self.stop()
            return True
        return False
    def run(self):
        try:
            self.display_welcome_message()
            self.session_id, greeting = self.chatbot.start_conversation()
            self.is_running = True
            while self.is_running:
                try:
                    user_input = input("\nAnda: ").strip()
                    if not user_input:
                        continue
                    if self.handle_special_commands(user_input):
                        continue
                    response = self.chatbot.process_message(user_input, self.session_id)
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    self.stop()
                    break
                except Exception as e:
                    logger.error(f"Error in conversation loop: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error running CLI: {e}")
        finally:
            self.cleanup()
    def stop(self):
        self.is_running = False
        goodbye_response = "Terima kasih telah menggunakan layanan kami! Sampai jumpa!"
    def cleanup(self):
        try:
            if hasattr(self.chatbot, 'session_manager'):
                self.chatbot.session_manager.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
def main():
    try:
        if not Path(RESTAURANTS_ENTITAS_CSV).exists():
            sys.exit(1)
        cli = ChatbotCLI()
        cli.run()
    except KeyboardInterrupt:
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()