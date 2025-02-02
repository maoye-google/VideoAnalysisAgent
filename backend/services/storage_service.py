import logging
import os
import uuid
from google.cloud import storage

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, config):
        self.config = config
        self.storage_client = storage.Client(project=config.GCP_PROJECT_ID)
        self.video_bucket_name = config.GCS_BUCKET_NAME_VIDEOS
        self.frame_bucket_name = config.GCS_BUCKET_NAME_FRAMES
        self.video_bucket = self.storage_client.bucket(self.video_bucket_name)
        self.frame_bucket = self.storage_client.bucket(self.frame_bucket_name)

    def upload_video(self, video_file):
        try:
            video_id = str(uuid.uuid4())
            filename = f"video_{video_id}_{video_file.filename}"
            blob = self.video_bucket.blob(filename)
            blob.upload_from_file(video_file)
            logger.info(f"Video {filename} uploaded to GCS bucket {self.video_bucket_name}")
            return video_id
        except Exception as e:
            logger.error(f"Error uploading video to GCS: {e}", exc_info=True)
            raise

    def download_video_to_temp(self, video_id):
        try:
            video_filename = self._get_video_filename(video_id) # Assuming you store video filename somewhere or can derive it
            if not video_filename:
                logger.warning(f"Video filename not found for video ID: {video_id}")
                return None

            blob = self.video_bucket.blob(video_filename)
            temp_filepath = os.path.join(self.config.VIDEO_UPLOAD_FOLDER_VIDEOS, video_filename) # Local temp path
            blob.download_to_filename(temp_filepath)
            logger.info(f"Video {video_filename} downloaded from GCS to {temp_filepath}")
            return temp_filepath
        except Exception as e:
            logger.error(f"Error downloading video from GCS: {e}", exc_info=True)
            return None

    def upload_frame(self, frame_filepath, frame_filename):
        try:
            blob = self.frame_bucket.blob(frame_filename)
            blob.upload_from_filename(frame_filepath)
            frame_gcs_uri = f"gs://{self.frame_bucket_name}/{frame_filename}"
            logger.info(f"Frame {frame_filename} uploaded to GCS bucket {self.frame_bucket_name}, URI: {frame_gcs_uri}")
            return frame_gcs_uri
        except Exception as e:
            logger.error(f"Error uploading frame to GCS: {e}", exc_info=True)
            return None

    def list_videos(self):
        try:
            videos = []
            blobs = self.storage_client.list_blobs(self.video_bucket)
            for blob in blobs:
                if blob.name.startswith('video_'): # Assuming video filenames start with 'video_'
                    video_id = blob.name.split('_')[1] # Extract video_id from filename
                    videos.append({'id': video_id, 'filename': blob.name}) # You might need to store more metadata
            return videos
        except Exception as e:
            logger.error(f"Error listing videos from GCS: {e}", exc_info=True)
            return []

    def delete_video(self, video_id):
        try:
            video_filename = self._get_video_filename(video_id)
            if video_filename:
                blob = self.video_bucket.blob(video_filename)
                blob.delete()
                logger.info(f"Video {video_filename} deleted from GCS bucket {self.video_bucket_name}")
            else:
                logger.warning(f"Video filename not found for video ID: {video_id}, cannot delete from GCS.")

            # Also delete frames associated with this video from frame bucket (optional, depending on requirements)
            # ... (implementation to delete frames based on video_id prefix)

        except Exception as e:
            logger.error(f"Error deleting video from GCS: {e}", exc_info=True)

    def get_video_info(self, video_id):
        # In a real app, you'd likely store video metadata (like GCS URL) in a database
        # For now, let's construct a placeholder GCS URL based on video_id and filename convention
        video_filename = self._get_video_filename(video_id)
        if video_filename:
            return {'video_url': f"gs://{self.video_bucket_name}/{video_filename}"}
        return None

    def _get_video_filename(self, video_id):
        # This is a simplified approach. In a real app, you'd likely store video filename in a database
        # or use a more robust naming convention that allows easy lookup.
        blobs = self.storage_client.list_blobs(self.video_bucket, prefix=f"video_{video_id}_")
        for blob in blobs:
            return blob.name # Return the first matching filename (assuming only one video per video_id prefix)
        return None