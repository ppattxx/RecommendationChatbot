import unittest
import sys
import os
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
def run_all_tests():
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    print("=" * 70)
    print("CHATBOT REKOMENDASI - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    result = runner.run(suite)
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0] if 'AssertionError: ' in traceback else 'See details above'}")
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\n')[-2] if traceback.split('\n') else 'Unknown error'}")
    print()
    return result.wasSuccessful()
def run_specific_test(test_module):
    loader = unittest.TestLoader()
    try:
        suite = loader.loadTestsFromName(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running test {test_module}: {e}")
        return False
def run_quick_tests():
    loader = unittest.TestLoader()
    test_modules = [
        'test_recommendation_engine',
        'test_chatbot_service'
    ]
    suite = unittest.TestSuite()
    for module in test_modules:
        try:
            module_suite = loader.loadTestsFromName(module)
            suite.addTest(module_suite)
        except Exception as e:
            print(f"Warning: Could not load {module}: {e}")
    runner = unittest.TextTestRunner(verbosity=2)
    print("=" * 70)
    print("CHATBOT REKOMENDASI - QUICK TEST SUITE")
    print("=" * 70)
    print()
    result = runner.run(suite)
    print()
    print("=" * 70)
    print(f"Quick tests completed: {result.testsRun} tests run")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    print("=" * 70)
    return result.wasSuccessful()
def check_test_environment():
    print("Checking test environment...")
    issues = []
    if sys.version_info < (3, 8):
        issues.append(f"Python version {sys.version_info.major}.{sys.version_info.minor} is too old. Need 3.8+")
    required_dirs = ['data', 'src', 'config', 'models', 'services', 'utils', 'interfaces']
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            issues.append(f"Required directory missing: {dir_name}")
    required_files = [
        'data/restaurants.csv',
        'data/restaurants_processed.csv',
        'config/settings.py',
        'main.py'
    ]
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            issues.append(f"Required file missing: {file_path}")
    try:
        from services.chatbot_service import ChatbotService
        from services.recommendation_engine import ContentBasedRecommendationEngine
        from config.settings import MODEL_CONFIG, CHATBOT_CONFIG
    except ImportError as e:
        issues.append(f"Import error: {e}")
    if issues:
        print("❌ Test environment issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Test environment OK")
        return True
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Chatbot Test Runner')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick tests only (skip end-to-end tests)')
    parser.add_argument('--test', type=str, 
                       help='Run specific test module (e.g., test_recommendation_engine)')
    parser.add_argument('--check', action='store_true',
                       help='Check test environment only')
    args = parser.parse_args()
    if args.check:
        success = check_test_environment()
        sys.exit(0 if success else 1)
    if not check_test_environment():
        print("\n❌ Test environment check failed. Please fix issues before running tests.")
        sys.exit(1)
    print()
    if args.test:
        success = run_specific_test(args.test)
    elif args.quick:
        success = run_quick_tests()
    else:
        success = run_all_tests()
    sys.exit(0 if success else 1)