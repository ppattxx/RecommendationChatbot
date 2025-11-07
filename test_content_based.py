"""
Script untuk testing apakah content-based filtering berjalan dengan benar
"""
from services.recommendation_engine import ContentBasedRecommendationEngine
from services.chatbot_service import ChatbotService

print("=" * 70)
print("TESTING CONTENT-BASED FILTERING")
print("=" * 70)

# Test 1: Direct Engine Test
print("\n### TEST 1: Direct ContentBasedRecommendationEngine ###\n")
engine = ContentBasedRecommendationEngine()

print("Query: 'seafood di senggigi'")
recs1 = engine.get_recommendations('seafood di senggigi', top_n=5)
print(f"Found {len(recs1)} recommendations")
for i, rec in enumerate(recs1[:3], 1):
    print(f"{i}. {rec.restaurant.name} - Score: {rec.similarity_score:.3f}")
    print(f"   Cuisines: {rec.restaurant.entitas_jenis_makanan}")
    print(f"   Location: {rec.restaurant.entitas_lokasi}")
    print(f"   Matching: {rec.matching_features}")
    print()

print("\nQuery: 'pizza yang enak'")
recs2 = engine.get_recommendations('pizza yang enak', top_n=5)
print(f"Found {len(recs2)} recommendations")
for i, rec in enumerate(recs2[:3], 1):
    print(f"{i}. {rec.restaurant.name} - Score: {rec.similarity_score:.3f}")
    print(f"   Cuisines: {rec.restaurant.entitas_jenis_makanan}")
    print(f"   Location: {rec.restaurant.entitas_lokasi}")
    print(f"   Matching: {rec.matching_features}")
    print()

# Test 2: Through ChatbotService
print("\n### TEST 2: Through ChatbotService Integration ###\n")
bot = ChatbotService()
session_id, _ = bot.start_conversation(device_token='test_debug')

print("Query: 'seafood di senggigi yang murah'")
response1 = bot.process_message('seafood di senggigi yang murah', session_id)
print("Response:")
print(response1)
print()

print("\nQuery: 'pizza yang enak'")
response2 = bot.process_message('pizza yang enak', session_id)
print("Response:")
print(response2)
print()

# Test 3: Check restaurants data
print("\n### TEST 3: Check Available Restaurants ###\n")
all_restaurants = engine.get_all_restaurants()
print(f"Total restaurants in engine: {len(all_restaurants)}")

# Check for seafood restaurants
seafood_count = 0
pizza_count = 0
for r in all_restaurants:
    cuisines_str = ' '.join(r.entitas_jenis_makanan).lower()
    if 'seafood' in cuisines_str or 'sea food' in cuisines_str:
        seafood_count += 1
    if 'pizza' in cuisines_str or 'italian' in cuisines_str:
        pizza_count += 1

print(f"Restaurants with Seafood cuisine: {seafood_count}")
print(f"Restaurants with Pizza/Italian cuisine: {pizza_count}")

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)
