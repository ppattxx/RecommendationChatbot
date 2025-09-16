import hashlib
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import platform
import socket
from utils.logger import get_logger

logger = get_logger("device_token_service")

class DeviceTokenService:
    def __init__(self):
        self.tokens_dir = Path("device_tokens")
        self.tokens_dir.mkdir(exist_ok=True)
        self.user_histories_dir = Path("user_histories") 
        self.user_histories_dir.mkdir(exist_ok=True)
    
    def generate_device_token(self, user_agent: str = "", ip_address: str = "", additional_info: Dict = None) -> str:
        """
        Generate unique device token based on browser fingerprint
        """
        try:
            device_info = {
                'user_agent': user_agent or "unknown",
                'ip_address': ip_address or "unknown", 
                'platform': platform.system(),
                'platform_version': platform.release(),
                'timestamp': datetime.now().isoformat()
            }
            
            if additional_info:
                device_info.update(additional_info)
            
            device_string = json.dumps(device_info, sort_keys=True)
            device_hash = hashlib.sha256(device_string.encode()).hexdigest()[:16]
            
            random_component = str(uuid.uuid4())[:8]
            
            device_token = f"dev_{device_hash}_{random_component}"
            
            self._save_token_metadata(device_token, device_info)
            
            return device_token
            
        except Exception as e:
            logger.error(f"Error generating device token: {e}")
            fallback_token = f"dev_{str(uuid.uuid4().hex[:16])}"
            try:
                basic_device_info = {
                    'user_agent': "fallback",
                    'ip_address': "unknown",
                    'platform': "unknown",
                    'platform_version': "unknown", 
                    'timestamp': datetime.now().isoformat(),
                    'is_fallback': True
                }
                self._save_token_metadata(fallback_token, basic_device_info)
            except Exception as save_error:
                logger.error(f"Error saving fallback token: {save_error}")
            return fallback_token
    
    def _save_token_metadata(self, token: str, device_info: Dict):
        try:
            self.tokens_dir.mkdir(exist_ok=True)
            
            token_file = self.tokens_dir / f"{token}.json"
            metadata = {
                'token': token,
                'created_at': datetime.now().isoformat(),
                'device_info': device_info,
                'last_seen': datetime.now().isoformat(),
                'session_count': 1
            }
            
            with open(token_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Device token metadata saved: {token_file}")
                
        except Exception as e:
            logger.error(f"Error saving token metadata for {token}: {e}")
            try:
                self.tokens_dir.mkdir(parents=True, exist_ok=True)
                with open(token_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                logger.info(f"Device token metadata saved on retry: {token_file}")
            except Exception as retry_error:
                logger.error(f"Failed to save token metadata on retry: {retry_error}")
    
    def update_token_activity(self, token: str):
        try:
            token_file = self.tokens_dir / f"{token}.json"
            if token_file.exists():
                with open(token_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata['last_seen'] = datetime.now().isoformat()
                metadata['session_count'] = metadata.get('session_count', 0) + 1
                
                with open(token_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                logger.debug(f"Updated token activity: {token}")
            else:
                logger.warning(f"Token file not found for update: {token_file}")
                self._create_missing_token_file(token)
                    
        except Exception as e:
            logger.error(f"Error updating token activity for {token}: {e}")
    
    def _create_missing_token_file(self, token: str):
        try:
            basic_device_info = {
                'user_agent': "recreated",
                'ip_address': "unknown",
                'platform': "unknown",
                'platform_version': "unknown",
                'timestamp': datetime.now().isoformat(),
                'is_recreated': True
            }
            self._save_token_metadata(token, basic_device_info)
            logger.info(f"Created missing token file: {token}")
        except Exception as e:
            logger.error(f"Failed to create missing token file: {e}")
    
    def get_or_create_user_history(self, device_token: str) -> Dict:
        """Get or create user history for device token"""
        try:
            history_file = self.user_histories_dir / f"{device_token}_history.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                new_history = {
                    'device_token': device_token,
                    'created_at': datetime.now().isoformat(),
                    'chat_sessions': [],
                    'preferences': {
                        'preferred_cuisines': [],
                        'preferred_locations': [],
                        'price_preference': None,
                        'mood_preferences': [],
                        'dietary_restrictions': []
                    },
                    'interaction_stats': {
                        'total_messages': 0,
                        'total_sessions': 0,
                        'favorite_restaurants': [],
                        'search_patterns': {}
                    }
                }
                
                self._save_user_history(device_token, new_history)
                return new_history
                
        except Exception as e:
            logger.error(f"Error getting user history: dor {e}")
            new_history = self._create_empty_history(device_token)
            self._save_user_history(device_token, new_history)
            return new_history
    
    def _create_empty_history(self, device_token: str) -> Dict:
        """Create empty history structure"""
        return {
            'device_token': device_token,
            'created_at': datetime.now().isoformat(),
            'chat_sessions': [],
            'preferences': {
                'preferred_cuisines': [],
                'preferred_locations': [],
                'price_preference': None,
                'mood_preferences': [],
                'dietary_restrictions': []
            },
            'interaction_stats': {
                'total_messages': 0,
                'total_sessions': 0,
                'favorite_restaurants': [],
                'search_patterns': {}
            }
        }
    
    def _save_user_history(self, device_token: str, history: Dict):
        """Save user history to file"""
        try:
            history_file = self.user_histories_dir / f"{device_token}_history.json"
            history['last_updated'] = datetime.now().isoformat()
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving user history: {e}")
    
    def add_chat_session(self, device_token: str, session_data: Dict):
        """Add new chat session to user history"""
        try:
            history = self.get_or_create_user_history(device_token)
            
            if 'interaction_stats' not in history:
                history['interaction_stats'] = {
                    'total_messages': 0,
                    'total_sessions': 0,
                    'favorite_restaurants': [],
                    'search_patterns': {}
                }
            
            session_entry = {
                'session_id': session_data.get('session_id'),
                'timestamp': datetime.now().isoformat(),
                'messages': session_data.get('messages', []),
                'recommendations_given': session_data.get('recommendations', []),
                'user_feedback': session_data.get('feedback', {})
            }
            
            print(session_entry['messages'])
            print(session_entry['timestamp'])
            print(session_entry['recommendations_given'])
            print(session_entry['user_feedback'])
            print(session_entry['session_id'])

            history['chat_sessions'].append(session_entry)
            history['interaction_stats']['total_sessions'] += 1
            history['interaction_stats']['total_messages'] += len(session_entry['messages'])
            
            if len(history['chat_sessions']) > 50:
                history['chat_sessions'] = history['chat_sessions'][-50:]
            
            self._save_user_history(device_token, history)
            
        except Exception as e:
            logger.error(f"Error adding chat session: {e}")
            try:
                self._repair_history_file(device_token)
                history = self.get_or_create_user_history(device_token)
                if 'interaction_stats' in history:
                    session_entry = {
                        'session_id': session_data.get('session_id'),
                        'timestamp': datetime.now().isoformat(),
                        'messages': session_data.get('messages', []),
                        'recommendations_given': session_data.get('recommendations', []),
                        'user_feedback': session_data.get('feedback', {})
                    }
                    history['chat_sessions'].append(session_entry)
                    history['interaction_stats']['total_sessions'] += 1
                    history['interaction_stats']['total_messages'] += len(session_entry['messages'])
                    self._save_user_history(device_token, history)
            except:
                logger.error(f"Failed to repair history file for {device_token}")
    
    def _repair_history_file(self, device_token: str):
        """Repair corrupted history file"""
        try:
            history_file = self.user_histories_dir / f"{device_token}_history.json"
            if history_file.exists():
                history_file.unlink()
        except Exception as e:
            logger.error(f"Error repairing history file: {e}")
    
    def update_user_preferences(self, device_token: str, preferences_update: Dict):
        """Update user preferences based on interactions"""
        try:
            history = self.get_or_create_user_history(device_token)
            
            for key, value in preferences_update.items():
                if key in history['preferences']:
                    if isinstance(history['preferences'][key], list):
                        if isinstance(value, list):
                            for item in value:
                                if item not in history['preferences'][key]:
                                    history['preferences'][key].append(item)
                        else:
                            if value not in history['preferences'][key]:
                                history['preferences'][key].append(value)
                    else:
                        history['preferences'][key] = value
            
            self._save_user_history(device_token, history)
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    
    def get_user_preferences(self, device_token: str) -> Dict:
        """Get user preferences for personalization"""
        try:
            history = self.get_or_create_user_history(device_token)
            return history.get('preferences', {})
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def get_user_stats(self, device_token: str) -> Dict:
        """Get user interaction statistics"""
        try:
            history = self.get_or_create_user_history(device_token)
            return history.get('interaction_stats', {})
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def cleanup_old_tokens(self, days_threshold: int = 90):
        """Clean up old inactive tokens"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_threshold * 24 * 60 * 60)
            
            for token_file in self.tokens_dir.glob("*.json"):
                try:
                    with open(token_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    last_seen = datetime.fromisoformat(metadata.get('last_seen', metadata.get('created_at')))
                    
                    if last_seen.timestamp() < cutoff_date:
                        token_file.unlink()
                        
                        token_name = token_file.stem
                        history_file = self.user_histories_dir / f"{token_name}_history.json"
                        if history_file.exists():
                            history_file.unlink()
                            
                        logger.info(f"Cleaned up old token: {token_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing token file {token_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up old tokens: {e}")
    
    def analyze_user_preferences(self, device_token: str) -> Dict:
        """Analyze user preferences from chat history"""
        try:
            history = self.get_or_create_user_history(device_token)
            preferences = {
                'preferred_cuisines': [],
                'preferred_locations': [],
                'price_preferences': [],
                'mood_preferences': [],
                'search_patterns': {}
            }
            
            cuisine_mentions = {}
            location_mentions = {}
            price_keywords = []
            mood_keywords = []
            
            for session in history.get('chat_sessions', []):
                for message in session.get('messages', []):
                    user_query = message.get('user', '').lower()
                    
                    cuisines = self._extract_cuisines(user_query)
                    for cuisine in cuisines:
                        cuisine_mentions[cuisine] = cuisine_mentions.get(cuisine, 0) + 1
                    
                    locations = self._extract_locations(user_query)
                    for location in locations:
                        location_mentions[location] = location_mentions.get(location, 0) + 1
                    
                    price_keywords.extend(self._extract_price_preferences(user_query))
                    
                    mood_keywords.extend(self._extract_mood_preferences(user_query))
            
            preferences['preferred_cuisines'] = [cuisine for cuisine, count in 
                                               sorted(cuisine_mentions.items(), key=lambda x: x[1], reverse=True)[:5]]
            preferences['preferred_locations'] = [location for location, count in 
                                                sorted(location_mentions.items(), key=lambda x: x[1], reverse=True)[:3]]
            preferences['price_preferences'] = list(set(price_keywords))
            preferences['mood_preferences'] = list(set(mood_keywords))
            
            history['preferences'] = preferences
            self._save_user_history(device_token, history)
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error analyzing user preferences: {e}")
            return {}
    
    def _extract_cuisines(self, text: str) -> list:
        """Extract cuisine types from text (improved with more keywords and substring matching)"""
        cuisine_keywords = {
            'italian': [
                'itali', 'italian', 'italia', 'pizza', 'pasta', 'spaghetti', 'ristorante', 'italian food', 'masakan italia', 'italian cuisine', 'ristorante italiano'
            ],
            'chinese': ['chinese', 'china', 'dimsum', 'noodle', 'mie', 'chinatown', 'chinese food', 'masakan china'],
            'japanese': ['japanese', 'jepang', 'sushi', 'ramen', 'tempura', 'japanese food', 'masakan jepang'],
            'indonesian': ['indonesian', 'indonesia', 'nasi', 'sate', 'rendang', 'gado', 'masakan indonesia', 'indonesian food'],
            'western': ['western', 'barat', 'steak', 'burger', 'sandwich', 'western food', 'masakan barat'],
            'seafood': ['seafood', 'fish', 'ikan', 'udang', 'kepiting', 'lobster', 'seafood restaurant', 'masakan laut'],
            'mexican': ['mexican', 'meksiko', 'burrito', 'taco', 'mexican food', 'masakan meksiko'],
            'indian': ['indian', 'india', 'curry', 'kari', 'indian food', 'masakan india'],
            'french': ['french', 'perancis', 'french food', 'masakan perancis'],
            'mediterranean': ['mediterranean', 'mediterania', 'mediterranean food', 'masakan mediterania'],
            'asian': ['asian', 'asia', 'asian food', 'masakan asia'],
            'barbecue': ['barbecue', 'bbq', 'bakar', 'panggang', 'barbecue food', 'masakan bakar']
        }
        found_cuisines = []
        text_lower = text.lower()
        for cuisine, keywords in cuisine_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_cuisines.append(cuisine)
                    break
        return found_cuisines
    
    def _extract_locations(self, text: str) -> list:
        """Extract location preferences from text"""
        location_keywords = {
            'kuta': ['kuta', 'legian'],
            'seminyak': ['seminyak', 'oberoi'],
            'denpasar': ['denpasar'],
            'ubud': ['ubud'],
            'sanur': ['sanur'],
            'jimbaran': ['jimbaran'],
            'canggu': ['canggu'],
            'nusa dua': ['nusa dua', 'nusadua'],
            'mataram': ['mataram'],
            'senggigi': ['senggigi'],
            'gili': ['gili', 'gili air', 'gili trawangan']
        }
        
        found_locations = []
        for location, keywords in location_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_locations.append(location)
        return found_locations
    
    def _extract_price_preferences(self, text: str) -> list:
        """Extract price preferences from text"""
        price_keywords = []
        if any(word in text for word in ['murah', 'cheap', 'budget', 'affordable']):
            price_keywords.append('budget')
        if any(word in text for word in ['mahal', 'expensive', 'premium', 'luxury']):
            price_keywords.append('premium')
        if any(word in text for word in ['sedang', 'moderate', 'menengah']):
            price_keywords.append('moderate')
        return price_keywords
    
    def _extract_mood_preferences(self, text: str) -> list:
        """Extract mood/atmosphere preferences from text"""
        mood_keywords = []
        if any(word in text for word in ['romantic', 'romantis', 'couple', 'intimate', 'cozy', 'pasangan']):
            mood_keywords.append('romantic')
        if any(word in text for word in ['family', 'keluarga', 'anak', 'kids', 'child', 'children', 'family-friendly', 'family oriented', 'for family']):
            mood_keywords.append('family')
        if any(word in text for word in ['casual', 'santai', 'rileks', 'laid-back', 'nonformal']):
            mood_keywords.append('casual')
        if any(word in text for word in ['formal', 'business', 'meeting', 'elegant', 'fine dining', 'upscale']):
            mood_keywords.append('formal')
        if any(word in text for word in ['view', 'pemandangan', 'sunset', 'sunrise', 'pantai', 'laut', 'garden']):
            mood_keywords.append('scenic')
        return mood_keywords
    
    def get_personalized_boost(self, device_token: str, restaurant_data: Dict) -> float:
        """Calculate personalized boost score for restaurant based on user preferences"""
        try:
            history = self.get_or_create_user_history(device_token)
            preferences = history.get('preferences', {})
            
            boost_score = 0.0
            
            restaurant_cuisines = restaurant_data.get('cuisines', [])
            if isinstance(restaurant_cuisines, str):
                restaurant_cuisines = [restaurant_cuisines]
            
            for cuisine in preferences.get('preferred_cuisines', []):
                if any(cuisine.lower() in str(rest_cuisine).lower() for rest_cuisine in restaurant_cuisines):
                    boost_score += 0.3
            
            restaurant_location = str(restaurant_data.get('location', '')).lower()
            for location in preferences.get('preferred_locations', []):
                if location.lower() in restaurant_location:
                    boost_score += 0.2
            
            restaurant_about = str(restaurant_data.get('about', '')).lower()
            for mood in preferences.get('mood_preferences', []):
                mood_indicators = {
                    'romantic': ['romantic', 'couple', 'intimate', 'cozy'],
                    'family': ['family', 'kids', 'children', 'playground'],
                    'casual': ['casual', 'relax', 'laid-back', 'informal'],
                    'formal': ['formal', 'elegant', 'fine dining', 'upscale'],
                    'scenic': ['view', 'beach', 'sunset', 'ocean', 'garden']
                }
                
                if mood in mood_indicators:
                    if any(indicator in restaurant_about for indicator in mood_indicators[mood]):
                        boost_score += 0.15
            
            return min(boost_score, 1.0)  
            
        except Exception as e:
            logger.error(f"Error calculating personalized boost: {e}")
            return 0.0
    
    def update_user_preferences_from_interaction(self, device_token: str, user_query: str, selected_restaurant: Dict = None):
        """Update user preferences based on interaction, now including dietary and price preferences"""
        try:
            logger.info(f"Updating preferences for device_token: {device_token}, query: '{user_query}'")
            
            new_cuisines = self._extract_cuisines(user_query.lower())
            new_locations = self._extract_locations(user_query.lower())
            new_moods = self._extract_mood_preferences(user_query.lower())
            new_dietary = self._extract_dietary_restrictions(user_query.lower())
            new_price = self._extract_price_preferences(user_query.lower())
            
            logger.info(f"Extracted - cuisines: {new_cuisines}, locations: {new_locations}, moods: {new_moods}, dietary: {new_dietary}, price: {new_price}")
            
            history = self.get_or_create_user_history(device_token)
            current_prefs = history.get('preferences', {})
            
            logger.info(f"Current preferences before update: {current_prefs}")
            
            if new_cuisines:
                current_cuisines = current_prefs.get('preferred_cuisines', [])
                for cuisine in new_cuisines:
                    if cuisine not in current_cuisines:
                        current_cuisines.append(cuisine)
                current_prefs['preferred_cuisines'] = current_cuisines[:5]  # Keep top 5
                logger.info(f"Updated cuisines: {current_prefs['preferred_cuisines']}")
            
            if new_locations:
                current_locations = current_prefs.get('preferred_locations', [])
                for location in new_locations:
                    if location not in current_locations:
                        current_locations.append(location)
                current_prefs['preferred_locations'] = current_locations[:3] 
                logger.info(f"Updated locations: {current_prefs['preferred_locations']}")
            
            if new_moods:
                current_moods = current_prefs.get('mood_preferences', [])
                for mood in new_moods:
                    if mood not in current_moods:
                        current_moods.append(mood)
                current_prefs['mood_preferences'] = current_moods
                logger.info(f"Updated moods: {current_prefs['mood_preferences']}")
            
            if new_dietary:
                current_dietary = current_prefs.get('dietary_restrictions', [])
                for diet in new_dietary:
                    if diet not in current_dietary:
                        current_dietary.append(diet)
                current_prefs['dietary_restrictions'] = current_dietary
                logger.info(f"Updated dietary restrictions: {current_prefs['dietary_restrictions']}")
            
            if new_price:
                current_prefs['price_preference'] = new_price[-1]
                logger.info(f"Updated price preference: {current_prefs['price_preference']}")
            
            if selected_restaurant:
                fav_restaurants = current_prefs.get('favorite_restaurants', [])
                restaurant_id = selected_restaurant.get('id')
                if restaurant_id and restaurant_id not in fav_restaurants:
                    fav_restaurants.append(restaurant_id)
                    current_prefs['favorite_restaurants'] = fav_restaurants[-10:]  
            
            history['preferences'] = current_prefs
            logger.info(f"Final preferences after update: {current_prefs}")
            self._save_user_history(device_token, history)
            logger.info(f"Preferences saved successfully for device_token: {device_token}")
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    def _extract_dietary_restrictions(self, text: str) -> list:
        """Extract dietary restrictions from text"""
        dietary_keywords = []
        if any(word in text for word in ['vegan', 'vegetarian', 'plant-based']):
            dietary_keywords.append('vegan')
        if any(word in text for word in ['vegetarian', 'ovo-lacto', 'ovo', 'lacto']):
            dietary_keywords.append('vegetarian')
        if 'halal' in text:
            dietary_keywords.append('halal')
        if 'kosher' in text:
            dietary_keywords.append('kosher')
        if 'gluten' in text:
            dietary_keywords.append('gluten-free')
        if 'allergy' in text or 'alergi' in text:
            dietary_keywords.append('allergy')
        return list(set(dietary_keywords))
