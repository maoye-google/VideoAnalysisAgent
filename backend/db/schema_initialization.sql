-- Target Database : video_analysis

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS alloydb_scann;
CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;

create table videos (
	video_id VARCHAR(255) PRIMARY KEY,
	filename VARCHAR(255),
	video_gcs_uri VARCHAR(255),
	upload_date TIMESTAMP
)

create table frames (
	frame_id VARCHAR(255) PRIMARY KEY,
	video_id VARCHAR(255) REFERENCES videos(video_id),
	frame_gcs_uri VARCHAR(255),
	timeframe VARCHAR(255),
	detected_objects_json TEXT,
	text_description TEXT,
	frame_embedding vector(768) GENERATED ALWAYS AS (embedding('text-embedding-005', text_description)) STORED,
	objects_embedding vector(768) GENERATED ALWAYS AS (embedding('text-embedding-005', detected_objects_json)) STORED
)
