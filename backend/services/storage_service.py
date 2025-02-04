import logging
import os
from datetime import datetime
import uuid

from google.cloud import storage
from db.database import Database

logger = logging.getLogger(__name__)

import urllib.parse

def _quote_file_name(filename):
    encoded_filename = urllib.parse.quote_plus(filename) # Encode the password    

    return encoded_filename

class StorageService:
    def __init__(self, config, db: Database):
        self.config = config
        self.db=db
        self.storage_client = storage.Client(project=config.get('GCP_PROJECT_ID'))
        self.video_bucket_name = config.get('GCS_BUCKET_NAME_VIDEOS')
        self.frame_bucket_name = config.get('GCS_BUCKET_NAME_FRAMES')
        self.video_bucket = self.storage_client.bucket(self.video_bucket_name)
        self.frame_bucket = self.storage_client.bucket(self.frame_bucket_name)

    def _compose_gcs_video_name(self,video_id, filename):
        gcs_file_name = f'{video_id}_{_quote_file_name(filename)}'
        return gcs_file_name

    def _compose_gcs_frame_name(self,video_id, frame_id):
        gcs_file_name = f'{video_id}_{frame_id}.jpg'
        return gcs_file_name

    def upload_video(self, video_file, video_id):
        try:
            # Use only the file name from the uploaded file
            gcs_file_name = self._compose_gcs_video_name(video_id, video_file.filename)

            video_url = f"gs://{self.video_bucket_name}/{gcs_file_name}"
            
            blob = self.video_bucket.blob(gcs_file_name)
            blob.upload_from_file(video_file)

            logger.info(f"Video {video_file.filename} uploaded to GCS bucket {self.video_bucket_name}")
            try:
                upload_date = datetime.now()
                video_metadata = {"video_id": video_id, "video_gcs_uri": video_url, "filename": video_file.filename, "upload_date": upload_date}
                self.db.store_video_metadata(video_metadata)
                logger.info(f"Video metadata for video_id {video_id} stored in the database.")
            except Exception as e:
                logger.error(f"Error storing video metadata in the database: {e}", exc_info=True)

            return video_metadata
        except Exception as e:
            logger.error(f"Error uploading video to GCS: {e}", exc_info=True)
            raise

    def download_video_to_temp(self, video_metadata):
        try:
            # video_metadata = self.db.get_video_metadata(video_id)
            if not video_metadata:
                logger.warning(f"Video metadata not found for video ID: {video_id}")
                return None

            video_gcs_uri = video_metadata.get("video_gcs_uri")
            _,_,bucket_name,_filename = video_gcs_uri.split("/")
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(_filename)

            if blob is None :
                logger.error(f"Cannot find GCS Object as {video_gcs_uri}", exc_info=True)
                return None
            
            temp_filepath = os.path.join(self.config.get('VIDEO_UPLOAD_FOLDER_VIDEOS'), _filename) # Local temp path
            blob.download_to_filename(temp_filepath)
            filename = video_metadata.get("filename")
            logger.info(f"Video {filename} downloaded from GCS to {temp_filepath}")
            return temp_filepath
        except Exception as e:
            logger.error(f"Error downloading video from GCS: {e}", exc_info=True)
            return None

    def upload_frame_bytes(self, frame_id, video_id, frame_bytes):
        
        try:
            gcs_file_name = self._compose_gcs_frame_name(video_id, frame_id)
            frame_url = f"gs://{self.frame_bucket_name}/{gcs_file_name}"
            
            blob = self.frame_bucket.blob(gcs_file_name)
            blob.upload(frame_bytes)

            logger.info(f"Frame {gcs_file_name} uploaded to GCS bucket {self.frame_bucket_name}")

            
            return frame_url
        except Exception as e:
            logger.error(f"Error uploading frame to GCS: {e}", exc_info=True)
            return None

    def list_videos(self):
        try:
            video_metadatas = self.db.list_video_metadata()
            return video_metadatas
        except Exception as e:
            logger.error(f"Error listing videos from GCS: {e}", exc_info=True)
            return []


    def _delete_blob(self,bucket_name,object_name):
        """Deletes a blob from the bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        try:
            blob.delete()
            print(f"Blob {object_name} deleted from bucket {bucket_name}.")
        except Exception as e:
            print(f"Error deleting blob {object_name} from bucket {bucket_name}: {e}")


    def delete_frames(self,video_id):
        """Deletes all frames related to the certain video_id."""
        try:
            logger.debug(f'Check Frame Existance')
            frames = self.db.get_frames_by_video_id(video_id)
            if frames:
                try:
                    logger.debug(f'Delete Frames from GCS Bucket')
                    for frame in frames:
                        self._delete_blob(self.frame_bucket_name,self._compose_gcs_frame_name(video_id,frame.get("frame_id")))
                    logger.debug(f"Frames related to video {video_id} have been deleted from GCS!")
                except Exception as e:
                    logger.error(f"Error deleting frames from GCS: {e}", exc_info=True)

                logger.debug(f'Delete Frames Metadata from DB')
                self.db.delete_video_metadata(video_id)
                logger.info(f"Frame Delete Complete for Video {video_id}")
        except Exception as e:
            logger.error(f"Error deleting video from GCS: {e}", exc_info=True)


    def delete_video(self, video_id):
        """Delete video file by querying metadata, and delete the file in gcs.

        Args:
            video_id (_type_): _description_
        """

        try:
            logger.debug("Check video metadata Existance")
            video_metadata = self.db.get_video_metadata(video_id)
            if video_metadata is None:
                logger.warning(f"Video metadata not found for video ID: {video_id}")
                return

            logger.debug(f'Delete Related Frames')
            self.delete_frames(video_id)
            
            logger.debug(f'Delete Video File from GCS')
            self._delete_blob(self.video_bucket_name,self._compose_gcs_video_name(video_id,video_metadata.get('filename')))
            
            logger.debug(f'Delete Video Metadata')
            self.db.delete_video_metadata(video_id)

            logger.info(f"Video {video_metadata.get('filename')} delete complete !")
        except Exception as e:
            logger.error(f"Error deleting video from GCS: {e}", exc_info=True)

    def get_video_info(self, video_id):
        video_metadata = self.db.get_video_metadata(video_id)
        return video_metadata
