import logging
import json
from google.cloud import storage
from datetime import timedelta
from services.storage_service import StorageService
from db.database import Database


logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self, config, db: Database, storage_service: StorageService):
        self.config = config
        self.db = db
        self.storage_service = storage_service
        self.storage_client = storage.Client()

    # When not specified what type of similarity search,
    # The system will use find_similar_frames_by_objects by default
    def query_video(self, video_id, query_text):
        try:
            similar_frames = self._find_similar_frames_by_description(query_text, video_id)
            if not similar_frames:
                return {'message': 'No relevant video frames found for your query.'}

            results = []
            
            for frame_data in similar_frames:
                logger.debug(f"Similar Find Result : {json.dumps(frame_data)}")
                frame_gcs_uri = frame_data['frame_gcs_uri']
                signed_frame_url = self.storage_service.get_signed_url(frame_gcs_uri)
                # frame_filename = frame_gcs_uri.split('/')[-1]
                # frame_url = f"/frames/{frame_filename}" # Serve from backend /frames endpoint
                video_info = self.storage_service.get_video_info(video_id) # Get video metadata to construct link
                video_gcs_uri = video_info.get('video_gcs_uri') if video_info else None
                signed_video_link = self.storage_service.get_signed_url(video_gcs_uri) if video_gcs_uri else "#"
                results.append({
                    'frame_url': signed_frame_url,
                    'timeframe': frame_data['timeframe'],
                    'video_link': signed_video_link,
                    'detected_objects': json.loads(frame_data['detected_objects_json']), # Include detected objects in results
                    'text_description': frame_data['text_description'] # Include detected objects in results
                })
            return {'frames': results}

        except Exception as e:
            logger.error(f"Error processing video query: {e}", exc_info=True)
            return {'message': 'Error processing your query.'}

    def _find_similar_frames_by_description(self, query_str, video_id, top_k=3):
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

    def _find_similar_frames_by_objects(self, query_str, video_id, top_k=3):
        try:
            similar_frames = self.db.objects_similarity_search(query_str, video_id, top_k=top_k)
            return similar_frames
        except Exception as e:
            logger.error(f"Error finding similar frames by objects for video {video_id} with query embedding: {e}", exc_info=True)
            return []