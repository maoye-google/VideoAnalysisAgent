import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    # General Config
    DEBUG = True  # Set to False in production
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO') # Default to INFO if not set

    # Google Cloud Config
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
    GCP_REGION = os.environ.get('GCP_REGION', 'us-central1') # Default region
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS','credential/agent-sa-key.json')
    GCP_VERTEX_AI_API_KEY = os.environ.get('GCP_VERTEX_AI_API_KEY')
    GEMINI_MODEL_NAME = os.environ.get('GEMINI_MODEL_NAME', 'gemini-2.0-flash') # Default model
    GCS_BUCKET_NAME_VIDEOS = os.environ.get('GCS_BUCKET_NAME_VIDEOS')
    GCS_BUCKET_NAME_FRAMES = os.environ.get('GCS_BUCKET_NAME_FRAMES')

    # AlloyDB Config (Example, adjust as needed for connection method)
    ALLOYDB_CONNECTION_STRING = os.environ.get('ALLOYDB_CONNECTION_STRING') # Or individual settings
    ALLOYDB_INSTANCE_ID = os.environ.get('ALLOYDB_INSTANCE_ID')
    ALLOYDB_DATABASE_NAME = os.environ.get('ALLOYDB_DATABASE_NAME')
    ALLOYDB_USER = os.environ.get('ALLOYDB_USER')
    ALLOYDB_PASSWORD = os.environ.get('ALLOYDB_PASSWORD')
    ALLOYDB_HOST = os.environ.get('ALLOYDB_HOST')
    ALLOYDB_PORT = os.environ.get('ALLOYDB_PORT')

    # Video Analysis Config
    VIDEO_UPLOAD_FOLDER_VIDEOS = 'uploads/videos' # Local upload folder for videos (for local dev)
    VIDEO_UPLOAD_FOLDER_FRAMES = 'uploads/frames' # Local folder for frames
    VIDEO_SAMPLING_RATE = int(os.environ.get('VIDEO_SAMPLING_RATE', 5)) # Frames per second, default 5
    ANALYSIS_PROGRESS_UPDATE_INTERVAL = 5 # seconds, interval to update analysis progress

    # Ensure upload folders exist
    os.makedirs(VIDEO_UPLOAD_FOLDER_VIDEOS, exist_ok=True)
    os.makedirs(VIDEO_UPLOAD_FOLDER_FRAMES, exist_ok=True)