# backend/models/frame.py

class Frame:
    def __init__(self, frame_id, video_id, frame_gcs_uri, seconds, embedding, detected_objects=None, text_description=None):
        self.frame_id = frame_id
        self.video_id = video_id
        self.frame_gcs_uri = frame_gcs_uri
        self.seconds = seconds
        self.detected_objects = detected_objects or [] # List of detected objects
        self.text_description = text_description