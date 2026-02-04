import pandas as pd
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
from models.data_models import Restaurant, UserProfile
from config.settings import RESTAURANTS_CSV, RESTAURANTS_ENTITAS_CSV
from utils.logger import get_logger
logger = get_logger("data_loader")
class DataLoader:
    @staticmethod
    def load_restaurants_csv(file_path = RESTAURANTS_CSV) -> pd.DataFrame:
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File {file_path} not found")
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logger.error(f"Error loading restaurants CSV: {e}")
            raise
    @staticmethod
    def load_processed_restaurants(file_path = RESTAURANTS_ENTITAS_CSV) -> pd.DataFrame:
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File {file_path} not found")
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logger.error(f"Error loading processed restaurants: {e}")
            raise
    @staticmethod
    def parse_list_column(value: Any) -> List[str]:
        # Handle NaN, None, empty values
        if pd.isna(value) or not value:
            return []
        # Handle float values (like NaN that wasn't caught above)
        if isinstance(value, (int, float)):
            return []
        try:
            if isinstance(value, str):
                return ast.literal_eval(value)
            elif isinstance(value, list):
                return value
            else:
                return []
        except (ValueError, SyntaxError):
            if isinstance(value, str):
                return [item.strip().strip("'\"") for item in value.split(',') if item.strip()]
            return []
    @staticmethod
    def restaurants_df_to_objects(df: pd.DataFrame) -> List[Restaurant]:
        restaurants = []
        for _, row in df.iterrows():
            try:
                # Get location from entitas_lokasi column
                location_list = DataLoader.parse_list_column(row.get('entitas_lokasi', []))
                location = ', '.join(location_list) if location_list else None
                
                restaurant = Restaurant(
                    id=int(row.get('id', 0)),
                    name=str(row.get('name', '')),
                    rating=float(row.get('rating', 0.0)),
                    about=row.get('about'),
                    address=row.get('address') if 'address' in row else location,  # Use location as address if no address column
                    location=location,
                    price_range=row.get('price_range'),
                    cuisines=DataLoader.parse_list_column(row.get('cuisines', [])),
                    features=DataLoader.parse_list_column(row.get('features', [])),
                    preferences=DataLoader.parse_list_column(row.get('preferences', []))
                )
                restaurants.append(restaurant)
            except Exception as e:
                logger.warning(f"Error parsing restaurant row {row.get('id', 'unknown')}: {e}")
                continue
        return restaurants

class DataValidator:
    @staticmethod
    def validate_restaurant_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_columns = ['id', 'name', 'rating']
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        if errors:
            return False, errors
        if not pd.api.types.is_numeric_dtype(df['id']):
            errors.append("ID column must be numeric")
        if not pd.api.types.is_numeric_dtype(df['rating']):
            errors.append("Rating column must be numeric")
        if df['rating'].min() < 0 or df['rating'].max() > 5:
            errors.append("Rating must be between 0 and 5")
        if df['id'].duplicated().any():
            errors.append("Duplicate restaurant IDs found")
        if df['name'].isna().any() or (df['name'] == '').any():
            errors.append("Some restaurants have empty names")
        is_valid = len(errors) == 0
        return is_valid, errors
    @staticmethod
    def validate_processed_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        is_valid, errors = DataValidator.validate_restaurant_data(df)
        if not is_valid:
            return False, errors
        entity_columns = [
            'entitas_lokasi', 'entitas_jenis_makanan', 
            'entitas_menu', 'entitas_preferensi', 'entitas_features'
        ]
        missing_entity_cols = [col for col in entity_columns if col not in df.columns]
        if missing_entity_cols:
            errors.append(f"Missing entity columns: {missing_entity_cols}")
        for col in entity_columns:
            if col in df.columns:
                sample_values = df[col].dropna().head(5)
                for val in sample_values:
                    try:
                        if isinstance(val, str) and val.startswith('['):
                            ast.literal_eval(val)
                    except (ValueError, SyntaxError):
                        errors.append(f"Invalid format in {col}: {val}")
                        break
        is_valid = len(errors) == 0
        return is_valid, errors
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        summary = {
            'total_restaurants': len(df),
            'columns': list(df.columns),
            'rating_stats': {
                'mean': df['rating'].mean() if 'rating' in df.columns else None,
                'min': df['rating'].min() if 'rating' in df.columns else None,
                'max': df['rating'].max() if 'rating' in df.columns else None
            },
            'missing_data': df.isnull().sum().to_dict(),
            'unique_cuisines': len(set([
                cuisine.strip().strip("'\"") 
                for cuisines in df.get('cuisines', []).dropna() 
                for cuisine in str(cuisines).split(',')
                if cuisine.strip()
            ])) if 'cuisines' in df.columns else 0
        }
        return summary