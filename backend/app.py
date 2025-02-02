from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from services.video_analysis_service import VideoAnalysisService
from services.query_service import QueryService
from services.storage_service import StorageService
from db.database import Database
import logging
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Allow CORS for /api endpoints
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.INFO) # Set default log level
logger = logging.getLogger(__name__)

# Initialize services
db = Database(app.config)  
storage_service = StorageService(app.config, db) #Pass db instance to storage service
query_service = QueryService(app.config, db, storage_service)
video_analysis_service = VideoAnalysisService(app.config, storage_service, db)


@app.route('/api/videos', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'message': 'No video file part'}), 400
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'message': 'No selected video file'}), 400

    try:
        video_id = storage_service.upload_video(video_file)
        return jsonify({'message': 'Video uploaded successfully', 'video_id': video_id}), 201
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        return jsonify({'message': 'Failed to upload video'}), 500

@app.route('/api/videos', methods=['GET'])
def list_videos():
    try:
        videos = storage_service.list_videos()
        return jsonify(videos), 200
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({'message': 'Failed to list videos'}), 500

@app.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    try:
        storage_service.delete_video(video_id)
        return jsonify({'message': 'Video deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {e}")
        return jsonify({'message': 'Failed to delete video'}), 500

@app.route('/api/videos/<video_id>/analyze', methods=['POST'])
def analyze_video(video_id):

    try:
        video_analysis_service.start_analysis(video_id)
        return jsonify({'message': 'Video analysis started'}), 202
    except Exception as e:
        logger.error(f"Error starting video analysis for {video_id}: {e}")
        return jsonify({'message': 'Failed to start video analysis'}), 500

@app.route('/api/videos/<video_id>/analysis-progress', methods=['GET'])
def get_analysis_progress(video_id):
    try:
        progress_data = video_analysis_service.get_analysis_progress(video_id)
        return jsonify(progress_data), 200
    except Exception as e:
        logger.error(f"Error getting analysis progress for {video_id}: {e}")
        return jsonify({'message': 'Failed to get analysis progress'}), 500

@app.route('/api/videos/<video_id>/cancel-analysis', methods=['POST'])
def cancel_analysis(video_id):
    try:
        video_analysis_service.cancel_analysis(video_id)
        return jsonify({'message': 'Video analysis cancellation requested'}), 202
    except Exception as e:
        logger.error(f"Error cancelling analysis for {video_id}: {e}")
        return jsonify({'message': 'Failed to cancel analysis'}), 500

@app.route('/api/videos/<video_id>/query', methods=['POST'])
def query_video(video_id):
    query_text = request.json.get('query')
    if not query_text:
        return jsonify({'message': 'Query text is required'}), 400

    try:
        results = query_service.query_video(video_id, query_text)
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Error querying video {video_id}: {e}")
        return jsonify({'message': 'Failed to process query'}), 500

@app.route('/frames/<filename>')
def get_frame_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_FRAMES'], filename)


if __name__ == '__main__':
    app.run(debug=True) # Run in debug mode for local development