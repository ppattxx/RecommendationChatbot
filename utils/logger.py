import logging
import logging.config
from pathlib import Path
from typing import Optional
from datetime import datetime
from config.settings import LOGGING_CONFIG, LOGS_DIR
class ChatbotLogger:
    def __init__(self, name: str = "chatbot", log_file: Optional[str] = None):
        self.name = name
        self.log_file = log_file or str(LOGS_DIR / f"{name}.log")
        self._setup_logger()
    def _setup_logger(self):
        LOGS_DIR.mkdir(exist_ok=True)
        config = LOGGING_CONFIG.copy()
        config['handlers']['file']['filename'] = self.log_file
        try:
            logging.config.dictConfig(config)
            self.logger = logging.getLogger(self.name)
        except Exception as e:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(self.name)
            self.logger.warning(f"Could not setup advanced logging config: {e}")
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, extra=kwargs)
    def log_user_query(self, user_id: str, query: str, session_id: str):
        self.info(
            f"User query received",
            user_id=user_id,
            query=query,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
    def log_recommendation(self, user_id: str, recommendations_count: int, 
                          avg_score: float, session_id: str):
        self.info(
            f"Recommendations generated",
            user_id=user_id,
            recommendations_count=recommendations_count,
            avg_similarity_score=avg_score,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
    def log_error(self, error_type: str, error_message: str, 
                  user_id: Optional[str] = None, **context):
        self.error(
            f"Error occurred: {error_type}",
            error_message=error_message,
            user_id=user_id,
            context=context,
            timestamp=datetime.now().isoformat()
        )
    def log_performance(self, operation: str, duration: float, **metrics):
        self.debug(
            f"Performance metric: {operation}",
            duration_seconds=duration,
            metrics=metrics,
            timestamp=datetime.now().isoformat()
        )
chatbot_logger = ChatbotLogger()
def get_logger(name: str = "chatbot") -> ChatbotLogger:
    if name == "chatbot":
        return chatbot_logger
    return ChatbotLogger(name)