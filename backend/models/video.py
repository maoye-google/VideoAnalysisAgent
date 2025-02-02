# backend/models/video.py
# Example, you might use SQLAlchemy or similar for database models

class Video:
    def __init__(self, video_id, filename, upload_date=None):
        self.video_id = video_id
        self.filename = filename
        self.upload_date = upload_date # Example metadata