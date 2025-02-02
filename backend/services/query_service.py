import logging
from services.llm_service import LLMService
from services.embedding_service import EmbeddingService
from services.storage_service import StorageService
from db.database import Database

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self, config, db: Database, storage_service: StorageService, embedding_service: EmbeddingService):
        self.config = config
        self.db = db
        self.storage_service = storage_service
        self.embedding_service = embedding_service
        self.llm_service = LLMService(config)

    def query_video(self, video_id, query_text):
        try:
            query_embedding = self._get_query_embedding(query_text)
            if query_embedding is None:
                return {'message': 'Could not create embedding for the query.'}

            similar_frames = self.embedding_service.find_similar_frames(query_embedding, video_id)
            if not similar_frames:
                return {'message': 'No relevant video frames found for your query.'}

            results = []
            for frame_data in similar_frames:
                frame_gcs_uri = frame_data['frame_gcs_uri']
                frame_filename = frame_gcs_uri.split('/')[-1]
                frame_url = f"/frames/{frame_filename}" # Serve from backend /frames endpoint
                video_info = self.storage_service.get_video_info(video_id) # Get video metadata to construct link
                video_link = video_info.get('video_url', '#') if video_info else '#' # Placeholder video link
                results.append({
                    'frame_url': frame_url,
                    'timeframe': frame_data['timeframe'],
                    'video_link': video_link,
                    'detected_objects': frame_data['detected_objects'] # Include detected objects in results
                })
            return {'frames': results}

        except Exception as e:
            logger.error(f"Error processing video query: {e}", exc_info=True)
            return {'message': 'Error processing your query.'}

    def _get_query_embedding(self, query_text):
        return self.embedding_service.create_embedding_from_text(query_text)