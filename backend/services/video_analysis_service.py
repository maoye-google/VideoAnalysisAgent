import logging
import os
import cv2
import numpy as np
import uuid
import threading
import time
from services.llm_service import LLMService
from services.storage_service import StorageService
from db.database import Database

logger = logging.getLogger(__name__)

class VideoAnalysisService:
    def __init__(self, config, storage_service: StorageService, db: Database):
        self.config = config
        self.storage_service = storage_service
        self.db = db
        self.llm_service = LLMService(config)
        self.analysis_processes = {} # track analysis process status, progress, cancellation
        self.analysis_progress_interval = config.ANALYSIS_PROGRESS_UPDATE_INTERVAL # seconds

    def start_analysis(self, video_id):
        if video_id in self.analysis_processes and self.analysis_processes[video_id]['status'] == 'Running':
            raise ValueError(f"Analysis already running for video ID: {video_id}")

        self.analysis_processes[video_id] = {
            'status': 'Pending',
            'progress': 0,
            'cancel_event': threading.Event() # For cancellation
        }
        thread = threading.Thread(target=self._analyze_video_thread, args=(video_id,))
        thread.start()
        self.analysis_processes[video_id]['status'] = 'Running'
        logger.info(f"Analysis thread started for video ID: {video_id}")

    def get_analysis_progress(self, video_id):
        if video_id not in self.analysis_processes:
            return {'status': 'NotFound', 'progress': 0}
        process_info = self.analysis_processes[video_id]
        return {'status': process_info['status'], 'progress': process_info['progress']}

    def cancel_analysis(self, video_id):
        if video_id in self.analysis_processes and self.analysis_processes[video_id]['status'] == 'Running':
            self.analysis_processes[video_id]['cancel_event'].set() # Signal cancellation
            self.analysis_processes[video_id]['status'] = 'Cancelling'
            logger.info(f"Cancellation requested for video ID: {video_id}")
        else:
            logger.warning(f"No running analysis to cancel for video ID: {video_id}")

    def _analyze_video_thread(self, video_id):
        try:
            logger.info(f"Starting video analysis for video ID: {video_id}")
            video_filepath = self.storage_service.download_video_to_temp(video_id)
            if not video_filepath:
                raise FileNotFoundError(f"Failed to download video {video_id} for analysis.")

            sampling_rate = self.config.VIDEO_SAMPLING_RATE
            frame_count = 0
            processed_frames = 0
            cap = cv2.VideoCapture(video_filepath)
            if not cap.isOpened():
                raise IOError(f"Cannot open video file: {video_filepath}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps / sampling_rate) if fps > sampling_rate else 1
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"Video FPS: {fps}, Sampling Rate: {sampling_rate}, Frame Interval: {frame_interval}, Total Frames: {total_frames}")

            while True:
                if self.analysis_processes[video_id]['cancel_event'].is_set():
                    logger.info(f"Analysis cancelled by user for video ID: {video_id}")
                    self.analysis_processes[video_id]['status'] = 'Cancelled'
                    break

                ret, frame = cap.read()
                if not ret:
                    logger.info(f"End of video reached for video ID: {video_id}")
                    break

                if frame_count % frame_interval == 0:
                    frame_id = str(uuid.uuid4())
                    frame_filename = f"frame_{video_id}_{frame_id}.jpg"

                    # Convert the frame to JPEG bytes
                    ret, frame_bytes = cv2.imencode('.jpg', frame)
                    if not ret:
                         raise Exception("Could not convert frame to bytes")
                    frame_bytes = frame_bytes.tobytes()

                    # Analyze frame using LLM
                    frame_analysis_result = self.llm_service.analyze_image(frame_bytes)

                    # Analyze frame using LLM and create embedding
                    if frame_analysis_result:
                        frame_gcs_uri = self.storage_service.upload_frame_bytes(frame_bytes, frame_filename)
                        logger.debug(f"Frame {frame_id} uploaded to GCS for video {video_id}")
                        frame_metadata = {
                            'frame_id': frame_id,
                            'video_id': video_id,
                            'frame_gcs_uri': frame_gcs_uri,
                            'timeframe': f"Frame {processed_frames // sampling_rate}s", # Example timeframe
                            'detected_objects': frame_analysis_result.get('detected_objects', []), # List of objects with labels and bounding boxes
                            'text_description': frame_analysis_result.get('text_description', '')
                        }
                        self.db.store_frame_metadata(frame_metadata)
                        logger.debug(f"Frame {frame_id} analysis result stored for video {video_id}")

                frame_count += 1
                processed_frames += 1
                progress = int((processed_frames / total_frames) * 100) if total_frames > 0 else 0
                self.analysis_processes[video_id]['progress'] = progress

                if processed_frames % (int(fps) * self.analysis_progress_interval) == 0: # Update status periodically
                    logger.info(f"Analysis progress for video {video_id}: {progress}% processed frames: {processed_frames}/{total_frames}")

            cap.release()
            os.remove(video_filepath) # Clean up temp video file
            self.analysis_processes[video_id]['status'] = 'Completed'
            logger.info(f"Video analysis completed for video ID: {video_id}")

        except Exception as e:
            logger.error(f"Error during video analysis for video ID: {video_id}: {e}", exc_info=True)
            self.analysis_processes[video_id]['status'] = 'Error'
        finally:
            if video_id in self.analysis_processes and self.analysis_processes[video_id]['status'] not in ['Completed', 'Cancelled', 'Error']:
                self.analysis_processes[video_id]['status'] = 'Error' # Ensure status is set even if exception occurs