"""
API Routes untuk Recommendations functionality
Endpoint: GET /api/recommendations
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
import json
from backend.models.database import db, ChatHistory, UserSession
from services.recommendation_engine import ContentBasedRecommendationEngine
from utils.logger import get_logger

logger = get_logger("recommendations_routes")

recommendations_bp = Blueprint('recommendations', __name__)

recommendation_engine = None
mock_engine = None

def get_recommendation_engine():
    """Get or create recommendation engine instance"""
    global recommendation_engine
    if recommendation_engine is None:
        try:
            # Try to use real ContentBasedRecommendationEngine with TF-IDF
            csv_path = str(project_root / 'data' / 'restaurants_entitas.csv')
            logger.info(f"Loading recommendation engine from {csv_path}")
            recommendation_engine = ContentBasedRecommendationEngine(data_path=csv_path)
            logger.info("ContentBasedRecommendationEngine initialized with TF-IDF")
        except Exception as e:
            logger.error(f"Failed to initialize ContentBasedRecommendationEngine: {e}", exc_info=True)
            logger.info("Falling back to MockRecommendationEngine")
            try:
                recommendation_engine = get_mock_engine()
            except Exception as mock_error:
                logger.error(f"Failed to initialize MockRecommendationEngine: {mock_error}", exc_info=True)
                recommendation_engine = None
    return recommendation_engine

def get_mock_engine():
    """Get or create mock recommendation engine instance"""
    global mock_engine
    if mock_engine is None:
        mock_engine = MockRecommendationEngine()
        logger.info("MockRecommendationEngine initialized")
    return mock_engine


class MockRecommendationEngine:
    """Mock recommendation engine untuk testing"""
    
    def __init__(self):
        """Initialize and load restaurant data from CSV"""
        self.restaurants_data = self._load_restaurants_from_csv()
        logger.info(f"Loaded {len(self.restaurants_data)} restaurants from CSV")
    
    def _load_restaurants_from_csv(self):
        """Load restaurant data from CSV file with preprocessed content"""
        try:
            # Use main CSV with 4 entities
            csv_path = project_root / 'data' / 'restaurants_entitas.csv'
            df = pd.read_csv(csv_path)
            
            restaurants = []
            for idx, row in df.iterrows():
                try:
                    # Parse cuisines from string to list
                    cuisines = []
                    if pd.notna(row['cuisines']):
                        try:
                            cuisines = eval(row['cuisines']) if isinstance(row['cuisines'], str) else []
                        except:
                            cuisines = []
                    cuisine_str = ', '.join(cuisines[:3]) if cuisines else 'Restaurant'
                    
                    # Determine category based on cuisines
                    category = self._determine_category(cuisines)
                    
                    # Extract location from address
                    location = self._extract_location(row['address'])
                
                    # Parse popular dishes safely
                    popular_dishes = []
                    if pd.notna(row.get('preferences')):
                        try:
                            popular_dishes = eval(row['preferences'])[:5] if isinstance(row['preferences'], str) else []
                        except:
                            popular_dishes = []
                    
                    restaurant = {
                        'id': int(row['id']),
                        'name': str(row['name']) if pd.notna(row['name']) else 'Unknown',
                        'location': location,
                        'rating': float(row['rating']) if pd.notna(row['rating']) else 4.0,
                        'price_range': str(row['price_range']) if pd.notna(row['price_range']) else '$$',
                        'cuisine': cuisine_str,
                        'image_url': str(row['img1_url']) if pd.notna(row['img1_url']) else '',
                        'description': (str(row['about'])[:200] + '...') if pd.notna(row['about']) and isinstance(row['about'], str) and len(row['about']) > 200 else (str(row['about']) if pd.notna(row['about']) and isinstance(row['about'], str) else ''),
                        'opening_hours': self._get_opening_hours(row),
                        'popular_dishes': popular_dishes,
                        'category': category,
                        'personalization_score': 0,
                        'url': str(row['url']) if pd.notna(row.get('url')) else '',
                        'address': str(row['address']) if pd.notna(row['address']) else '',
                        'konten_stemmed': str(row['konten_stemmed']) if pd.notna(row.get('konten_stemmed')) else ''  # For content-based filtering
                    }
                    restaurants.append(restaurant)
                except Exception as e:
                    logger.warning(f"Error parsing restaurant row {idx}: {e}")
                    continue
            
            return restaurants
        except Exception as e:
            logger.error(f"Error loading restaurants from CSV: {e}")
            return []
    
    def _determine_category(self, cuisines):
        """Determine category based on cuisines"""
        cuisines_lower = [c.lower() for c in cuisines]
        
        if any(c in cuisines_lower for c in ['italian', 'pizza', 'pasta']):
            return 'italian'
        elif any(c in cuisines_lower for c in ['mexican', 'tacos']):
            return 'mexican'
        elif any(c in cuisines_lower for c in ['asian', 'indonesian', 'chinese', 'japanese', 'thai']):
            return 'asian'
        elif any(c in cuisines_lower for c in ['bar', 'cafe', 'coffee']):
            return 'cafe'
        elif any(c in cuisines_lower for c in ['healthy', 'vegetarian', 'vegan']):
            return 'healthy'
        else:
            return 'international'
    
    def _extract_location(self, address):
        """Extract location from address"""
        if pd.isna(address):
            return 'Lombok'
        
        # Extract key location names
        if 'Gili Trawangan' in address or 'Gili T' in address:
            return 'Gili Trawangan'
        elif 'Gili Air' in address:
            return 'Gili Air'
        elif 'Gili Meno' in address:
            return 'Gili Meno'
        elif 'Kuta' in address:
            return 'Kuta, Lombok'
        elif 'Senggigi' in address:
            return 'Senggigi'
        elif 'Mataram' in address:
            return 'Mataram'
        else:
            return 'Lombok'
    
    def _get_opening_hours(self, row):
        """Get opening hours from row data"""
        # Try to get Monday hours as representative
        if pd.notna(row.get('monday_hours')):
            return row['monday_hours']
        elif pd.notna(row.get('sunday_hours')):
            return row['sunday_hours']
        else:
            return 'Contact for hours'
    
    def get_personalized_recommendations(self, user_preferences=None, limit=10, category=None):
        """Get personalized restaurant recommendations"""
        restaurants = self.restaurants_data.copy() if self.restaurants_data else []
        
        # Filter by category if specified
        if category:
            restaurants = [r for r in restaurants if r.get('category') == category]
        
        # Simple personalization based on user preferences
        if user_preferences:
            # Prioritize based on user's preferred cuisines and locations
            scored_restaurants = []
            for restaurant in restaurants:
                score = 0
                
                # Score based on cuisine preferences
                if user_preferences.get('preferred_cuisines'):
                    for cuisine, count in user_preferences['preferred_cuisines'].items():
                        if cuisine.lower() in restaurant['cuisine'].lower():
                            score += count * 3  # Increased weight for cuisine match
                
                # Score based on location preferences
                if user_preferences.get('preferred_locations'):
                    for location, count in user_preferences['preferred_locations'].items():
                        if location.lower() in restaurant['location'].lower():
                            score += count * 2  # Increased weight for location match
                
                # Add base rating boost
                score += restaurant.get('rating', 0) * 0.5
                
                restaurant['personalization_score'] = round(score, 2)
                scored_restaurants.append(restaurant)
            
            # Sort by personalization score first, then by rating
            restaurants = sorted(scored_restaurants, 
                               key=lambda x: (x.get('personalization_score', 0), x.get('rating', 0)), 
                               reverse=True)
        else:
            # Set score to 0 for non-personalized
            for restaurant in restaurants:
                restaurant['personalization_score'] = 0
        
        return restaurants[:limit]
    
    def get_popular_recommendations(self, limit=10, category=None):
        """Get popular restaurant recommendations"""
        restaurants = self.restaurants_data.copy() if self.restaurants_data else []
        
        # Filter by category if specified
        if category:
            restaurants = [r for r in restaurants if r.get('category') == category]
        
        # Set personalization_score to 0 for all (not personalized)
        for restaurant in restaurants:
            restaurant['personalization_score'] = 0
        
        # Sort by rating
        restaurants = sorted(restaurants, key=lambda x: x['rating'], reverse=True)
        return restaurants[:limit]
    
    def get_available_categories(self):
        """Get available restaurant categories"""
        return [
            {'key': 'indonesian', 'label': 'Masakan Indonesia'},
            {'key': 'western', 'label': 'Western Food'},
            {'key': 'asian', 'label': 'Asian Cuisine'},
            {'key': 'seafood', 'label': 'Seafood'},
            {'key': 'vegetarian', 'label': 'Vegetarian'},
            {'key': 'fast_food', 'label': 'Fast Food'},
            {'key': 'fine_dining', 'label': 'Fine Dining'},
            {'key': 'street_food', 'label': 'Street Food'}
        ]
    
    


def get_popular_recommendations_from_engine(engine, limit=9999, category=None):
    """Get popular recommendations from any engine type"""
    # Check if it's ContentBasedRecommendationEngine or MockRecommendationEngine
    if isinstance(engine, ContentBasedRecommendationEngine):
        # Get all or limited restaurants from ContentBasedRecommendationEngine
        max_items = min(limit, len(engine.restaurants_objects))
        restaurants = []
        for rest_obj in engine.restaurants_objects[:max_items]:
            # Safely handle about field
            about_text = ''
            if isinstance(rest_obj.about, str):
                about_text = rest_obj.about[:200] + '...' if len(rest_obj.about) > 200 else rest_obj.about
            
            # Safely handle address field
            location = 'Lombok'
            if isinstance(rest_obj.address, str) and rest_obj.address:
                location = rest_obj.address.split(',')[-1].strip()
            
            restaurant = {
                'id': rest_obj.id,
                'name': str(rest_obj.name) if rest_obj.name else 'Unknown',
                'location': location,
                'rating': rest_obj.rating,
                'price_range': str(rest_obj.price_range) if rest_obj.price_range else '$$',
                'cuisine': ', '.join(rest_obj.cuisines[:3]) if rest_obj.cuisines else 'Restaurant',
                'image_url': rest_obj.images[0] if rest_obj.images else '',
                'description': about_text,
                'opening_hours': rest_obj.hours.get('monday', 'Contact for hours') if rest_obj.hours else 'Contact for hours',
                'popular_dishes': [],
                'category': _determine_category_from_cuisines(rest_obj.cuisines or []),
                'personalization_score': 0,
                'url': '',
                'address': str(rest_obj.address) if isinstance(rest_obj.address, str) else ''
            }
            restaurants.append(restaurant)
        # Sort by rating
        restaurants = sorted(restaurants, key=lambda x: x['rating'], reverse=True)
        return restaurants[:limit]
    else:
        # Use MockRecommendationEngine methods
        return engine.get_popular_recommendations(limit=limit, category=category)

def _determine_category_from_cuisines(cuisines):
    """Helper to determine category from cuisines list"""
    cuisines_lower = [c.lower() for c in cuisines] if cuisines else []
    if any(c in cuisines_lower for c in ['italian', 'pizza', 'pasta']):
        return 'italian'
    elif any(c in cuisines_lower for c in ['mexican', 'tacos']):
        return 'mexican'
    elif any(c in cuisines_lower for c in ['asian', 'indonesian', 'chinese', 'japanese', 'thai']):
        return 'asian'
    elif any(c in cuisines_lower for c in ['bar', 'cafe', 'coffee']):
        return 'cafe'
    elif any(c in cuisines_lower for c in ['healthy', 'vegetarian', 'vegan']):
        return 'healthy'
    else:
        return 'international'

def apply_personalization_scoring(restaurants, user_preferences):
    """
    Apply personalization scoring to restaurants based on ALL user history
    Uses frequency counts from all conversations to weight preferences
    """
    scored_restaurants = []
    
    total_convos = user_preferences.get('total_conversations', 1)
    
    for restaurant in restaurants:
        score = 0
        matching_features = []
        
        # Score based on cuisine preferences (weighted by frequency across ALL history)
        if user_preferences.get('preferred_cuisines'):
            for cuisine, count in user_preferences['preferred_cuisines'].items():
                if cuisine.lower() in restaurant.get('cuisine', '').lower():
                    # Higher weight for frequently mentioned cuisines
                    weight = count * 3
                    score += weight
                    matching_features.append(f"Cuisine: {cuisine} (mentioned {count}x)")
        
        # Score based on location preferences (weighted by frequency across ALL history)
        if user_preferences.get('preferred_locations'):
            for location, count in user_preferences['preferred_locations'].items():
                if location.lower() in restaurant.get('location', '').lower():
                    # Higher weight for frequently mentioned locations
                    weight = count * 2
                    score += weight
                    matching_features.append(f"Location: {location} (mentioned {count}x)")
        
        # Score based on price preferences
        if user_preferences.get('price_preferences'):
            for price_pref, count in user_preferences['price_preferences'].items():
                if price_pref.lower() in restaurant.get('price_range', '').lower():
                    score += count * 1.5
                    matching_features.append(f"Price: {price_pref}")
        
        # Add base rating boost
        score += restaurant.get('rating', 0) * 0.5
        
        # Bonus for restaurants matching multiple preferences
        if len(matching_features) > 1:
            score += len(matching_features) * 0.5
        
        restaurant['personalization_score'] = round(score, 2)
        restaurant['matching_features'] = matching_features[:3]  # Top 3 matches
        scored_restaurants.append(restaurant)
    
    # Sort by personalization score first, then by rating
    scored_restaurants.sort(key=lambda x: (x.get('personalization_score', 0), x.get('rating', 0)), reverse=True)
    
    logger.info(f"Scored {len(scored_restaurants)} restaurants. Top score: {scored_restaurants[0].get('personalization_score', 0) if scored_restaurants else 0}")
    
    return scored_restaurants

@recommendations_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Get personalized restaurant recommendations with pagination
    
    Query Parameters:
    - session_id: optional, for personalized recommendations
    - device_token: optional, alternative to session_id
    - page: optional, page number (default: 1)
    - per_page: optional, items per page (default: 20, max: 100)
    - category: optional, filter by category
    
    Response:
    {
        "success": true,
        "data": {
            "restaurants": [...],
            "total": 1163,
            "page": 1,
            "per_page": 20,
            "total_pages": 59,
            "has_next": true,
            "has_prev": false,
            "personalized": true/false
        }
    }
    """
    try:
        session_id = request.args.get('session_id')
        device_token = request.args.get('device_token')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Max 100 per page
        category = request.args.get('category')
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        
        engine = get_recommendation_engine()
        
        # Check if engine loaded successfully
        if engine is None:
            logger.error("Recommendation engine failed to initialize")
            return jsonify({
                'success': False,
                'error': 'Recommendation system is currently unavailable'
            }), 503
        
        # Get user preferences if available
        user_preferences = None
        if session_id or device_token:
            user_preferences = get_user_preferences(session_id, device_token)
            logger.info(f"User preferences found: {user_preferences is not None}")
        
        # Get ALL recommendations first (without limit)
        is_personalized = bool(user_preferences)
        
        if user_preferences and isinstance(engine, MockRecommendationEngine):
            # Use mock engine's personalization - get all
            all_recommendations = engine.get_personalized_recommendations(
                user_preferences=user_preferences,
                limit=9999,  # Get all
                category=category
            )
            logger.info(f"Got {len(all_recommendations)} personalized recommendations from MockEngine")
        else:
            # Get all recommendations and apply personalization scoring
            all_recommendations = get_popular_recommendations_from_engine(
                engine=engine,
                limit=9999,  # Get all
                category=category
            )
            
            # Apply personalization scoring if user has preferences
            if user_preferences:
                all_recommendations = apply_personalization_scoring(all_recommendations, user_preferences)
                logger.info(f"Applied personalization scoring to {len(all_recommendations)} recommendations")
            else:
                logger.info(f"Got {len(all_recommendations)} popular recommendations (no preferences)")
        
        # Calculate pagination metadata
        total_items = len(all_recommendations)
        total_pages = (total_items + per_page - 1) // per_page  # Ceiling division
        
        # Validate page number
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # Calculate slice indices
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Get paginated results
        paginated_recommendations = all_recommendations[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'data': {
                'restaurants': paginated_recommendations,
                'total': total_items,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'personalized': is_personalized,
                'category': category
            }
        }), 200
        
    except Exception as e:
        import traceback
        logger.error(f"Error getting recommendations: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendations_bp.route('/recommendations/categories', methods=['GET'])
def get_categories():
    """
    Get available restaurant categories
    
    Response:
    {
        "success": true,
        "data": {
            "categories": [...]
        }
    }
    """
    try:
        categories = [
            {"key": "all", "label": "Semua", "count": 8},
            {"key": "local_food", "label": "Makanan Lokal", "count": 3},
            {"key": "beach", "label": "Pantai", "count": 2},
            {"key": "nature", "label": "Alam", "count": 1},
            {"key": "religious", "label": "Wisata Religi", "count": 1},
            {"key": "spicy_food", "label": "Pedas", "count": 1}
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'categories': categories
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendations_bp.route('/recommendations/trending', methods=['GET'])
def get_trending():
    """
    Get trending restaurants based on recent user interactions
    
    Response:
    {
        "success": true,
        "data": {
            "restaurants": [...],
            "period": "7_days"
        }
    }
    """
    try:
        limit = int(request.args.get('limit', 5))
        
        # Get trending based on recent chat history
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # For now, return popular items as trending
        engine = get_recommendation_engine()
        trending_restaurants = engine.get_popular_recommendations(limit=limit)
        # Sort by rating to simulate trending
        trending_restaurants.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'restaurants': trending_restaurants[:limit],
                'period': '7_days',
                'based_on': 'popularity and ratings'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting trending: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendations_bp.route('/recommendations/top5', methods=['GET'])
def get_top5_recommendations():
    """
    Get Top 5 restaurant recommendations dengan Cosine Similarity
    
    Menggunakan:
    1. Cosine Similarity untuk menghitung kemiripan
    2. Sorting berdasarkan skor tertinggi
    3. Tie-breaker: jika skor sama, urutkan berdasarkan rating dan jumlah review
    
    Query Parameters:
    - session_id: optional, untuk personalized recommendations
    - device_token: optional, alternative to session_id
    - query: optional, user query untuk similarity matching
    
    Response:
    {
        "success": true,
        "data": {
            "restaurants": [...],
            "query": "pizza di senggigi",
            "personalized": true/false,
            "algorithm": "cosine_similarity"
        }
    }
    """
    try:
        session_id = request.args.get('session_id')
        device_token = request.args.get('device_token')
        user_query = request.args.get('query', '')
        
        engine = get_recommendation_engine()
        
        if engine is None:
            return jsonify({
                'success': False,
                'error': 'Recommendation system unavailable'
            }), 503
        
        # Get user preferences for personalization context
        user_preferences = None
        if session_id or device_token:
            user_preferences = get_user_preferences(session_id, device_token)
        
        # Build query from user preferences if no explicit query
        if not user_query and user_preferences:
            query_parts = []
            if user_preferences.get('preferred_cuisines'):
                top_cuisines = list(user_preferences['preferred_cuisines'].keys())[:3]
                query_parts.extend(top_cuisines)
            if user_preferences.get('preferred_locations'):
                top_locations = list(user_preferences['preferred_locations'].keys())[:2]
                query_parts.extend(top_locations)
            user_query = ' '.join(query_parts)
        
        top5_restaurants = []
        
        if isinstance(engine, ContentBasedRecommendationEngine):
            # Use real Cosine Similarity from ContentBasedRecommendationEngine
            if user_query:
                # Get recommendations using TF-IDF cosine similarity
                recommendations = engine.get_recommendations(user_query, top_n=20)
                
                # Convert to response format with similarity scores
                for rec in recommendations:
                    rest = rec.restaurant
                    
                    # Safe handling for about/address fields
                    about_text = ''
                    if isinstance(rest.about, str):
                        about_text = rest.about[:200] + '...' if len(rest.about) > 200 else rest.about
                    
                    location = 'Lombok'
                    if isinstance(rest.address, str) and rest.address:
                        location = rest.address.split(',')[-1].strip()
                    
                    top5_restaurants.append({
                        'id': rest.id,
                        'name': str(rest.name) if rest.name else 'Unknown',
                        'location': location,
                        'rating': rest.rating,
                        'review_count': rest.review_count if hasattr(rest, 'review_count') else 0,
                        'price_range': str(rest.price_range) if rest.price_range else '$$',
                        'cuisine': ', '.join(rest.cuisines[:3]) if rest.cuisines else 'Restaurant',
                        'image_url': rest.images[0] if rest.images else '',
                        'description': about_text,
                        'similarity_score': round(rec.similarity_score, 4),
                        'matching_features': rec.matching_features,
                        'explanation': rec.explanation,
                        'address': str(rest.address) if isinstance(rest.address, str) else ''
                    })
            else:
                # No query, use popularity + rating
                sorted_restaurants = sorted(
                    engine.restaurants_objects,
                    key=lambda x: (x.rating, getattr(x, 'review_count', 0)),
                    reverse=True
                )
                for rest in sorted_restaurants[:20]:
                    about_text = ''
                    if isinstance(rest.about, str):
                        about_text = rest.about[:200] + '...' if len(rest.about) > 200 else rest.about
                    
                    location = 'Lombok'
                    if isinstance(rest.address, str) and rest.address:
                        location = rest.address.split(',')[-1].strip()
                    
                    top5_restaurants.append({
                        'id': rest.id,
                        'name': str(rest.name) if rest.name else 'Unknown',
                        'location': location,
                        'rating': rest.rating,
                        'review_count': getattr(rest, 'review_count', 0),
                        'price_range': str(rest.price_range) if rest.price_range else '$$',
                        'cuisine': ', '.join(rest.cuisines[:3]) if rest.cuisines else 'Restaurant',
                        'image_url': rest.images[0] if rest.images else '',
                        'description': about_text,
                        'similarity_score': 0.5 + (rest.rating / 10.0),
                        'matching_features': ['popular', 'highly rated'],
                        'explanation': f'Restoran populer dengan rating {rest.rating}/5.0',
                        'address': str(rest.address) if isinstance(rest.address, str) else ''
                    })
        else:
            # MockEngine fallback
            mock_recs = engine.get_popular_recommendations(limit=20)
            for r in mock_recs:
                r['similarity_score'] = 0.5 + (r.get('rating', 0) / 10.0)
                r['review_count'] = r.get('review_count', 0)
            top5_restaurants = mock_recs
        
        # CRITICAL: Sort by similarity score, then by rating, then by review_count (tie-breaker)
        top5_restaurants.sort(
            key=lambda x: (
                x.get('similarity_score', 0),
                x.get('rating', 0),
                x.get('review_count', 0)
            ),
            reverse=True
        )
        
        # Slice Top 5 only
        top5_result = top5_restaurants[:5]
        
        logger.info(f"Top 5 recommendations - Query: '{user_query}', Results: {len(top5_result)}")
        if top5_result:
            logger.info(f"Top scores: {[r.get('similarity_score', 0) for r in top5_result]}")
        
        return jsonify({
            'success': True,
            'data': {
                'restaurants': top5_result,
                'query': user_query,
                'personalized': bool(user_preferences),
                'algorithm': 'cosine_similarity',
                'tie_breaker': 'rating_and_review_count'
            }
        }), 200
        
    except Exception as e:
        import traceback
        logger.error(f"Error getting top 5 recommendations: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendations_bp.route('/recommendations/all-ranked', methods=['GET'])
def get_all_ranked_recommendations():
    """
    Get ALL restaurant recommendations sorted by Cosine Similarity dengan pagination
    
    Top 5 akan memiliki flag 'is_top5' = true untuk UI labeling.
    Menggunakan:
    1. Cosine Similarity untuk menghitung kemiripan
    2. Sorting berdasarkan skor tertinggi
    3. Tie-breaker: jika skor sama, urutkan berdasarkan rating dan jumlah review
    
    Query Parameters:
    - session_id: optional, untuk personalized recommendations
    - device_token: optional, alternative to session_id
    - query: optional, user query untuk similarity matching
    - page: pagination page (default 1)
    - limit: items per page (default 20)
    
    Response:
    {
        "success": true,
        "data": {
            "restaurants": [...],
            "pagination": {
                "current_page": 1,
                "total_pages": 10,
                "total_items": 200,
                "items_per_page": 20,
                "has_next": true,
                "has_prev": false
            },
            "query": "pizza di senggigi",
            "personalized": true/false,
            "algorithm": "cosine_similarity"
        }
    }
    """
    try:
        session_id = request.args.get('session_id')
        device_token = request.args.get('device_token')
        user_query = request.args.get('query', '')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Validate pagination params
        page = max(1, page)
        limit = min(max(1, limit), 100)  # Max 100 per page
        
        engine = get_recommendation_engine()
        
        if engine is None:
            return jsonify({
                'success': False,
                'error': 'Recommendation system unavailable'
            }), 503
        
        # Get user preferences for personalization context
        user_preferences = None
        if session_id or device_token:
            user_preferences = get_user_preferences(session_id, device_token)
        
        # Build query from user preferences if no explicit query
        if not user_query and user_preferences:
            query_parts = []
            if user_preferences.get('preferred_cuisines'):
                top_cuisines = list(user_preferences['preferred_cuisines'].keys())[:3]
                query_parts.extend(top_cuisines)
            if user_preferences.get('preferred_locations'):
                top_locations = list(user_preferences['preferred_locations'].keys())[:2]
                query_parts.extend(top_locations)
            user_query = ' '.join(query_parts)
        
        all_restaurants = []
        
        if isinstance(engine, ContentBasedRecommendationEngine):
            # Use real Cosine Similarity from ContentBasedRecommendationEngine
            if user_query:
                # Get ALL recommendations using TF-IDF cosine similarity
                # Use a very large top_n to get all results
                recommendations = engine.get_recommendations(user_query, top_n=2000)
                
                # Convert to response format with similarity scores
                for rec in recommendations:
                    rest = rec.restaurant
                    
                    # Safe handling for about/address fields
                    about_text = ''
                    if isinstance(rest.about, str):
                        about_text = rest.about[:200] + '...' if len(rest.about) > 200 else rest.about
                    
                    location = 'Lombok'
                    if isinstance(rest.address, str) and rest.address:
                        location = rest.address.split(',')[-1].strip()
                    
                    all_restaurants.append({
                        'id': rest.id,
                        'name': str(rest.name) if rest.name else 'Unknown',
                        'location': location,
                        'rating': rest.rating,
                        'review_count': rest.review_count if hasattr(rest, 'review_count') else 0,
                        'price_range': str(rest.price_range) if rest.price_range else '$$',
                        'cuisine': ', '.join(rest.cuisines[:3]) if rest.cuisines else 'Restaurant',
                        'image_url': rest.images[0] if rest.images else '',
                        'description': about_text,
                        'similarity_score': round(rec.similarity_score, 4),
                        'matching_features': rec.matching_features,
                        'explanation': rec.explanation,
                        'address': str(rest.address) if isinstance(rest.address, str) else ''
                    })
            else:
                # No query, use popularity + rating for ALL restaurants
                sorted_restaurants = sorted(
                    engine.restaurants_objects,
                    key=lambda x: (x.rating, getattr(x, 'review_count', 0)),
                    reverse=True
                )
                for rest in sorted_restaurants:
                    about_text = ''
                    if isinstance(rest.about, str):
                        about_text = rest.about[:200] + '...' if len(rest.about) > 200 else rest.about
                    
                    location = 'Lombok'
                    if isinstance(rest.address, str) and rest.address:
                        location = rest.address.split(',')[-1].strip()
                    
                    all_restaurants.append({
                        'id': rest.id,
                        'name': str(rest.name) if rest.name else 'Unknown',
                        'location': location,
                        'rating': rest.rating,
                        'review_count': getattr(rest, 'review_count', 0),
                        'price_range': str(rest.price_range) if rest.price_range else '$$',
                        'cuisine': ', '.join(rest.cuisines[:3]) if rest.cuisines else 'Restaurant',
                        'image_url': rest.images[0] if rest.images else '',
                        'description': about_text,
                        'similarity_score': 0.5 + (rest.rating / 10.0),
                        'matching_features': ['popular', 'highly rated'],
                        'explanation': f'Restoran populer dengan rating {rest.rating}/5.0',
                        'address': str(rest.address) if isinstance(rest.address, str) else ''
                    })
        else:
            # MockEngine fallback - get all
            mock_recs = engine.get_popular_recommendations(limit=2000)
            for r in mock_recs:
                r['similarity_score'] = 0.5 + (r.get('rating', 0) / 10.0)
                r['review_count'] = r.get('review_count', 0)
            all_restaurants = mock_recs
        
        # CRITICAL: Sort ALL by similarity score, then by rating, then by review_count (tie-breaker)
        all_restaurants.sort(
            key=lambda x: (
                x.get('similarity_score', 0),
                x.get('rating', 0),
                x.get('review_count', 0)
            ),
            reverse=True
        )
        
        # Add rank and is_top5 flag to each restaurant
        for idx, restaurant in enumerate(all_restaurants):
            restaurant['rank'] = idx + 1
            restaurant['is_top5'] = idx < 5
        
        # Calculate pagination
        total_items = len(all_restaurants)
        total_pages = (total_items + limit - 1) // limit  # Ceiling division
        
        # Slice for current page
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_restaurants = all_restaurants[start_idx:end_idx]
        
        logger.info(f"All-Ranked recommendations - Query: '{user_query}', Page: {page}, Total: {total_items}")
        
        return jsonify({
            'success': True,
            'data': {
                'restaurants': paginated_restaurants,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total_items,
                    'items_per_page': limit,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                },
                'query': user_query,
                'personalized': bool(user_preferences),
                'algorithm': 'cosine_similarity',
                'tie_breaker': 'rating_and_review_count'
            }
        }), 200
        
    except Exception as e:
        import traceback
        logger.error(f"Error getting all-ranked recommendations: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def get_user_preferences(session_id=None, device_token=None):
    """
    Extract user preferences from ALL chat history (no limit)
    Aggregates preferences from every conversation the user has had
    """
    try:
        # Get ALL user's chat history (no limit)
        query = ChatHistory.query
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        elif device_token:
            query = query.filter_by(device_token=device_token)
        else:
            return None
        
        # Get ALL chat history ordered by timestamp
        chat_history = query.order_by(ChatHistory.timestamp.desc()).all()
        
        if not chat_history:
            return None
        
        logger.info(f"Processing {len(chat_history)} chat messages for personalization")
        
        # Extract preferences from ALL chat history
        cuisines = []
        locations = []
        moods = []
        price_preferences = []
        
        for chat in chat_history:
            if chat.extracted_cuisine:
                cuisines.extend([c.strip() for c in chat.extracted_cuisine.split(',')])
            if chat.extracted_location:
                locations.extend([l.strip() for l in chat.extracted_location.split(',')])
            if chat.extracted_mood:
                moods.extend([m.strip() for m in chat.extracted_mood.split(',')])
            if chat.extracted_price:
                price_preferences.extend([p.strip() for p in chat.extracted_price.split(',')])
        
        # Count frequencies from ALL history
        from collections import Counter
        
        cuisine_counter = Counter(cuisines)
        location_counter = Counter(locations)
        
        logger.info(f"Aggregated preferences - Cuisines: {len(cuisines)}, Locations: {len(locations)}")
        
        return {
            'preferred_cuisines': dict(cuisine_counter.most_common(10)),  # Top 10 cuisines
            'preferred_locations': dict(location_counter.most_common(10)),  # Top 10 locations
            'preferred_moods': dict(Counter(moods).most_common(5)),
            'price_preferences': dict(Counter(price_preferences).most_common(3)),
            'total_conversations': len(chat_history),
            'total_cuisines_mentioned': len(cuisines),
            'total_locations_mentioned': len(locations)
        }
        
    except Exception as e:
        logger.error(f"Error extracting user preferences: {e}")
        return None


def get_mock_recommendations(limit=10, category=None):
    """
    Get mock restaurant recommendations for testing
    """
    mock_restaurants = [
        {
            "id": 1,
            "name": "Pura Batu Bolong",
            "location": "Lombok Barat, Nusa Tenggara Barat",
            "rating": 3.8,
            "price_range": "Murah",
            "cuisine": "Wisata Religi",
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop",
            "description": "Pura yang terletak di atas tebing dengan pemandangan laut yang menakjubkan",
            "opening_hours": "06:00 - 18:00",
            "popular_dishes": ["Spot Foto", "Sunset View", "Wisata Spiritual"],
            "category": "religious"
        },
        {
            "id": 2,
            "name": "Dersi Coffee Roastery & Vanilla Farm",
            "location": "Senggigi, Lombok",
            "rating": 4.8,
            "price_range": "Menengah",
            "cuisine": "Coffee & Farm",
            "image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&h=200&fit=crop",
            "description": "Farm kopi dan vanila dengan pengalaman langsung dari kebun ke cangkir",
            "opening_hours": "08:00 - 17:00",
            "popular_dishes": ["Kopi Arabika", "Vanilla Ice Cream", "Farm Tour"],
            "category": "farm"
        },
        {
            "id": 3,
            "name": "Puncak Pusuk Pass",
            "location": "Lombok Barat",
            "rating": 4.1,
            "price_range": "Murah",
            "cuisine": "Alam & Satwa",
            "image_url": "https://images.unsplash.com/photo-1574263867128-a3d5c1b1deac?w=400&h=200&fit=crop",
            "description": "Spot wisata alam dengan pemandangan indah dan monyet-monyet lucu",
            "opening_hours": "24 Jam",
            "popular_dishes": ["Monyet Liar", "Pemandangan Alam", "Foto Alam"],
            "category": "nature"
        },
        {
            "id": 4,
            "name": "Warung Sate Pusut",
            "location": "Mataram, Lombok",
            "rating": 4.5,
            "price_range": "Murah",
            "cuisine": "Makanan Lokal",
            "image_url": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400&h=200&fit=crop",
            "description": "Sate pusut khas Lombok dengan bumbu rempah tradisional yang kaya rasa",
            "opening_hours": "17:00 - 23:00",
            "popular_dishes": ["Sate Pusut", "Plecing Kangkung", "Es Kelapa Muda"],
            "category": "local_food"
        },
        {
            "id": 5,
            "name": "Pantai Senggigi",
            "location": "Senggigi, Lombok Barat",
            "rating": 4.3,
            "price_range": "Gratis",
            "cuisine": "Pantai & Snorkeling",
            "image_url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=200&fit=crop",
            "description": "Pantai dengan air jernih, coral reef, dan pemandangan sunset yang memukau",
            "opening_hours": "24 Jam",
            "popular_dishes": ["Snorkeling", "Sunset View", "Water Sports"],
            "category": "beach"
        },
        {
            "id": 6,
            "name": "Rumah Makan Taliwang Irama",
            "location": "Mataram, Lombok",
            "rating": 4.6,
            "price_range": "Menengah",
            "cuisine": "Ayam Taliwang",
            "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400&h=200&fit=crop",
            "description": "Rumah makan legendaris dengan ayam taliwang bumbu khas yang pedas mantap",
            "opening_hours": "10:00 - 22:00",
            "popular_dishes": ["Ayam Taliwang", "Plecing Kangkung", "Sate Rembiga"],
            "category": "spicy_food"
        },
        {
            "id": 7,
            "name": "Warung Plecing Kangkung Khas Lombok",
            "location": "Mataram, Lombok",
            "rating": 4.2,
            "price_range": "Murah",
            "cuisine": "Sayuran Tradisional",
            "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=200&fit=crop",
            "description": "Plecing kangkung autentik dengan sambal terasi yang pedas menggigit",
            "opening_hours": "11:00 - 21:00",
            "popular_dishes": ["Plecing Kangkung", "Gado-gado", "Es Kelapa"],
            "category": "local_food"
        },
        {
            "id": 8,
            "name": "Gili Trawangan Snorkeling",
            "location": "Gili Trawangan, Lombok",
            "rating": 4.7,
            "price_range": "Menengah",
            "cuisine": "Aktivitas Laut",
            "image_url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=200&fit=crop",
            "description": "Eksplorasi bawah laut dengan turtle dan coral reef yang eksotis",
            "opening_hours": "08:00 - 17:00",
            "popular_dishes": ["Snorkeling", "Turtle Watching", "Coral Garden"],
            "category": "beach"
        }
    ]
    
    # Filter by category if specified
    if category and category != 'all':
        mock_restaurants = [r for r in mock_restaurants if r.get('category') == category]
    
    # Limit results
    return mock_restaurants[:limit]