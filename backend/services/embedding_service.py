import logging
import numpy as np
from google.generativeai import GenerativeModel, configure
from db.database import Database
from services.storage_service import StorageService

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, config, db: Database, storage_service: StorageService):
        self.config = config
        self.db = db
        self.storage_service = storage_service
        configure(api_key=config.GCP_VERTEX_AI_API_KEY)
        self.embedding_model = GenerativeModel(config.GEMINI_MODEL_NAME) # Use same model for embedding and analysis

    def create_embedding_from_text(self, text):
        try:
            response = self.embedding_model.generate_content([f"Create embedding for: {text}"]) # Simple text embedding
            embedding_vector = response.parts[0].text # Assuming model returns text embedding, may need adjustment based on actual output
            # Convert text embedding to vector (example - needs proper conversion based on Gemini output format)
            embedding = np.array([float(x) for x in embedding_vector.split(',')]) # Placeholder conversion
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding for text: '{text}': {e}", exc_info=True)
            return None

    def find_similar_frames(self, query_embedding, video_id, top_k=3):
        try:
            similar_frames = self.db.vector_similarity_search(
                query_embedding, video_id, top_k=top_k
            )
            return similar_frames
        except Exception as e:
            logger.error(f"Error finding similar frames for video {video_id} with query embedding: {e}", exc_info=True)
            return []