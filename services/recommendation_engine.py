"""
Restaurant Recommendation Engine Module

This module implements a Content-Based Filtering recommendation system using
TF-IDF vectorization and Cosine Similarity for restaurant recommendations.

Classes:
    ContentBasedRecommendationEngine: Main recommendation engine class

Algorithm:
    1. TF-IDF Vectorization of restaurant text data (name, about, cuisines, etc.)
    2. User query transformation using the same vectorizer
    3. Cosine Similarity calculation between query and all restaurants
    4. Multi-tier boosting based on location, cuisine, preferences matches
    5. Tie-breaker sorting using rating and review_count

Author: Chatbot Rekomendasi Team
Version: 1.0.0
"""

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
from utils.helpers import timing_decorator, ResponseGenerator, calculate_similarity_score, calculate_boosted_score
from utils.logger import get_logger
from config.settings import MODEL_CONFIG, RECOMMENDATION_CONFIG, RESTAURANTS_ENTITAS_CSV

logger = get_logger("recommendation_engine")


class ContentBasedRecommendationEngine:
    """
    Content-Based Recommendation Engine using TF-IDF and Cosine Similarity.
    
    This engine provides personalized restaurant recommendations based on
    user queries by calculating text similarity between the query and
    restaurant attributes.
    
    Attributes:
        data_path (str): Path to the restaurant dataset CSV file
        restaurants_df (pd.DataFrame): DataFrame containing restaurant data
        restaurants_objects (List[Restaurant]): List of Restaurant objects
        tfidf_vectorizer (TfidfVectorizer): Fitted TF-IDF vectorizer
        tfidf_matrix (sparse matrix): TF-IDF matrix for all restaurants
        text_preprocessor (TextPreprocessor): Text preprocessing utility
        entity_extractor (EntityExtractor): Entity extraction utility
        response_generator (ResponseGenerator): Response generation utility
        
    Example:
        >>> engine = ContentBasedRecommendationEngine()
        >>> recommendations = engine.get_recommendations("pizza di kuta", top_n=5)
        >>> for rec in recommendations:
        ...     print(f"{rec.restaurant.name}: {rec.similarity_score:.2f}")
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the recommendation engine.
        
        Args:
            data_path (str, optional): Path to restaurant dataset CSV.
                                       Defaults to RESTAURANTS_ENTITAS_CSV from config.
        """
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
        """
        Initialize the engine by loading data and building TF-IDF model.
        
        Raises:
            Exception: If initialization fails due to data loading or model building errors.
        """
        try:
            self._load_data()
            self._build_tfidf_model()
        except Exception as e:
            logger.error(f"Failed to initialize recommendation engine: {e}")
            raise

    def _load_data(self):
        """
        Load restaurant data from CSV file into DataFrame and Restaurant objects.
        
        Raises:
            Exception: If data loading fails.
        """
        try:
            self.restaurants_df = DataLoader.load_processed_restaurants(self.data_path)
            self.restaurants_objects = DataLoader.restaurants_df_to_objects(self.restaurants_df)
        except Exception as e:
            logger.error(f"Error loading restaurant data: {e}")
            raise

    def _build_tfidf_model(self):
        """
        Build TF-IDF model from restaurant text data.
        
        Creates a TF-IDF vectorizer and transforms all restaurant text data
        into a sparse matrix for efficient similarity calculations.
        
        The text data includes:
        - Restaurant name
        - About/description
        - Address/location
        - Cuisines
        - Preferences/keywords
        - Features
        
        Raises:
            Exception: If model building fails.
        """
        try:
            content_texts = []
            for idx, row in self.restaurants_df.iterrows():
                content_parts = []
                
                # About field - main description
                if pd.notna(row.get('about')):
                    content_parts.append(str(row['about']).lower())
                
                # Name field
                if pd.notna(row.get('name')):
                    content_parts.append(str(row['name']).lower())
                
                # Location from address
                if pd.notna(row.get('address')):
                    content_parts.append(str(row['address']).lower())
                
                # Cuisines field
                cuisines = self._parse_list_field(row.get('cuisines', []))
                content_parts.extend(cuisines)
                
                # Preferences field
                preferences = self._parse_list_field(row.get('preferences', []))
                content_parts.extend(preferences)
                
                # Features field
                features = self._parse_list_field(row.get('features', []))
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
        """
        Parse a field that may contain a list stored as string.
        
        Args:
            field_value: Value that may be a string representation of a list,
                        an actual list, or None/NaN.
                        
        Returns:
            List[str]: Parsed list of strings, or empty list if parsing fails.
        """
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
            
            # Fallback for ambiguous queries with no results
            if not final_recommendations and self._is_ambiguous_query(query_result.entities):
                final_recommendations = self._get_fallback_recommendations(query_result.entities, top_n)
            
            return final_recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _is_ambiguous_query(self, entities: Dict[str, List[str]]) -> bool:
        """Check if query is ambiguous (has very few or no specific entities)"""
        entity_count = sum(len(v) for v in entities.values())
        return entity_count < 2
    
    def _get_fallback_recommendations(self, entities: Dict[str, List[str]], top_n: int) -> List[Recommendation]:
        """Get fallback recommendations based on popularity and rating"""
        # If location is specified, return top-rated in that location
        if 'lokasi' in entities and entities['lokasi']:
            location = entities['lokasi'][0].lower()
            filtered = [r for r in self.restaurants_objects 
                       if r.entitas_lokasi and location in r.entitas_lokasi.lower()]
            if filtered:
                filtered.sort(key=lambda x: x.rating, reverse=True)
                return [Recommendation(
                    restaurant=r,
                    similarity_score=0.5 + (r.rating / 10.0),
                    matching_features=['popular', 'highly rated'],
                    explanation=f"Restoran populer di {location} dengan rating tinggi"
                ) for r in filtered[:top_n]]
        
        # Return overall top-rated restaurants
        sorted_restaurants = sorted(self.restaurants_objects, key=lambda x: x.rating, reverse=True)
        return [Recommendation(
            restaurant=r,
            similarity_score=0.5 + (r.rating / 10.0),
            matching_features=['popular', 'highly rated'],
            explanation="Restoran populer dengan rating tinggi"
        ) for r in sorted_restaurants[:top_n]]
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
            base_score = calculate_similarity_score(entities, restaurant)
            # Apply boosting for exact matches
            boosted_score = calculate_boosted_score(base_score, entities, restaurant)
            
            if boosted_score >= self.recommendation_config['min_similarity_score']:
                matching_features = self._find_matching_features(entities, restaurant)
                recommendation = Recommendation(
                    restaurant=restaurant,
                    similarity_score=boosted_score,
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
            
            # Extract entities for boosting
            entities = self.entity_extractor.extract_entities(user_query)
            
            top_indices = similarities.argsort()[-top_n:][::-1]
            recommendations = []
            for idx in top_indices:
                if similarities[idx] >= self.model_config['similarity']['threshold']:
                    restaurant = self.restaurants_objects[idx]
                    base_score = float(similarities[idx])
                    # Apply boosting
                    boosted_score = calculate_boosted_score(base_score, entities, restaurant)
                    
                    recommendation = Recommendation(
                        restaurant=restaurant,
                        similarity_score=boosted_score,
                        matching_features=[],
                        explanation=f"Kecocokan berdasarkan analisis konten: {boosted_score:.2f}"
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
        
        # Check location field (HIGHEST PRIORITY)
        if 'location' in entities and hasattr(restaurant, 'location') and restaurant.location:
            for loc in entities['location']:
                if loc.lower() in restaurant.location.lower():
                    matching_features.append(f"Lokasi: {loc}")
                elif hasattr(restaurant, 'address') and restaurant.address and loc.lower() in restaurant.address.lower():
                    matching_features.append(f"Lokasi: {loc}")
        
        # Check about field
        if 'about' in entities and hasattr(restaurant, 'about') and restaurant.about:
            for term in entities['about']:
                if term.lower() in restaurant.about.lower():
                    matching_features.append(f"Deskripsi: {term}")
        
        # Check cuisines field
        if 'cuisine' in entities and hasattr(restaurant, 'cuisines') and restaurant.cuisines:
            restaurant_cuisines = [c.lower() for c in restaurant.cuisines]
            for cuisine in entities['cuisine']:
                if cuisine.lower() in restaurant_cuisines:
                    matching_features.append(f"Jenis masakan: {cuisine}")
        
        # Check preferences field
        if 'preferences' in entities and hasattr(restaurant, 'preferences') and restaurant.preferences:
            restaurant_prefs = [p.lower() for p in restaurant.preferences]
            for pref in entities['preferences']:
                if pref.lower() in restaurant_prefs:
                    matching_features.append(f"Suasana: {pref}")
        
        # Check features field
        if 'features' in entities and hasattr(restaurant, 'features') and restaurant.features:
            restaurant_features = [f.lower() for f in restaurant.features]
            for feature in entities['features']:
                if feature.lower() in restaurant_features:
                    matching_features.append(f"Fasilitas: {feature}")
        
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
                
                # Check location (HIGHEST PRIORITY)
                if hasattr(restaurant, 'location') and restaurant.location and category_lower in restaurant.location.lower():
                    score += 1.0
                    matching_features.append(f"Lokasi: {category}")
                elif hasattr(restaurant, 'address') and restaurant.address and category_lower in restaurant.address.lower():
                    score += 0.9
                    matching_features.append(f"Lokasi: {category}")
                
                # Check cuisines
                if hasattr(restaurant, 'cuisines') and restaurant.cuisines:
                    restaurant_cuisines = [c.lower() for c in restaurant.cuisines]
                    if any(category_lower in cuisine for cuisine in restaurant_cuisines):
                        score += 0.8
                        matching_features.append(f"Jenis masakan: {category}")
                
                # Check about field
                if hasattr(restaurant, 'about') and restaurant.about and category_lower in restaurant.about.lower():
                    score += 0.6
                    matching_features.append(f"Deskripsi: {category}")
                
                # Check preferences
                if hasattr(restaurant, 'preferences') and restaurant.preferences:
                    restaurant_prefs = [p.lower() for p in restaurant.preferences]
                    if any(category_lower in pref for pref in restaurant_prefs):
                        score += 0.4
                        matching_features.append(f"Suasana: {category}")
                
                # Check features
                if hasattr(restaurant, 'features') and restaurant.features:
                    restaurant_features = [f.lower() for f in restaurant.features]
                    if any(category_lower in feat for feat in restaurant_features):
                        score += 0.3
                        matching_features.append(f"Fasilitas: {category}")
                
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
            if hasattr(restaurant, 'cuisines') and restaurant.cuisines:
                all_cuisines.extend(restaurant.cuisines)
        unique_cuisines = len(set(all_cuisines))
        
        all_features = []
        for restaurant in self.restaurants_objects:
            if hasattr(restaurant, 'features') and restaurant.features:
                all_features.extend(restaurant.features)
        unique_features = len(set(all_features))
        
        return {
            'total_restaurants': total_restaurants,
            'average_rating': round(avg_rating, 2),
            'unique_cuisines': unique_cuisines,
            'unique_features': unique_features,
            'tfidf_features': self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0
        }