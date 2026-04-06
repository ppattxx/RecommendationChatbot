#!/usr/bin/env python3
"""
Test script untuk entity extraction dari user queries

Usage:
    python tests/test_entity_extraction.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.entity_extractor import EntityExtractor
from services.chatbot_service import ChatbotService


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
        
        # Extract entities
        entities = extractor.extract_entities(query)
        print(f"   Entities extracted:")
        for key, values in entities.items():
            if values:
                print(f"   - {key}: {values}")
        
        # Get context
        context = extractor.get_search_context(query, entities)
        print(f"\n   Search Context:")
        print(f"   - Intent: {context['intent']}")
        print(f"   - Primary entity type: {context['primary_entity_type']}")
        print(f"   - Has location: {context['has_location']}")
        print(f"   - Has cuisine: {context['has_cuisine']}")
        print(f"   - Has menu: {context['has_menu']}")
        print(f"   - Has mood: {context['has_mood']}")
        
        # Get summary
        summary = extractor.get_entity_summary(entities)
        if summary:
            print(f"\n   Entity Summary:")
            for line in summary.split('\n'):
                print(f"   {line}")


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
        
        # Extract intent and entities
        intent, entities = chatbot._extract_intent_and_entities(query)
        print(f"   Intent: {intent}")
        print(f"   Entities:")
        for key, values in entities.items():
            if values:
                print(f"   - {key}: {values}")
        
        # Get entity summary
        summary = chatbot._get_entity_summary(entities)
        if summary:
            print(f"\n   Entity Summary for User:")
            for line in summary.split('\n'):
                print(f"   {line}")


def test_entity_patterns():
    """Test entity patterns yang dibangun dari dataset"""
    print("\n" + "=" * 80)
    print("TESTING ENTITY PATTERNS FROM DATASET")
    print("=" * 80)
    
    extractor = EntityExtractor()
    
    print("\nAvailable entity patterns:")
    if extractor.entity_patterns:
        for pattern_type, pattern_data in extractor.entity_patterns.items():
            print(f"\n{pattern_type.upper()}:")
            for key, values in pattern_data.items():
                if isinstance(values, list) and values:
                    print(f"  {key}: ({len(values)} items) {values[:10]}")
                    if len(values) > 10:
                        print(f"           ... and {len(values) - 10} more")


def test_matching():
    """Test entity matching dengan restaurants"""
    print("\n" + "=" * 80)
    print("TESTING ENTITY MATCHING WITH RESTAURANTS")
    print("=" * 80)
    
    import pandas as pd
    from utils.entity_extractor import EntityMatcher
    
    # Load data
    data_path = Path(__file__).parent.parent / "data" / "restaurants_entitas.csv"
    df = pd.read_csv(data_path)
    
    matcher = EntityMatcher(df)
    
    test_entities = [
        {
            'cuisine': ['pizza'],
            'location': ['Kuta'],
            'menu': [],
            'mood': [],
            'features': [],
            'price_range': []
        },
        {
            'cuisine': ['seafood'],
            'location': ['Gili Trawangan'],
            'menu': [],
            'mood': ['romantic'],
            'features': [],
            'price_range': ['mahal']
        },
        {
            'cuisine': [],
            'location': [],
            'menu': ['nasi goreng'],
            'mood': ['healthy'],
            'features': [],
            'price_range': ['murah']
        }
    ]
    
    for i, entities in enumerate(test_entities, 1):
        print(f"\n{i}. ENTITIES: {entities}")
        
        matching_indices = matcher.find_matching_restaurants(entities, match_threshold=0.3)
        print(f"   Found {len(matching_indices)} matching restaurants")
        
        if matching_indices:
            print(f"   Top matches:")
            for idx in matching_indices[:5]:
                rest = df.iloc[idx]
                print(f"   - {rest['name']} (Rating: {rest['rating']})")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("ENTITY EXTRACTION TEST SUITE")
    print("=" * 80)
    
    try:
        test_entity_extractor()
        test_entity_patterns()
        test_chatbot_service()
        test_matching()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
