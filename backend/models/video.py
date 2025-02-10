# backend/models/video.py
# Example, you might use SQLAlchemy or similar for database models

class Video:
    def __init__(self, video_id, filename, video_gcs_uri, upload_date=None):
        self.video_id = video_id
        self.filename = filename
        self.video_gcs_uri = video_gcs_uri
        self.upload_date = upload_date # Example metadata