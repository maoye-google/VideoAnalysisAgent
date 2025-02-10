import React, { useState, useEffect } from 'react';
import axios from 'axios';

function VideoList({ onVideoSelected, onVideoDeleted, refresh }) {
    const [videos, setVideos] = useState([]);

    useEffect(() => {
        fetchVideos();
    }, [refresh]);

    const fetchVideos = async () => {
        try {
            const response = await axios.get('/api/videos');
            setVideos(response.data);
        } catch (error) {
            console.error('Error fetching videos:', error);
        }
    };

    const handleDeleteVideo = async (videoId) => {
        if (window.confirm('Are you sure you want to delete this video?')) {
            try {
                await axios.delete(`/api/videos/${videoId}`);
                console.log('Video deleted successfully:', videoId);
                fetchVideos(); // Refresh video list
                if (onVideoDeleted) {
                    onVideoDeleted(); // Callback if needed
                }
            } catch (error) {
                console.error('Error deleting video:', error);
                alert('Failed to delete video.');
            }
        }
    };

    const handleAnalyzeVideo = async (videoId) => {
        try {
            await axios.post(`/api/videos/${videoId}/analyze`);
            console.log('Video analysis started:', videoId);
            alert('Video analysis started. Check progress in analysis section.');
        } catch (error) {
            console.error('Error starting video analysis:', error);
            alert('Failed to start video analysis.');
        }
    };


    return (
        <div>
            <h2>Available Videos</h2>
            <ul>
                {videos.map((video) => (
                    <li key={video.video_id}>
                        <td width="150px">{video.filename}</td>
                        <td><button onClick={() => onVideoSelected(video.video_id)}>Select</button></td>
                        <td><button onClick={() => handleAnalyzeVideo(video.video_id)}>Analyze</button></td>
                        <td><button onClick={() => handleDeleteVideo(video.video_id)}>Delete</button></td>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default VideoList;