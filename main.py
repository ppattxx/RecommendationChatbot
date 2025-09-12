import sys
import argparse
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
from interfaces.cli_interface import ChatbotCLI
from services.chatbot_service import ChatbotService
from utils.logger import get_logger
from config.settings import RESTAURANTS_ENTITAS_CSV
logger = get_logger("main_app")
def run_cli_interface(data_path: str = None):
    try:
        cli = ChatbotCLI(data_path)
        cli.run()
    except Exception as e:
        print(f"Error menjalankan CLI: {e}")
        logger.error(f"Error running CLI: {e}")
        sys.exit(1)
def run_web_interface(data_path: str = None):
    try:
        print("Memulai Chatbot Rekomendasi Restoran (Web)")
        from interfaces.web_interface import run_web_interface
        run_web_interface()
    except ImportError as e:
        print("Flask tidak terinstall. Install dependencies dengan:")
        print("   pip install flask flask-cors")
        logger.error(f"Flask import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error menjalankan web interface: {e}")
        logger.error(f"Error running web interface: {e}")
        sys.exit(1)
def run_test_mode(data_path: str = None):
    try:
        print("Mode Testing - Chatbot Rekomendasi Restoran")
        print("=" * 50)
        print("Menginisialisasi service...")
        chatbot = ChatbotService(data_path)
        session_id, greeting = chatbot.start_conversation()
        print(f"Sesi dimulai: {session_id}")
        print(f"Greeting: {greeting}\n")
        test_queries = [
            "pizza di kuta yang romantis",
            "seafood murah di gili trawangan", 
            "tempat makan keluarga yang santai",
            "sushi dengan pemandangan bagus",
            "restoran italian di senggigi"
        ]
        print("Testing dengan query contoh:")
        print("-" * 30)
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Test {i}] Query: '{query}'")
            response = chatbot.process_message(query, session_id)
            print(f"Response: {response[:200]}...")
            print("-" * 30)
        print("\nStatistik Sistem:")
        stats = chatbot.get_statistics()
        for category, data in stats.items():
            print(f"\n{category.upper()}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        print("\nTesting selesai!")
    except Exception as e:
        print(f"Error dalam mode testing: {e}")
        logger.error(f"Error in test mode: {e}")
        sys.exit(1)
def check_requirements():
    issues = []
    if not Path(RESTAURANTS_ENTITAS_CSV).exists():
        issues.append(f"File data tidak ditemukan: {RESTAURANTS_ENTITAS_CSV}")
        issues.append("Jalankan: python src/train_data.py untuk memproses data")
    if sys.version_info < (3, 8):
        issues.append(f"Python {sys.version_info.major}.{sys.version_info.minor} terdeteksi. Minimum Python 3.8 diperlukan")
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'Sastrawi', 'unidecode'
    ]
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    if missing_packages:
        issues.append(f"Package tidak ditemukan: {', '.join(missing_packages)}")
        issues.append("Install dengan: pip install -r requirements.txt")
    if issues:
        print("Ditemukan masalah:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    return True
def main():
    parser = argparse.ArgumentParser(
        description="Chatbot Rekomendasi Restoran - Content-Based Filtering System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Contoh penggunaan:\n  python main.py --mode cli\n  python main.py --mode web\n  python main.py --mode test"
    )
    parser.add_argument(
        '--mode', 
        choices=['cli', 'web', 'test'],
        default='cli',
        help='Mode operasi (default: cli)'
    )
    parser.add_argument(
        '--data',
        type=str,
        help='Path ke file data (opsional)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Periksa persyaratan sistem'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Output verbose'
    )
    args = parser.parse_args()
    
    if args.check:
        check_requirements()
        return
    if not check_requirements():
        print("\nPerbaiki masalah di atas sebelum menjalankan aplikasi.")
        sys.exit(1)
    data_path = args.data or str(RESTAURANTS_ENTITAS_CSV)
    try:
        if args.mode == 'cli':
            run_cli_interface(data_path)
        elif args.mode == 'web':
            run_web_interface(data_path)
        elif args.mode == 'test':
            run_test_mode(data_path)
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh pengguna.")
    except Exception as e:
        print(f"\nError fatal: {e}")
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()