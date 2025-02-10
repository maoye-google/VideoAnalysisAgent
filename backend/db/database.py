import logging
import numpy as np
import json
import psycopg2
import traceback

logger = logging.getLogger(__name__)

import urllib.parse

def _create_connection_string(user,password,host,port,database):
    encoded_password = urllib.parse.quote_plus(password) # Encode the password
    
    # Construct the connection string
    conn_string = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"

    return conn_string

class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None

        # connection_string = self.config.get("ALLOYDB_CONNECTION_STRING")

        connection_string = _create_connection_string(
            self.config.get("ALLOYDB_USER"),
            self.config.get("ALLOYDB_PASSWORD"),
            self.config.get("ALLOYDB_HOST"),
            self.config.get("ALLOYDB_PORT"),
            self.config.get("ALLOYDB_DATABASE_NAME")
        )
        print(f" Connection String is {connection_string}")

        try:
            self.connection = psycopg2.connect(connection_string)
            logger.info("Successfully connected to AlloyDB using connection string.")
        except psycopg2.Error as e:
            logger.error(f"Error connecting to AlloyDB using connection string: {e}", exc_info=True)
            raise  # Re-raise the exception to halt application startup

    def __del__(self):
        """Ensure database connection is closed when the object is destroyed."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")
            
    def store_video_metadata(self, video_metadata):
        """Stores video metadata."""
        # Placeholder implementation - replace with actual AlloyDB insert
        video_id = video_metadata['video_id']
        video_gcs_uri = video_metadata['video_gcs_uri']
        filename = video_metadata['filename']
        upload_date = video_metadata['upload_date']
        
        logger.debug(f"Storing video metadata for video ID: {video_id}, video Name: {filename}")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO videos (video_id, video_gcs_uri, filename, upload_date)
                    VALUES (%s, %s, %s, %s)
                """, (video_id, video_gcs_uri, filename, upload_date))
            self.connection.commit()
            logger.debug(f"Video metadata stored successfully for video ID: {video_id}")
        except Exception as e:
            logger.error(f"Error storing video metadata for video ID {video_id}: {e}", exc_info=True)


    def get_video_metadata(self, video_id):
        """Performs basic CRUD operation in AlloyDB to get video metadata."""
        # Placeholder implementation - replace with actual AlloyDB vector search
        logger.debug(f"Get video metadata for video ID: {video_id}")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT video_id, video_gcs_uri, filename, upload_date
                    FROM videos
                    WHERE video_id = %(video_id)s
                """, {"video_id": video_id}) # Convert numpy array to list for psycopg2
                result = cur.fetchone()
                if not result:
                    logger.debug(f"No videos found with id {video_id}.")
                    return None
                else:
                    logger.debug(f"Found video with id {video_id}.")
                    return dict(zip(['video_id', 'video_gcs_uri', 'filename', 'upload_date'], result))
                    # return result
        except Exception as e:
            logger.error(f"Error during video get operation for video {video_id}: {e}", exc_info=True)
            return None # Placeholder - return Null for now
    
    def list_video_metadata(self):
        """Lists all videos' metadata."""
        logger.debug("Listing all video metadata")
        try:
            with self.connection.cursor() as cur:
              cur.execute("""
                  SELECT video_id, video_gcs_uri, filename, upload_date
                  FROM videos
              """)
              results = cur.fetchall()
              logger.debug(f"Found {len(results)} videos")
              video_list = [dict(zip(['video_id', 'video_gcs_uri', 'filename', 'upload_date'], row)) for row in results]
              return video_list
        except Exception as e:
            logger.error(f"Error during list all video metadata: {e}", exc_info=True)
            return []

    def delete_video_metadata(self, video_id):
        """Deletes a video's metadata."""
        logger.debug(f"Deleting video metadata for video ID: {video_id}")
        
        # First, delete related frames
        
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    DELETE FROM frames
                    WHERE video_id = %(video_id)s
                """, {"video_id" : video_id})
                self.connection.commit()
                logger.debug(f"Frame metadata deleted successfully for video ID: {video_id}")
                
        except Exception as e:
            logger.error(f"Error during delete frame operation for video {video_id}: {e}", exc_info=True)
        
        # Then delete video    
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM videos WHERE video_id = %(video_id)s", {"video_id" : video_id})
                self.connection.commit()  # Commit the deletion
                
                logger.debug(f"Video metadata deleted successfully for video ID: {video_id}")
        except Exception as e:
            logger.error(f"Error during video deletion operation for video {video_id}: {e}", exc_info=True)
        return None # Placeholder - return Null for now


    def get_frames_by_video_id(self, video_id):
        """Gets all frames associated with a video ID."""
        logger.debug(f"Fetching frames for video ID: {video_id}")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT frame_id, video_id, frame_gcs_uri, timeframe, detected_objects_json, text_description
                    FROM frames
                    WHERE video_id = %(video_id)s
                """, {"video_id" : video_id})
                results = cur.fetchall()
                frames = [dict(zip(['frame_id', 'video_id', 'frame_gcs_uri', 'timeframe','detected_objects_json','text_description'], row)) for row in results]
                return frames
        except Exception as e:
            logger.error(f"Error fetching frames for video ID {video_id}: {e}", exc_info=True)
            return []

    def get_analyzed_video_list(self):
        """Gets all videos associated with frames."""
        logger.debug("Fetching analyzed Video IDs")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                   SELECT distinct(video_id) FROM frames
                """)
                results = cur.fetchall()
                frames = [dict(zip(['video_id'], row)) for row in results]
                return frames
        except Exception as e:
            logger.error(f"Error fetching analyzed videos : {e}", exc_info=True)
            return []

    def store_frame_metadata(self, frame_metadata):
        """Stores frame metadata and its embedding vector."""
        # Placeholder implementation - replace with actual AlloyDB insert
        frame_id = frame_metadata['frame_id']
        video_id = frame_metadata['video_id']
        frame_gcs_uri = frame_metadata['frame_gcs_uri']
        timeframe = frame_metadata['timeframe']
        detected_objects_json = frame_metadata.get('detected_objects', []) # Example: store detected objects as JSON
        text_description = frame_metadata.get('text_description', '')

        logger.debug(f"Storing frame metadata for frame ID: {frame_id}, video ID: {video_id}")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO frames (frame_id, video_id, frame_gcs_uri, timeframe, detected_objects_json, text_description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (frame_id, video_id, frame_gcs_uri, timeframe, json.dumps(detected_objects_json), text_description))
            self.connection.commit()
            logger.debug(f"Frame metadata stored successfully for frame ID: {frame_id}")
        except Exception as e:
            logger.error(f"Error storing frame metadata for frame ID {frame_id}: {e}", exc_info=True)


    def frame_description_similarity_search(self, query_str, video_id, top_k=3):
        """Performs vector similarity search in AlloyDB to find similar frames."""
        # Placeholder implementation - replace with actual AlloyDB vector search
        logger.debug(f"Performing Frame Similarity Search for video ID: {video_id}")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT frame_id, video_id, frame_gcs_uri, timeframe, detected_objects_json, text_description
                    FROM frames
                    WHERE video_id = %(video_id)s
                    ORDER BY frame_embedding <=> embedding('text-embedding-005', %(query_str)s)::vector
                    LIMIT %(top_k)s
                """, {
                    "video_id":video_id, 
                    "query_str":query_str, 
                    "top_k":top_k
                }) # Convert numpy array to list for psycopg2
                results = cur.fetchall()
                similar_frames = [dict(zip(['frame_id', 'video_id', 'frame_gcs_uri', 'timeframe','detected_objects_json','text_description'], row)) for row in results]
                return similar_frames
        except Exception as e:
            logger.error(f"Error during Frame Similarity Search for video {video_id}: {e}", exc_info=True)
        return [] # Placeholder - return empty list for now

    def objects_similarity_search(self, query_str, video_id, top_k=3):
        """Performs vector similarity search in AlloyDB to find similar frames."""
        # Placeholder implementation - replace with actual AlloyDB vector search
        logger.debug(f"Performing Detected Objects Similarity Search for video ID: {video_id}")
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT frame_id, video_id, frame_gcs_uri, timeframe, detected_objects_json, text_description
                    FROM frames
                    WHERE video_id = %(video_id)s
                    ORDER BY objects_embedding <=> embedding('text-embedding-005', %(query_str)s)::vector
                    LIMIT %(top_k)s
                 """, {
                    "video_id":video_id, 
                    "query_str":query_str, 
                    "top_k":top_k
                }) # Convert numpy array to list for psycopg2
                results = cur.fetchall()
                similar_frames = [dict(zip(['frame_id', 'video_id', 'frame_gcs_uri', 'timeframe','detected_objects_json','text_description'], row)) for row in results]
                return similar_frames
        except Exception as e:
            logger.error(f"Error during Detected Objects Similarity Search for video {video_id}: {e}", exc_info=True)
        return [] # Placeholder - return empty list for now