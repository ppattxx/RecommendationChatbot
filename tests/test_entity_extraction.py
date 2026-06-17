#!/usr/bin/env python3
"""
Test script untuk entity extraction dari user queries (backend.app version).

Usage:
    python tests/test_entity_extraction.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.utils.text_processing import EntityExtractor
from backend.app.services.chatbot_engine import ChatbotService


def test_entity_extractor():
    """Test EntityExtractor dengan berbagai queries"""
    print("=" * 80)
    print("TESTING ENTITY EXTRACTOR")
    print("=" * 80)

    extractor = EntityExtractor()

    test_queries = [
        "Cari pizza di Kuta",
        "Sushi murah di Senggigi",
        "Restoran romantic dengan seafood",
        "Makanan sehat di Lombok",
        "Tempat makan keluarga yang nyaman",
        "Tempat fine dining di Gili Trawangan",
        "Burger dengan harga terjangkau",
        "Restoran dengan suasana sunset di pantai",
        "Nasi goreng di Pemenang yang murah",
        "Tempat makan dengan view bagus",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. QUERY: '{query}'")
        print("-" * 80)

        entities = extractor.extract_entities(query)
        print("   Entities extracted:")
        if not entities:
            print("   - (none)")
        for key, values in entities.items():
            if values:
                print(f"   - {key}: {values}")

        intent = extractor.extract_intent(query)
        print(f"\n   Intent: {intent}")


def test_chatbot_service():
    """Test ChatbotService integration dengan entity extraction"""
    print("\n" + "=" * 80)
    print("TESTING CHATBOT SERVICE INTEGRATION")
    print("=" * 80)

    chatbot = ChatbotService()

    test_queries = [
        "Cari pizza di Kuta",
        "Sushi murah",
        "Seafood romantis",
        "Makan sehat untuk keluarga",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. USER QUERY: '{query}'")
        print("-" * 80)

        intent, entities = chatbot._extract_intent_and_entities(query)
        print(f"   Intent: {intent}")
        print("   Entities:")
        if not entities:
            print("   - (none)")
        for key, values in entities.items():
            if values:
                print(f"   - {key}: {values}")


def test_location_and_cuisine_helpers():
    """Test helper methods for key entity types."""
    print("\n" + "=" * 80)
    print("TESTING ENTITY HELPER METHODS")
    print("=" * 80)

    extractor = EntityExtractor()
    samples = [
        "pizza di kuta",
        "sushi gili trawangan",
        "halal food mataram",
    ]

    for i, query in enumerate(samples, 1):
        locs = extractor.get_location_entities(query)
        cuisines = extractor.get_cuisine_entities(query)
        print(f"\n{i}. {query}")
        print(f"   locations: {locs}")
        print(f"   cuisines: {cuisines}")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("ENTITY EXTRACTION TEST SUITE")
    print("=" * 80)

    try:
        test_entity_extractor()
        test_chatbot_service()
        test_location_and_cuisine_helpers()

        print("\n" + "=" * 80)
        print("OK: ALL TESTS COMPLETED")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
