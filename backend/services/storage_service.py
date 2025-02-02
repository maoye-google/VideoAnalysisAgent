import logging
import os
from datetime import datetime

from google.cloud import storage
from db.database import Database

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, config, db: Database):
        self.config = config
        self.db=db
        self.storage_client = storage.Client(project=config.GCP_PROJECT_ID)
        self.db = db
        self.video_bucket_name = config.GCS_BUCKET_NAME_VIDEOS
        self.frame_bucket_name = config.GCS_BUCKET_NAME_FRAMES
        self.video_bucket = self.storage_client.bucket(self.video_bucket_name)
        self.frame_bucket = self.storage_client.bucket(self.frame_bucket_name)

    def upload_video(self, video_file):
        try:
            # Use only the file name from the uploaded file
            filename = video_file.filename
            blob = self.video_bucket.blob(filename)
            video_url = f"gs://{self.video_bucket_name}/{filename}"

            blob.upload_from_file(video_file)

            logger.info(f"Video {filename} uploaded to GCS bucket {self.video_bucket_name}")
            try:
                upload_date = datetime.now()
                video_metadata = {"video_id": video_id, "video_gcs_uri": video_url, "filename": filename, "upload_date": upload_date}
                self.db.store_video_metadata(video_metadata)
                logger.info(f"Video metadata for video_id {video_id} stored in the database.")
            except Exception as e:
                logger.error(f"Error storing video metadata in the database: {e}", exc_info=True)

            return video_metadata["video_id"]
        except Exception as e:
            logger.error(f"Error uploading video to GCS: {e}", exc_info=True)
            raise

    def download_video_to_temp(self, video_id):
        try:
            video_metadata = self.db.get_video_metadata(video_id)
            if not video_metadata:
                logger.warning(f"Video metadata not found for video ID: {video_id}")
                return None

            video_gcs_uri = video_metadata["video_gcs_uri"]
            filename = video_metadata["filename"]
            
            if not video_gcs_uri:
                raise ValueError("video gcs uri is null")

            blob = self.storage_client.blob_from_uri(video_gcs_uri)
            temp_filepath = os.path.join(self.config.VIDEO_UPLOAD_FOLDER_VIDEOS, filename) # Local temp path
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
            video_metadatas = self.db.list_video_metadata()
            for video_metadata in video_metadatas:
                videos.append({'id': video_metadata["video_id"], 'filename': video_metadata["filename"]})
            return videos
        except Exception as e:
            logger.error(f"Error listing videos from GCS: {e}", exc_info=True)
            return []

    def delete_video(self, video_id):
        """Delete video file by querying metadata, and delete the file in gcs.

        Args:
            video_id (_type_): _description_
        """

        try:
            video_metadata = self.db.get_video_metadata(video_id)
            if not video_metadata:
                logger.warning(f"Video metadata not found for video ID: {video_id}")
            return
            
            # Delete related frames from GCS
            frames = self.db.get_frames_by_video_id(video_id)
            if frames:
                for frame in frames:
                    frame_gcs_uri = frame["frame_gcs_uri"]
                    try:
                        frame_blob = self.storage_client.blob_from_uri(frame_gcs_uri)
                        frame_blob.delete()
                        logger.info(f"Frame {frame_gcs_uri} deleted from GCS.")
                    except Exception as e:
                        logger.error(f"Error deleting frame {frame_gcs_uri} from GCS: {e}", exc_info=True)

            video_gcs_uri = video_metadata["video_gcs_uri"]
            video_blob = self.storage_client.blob_from_uri(video_gcs_uri)
            video_blob.delete()
            self.db.delete_video_metadata(video_id)

            logger.info(f"Video {video_metadata['filename']} deleted from GCS bucket {self.video_bucket_name}")
        except Exception as e:
            logger.error(f"Error deleting video from GCS: {e}", exc_info=True)

    def get_video_info(self, video_id):
        video_metadata = self.db.get_video_metadata(video_id)
        if video_metadata:
            return {"video_url": video_metadata["video_gcs_uri"]}
        return None
