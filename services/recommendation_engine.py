import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import time
from models.data_models import Restaurant, Recommendation, UserQuery, EntityExtractionResult
from utils.text_processing import TextPreprocessor, EntityExtractor
from utils.data_loader import DataLoader
from utils.helpers import timing_decorator, ResponseGenerator, calculate_similarity_score
from utils.logger import get_logger
from config.settings import MODEL_CONFIG, RECOMMENDATION_CONFIG, RESTAURANTS_ENTITAS_CSV
logger = get_logger("recommendation_engine")
class ContentBasedRecommendationEngine:
    def __init__(self, data_path: str = None):
        self.data_path = data_path or str(RESTAURANTS_ENTITAS_CSV)
        self.restaurants_df = None
        self.restaurants_objects = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.text_preprocessor = TextPreprocessor()
        self.entity_extractor = EntityExtractor()
        self.response_generator = ResponseGenerator()
        self.model_config = MODEL_CONFIG
        self.recommendation_config = RECOMMENDATION_CONFIG
        self._initialize_engine()
    @timing_decorator
    def _initialize_engine(self):
        try:
            self._load_data()
            self._build_tfidf_model()
        except Exception as e:
            logger.error(f"Failed to initialize recommendation engine: {e}")
            raise
    def _load_data(self):
        try:
            self.restaurants_df = DataLoader.load_processed_restaurants(self.data_path)
            self.restaurants_objects = DataLoader.restaurants_df_to_objects(self.restaurants_df)
        except Exception as e:
            logger.error(f"Error loading restaurant data: {e}")
            raise
    def _build_tfidf_model(self):
        try:
            content_texts = []
            for idx, row in self.restaurants_df.iterrows():
                content_parts = []
                
                if pd.notna(row.get('name')):
                    content_parts.append(str(row['name']).lower())
                
                if pd.notna(row.get('about')):
                    content_parts.append(str(row['about']).lower())
                
                if pd.notna(row.get('entitas_lokasi')):
                    content_parts.append(str(row['entitas_lokasi']))
                    
                cuisines = self._parse_list_field(row.get('entitas_jenis_makanan', []))
                content_parts.extend(cuisines)
                
                menu_items = self._parse_list_field(row.get('entitas_menu', []))
                content_parts.extend(menu_items)
                
                preferences = self._parse_list_field(row.get('entitas_preferensi', []))
                content_parts.extend(preferences)
                
                features = self._parse_list_field(row.get('entitas_features', []))
                content_parts.extend(features)
                
                combined_content = ' '.join(content_parts).lower()
                content_texts.append(combined_content)
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=self.model_config['tfidf']['max_features'],
                min_df=self.model_config['tfidf']['min_df'],
                max_df=self.model_config['tfidf']['max_df'],
                ngram_range=self.model_config['tfidf']['ngram_range'],
                stop_words=None
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(content_texts)
        except Exception as e:
            logger.error(f"Error building TF-IDF model: {e}")
            raise
    def _parse_list_field(self, field_value) -> List[str]:
        if pd.isna(field_value) or not field_value:
            return []
        try:
            if isinstance(field_value, str):
                return ast.literal_eval(field_value)
            elif isinstance(field_value, list):
                return field_value
            else:
                return []
        except (ValueError, SyntaxError):
            return []
    @timing_decorator
    def get_recommendations(self, user_query: str, top_n: int = None) -> List[Recommendation]:
        if top_n is None:
            top_n = self.recommendation_config['default_top_n']
        try:
            query_result = self._process_user_query(user_query)
            recommendations = []
            entity_recommendations = self._get_entity_based_recommendations(
                query_result.entities, top_n * 2
            )
            recommendations.extend(entity_recommendations)
            tfidf_recommendations = self._get_tfidf_recommendations(
                user_query, top_n * 2
            )
            recommendations.extend(tfidf_recommendations)
            final_recommendations = self._combine_and_rank_recommendations(
                recommendations, top_n
            )
            return final_recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []
    def _process_user_query(self, user_query: str) -> EntityExtractionResult:
        processed_text = self.text_preprocessor.preprocess(user_query)
        entities = self.entity_extractor.extract_entities(user_query)
        result = EntityExtractionResult(
            entities=entities,
            raw_text=user_query,
            processed_text=processed_text
        )
        return result
    def _get_entity_based_recommendations(self, entities: Dict[str, List[str]], 
                                        top_n: int) -> List[Recommendation]:
        recommendations = []
        for restaurant in self.restaurants_objects:
            similarity_score = calculate_similarity_score(entities, restaurant)
            if similarity_score >= self.recommendation_config['min_similarity_score']:
                matching_features = self._find_matching_features(entities, restaurant)
                recommendation = Recommendation(
                    restaurant=restaurant,
                    similarity_score=similarity_score,
                    matching_features=matching_features,
                    explanation=self._generate_explanation(entities, restaurant, matching_features)
                )
                recommendations.append(recommendation)
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        return recommendations[:top_n]
    def _get_tfidf_recommendations(self, user_query: str, top_n: int) -> List[Recommendation]:
        try:
            processed_query = self.text_preprocessor.preprocess(
                user_query,
                remove_stopwords=True
            )
            query_vector = self.tfidf_vectorizer.transform([processed_query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            top_indices = similarities.argsort()[-top_n:][::-1]
            recommendations = []
            for idx in top_indices:
                if similarities[idx] >= self.model_config['similarity']['threshold']:
                    restaurant = self.restaurants_objects[idx]
                    recommendation = Recommendation(
                        restaurant=restaurant,
                        similarity_score=float(similarities[idx]),
                        matching_features=[],
                        explanation=f"Kecocokan berdasarkan analisis konten: {similarities[idx]:.2f}"
                    )
                    recommendations.append(recommendation)
            return recommendations
        except Exception as e:
            logger.error(f"Error in TF-IDF recommendations: {e}")
            return []
    def _combine_and_rank_recommendations(self, recommendations: List[Recommendation], 
        top_n: int) -> List[Recommendation]:
        restaurant_scores = {}
        for rec in recommendations:
            restaurant_id = rec.restaurant.id
            if restaurant_id not in restaurant_scores:
                restaurant_scores[restaurant_id] = rec
            else:
                existing_rec = restaurant_scores[restaurant_id]
                if rec.similarity_score > existing_rec.similarity_score:
                    restaurant_scores[restaurant_id] = rec
                existing_features = set(existing_rec.matching_features)
                new_features = set(rec.matching_features)
                combined_features = list(existing_features.union(new_features))
                restaurant_scores[restaurant_id].matching_features = combined_features
        final_recommendations = list(restaurant_scores.values())
        final_recommendations.sort(
            key=lambda x: (x.similarity_score, x.restaurant.rating), 
            reverse=True
        )
        return final_recommendations[:top_n]
    def _find_matching_features(self, entities: Dict[str, List[str]],
        restaurant: Restaurant) -> List[str]:
        matching_features = []
        if 'lokasi' in entities and restaurant.entitas_lokasi:
            for location in entities['lokasi']:
                if location.lower() in restaurant.entitas_lokasi.lower():
                    matching_features.append(f"Lokasi: {location}")
        if 'jenis_makanan' in entities:
            restaurant_cuisines = [c.lower() for c in restaurant.entitas_jenis_makanan]
            for cuisine in entities['jenis_makanan']:
                if cuisine.lower() in restaurant_cuisines:
                    matching_features.append(f"Jenis masakan: {cuisine}")
        if 'menu' in entities:
            restaurant_menus = [m.lower() for m in restaurant.entitas_menu]
            for menu in entities['menu']:
                if menu.lower() in restaurant_menus:
                    matching_features.append(f"Menu: {menu}")
        if 'preferensi' in entities:
            restaurant_prefs = [p.lower() for p in restaurant.entitas_preferensi]
            for pref in entities['preferensi']:
                if pref.lower() in restaurant_prefs:
                    matching_features.append(f"Suasana: {pref}")
        return matching_features
    def _generate_explanation(self, entities: Dict[str, List[str]], 
                            restaurant: Restaurant, 
                            matching_features: List[str]) -> str:
        if not matching_features:
            return f"Direkomendasikan berdasarkan rating tinggi ({restaurant.rating}/5.0)"
        explanation_parts = [
            f"Cocok karena: {', '.join(matching_features[:3])}"
        ]
        if len(matching_features) > 3:
            explanation_parts.append(f"dan {len(matching_features) - 3} kecocokan lainnya")
        return " ".join(explanation_parts)
    def get_similar_restaurants(self, restaurant_id: int, top_n: int = 5) -> List[Recommendation]:
        try:
            target_restaurant = None
            target_index = None
            for i, restaurant in enumerate(self.restaurants_objects):
                if restaurant.id == restaurant_id:
                    target_restaurant = restaurant
                    target_index = i
                    break
            if target_restaurant is None:
                logger.warning(f"Restaurant with ID {restaurant_id} not found")
                return []
            target_vector = self.tfidf_matrix[target_index]
            similarities = cosine_similarity(target_vector, self.tfidf_matrix).flatten()
            similar_indices = []
            for idx in similarities.argsort()[::-1]:
                if idx != target_index and len(similar_indices) < top_n:
                    similar_indices.append(idx)
            recommendations = []
            for idx in similar_indices:
                if similarities[idx] > 0.1:
                    restaurant = self.restaurants_objects[idx]
                    recommendation = Recommendation(
                        restaurant=restaurant,
                        similarity_score=float(similarities[idx]),
                        matching_features=[],
                        explanation=f"Mirip dengan {target_restaurant.name}"
                    )
                    recommendations.append(recommendation)
            return recommendations
        except Exception as e:
            logger.error(f"Error finding similar restaurants: {e}")
            return []
    def get_recommendations_by_category(self, category: str, top_n: int = 5) -> List[Recommendation]:
        try:
            recommendations = []
            category_lower = category.lower()
            for restaurant in self.restaurants_objects:
                score = 0.0
                matching_features = []
                restaurant_cuisines = [c.lower() for c in restaurant.entitas_jenis_makanan]
                if any(category_lower in cuisine for cuisine in restaurant_cuisines):
                    score += 0.8
                    matching_features.append(f"Jenis masakan: {category}")
                if restaurant.entitas_lokasi and category_lower in restaurant.entitas_lokasi.lower():
                    score += 0.6
                    matching_features.append(f"Lokasi: {category}")
                restaurant_prefs = [p.lower() for p in restaurant.entitas_preferensi]
                if any(category_lower in pref for pref in restaurant_prefs):
                    score += 0.4
                    matching_features.append(f"Suasana: {category}")
                if score > 0:
                    recommendation = Recommendation(
                        restaurant=restaurant,
                        similarity_score=score,
                        matching_features=matching_features,
                        explanation=f"Kategori yang cocok: {category}"
                    )
                    recommendations.append(recommendation)
            recommendations.sort(key=lambda x: (x.similarity_score, x.restaurant.rating), reverse=True)
            return recommendations[:top_n]
        except Exception as e:
            logger.error(f"Error getting recommendations by category: {e}")
            return []
    def get_restaurant_by_id(self, restaurant_id: int) -> Optional[Restaurant]:
        for restaurant in self.restaurants_objects:
            if restaurant.id == restaurant_id:
                return restaurant
        return None
    def get_all_restaurants(self) -> List[Restaurant]:
        return self.restaurants_objects.copy()
    def get_statistics(self) -> Dict[str, Any]:
        if not self.restaurants_objects:
            return {}
        total_restaurants = len(self.restaurants_objects)
        avg_rating = sum(r.rating for r in self.restaurants_objects) / total_restaurants
        all_cuisines = []
        for restaurant in self.restaurants_objects:
            all_cuisines.extend(restaurant.entitas_jenis_makanan)
        unique_cuisines = len(set(all_cuisines))
        locations = set()
        for restaurant in self.restaurants_objects:
            if restaurant.entitas_lokasi:
                locations.add(restaurant.entitas_lokasi)
        return {
            'total_restaurants': total_restaurants,
            'average_rating': round(avg_rating, 2),
            'unique_cuisines': unique_cuisines,
            'unique_locations': len(locations),
            'tfidf_features': self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0
        }