from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime
import random
import pandas as pd
from pathlib import Path
import re
from services.device_token_service import DeviceTokenService
from services.recommendation_engine import ContentBasedRecommendationEngine
from utils.session_manager import SessionManager
from config.settings import RESTAURANTS_ENTITAS_CSV
from utils.logger import get_logger

logger = get_logger("chatbot_service")

class ChatbotService:
    def __init__(self, data_path: str = None):
        self.data_path = data_path or str(RESTAURANTS_ENTITAS_CSV)
        self.restaurants_data = None
        self.sessions = {} 
        self.device_token_service = DeviceTokenService()
        self.session_manager = SessionManager(device_token_service=self.device_token_service)
        
        # Use ContentBasedRecommendationEngine instead of manual TF-IDF
        self.recommendation_engine = ContentBasedRecommendationEngine(data_path=self.data_path)
        
        self._load_restaurant_data()
    def _load_restaurant_data(self):
        """Load restaurant data for display purposes (ContentBasedRecommendationEngine handles its own data)"""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            csv_file = data_dir / "restaurants_entitas.csv"
            if csv_file.exists():
                self.restaurants_data = pd.read_csv(csv_file)
            else:
                for filename in ["restaurants_processed.csv", "restaurants.csv"]:
                    fallback_file = data_dir / filename
                    if fallback_file.exists():
                        self.restaurants_data = pd.read_csv(fallback_file)
                        break
            logger.info(f"Loaded {len(self.restaurants_data) if self.restaurants_data is not None else 0} restaurants for display")
        except Exception as e:
            logger.error(f"Error loading restaurant data: {e}")
            self.restaurants_data = None
    def start_conversation(self, user_id: str = None, device_token: str = None):
        if device_token:
            existing_session_id = self.session_manager.get_active_session_for_device(device_token)
            if existing_session_id:
                session_info = self.session_manager.get_session(existing_session_id)
                if session_info:
                    greeting = self._get_personalized_greeting(device_token, session_info)
                    
                    self.sessions[existing_session_id] = {
                        'user_id': session_info['device_token'], 
                        'device_token': device_token,
                        'messages': session_info['session_data'].get('messages', []),
                        'context': {},
                        'preferences': session_info['history_data'].get('preferences', {})
                    }
                    
                    return existing_session_id, greeting
        
        # Create new session
        session_id, greeting = self.session_manager.create_session(device_token, user_id)
        
        # Also add to memory sessions for backward compatibility
        if not user_id:
            user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'device_token': device_token,
            'messages': [],
            'context': {},
            'preferences': {}
        }
        
        return session_id, greeting
    def process_message(self, message: str, session_id: str):
        try:
            if not message or not message.strip():
                return "Silakan berikan kriteria restoran yang Anda cari."
            
            # Try to get session from persistent storage first
            session_info = self.session_manager.get_session(session_id)
            
            if not session_info:
                # Session not found or expired
                print(f"Warning: Session {session_id} not found or expired")
                return "Maaf, sesi Anda telah berakhir. Silakan mulai percakapan baru."
            
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'user_id': session_info['device_token'],
                    'device_token': session_info['device_token'],
                    'messages': session_info['session_data'].get('messages', []),
                    'context': {},
                    'preferences': session_info['history_data'].get('preferences', {})
                }
            
            self.sessions[session_id]['messages'].append({
                'user': message,
                'timestamp': datetime.now().isoformat()
            })
            
            message = message.lower().strip()
        except Exception as e:
            print(f"Error in process_message initialization: {e}")
            return "Maaf, terjadi kesalahan sistem. Silakan coba lagi."
        greeting_words = ['halo', 'hai', 'hello', 'hi']
        message_words = message.split()
        is_greeting_only = (
            len(message_words) <= 3 and 
            any(word in message for word in greeting_words) and
            not any(word in message for word in ['restoran', 'cari', 'mau', 'pizza', 'sushi', 'seafood', 'yang', 'di'])
        )
        if is_greeting_only:
            return self._get_greeting_response()
        
        import re
        exit_pattern = r'\b(' + '|'.join(['bye', 'keluar', 'selesai', 'exit', 'sampai jumpa']) + r')\b'
        if re.search(exit_pattern, message.lower()):
            return "Terima kasih telah menggunakan layanan kami! Sampai jumpa!"
        
        if any(word in message for word in ['help', 'bantuan', 'gimana', 'cara']):
            return self._get_help_response()
        
        try:
            intent, entities = self._extract_intent_and_entities(message)
            print(f"Intent: {intent}, Entities: {entities}")
            
            if intent == 'restaurant_search':
                bot_response = self._get_restaurant_recommendations_nlp(message, entities, session_id)
            elif intent == 'restaurant_details':
                restaurant_name = entities.get('restaurant_name', '')
                bot_response = self.get_restaurant_details(restaurant_name)
            else:
                bot_response = self._get_restaurant_recommendations_nlp(message, entities, session_id)
            
            # Save conversation to persistent storage
            self._save_conversation_to_session(session_id, message, bot_response)
            
            return bot_response
                
        except Exception as e:
            print(f"Error in processing intent/entities: {e}")
            # Fallback to simple keyword search
            fallback_entities = {'cuisine': [], 'location': [], 'price': []}
            bot_response = self._get_restaurant_recommendations_nlp(message, fallback_entities, session_id)
            
            # Save conversation to persistent storage
            self._save_conversation_to_session(session_id, message, bot_response)
            
            return bot_response
    
    def _get_personalized_greeting(self, device_token: str, session_info: dict):
        """Generate personalized greeting based on user's history and preferences"""
        try:
            preferences = session_info.get('history_data', {}).get('preferences', {})
            
            greeting_parts = ["Selamat datang kembali! "]
            
            # Add personalized content based on preferences
            preferred_cuisines = preferences.get('preferred_cuisines', [])
            mood_preferences = preferences.get('mood_preferences', [])
            
            if preferred_cuisines:
                if len(preferred_cuisines) == 1:
                    greeting_parts.append(f"Saya ingat Anda suka masakan {preferred_cuisines[0]}. ")
                else:
                    greeting_parts.append(f"Saya ingat preferensi Anda untuk masakan {', '.join(preferred_cuisines[:2])}. ")
            
            if mood_preferences:
                if 'family' in mood_preferences and 'romantic' in mood_preferences:
                    greeting_parts.append("Apakah kali ini untuk acara keluarga atau momen romantis? ")
                elif 'family' in mood_preferences:
                    greeting_parts.append("Ada rencana makan bersama keluarga lagi? ")
                elif 'romantic' in mood_preferences:
                    greeting_parts.append("Sedang mencari tempat yang romantis? ")
            
            greeting_parts.append("\n\nApa yang Anda cari hari ini?")
            
            return "".join(greeting_parts)
            
        except Exception as e:
            print(f"Error generating personalized greeting: {e}")
            return "Selamat datang kembali! Mari lanjutkan percakapan kita."
    
    def _get_greeting_response(self):
        responses = [
            "Halo! Saya siap membantu Anda mencari restoran yang pas!\n\nCoba ceritakan apa yang Anda inginkan, misalnya:\n- 'Pizza yang romantis di Kuta'\n- 'Seafood murah di Gili Trawangan'\n- 'Tempat makan keluarga yang santai'",
            "Hai! Senang bisa membantu Anda!\n\nSilakan beri tahu saya kriteria restoran yang Anda cari. Saya bisa membantu berdasarkan:\n- Jenis masakan\n- Lokasi\n- Suasana\n- Budget"
        ]
        return random.choice(responses)
    def _get_help_response(self):
        return """Panduan Chatbot Rekomendasi Restoran

Cara Mencari Restoran:
• Sebutkan jenis makanan: "pizza", "seafood", "sushi", "italian"
• Tambahkan lokasi: "di Kuta", "Senggigi", "Gili Trawangan"
• Sebutkan budget: "murah", "mahal", "budget"
• Suasana: "romantis", "santai", "keluarga"

Contoh Pencarian:
• "Pizza enak di Kuta"
• "Seafood murah di Senggigi"
• "Restoran romantis untuk dinner"
• "Tempat makan keluarga yang santai"

Perintah Lain:
• "bye" - Mengakhiri percakapan
• "help" - Menampilkan bantuan ini

Tips: Semakin spesifik permintaan Anda, semakin baik rekomendasi yang saya berikan!""" 
    def _extract_intent_and_entities(self, message: str):
        entities = {
            'cuisine': [],
            'location': [],
            'mood': [],
            'price': [],
            'restaurant_name': ''
        }
        cuisine_patterns = {
            'pizza': ['pizza', 'pizzeria'],
            'seafood': ['seafood', 'sea food', 'ikan', 'udang', 'kepiting'],
            'sushi': ['sushi', 'japanese', 'jepang'],
            'italian': ['italian', 'italia', 'pasta'],
            'chinese': ['chinese', 'china', 'dim sum'],
            'local': ['local', 'lokal', 'tradisional', 'nusantara'],
            'western': ['western', 'barat', 'steak', 'burger']
        }
        location_patterns = {
            'kuta': ['kuta'],
            'gili_trawangan': ['gili trawangan', 'trawangan', 'gili'],
            'senggigi': ['senggigi'],
            'mataram': ['mataram'],
            'gili_air': ['gili air'],
            'gili_meno': ['gili meno']
        }
        mood_patterns = {
            'romantic': ['romantis', 'romantic', 'dinner', 'malam'],
            'family': ['keluarga', 'family', 'anak', 'kids'],
            'casual': ['santai', 'casual', 'biasa'],
            'beachside': ['tepi pantai', 'beach', 'pantai']
        }
        price_patterns = {
            'cheap': ['murah', 'terjangkau', 'budget'],
            'expensive': ['mahal', 'mewah', 'premium']
        }
        for category, pattern_dict in [
            ('cuisine', cuisine_patterns),
            ('location', location_patterns), 
            ('mood', mood_patterns),
            ('price', price_patterns)
        ]:
            for entity, patterns in pattern_dict.items():
                for pattern in patterns:
                    if pattern in message:
                        entities[category].append(entity)
        if 'restoran' in message or 'restaurant' in message:
            words = message.split()
            for i, word in enumerate(words):
                if word in ['restoran', 'restaurant'] and i < len(words) - 1:
                    entities['restaurant_name'] = words[i + 1]
                    break
        intent = 'restaurant_search'
        if any(word in message for word in ['detail', 'info', 'tentang']):
            intent = 'restaurant_details'
        return intent, entities
    def _get_restaurant_recommendations_nlp(self, query: str, entities: dict, session_id: str = None):
        """Get restaurant recommendations using ContentBasedRecommendationEngine"""
        if self.restaurants_data is None:
            return "Maaf, data restoran belum tersedia. Silakan coba lagi nanti."
        
        try:
            logger.info(f"Getting recommendations for query: '{query}'")
            
            # Use ContentBasedRecommendationEngine to get recommendations
            recommendations_objects = self.recommendation_engine.get_recommendations(query, top_n=15)
            
            if not recommendations_objects:
                logger.warning(f"No recommendations found for query: '{query}'")
                return self._get_smart_fallback_response(query, entities)
            
            # Convert recommendation objects to the format expected by the rest of the code
            recommendations = []
            device_token = None
            if session_id and session_id in self.sessions:
                device_token = self.sessions[session_id].get('device_token')
            
            for rec_obj in recommendations_objects:
                restaurant = rec_obj.restaurant
                
                # Find matching row in restaurants_data for additional info
                matching_rows = self.restaurants_data[self.restaurants_data['name'] == restaurant.name]
                if not matching_rows.empty:
                    restaurant_row = matching_rows.iloc[0]
                else:
                    # If not found, skip this recommendation
                    continue
                
                # Calculate entity bonus
                bonus_score = self._calculate_entity_bonus(restaurant_row, entities)
                
                # Get personalized boost
                preference_boost = 0.0
                if device_token:
                    restaurant_data = self._extract_restaurant_data(restaurant_row)
                    preference_boost = self.device_token_service.get_personalized_boost(device_token, restaurant_data)
                
                # Combine scores
                total_score = rec_obj.similarity_score + bonus_score + (preference_boost * 0.5)
                
                recommendations.append({
                    'restaurant': restaurant_row,
                    'similarity': rec_obj.similarity_score,
                    'bonus_score': bonus_score,
                    'preference_boost': preference_boost,
                    'total_score': total_score,
                    'device_token': device_token,
                    'base_score': rec_obj.similarity_score + bonus_score
                })
            
            if not recommendations:
                logger.warning("No matching restaurants found in DataFrame")
                return self._get_smart_fallback_response(query, entities)
            
            logger.info(f"ContentBasedRecommendationEngine returned {len(recommendations)} recommendations")
            
            # Update user preferences
            if device_token:
                self.device_token_service.update_user_preferences_from_interaction(device_token, query)
            
            # Sort by total score
            recommendations.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Return formatted response
            return self._format_recommendations_nlp(recommendations[:5], query, entities, session_id)
                
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            import traceback
            traceback.print_exc()
            return self._get_smart_fallback_response(query, entities)
    def _calculate_entity_bonus(self, restaurant, entities):
        bonus = 0.0
        for cuisine in entities.get('cuisine', []):
            if pd.notna(restaurant.get('cuisines')):
                cuisine_text = str(restaurant['cuisines']).lower()
                if cuisine.replace('_', ' ') in cuisine_text:
                    bonus += 0.3
        for location in entities.get('location', []):
            if pd.notna(restaurant.get('location')):
                location_text = str(restaurant['location']).lower()
                if location.replace('_', ' ') in location_text:
                    bonus += 0.4
        if entities.get('price'):
            if pd.notna(restaurant.get('price_range')):
                price_text = str(restaurant['price_range']).lower()
                for price in entities['price']:
                    if (price == 'cheap' and any(word in price_text for word in ['$', 'budget', 'cheap'])) or \
                       (price == 'expensive' and any(word in price_text for word in ['$$$', 'premium', 'expensive'])):
                        bonus += 0.2
        return bonus
    
    def _format_recommendations_nlp(self, recommendations, query, entities, session_id: str = None):
        entity_summary = []
        if entities.get('cuisine'):
            entity_summary.append(f"masakan {', '.join(entities['cuisine'])}")
        if entities.get('location'):
            entity_summary.append(f"di {', '.join(entities['location'])}")
        if entities.get('mood'):
            entity_summary.append(f"suasana {', '.join(entities['mood'])}")
        if entities.get('price'):
            entity_summary.append(f"harga {', '.join(entities['price'])}")
        
        context = " dengan " + " dan ".join(entity_summary) if entity_summary else ""
        
        has_personal_recs = any(rec.get('preference_boost', 0) > 0.1 for rec in recommendations)
        
        response = f"Berdasarkan pencarian '{query}'{context}, saya menemukan {len(recommendations)} restoran terbaik"
        if has_personal_recs:
            response += " (sesuai preferensi Anda)"
        response += ":\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            restaurant = rec['restaurant']
            total_score = rec.get('total_score', rec.get('similarity', rec.get('score', 0)))
            preference_boost = rec.get('preference_boost', 0)
            base_score = rec.get('base_score', rec.get('score', 0))
            similarity = rec.get('similarity', 0)
            
            response += f"{i}. {restaurant.get('name', 'Unknown')}\n"
            
            rating = restaurant.get('rating', 'N/A')
            if pd.notna(rating) and rating != 'N/A':
                response += f"   Rating: {rating}/5.0"
            else:
                response += f"   Rating: Belum tersedia"
            
            if similarity > 0:  
                match_percentage = min(int((similarity + preference_boost) * 100), 100)
            else: 
                max_possible_score = 15 
                normalized_score = min(base_score / max_possible_score, 1.0)
                match_percentage = min(int((normalized_score + preference_boost) * 100), 100)
            
            response += f" | Kecocokan: {match_percentage}%"
            
            if preference_boost > 0.1:
                response += ""
            response += "\n"
            
            if pd.notna(restaurant.get('about')):
                desc = str(restaurant['about'])
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                response += f"   {desc}\n"
            
            if pd.notna(restaurant.get('cuisines')):
                cuisines = str(restaurant['cuisines'])
                response += f"   Jenis masakan: {cuisines}\n"
                
                if preference_boost > 0.1:
                    device_token = rec.get('device_token')
                    if device_token:
                        personal_reason = self._get_personal_recommendation_reason(device_token, restaurant)
                        if personal_reason:
                            response += f"  {personal_reason}\n"
            
            if pd.notna(restaurant.get('location')):
                location = str(restaurant['location'])
                response += f"   Lokasi: {location}\n"
            
            if pd.notna(restaurant.get('price_range')):
                price = str(restaurant['price_range'])
                response += f"   Harga: {price}\n"
            
            response += "\n"
                
        follow_ups = []
        if not entities.get('location'):
            follow_ups.append("Mau cari di lokasi tertentu?")
        if not entities.get('price'):
            follow_ups.append("Ada budget khusus?")
        if not entities.get('mood'):
            follow_ups.append("Untuk acara apa?")
        
        if follow_ups:
            response += "\n".join(follow_ups[:2])
            response += "\nAtau butuh info lebih detail?"
        else:
            response += "Butuh info lebih detail?\nAtau mau cari dengan kriteria lain?"
        
        return response
    def _get_smart_fallback_response(self, query, entities):
        try:
            response = f"Hmm, saya tidak menemukan restoran yang persis cocok dengan '{query}'.\n\n"
            
            if self.restaurants_data is not None and len(self.restaurants_data) > 0:
                try:
                    top_restaurants = self.restaurants_data.nlargest(3, 'rating', keep='first')
                    if not top_restaurants.empty:
                        response += "Bagaimana dengan beberapa restoran populer ini?\n\n"
                        for idx, restaurant in top_restaurants.iterrows():
                            name = restaurant.get('name', 'Unknown')
                            rating = restaurant.get('rating', 'N/A')
                            location = restaurant.get('location', 'Unknown')
                            cuisines = restaurant.get('cuisines', 'Various')
                            response += f"{name} ({rating}/5.0)\n"
                            response += f"{location} | {cuisines}\n\n"
                        
                        response += "Atau coba pencarian yang lebih spesifik:\n"
                except Exception as e:
                    print(f"Error getting popular restaurants: {e}")
            
            suggestions = []
            if not entities.get('cuisine') and not entities.get('location'):
                suggestions.extend([
                    "Coba: 'pizza enak di Kuta'",
                    "Atau: 'seafood murah di Senggigi'",
                    "Contoh: 'italian food romantic'"
                ])
            elif not entities.get('cuisine'):
                suggestions.extend([
                    "Tambahkan jenis makanan: 'pizza', 'seafood', 'sushi'",
                    "Atau masakan: 'italian', 'japanese', 'chinese'"
                ])
            elif not entities.get('location'):
                suggestions.extend([
                    "Sebutkan lokasi: 'Kuta', 'Senggigi', 'Gili Trawangan'",
                    "Atau area: 'dekat pantai', 'pusat kota'"
                ])
            
            if suggestions:
                for suggestion in suggestions:
                    response += f"{suggestion}\n"
                response += "\n"
            
            response += "Butuh bantuan lain? Ketik 'help' untuk panduan lengkap!"
            return response
            
        except Exception as e:
            print(f"Error in fallback response: {e}")
            return "Maaf, saya tidak dapat memproses permintaan Anda saat ini. Silakan coba dengan kata kunci yang lebih sederhana seperti 'pizza Kuta' atau 'seafood murah'."
    def get_conversation_history(self, session_id: str):
        return []
    def get_restaurant_details(self, name: str):
        if self.restaurants_data is None:
            return "Data restoran tidak tersedia."
        matches = self.restaurants_data[
            self.restaurants_data['name'].str.contains(name, case=False, na=False)
        ]
        if matches.empty:
            return f"Maaf, tidak ditemukan restoran dengan nama '{name}'. Coba gunakan nama yang lebih spesifik."
        restaurant = matches.iloc[0]
        details = f"{restaurant.get('name', 'Unknown')}\n"
        details += f"Rating: {restaurant.get('rating', 'N/A')}/5.0\n\n"
        if pd.notna(restaurant.get('about')):
            details += f"Tentang: {restaurant['about']}\n\n"
        if pd.notna(restaurant.get('cuisines')):
            details += f"Jenis Masakan: {restaurant['cuisines']}\n"
        if pd.notna(restaurant.get('location')):
            details += f"Lokasi: {restaurant['location']}\n"
        if pd.notna(restaurant.get('price_range')):
            details += f"Harga: {restaurant['price_range']}\n"
        return details
    def get_recommendations_by_category(self, category: str):
        if self.restaurants_data is None:
            return "Data restoran tidak tersedia."
        matches = self.restaurants_data[
            self.restaurants_data['cuisines'].str.contains(category, case=False, na=False) |
            self.restaurants_data['location'].str.contains(category, case=False, na=False)
        ]
        if matches.empty:
            return f"Maaf, tidak ditemukan restoran untuk kategori '{category}'."
        response = f"Rekomendasi Restoran untuk kategori '{category}':\n\n"
        for i, (idx, restaurant) in enumerate(matches.head(5).iterrows(), 1):
            response += f"{i}. {restaurant.get('name', 'Unknown')} (Rating: {restaurant.get('rating', 'N/A')}/5.0)\n"
            if pd.notna(restaurant.get('cuisines')):
                response += f"   {restaurant['cuisines']}\n"
            response += "\n"
        return response
    def get_statistics(self):
        """Get statistics from recommendation engine"""
        try:
            stats = self.recommendation_engine.get_statistics()
            return {
                'chatbot': {
                    'current_session_turns': 0, 
                    'user_profile_interactions': 0, 
                    'active_sessions': 1
                },
                'recommendation_engine': stats
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            total_restaurants = len(self.restaurants_data) if self.restaurants_data is not None else 0
            return {
                'chatbot': {
                    'current_session_turns': 0, 
                    'user_profile_interactions': 0, 
                    'active_sessions': 1
                },
                'recommendation_engine': {
                    'total_restaurants': total_restaurants,
                    'average_rating': 0
                }
            }
    
    def _extract_restaurant_entities(self, restaurant) -> Dict[str, List[str]]:
        entities = {}
        
        if pd.notna(restaurant.get('entitas_jenis_makanan')):
            try:
                entities['jenis_makanan'] = eval(restaurant['entitas_jenis_makanan']) if isinstance(restaurant['entitas_jenis_makanan'], str) else restaurant['entitas_jenis_makanan']
            except:
                entities['jenis_makanan'] = []
        else:
            entities['jenis_makanan'] = []
        
        if pd.notna(restaurant.get('entitas_lokasi')):
            entities['lokasi'] = [restaurant['entitas_lokasi']] if isinstance(restaurant['entitas_lokasi'], str) else [str(restaurant['entitas_lokasi'])]
        else:
            entities['lokasi'] = []
        
        if pd.notna(restaurant.get('entitas_features')):
            try:
                entities['features'] = eval(restaurant['entitas_features']) if isinstance(restaurant['entitas_features'], str) else restaurant['entitas_features']
            except:
                entities['features'] = []
        else:
            entities['features'] = []
        
        return entities
    
    def _extract_restaurant_data(self, restaurant) -> Dict:
        restaurant_data = {
            'id': restaurant.get('id', ''),
            'name': restaurant.get('name', ''),
            'cuisines': restaurant.get('cuisines', ''),
            'location': restaurant.get('location', ''),
            'about': restaurant.get('about', ''),
            'price_range': restaurant.get('price_range', ''),
            'rating': restaurant.get('rating', 0)
        }
        return restaurant_data
    
    def _save_conversation_to_session(self, session_id: str, user_message: str, bot_response: str):
        try:
            self.session_manager.update_session(session_id, user_message, bot_response)
        except Exception as e:
            print(f"Error saving conversation to session: {e}")
    
    def _get_personal_recommendation_reason(self, device_token: str, restaurant) -> str:
        try:
            history = self.device_token_service.get_or_create_user_history(device_token)
            preferences = history.get('preferences', {})
            
            reasons = []
            
            restaurant_cuisines = str(restaurant.get('cuisines', '')).lower()
            preferred_cuisines = preferences.get('preferred_cuisines', [])
            matching_cuisines = []
            for cuisine in preferred_cuisines:
                if cuisine.lower() in restaurant_cuisines:
                    matching_cuisines.append(cuisine)
            
            if matching_cuisines:
                if len(matching_cuisines) == 1:
                    reasons.append(f"Sesuai preferensi Anda, masakan {matching_cuisines[0]}")
                else:
                    reasons.append(f"Sesuai preferensi Anda, masakan {', '.join(matching_cuisines)}")
            
            restaurant_about = str(restaurant.get('about', '')).lower()
            mood_preferences = preferences.get('mood_preferences', [])
            matching_moods = []
            
            mood_indicators = {
                'romantic': ['romantic', 'couple', 'intimate', 'cozy'],
                'family': ['family', 'kids', 'children', 'playground'],
                'casual': ['casual', 'relax', 'laid-back', 'informal'],
                'formal': ['formal', 'elegant', 'fine dining', 'upscale'],
                'scenic': ['view', 'beach', 'sunset', 'ocean', 'garden']
            }
            
            for mood in mood_preferences:
                if mood in mood_indicators:
                    if any(indicator in restaurant_about for indicator in mood_indicators[mood]):
                        matching_moods.append(mood)
            
            if matching_moods:
                if 'family' in matching_moods:
                    reasons.append("Cocok untuk acara keluarga")
                if 'romantic' in matching_moods:
                    reasons.append("Suasana romantis yang Anda suka")
            
            return ". ".join(reasons) if reasons else ""
            
        except Exception as e:
            print(f"Error generating personal reason: {e}")
            return ""
    
    def get_user_preferences_summary(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        user_id = self.sessions[session_id].get('user_id')
        if not user_id:
            return {"error": "User ID not found"}
        
        return {"message": "User preferences migrated to device token system"}