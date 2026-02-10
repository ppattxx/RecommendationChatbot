"""
Flask extensions initialization
Centralized extension instances to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
