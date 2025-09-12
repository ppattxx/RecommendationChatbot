from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
@dataclass
class Restaurant:
    id: int
    name: str
    rating: float
    about: Optional[str] = None
    address: Optional[str] = None
    price_range: Optional[str] = None
    cuisines: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)
    hours: Dict[str, str] = field(default_factory=dict)
    images: List[str] = field(default_factory=list)
    entitas_lokasi: Optional[str] = None
    entitas_jenis_makanan: List[str] = field(default_factory=list)
    entitas_menu: List[str] = field(default_factory=list)
    entitas_preferensi: List[str] = field(default_factory=list)
    entitas_features: List[str] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'about': self.about,
            'address': self.address,
            'price_range': self.price_range,
            'cuisines': self.cuisines,
            'features': self.features,
            'preferences': self.preferences,
            'hours': self.hours,
            'images': self.images,
            'entitas_lokasi': self.entitas_lokasi,
            'entitas_jenis_makanan': self.entitas_jenis_makanan,
            'entitas_menu': self.entitas_menu,
            'entitas_preferensi': self.entitas_preferensi,
            'entitas_features': self.entitas_features
        }
@dataclass
class UserQuery:
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    processed_text: Optional[str] = None
    extracted_entities: Dict[str, List[str]] = field(default_factory=dict)
    intent: Optional[str] = None
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query_id': self.query_id,
            'text': self.text,
            'timestamp': self.timestamp.isoformat(),
            'processed_text': self.processed_text,
            'extracted_entities': self.extracted_entities,
            'intent': self.intent
        }
@dataclass
class Recommendation:
    restaurant: Restaurant
    similarity_score: float
    matching_features: List[str] = field(default_factory=list)
    explanation: Optional[str] = None
    def to_dict(self) -> Dict[str, Any]:
        return {
            'restaurant': self.restaurant.to_dict(),
            'similarity_score': self.similarity_score,
            'matching_features': self.matching_features,
            'explanation': self.explanation
        }
@dataclass
class ConversationTurn:
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_query: UserQuery = field(default_factory=UserQuery)
    recommendations: List[Recommendation] = field(default_factory=list)
    bot_response: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    def to_dict(self) -> Dict[str, Any]:
        return {
            'turn_id': self.turn_id,
            'user_query': self.user_query.to_dict(),
            'recommendations': [rec.to_dict() for rec in self.recommendations],
            'bot_response': self.bot_response,
            'timestamp': self.timestamp.isoformat()
        }
@dataclass
class UserSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    conversation_turns: List[ConversationTurn] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    def add_turn(self, turn: ConversationTurn):
        self.conversation_turns.append(turn)
        self.updated_at = datetime.now()
    def get_recent_queries(self, limit: int = 5) -> List[UserQuery]:
        recent_turns = self.conversation_turns[-limit:]
        return [turn.user_query for turn in recent_turns]
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'conversation_turns': [turn.to_dict() for turn in self.conversation_turns],
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
@dataclass
class UserPreferenceProfile:
    cuisine_preferences: Dict[str, float] = field(default_factory=dict)
    location_preferences: Dict[str, float] = field(default_factory=dict)
    feature_preferences: Dict[str, float] = field(default_factory=dict)
    price_preference: Optional[str] = None
    rating_threshold: float = 3.0
    interaction_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_from_query(self, entities: Dict[str, List[str]], weight: float = 0.1):
        self.interaction_count += 1
        for entity_type, entity_values in entities.items():
            if entity_type == 'jenis_makanan':
                for cuisine in entity_values:
                    self.cuisine_preferences[cuisine] = self.cuisine_preferences.get(cuisine, 0) + weight
            elif entity_type == 'lokasi':
                for location in entity_values:
                    self.location_preferences[location] = self.location_preferences.get(location, 0) + weight
            elif entity_type == 'features':
                for feature in entity_values:
                    self.feature_preferences[feature] = self.feature_preferences.get(feature, 0) + weight
        self.last_updated = datetime.now()
    
    def get_preference_score(self, restaurant_entities: Dict[str, List[str]]) -> float:
        score = 0.0
        total_weight = 0.0
        
        cuisines = restaurant_entities.get('jenis_makanan', [])
        for cuisine in cuisines:
            if cuisine in self.cuisine_preferences:
                score += self.cuisine_preferences[cuisine] * 2.0
                total_weight += 2.0
        
        location = restaurant_entities.get('lokasi', [])
        for loc in location:
            if loc in self.location_preferences:
                score += self.location_preferences[loc] * 1.5
                total_weight += 1.5
        
        features = restaurant_entities.get('features', [])
        for feature in features:
            if feature in self.feature_preferences:
                score += self.feature_preferences[feature] * 1.0
                total_weight += 1.0
        
        return score / max(total_weight, 1.0)
    
    def get_top_preferences(self, limit: int = 5) -> Dict[str, List[tuple]]:
        return {
            'cuisines': sorted(self.cuisine_preferences.items(), key=lambda x: x[1], reverse=True)[:limit],
            'locations': sorted(self.location_preferences.items(), key=lambda x: x[1], reverse=True)[:limit],
            'features': sorted(self.feature_preferences.items(), key=lambda x: x[1], reverse=True)[:limit]
        }

@dataclass
class UserProfile:
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    favorite_cuisines: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    budget_preference: Optional[str] = None
    location_preference: Optional[str] = None
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    preference_profile: UserPreferenceProfile = field(default_factory=UserPreferenceProfile)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    def update_preferences(self, new_preferences: Dict[str, Any]):
        self.preferences.update(new_preferences)
        self.updated_at = datetime.now()
    
    def add_interaction(self, interaction: Dict[str, Any]):
        interaction['timestamp'] = datetime.now().isoformat()
        self.interaction_history.append(interaction)
        self.updated_at = datetime.now()
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def update_preferences_from_query(self, entities: Dict[str, List[str]], selected_restaurant: Optional[Dict] = None):
        self.preference_profile.update_from_query(entities)
        
        if selected_restaurant:
            self.add_interaction({
                'type': 'restaurant_selection',
                'restaurant_name': selected_restaurant.get('name'),
                'entities_used': entities,
                'rating': selected_restaurant.get('rating')
            })
        else:
            self.add_interaction({
                'type': 'query',
                'entities_used': entities
            })
        
        self.updated_at = datetime.now()
    
    def get_personalized_recommendations_boost(self, restaurant_entities: Dict[str, List[str]]) -> float:
        return self.preference_profile.get_preference_score(restaurant_entities)
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'preferences': self.preferences,
            'favorite_cuisines': self.favorite_cuisines,
            'dietary_restrictions': self.dietary_restrictions,
            'budget_preference': self.budget_preference,
            'location_preference': self.location_preference,
            'interaction_history': self.interaction_history,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
@dataclass
class EntityExtractionResult:
    entities: Dict[str, List[str]] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    raw_text: str = ""
    processed_text: str = ""
    def get_entity(self, entity_type: str) -> List[str]:
        return self.entities.get(entity_type, [])
    def has_entity(self, entity_type: str) -> bool:
        return entity_type in self.entities and len(self.entities[entity_type]) > 0
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entities': self.entities,
            'confidence_scores': self.confidence_scores,
            'raw_text': self.raw_text,
            'processed_text': self.processed_text
        }
@dataclass
class ModelMetrics:
    total_queries: int = 0
    successful_recommendations: int = 0
    avg_similarity_score: float = 0.0
    user_satisfaction_score: float = 0.0
    response_time_avg: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    def update_metrics(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_updated = datetime.now()
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_queries': self.total_queries,
            'successful_recommendations': self.successful_recommendations,
            'avg_similarity_score': self.avg_similarity_score,
            'user_satisfaction_score': self.user_satisfaction_score,
            'response_time_avg': self.response_time_avg,
            'last_updated': self.last_updated.isoformat()
        }