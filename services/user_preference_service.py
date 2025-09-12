import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from models.data_models import UserProfile, UserPreferenceProfile
from utils.logger import get_logger

logger = get_logger("user_preference_manager")

class UserPreferenceManager:
    def __init__(self, profiles_dir: str = "user_profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        self.active_profiles: Dict[str, UserProfile] = {}
    
    def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        if user_id in self.active_profiles:
            return self.active_profiles[user_id]
        
        profile_file = self.profiles_dir / f"{user_id}.json"
        
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                profile = self._dict_to_profile(profile_data)
                self.active_profiles[user_id] = profile
                logger.info(f"Loaded user profile for {user_id}")
                return profile
            except Exception as e:
                logger.error(f"Error loading profile for {user_id}: {e}")
        
        profile = UserProfile(user_id=user_id)
        self.active_profiles[user_id] = profile
        logger.info(f"Created new user profile for {user_id}")
        return profile
    
    def save_user_profile(self, user_profile: UserProfile):
        try:
            profile_file = self.profiles_dir / f"{user_profile.user_id}.json"
            profile_dict = self._profile_to_dict(user_profile)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_dict, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved user profile for {user_profile.user_id}")
        except Exception as e:
            logger.error(f"Error saving profile for {user_profile.user_id}: {e}")
    
    def update_user_preferences(self, user_id: str, entities: Dict[str, List[str]], 
                              selected_restaurant: Optional[Dict] = None):
        profile = self.get_or_create_user_profile(user_id)
        profile.update_preferences_from_query(entities, selected_restaurant)
        self.save_user_profile(profile)
        
        logger.info(f"Updated preferences for user {user_id}")
    
    def get_personalized_boost(self, user_id: str, restaurant_entities: Dict[str, List[str]]) -> float:
        if user_id not in self.active_profiles:
            return 0.0
        
        profile = self.active_profiles[user_id]
        return profile.get_personalized_recommendations_boost(restaurant_entities)
    
    def get_user_preference_summary(self, user_id: str) -> Dict:
        profile = self.get_or_create_user_profile(user_id)
        top_prefs = profile.preference_profile.get_top_preferences()
        
        return {
            'user_id': user_id,
            'interaction_count': profile.preference_profile.interaction_count,
            'top_cuisines': top_prefs['cuisines'],
            'top_locations': top_prefs['locations'],
            'top_features': top_prefs['features'],
            'last_updated': profile.updated_at.isoformat()
        }
    
    def _profile_to_dict(self, profile: UserProfile) -> Dict:
        return {
            'user_id': profile.user_id,
            'name': profile.name,
            'email': profile.email,
            'preferences': profile.preferences,
            'favorite_cuisines': profile.favorite_cuisines,
            'dietary_restrictions': profile.dietary_restrictions,
            'budget_preference': profile.budget_preference,
            'location_preference': profile.location_preference,
            'interaction_history': profile.interaction_history,
            'preference_profile': {
                'cuisine_preferences': profile.preference_profile.cuisine_preferences,
                'location_preferences': profile.preference_profile.location_preferences,
                'feature_preferences': profile.preference_profile.feature_preferences,
                'price_preference': profile.preference_profile.price_preference,
                'rating_threshold': profile.preference_profile.rating_threshold,
                'interaction_count': profile.preference_profile.interaction_count,
                'last_updated': profile.preference_profile.last_updated.isoformat()
            },
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat()
        }
    
    def _dict_to_profile(self, data: Dict) -> UserProfile:
        pref_profile_data = data.get('preference_profile', {})
        pref_profile = UserPreferenceProfile(
            cuisine_preferences=pref_profile_data.get('cuisine_preferences', {}),
            location_preferences=pref_profile_data.get('location_preferences', {}),
            feature_preferences=pref_profile_data.get('feature_preferences', {}),
            price_preference=pref_profile_data.get('price_preference'),
            rating_threshold=pref_profile_data.get('rating_threshold', 3.0),
            interaction_count=pref_profile_data.get('interaction_count', 0),
            last_updated=datetime.fromisoformat(pref_profile_data.get('last_updated', datetime.now().isoformat()))
        )
        
        return UserProfile(
            user_id=data['user_id'],
            name=data.get('name'),
            email=data.get('email'),
            preferences=data.get('preferences', {}),
            favorite_cuisines=data.get('favorite_cuisines', []),
            dietary_restrictions=data.get('dietary_restrictions', []),
            budget_preference=data.get('budget_preference'),
            location_preference=data.get('location_preference'),
            interaction_history=data.get('interaction_history', []),
            preference_profile=pref_profile,
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )
    
    def cleanup_old_profiles(self, days_threshold: int = 30):
        cutoff_date = datetime.now().timestamp() - (days_threshold * 24 * 60 * 60)
        
        for profile_file in self.profiles_dir.glob("*.json"):
            if profile_file.stat().st_mtime < cutoff_date:
                try:
                    profile_file.unlink()
                    logger.info(f"Deleted old profile: {profile_file.name}")
                except Exception as e:
                    logger.error(f"Error deleting old profile {profile_file.name}: {e}")
