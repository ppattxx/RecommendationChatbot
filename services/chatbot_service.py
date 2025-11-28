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
from utils.entity_builder import EntityBuilder

logger = get_logger("chatbot_service")

class ChatbotService:
    def __init__(self, data_path: str = None):
        self.data_path = data_path or str(RESTAURANTS_ENTITAS_CSV)
        self.restaurants_data = None
        self.sessions = {} 
        self.device_token_service = DeviceTokenService()
        self.session_manager = SessionManager(device_token_service=self.device_token_service)
        self.recommendation_engine = ContentBasedRecommendationEngine(data_path=self.data_path)
        
        self.entity_builder = EntityBuilder(data_path=self.data_path)
        self.entity_patterns = None
        
        self._load_restaurant_data()
    def _load_restaurant_data(self):
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
        
        session_id, greeting = self.session_manager.create_session(device_token, user_id)
        
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
            
            session_info = self.session_manager.get_session(session_id)
            
            if not session_info:
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
            return "Maaf, terjadi kesalahan sistem. Silakan coba lagi."
        
        invalid_patterns = [
            r'^/api/',
            r'^\w+\.\w+',
            r'^http[s]?://',
            r'^[^a-zA-Z0-9\s]{5,}',
            r'^\d{10,}$'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, message):
                return "Maaf, saya tidak mengerti input tersebut. Silakan tanyakan tentang restoran seperti:\n\n• 'Pizza di Kuta'\n• 'Seafood murah di Senggigi'\n• 'Restoran romantis untuk dinner'\n\nKetik 'help' untuk panduan lengkap!"
        
        greeting_words = ['halo', 'hai', 'hello', 'hi']
        message_words = message.split()
        is_greeting_only = (
            len(message_words) <= 3 and 
            any(word in message for word in greeting_words) and
            not any(word in message for word in ['restoran', 'cari', 'mau', 'pizza', 'sushi', 'seafood', 'yang', 'di'])
        )
        if is_greeting_only:
            return self._get_greeting_response()
        
        exit_pattern = r'\b(' + '|'.join(['bye', 'keluar', 'selesai', 'exit', 'sampai jumpa']) + r')\b'
        if re.search(exit_pattern, message.lower()):
            return "Terima kasih telah menggunakan layanan kami! Sampai jumpa!"
        
        if any(word in message for word in ['help', 'bantuan', 'gimana', 'cara']):
            return self._get_help_response()
        
        try:
            intent, entities = self._extract_intent_and_entities(message)
            
            if intent == 'restaurant_search':
                bot_response = self._get_restaurant_recommendations_nlp(message, entities, session_id)
            elif intent == 'restaurant_details':
                restaurant_name = entities.get('restaurant_name', '')
                bot_response = self.get_restaurant_details(restaurant_name)
            else:
                bot_response = self._get_restaurant_recommendations_nlp(message, entities, session_id)
            
            self._save_conversation_to_session(session_id, message, bot_response)
            
            return bot_response
                
        except Exception as e:
            fallback_entities = {'cuisine': [], 'location': [], 'price': []}
            bot_response = self._get_restaurant_recommendations_nlp(message, fallback_entities, session_id)
            
            self._save_conversation_to_session(session_id, message, bot_response)
            
            return bot_response
    
    def _get_personalized_greeting(self, device_token: str, session_info: dict):
        try:
            preferences = session_info.get('history_data', {}).get('preferences', {})
            
            greeting_parts = ["Selamat datang kembali! "]
            
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
        
        if self.entity_patterns is None:
            self.entity_patterns = self.entity_builder.get_flattened_patterns()
        
        message_lower = message.lower()
        
        matched_tokens = set()
        
        for location in sorted(self.entity_patterns['location'], key=len, reverse=True):
            if re.search(r'\b' + re.escape(location) + r'\b', message_lower):
                if location not in entities['location']:
                    entities['location'].append(location)
                    matched_tokens.add(location)
                    for word in location.split():
                        matched_tokens.add(word)
                    break
        
        for cuisine in sorted(self.entity_patterns['cuisine'], key=len, reverse=True):
            if cuisine in matched_tokens:
                continue
            if re.search(r'\b' + re.escape(cuisine) + r'\b', message_lower):
                if cuisine not in entities['cuisine']:
                    entities['cuisine'].append(cuisine)
                    matched_tokens.add(cuisine)
                    for word in cuisine.split():
                        matched_tokens.add(word)
        
        if not entities['cuisine']:
            for menu_item in sorted(self.entity_patterns['menu'], key=len, reverse=True):
                if menu_item in matched_tokens:
                    continue
                if re.search(r'\b' + re.escape(menu_item) + r'\b', message_lower):
                    if menu_item not in entities['cuisine']:
                        entities['cuisine'].append(menu_item)
                        matched_tokens.add(menu_item)
                        for word in menu_item.split():
                            matched_tokens.add(word)
        
        food_related_keywords = ['pizza', 'pasta', 'burger', 'sushi', 'ramen', 'noodle', 'rice', 
                                  'chicken', 'beef', 'pork', 'fish', 'seafood', 'vegetarian', 'vegan',
                                  'taco', 'tacos', 'burrito', 'sandwich', 'salad', 'soup', 'curry',
                                  'steak', 'bbq', 'barbecue', 'grill', 'fried', 'bakery', 'dessert']
        
        for mood in sorted(self.entity_patterns['mood'], key=len, reverse=True):
            if mood in matched_tokens:
                continue
            skip_mood = False
            for token in matched_tokens:
                if mood in token or token in mood:
                    skip_mood = True
                    break
            if skip_mood:
                continue
            
            if not re.search(r'\b' + re.escape(mood) + r'\b', message_lower):
                continue
            
            if mood.lower() in food_related_keywords:
                if mood not in entities['cuisine']:
                    entities['cuisine'].append(mood)
            else:
                if mood not in entities['mood']:
                    entities['mood'].append(mood)
        
        price_patterns = {
            'cheap': ['murah', 'terjangkau', 'budget'],
            'expensive': ['mahal', 'mewah', 'premium']
        }
        for price_type, keywords in price_patterns.items():
            if any(kw in message_lower for kw in keywords):
                entities['price'].append(price_type)
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
        if self.restaurants_data is None:
            return "Maaf, data restoran belum tersedia. Silakan coba lagi nanti."
        
        try:
            
            recommendations_objects = self.recommendation_engine.get_recommendations(query, top_n=15)
            
            if not recommendations_objects:
                logger.warning(f"No recommendations found for query: '{query}'")
                return self._get_smart_fallback_response(query, entities)
            
            recommendations = []
            device_token = None
            if session_id and session_id in self.sessions:
                device_token = self.sessions[session_id].get('device_token')
            
            for rec_obj in recommendations_objects:
                restaurant = rec_obj.restaurant
                
                matching_rows = self.restaurants_data[self.restaurants_data['name'] == restaurant.name]
                if not matching_rows.empty:
                    restaurant_row = matching_rows.iloc[0]
                else:
                    continue
                
                bonus_score = self._calculate_entity_bonus(restaurant_row, entities)
                
                preference_boost = 0.0
                if device_token:
                    restaurant_data = self._extract_restaurant_data(restaurant_row)
                    preference_boost = self.device_token_service.get_personalized_boost(device_token, restaurant_data)
                
                rating = float(restaurant_row.get('rating', 0))
                rating_factor = (rating / 5.0) * 0.5
                
                reviews_count = int(restaurant_row.get('reviews_count', 0))
                popularity_factor = min(reviews_count / 1000.0, 0.3)
                
                total_score = rec_obj.similarity_score + bonus_score + (preference_boost * 1.5) + rating_factor + popularity_factor
                
                if entities.get('location'):
                    restaurant_location = restaurant_row['entitas_lokasi'] if 'entitas_lokasi' in restaurant_row.index else 'UNKNOWN'
                
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
            if entities.get('location'):
                initial_count = len(recommendations)
                recommendations = [rec for rec in recommendations if rec['total_score'] > 0]
                filtered_count = initial_count - len(recommendations)
            
            if not recommendations:
                logger.warning("No recommendations after filtering negative scores")
                return self._get_smart_fallback_response(query, entities)
            
            if device_token:
                self.device_token_service.update_user_preferences_from_interaction(device_token, query)
            
            for rec in recommendations:
                rec['tie_breaker'] = random.random() * 0.01
            
            recommendations.sort(
                key=lambda x: (
                    x['total_score'], 
                    x.get('preference_boost', 0),
                    x['restaurant'].get('rating', 0),
                    x['restaurant'].get('reviews_count', 0),
                    x.get('similarity', 0),
                    x.get('tie_breaker', 0)
                ), 
                reverse=True
            )
            
            recommendations = self._apply_diversity_ranking(recommendations[:10])
            
            return self._format_recommendations_nlp(recommendations[:5], query, entities, session_id)
                
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            import traceback
            traceback.print_exc()
            return self._get_smart_fallback_response(query, entities)
    def _calculate_entity_bonus(self, restaurant, entities):
        bonus = 0.0
        match_count = 0
        
        location_match = False
        if entities.get('location'):
            restaurant_location = restaurant['entitas_lokasi'] if 'entitas_lokasi' in restaurant.index else None
            
            if pd.notna(restaurant_location):
                location_text = str(restaurant_location).lower()
                for location in entities['location']:
                    location_normalized = location.replace('_', ' ')
                    if location_normalized in location_text:
                        bonus += 2.0
                        location_match = True
                        match_count += 1
                        break
                
                if not location_match:
                    bonus -= 3.0
        
        cuisine_matches = 0
        for cuisine in entities.get('cuisine', []):
            restaurant_cuisines = restaurant['cuisines'] if 'cuisines' in restaurant.index else None
            if pd.notna(restaurant_cuisines):
                cuisine_text = str(restaurant_cuisines).lower()
                if cuisine.replace('_', ' ') in cuisine_text:
                    cuisine_matches += 1
                    match_count += 1
        
        if cuisine_matches > 0:
            bonus += 0.5 + (cuisine_matches * 0.2)
        
        if entities.get('price'):
            restaurant_price = restaurant['price_range'] if 'price_range' in restaurant.index else None
            if pd.notna(restaurant_price):
                price_text = str(restaurant_price).lower()
                for price in entities['price']:
                    if (price == 'cheap' and any(word in price_text for word in ['$', 'budget', 'cheap'])) or \
                       (price == 'expensive' and any(word in price_text for word in ['$$$', 'premium', 'expensive'])):
                        bonus += 0.2
        
        return bonus
    
    def _apply_diversity_ranking(self, recommendations):
        if len(recommendations) <= 1:
            return recommendations
        
        score_groups = []
        current_group = [recommendations[0]]
        
        for i in range(1, len(recommendations)):
            score_diff = abs(recommendations[i]['total_score'] - current_group[0]['total_score'])
            if score_diff < 0.1:
                current_group.append(recommendations[i])
            else:
                score_groups.append(current_group)
                current_group = [recommendations[i]]
        score_groups.append(current_group)
        
        final_recommendations = []
        for group in score_groups:
            if len(group) > 1:
                seen_cuisines = set()
                diverse_group = []
                personalized_group = []
                
                for rec in sorted(group, key=lambda x: x['preference_boost'], reverse=True):
                    if rec['preference_boost'] > 0.1:
                        personalized_group.append(rec)
                
                personalized_ids = {r.get('restaurant_id') for r in personalized_group}
                
                for rec in group:
                    if rec.get('restaurant_id') in personalized_ids:
                        continue
                    cuisines = str(rec['restaurant'].get('cuisines', '')).lower()
                    is_diverse = True
                    for seen in seen_cuisines:
                        if seen in cuisines or cuisines in seen:
                            is_diverse = False
                            break
                    if is_diverse or len(diverse_group) < 2:
                        diverse_group.append(rec)
                        seen_cuisines.add(cuisines)
                
                diverse_ids = {r.get('restaurant_id') for r in diverse_group}
                all_selected_ids = personalized_ids | diverse_ids
                
                final_recommendations.extend(personalized_group)
                final_recommendations.extend([r for r in diverse_group if r.get('restaurant_id') not in personalized_ids])
                final_recommendations.extend([r for r in group if r.get('restaurant_id') not in all_selected_ids])
            else:
                final_recommendations.extend(group)
        
        return final_recommendations
    
    def _format_recommendations_nlp(self, recommendations, query, entities, session_id: str = None):
        has_personal_recs = any(rec.get('preference_boost', 0) > 0.1 for rec in recommendations)
        
        device_token = None
        if session_id and session_id in self.sessions:
            device_token = self.sessions[session_id].get('device_token')
        
        response = ""
        
        if has_personal_recs and device_token:
            history = self.device_token_service.get_or_create_user_history(device_token)
            preferences = history.get('preferences', {})
            
            pref_parts = []
            if preferences.get('preferred_cuisines'):
                top_cuisines = preferences['preferred_cuisines'][:3]
                pref_parts.append(f"masakan {', '.join(top_cuisines)}")
            if preferences.get('preferred_locations'):
                top_locations = preferences['preferred_locations'][:2]
                pref_parts.append(f"area {', '.join(top_locations)}")
            if preferences.get('mood_preferences'):
                top_moods = preferences['mood_preferences'][:2]
                pref_parts.append(f"suasana {', '.join(top_moods)}")
            
            if pref_parts:
                response = f"Berdasarkan preferensi Anda ({', '.join(pref_parts)}), "
            else:
                response = f"Berdasarkan pencarian '{query}', "
        else:
            response = f"Berdasarkan pencarian '{query}', "
        
        response += f"saya menemukan {len(recommendations)} restoran terbaik untuk Anda:\n\n"
        
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
            max_realistic_score = 4.225
            normalized_total = min(total_score / max_realistic_score, 1.0)
            match_percentage = min(int(normalized_total * 100), 100)
            
            response += f" | Kecocokan: {match_percentage}%"
            
            if preference_boost > 0.15:
                response += " "
            elif preference_boost > 0.05:
                response += " (Sesuai preferensi Anda) "
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
                            
                            cuisines_raw = restaurant.get('cuisines', 'Various')
                            if isinstance(cuisines_raw, str) and cuisines_raw.startswith('['):
                                try:
                                    import ast
                                    cuisines_list = ast.literal_eval(cuisines_raw)
                                    cuisines = ', '.join(cuisines_list) if isinstance(cuisines_list, list) else cuisines_raw
                                except:
                                    cuisines = cuisines_raw.replace('[','').replace(']','').replace("'",'')
                            else:
                                cuisines = str(cuisines_raw)
                            
                            response += f"{name} ({rating}/5.0)\n"
                            response += f"Masakan: {cuisines}\n\n"
                        
                        response += "Atau coba pencarian yang lebih spesifik:\n"
                except Exception as e:
                    logger.error(f"Error getting popular restaurants: {e}")
            
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
            pass
    
    def _get_personal_recommendation_reason(self, device_token: str, restaurant) -> str:
        try:
            history = self.device_token_service.get_or_create_user_history(device_token)
            preferences = history.get('preferences', {})
            
            reasons = []
            
            restaurant_cuisines = str(restaurant.get('cuisines', '')).lower()
            preferred_cuisines = preferences.get('preferred_cuisines', [])
            matching_cuisines = []
            for cuisine in preferred_cuisines[:5]:
                if cuisine.lower() in restaurant_cuisines:
                    matching_cuisines.append(cuisine)
            
            if matching_cuisines:
                reasons.append(f"Anda sering mencari {', '.join(matching_cuisines[:2])}")
            
            restaurant_location = str(restaurant.get('entitas_lokasi', '')).lower()
            preferred_locations = preferences.get('preferred_locations', [])
            matched_fav_location = None
            if preferred_locations:
                for i, location in enumerate(preferred_locations[:3]):
                    if location.lower() in restaurant_location:
                        matched_fav_location = (location, i + 1)
                        break
            
            if matched_fav_location:
                location_name, rank = matched_fav_location
                if rank == 1:
                    reasons.append(f"Lokasi favorit #1 Anda: {location_name}")
                elif rank == 2:
                    reasons.append(f"Area yang sering Anda cari: {location_name}")
                else:
                    reasons.append(f"Sesuai preferensi lokasi: {location_name}")
            
            restaurant_about = str(restaurant.get('about', '')).lower()
            restaurant_features = str(restaurant.get('entitas_features', '')).lower()
            mood_preferences = preferences.get('mood_preferences', [])
            matching_moods = []
            
            mood_indicators = {
                'romantic': ['romantic', 'couple', 'intimate', 'cozy', 'romantis'],
                'family': ['family', 'kids', 'children', 'playground', 'keluarga'],
                'casual': ['casual', 'relax', 'laid-back', 'informal', 'santai'],
                'formal': ['formal', 'elegant', 'fine dining', 'upscale', 'mewah'],
                'scenic': ['view', 'beach', 'sunset', 'ocean', 'garden', 'pemandangan']
            }
            
            for mood in mood_preferences[:3]:
                mood_lower = mood.lower()
                if mood_lower in mood_indicators:
                    if any(indicator in restaurant_about or indicator in restaurant_features 
                           for indicator in mood_indicators[mood_lower]):
                        matching_moods.append(mood)
            
            if matching_moods:
                reasons.append(f"Sesuai preferensi suasana: {', '.join(matching_moods[:2])}")
            
            visit_count = history.get('interaction_count', 0)
            if visit_count > 5 and reasons:
                reasons.append(f"Berdasarkan {visit_count} pencarian Anda")
            
            return " | ".join(reasons) if reasons else ""
            
        except Exception as e:
            return ""
    
    def get_user_preferences_summary(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        user_id = self.sessions[session_id].get('user_id')
        if not user_id:
            return {"error": "User ID not found"}
        
        return {"message": "User preferences migrated to device token system"}