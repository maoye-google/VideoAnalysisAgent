import logging
from services.storage_service import StorageService
from db.database import Database

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self, config, db: Database, storage_service: StorageService):
        self.config = config
        self.db = db
        self.storage_service = storage_service

    # When not specified what type of similarity search,
    # The system will use find_similar_frames_by_objects by default
    def query_video(self, video_id, query_text):
        try:
            similar_frames = self.find_similar_frames_by_objects(query_text, video_id)
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

    def find_similar_frames_by_description(self, query_str, video_id, top_k=3):
        try:
            similar_frames = self.db.frame_description_similarity_search(
                query_str, video_id, top_k=top_k
            )
            return similar_frames
        except Exception as e:
            logger.error(
                f"Error finding similar frames by description for video {video_id} with query embedding: {e}", exc_info=True
            )
            return []

    def find_similar_frames_by_objects(self, query_str, video_id, top_k=3):
        try:
            similar_frames = self.db.objects_similarity_search(query_str, video_id, top_k=top_k)
            return similar_frames
        except Exception as e:
            logger.error(f"Error finding similar frames by objects for video {video_id} with query embedding: {e}", exc_info=True)
            return []