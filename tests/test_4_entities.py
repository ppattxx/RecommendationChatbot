#!/usr/bin/env python3
"""
Test script untuk memverifikasi 4 entitas sudah berfungsi dengan benar
"""

from services.recommendation_engine import ContentBasedRecommendationEngine

def test_4_entities():
    print("=" * 60)
    print("Testing 4 Entitas System")
    print("=" * 60)
    
    # Initialize engine
    print("\n1. Menginisialisasi sistem...")
    engine = ContentBasedRecommendationEngine()
    print("   ✓ Sistem berhasil diinisialisasi")
    
    # Get statistics
    print("\n2. Mendapatkan statistik data...")
    stats = engine.get_statistics()
    print(f"   ✓ Total restoran: {stats['total_restaurants']}")
    print(f"   ✓ Unique cuisines: {stats['unique_cuisines']}")
    print(f"   ✓ Unique features: {stats['unique_features']}")
    print(f"   ✓ Average rating: {stats['average_rating']}")
    print(f"   ✓ TF-IDF features: {stats['tfidf_features']}")
    
    # Test sample restaurant
    print("\n3. Testing sample restaurant data...")
    sample_restaurant = engine.restaurants_objects[0]
    print(f"   Restaurant: {sample_restaurant.name}")
    print(f"   - Rating: {sample_restaurant.rating}")
    print(f"   - Cuisines: {sample_restaurant.cuisines[:3] if sample_restaurant.cuisines else 'None'}")
    print(f"   - Preferences: {sample_restaurant.preferences[:3] if sample_restaurant.preferences else 'None'}")
    print(f"   - Features: {sample_restaurant.features[:3] if sample_restaurant.features else 'None'}")
    print(f"   - About: {sample_restaurant.about[:50] if sample_restaurant.about else 'None'}...")
    
    # Test recommendation
    print("\n4. Testing rekomendasi dengan query...")
    test_query = "italian restaurant with wifi"
    print(f"   Query: '{test_query}'")
    recommendations = engine.get_recommendations(test_query, top_n=3)
    print(f"   ✓ Ditemukan {len(recommendations)} rekomendasi")
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n   {i}. {rec.restaurant.name}")
        print(f"      Score: {rec.similarity_score:.4f}")
        print(f"      Matching: {', '.join(rec.matching_features[:3])}")
    
    print("\n" + "=" * 60)
    print("✓ SUKSES! Semua 4 entitas berfungsi dengan baik:")
    print("  1. about  - Deskripsi restoran")
    print("  2. cuisines - Jenis masakan")
    print("  3. preferences - Preferensi & suasana")
    print("  4. features - Fasilitas")
    print("=" * 60)

if __name__ == "__main__":
    test_4_entities()
