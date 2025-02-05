import React, { useState } from 'react';
import axios from 'axios';

function VideoUpload({ onVideoUploaded }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            alert('Please select a video file.');
            return;
        }

        setIsUploading(true);
        const formData = new FormData();
        formData.append('video', selectedFile);

        try {
            const response = await axios.post('/api/videos', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(progress);
                },
            });
            console.log('Video uploaded successfully:', response.data);
            setSelectedFile(null);
            setUploadProgress(0);
            setIsUploading(false);
            if (onVideoUploaded) {
                onVideoUploaded(); // Callback to refresh video list
            }
        } catch (error) {
            console.error('Error uploading video:', error);
            alert('Failed to upload video.');
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

        return (
                <div className="container mt-3">
                        <div className="row justify-content-center">
                                <div className="col-md-6">
                                        <div className="card">
                                                <div className="card-body">
                                                        <h5 className="card-title">Upload Video</h5>
                                                        <div className="mb-3">
                                                                <label htmlFor="videoFile" className="form-label">Select Video File:</label>
                                                                <input type="file" id="videoFile" className="form-control" accept="video/*" onChange={handleFileChange} disabled={isUploading} />
                                                        </div>
                                                        <button type="button" className="btn btn-primary" onClick={handleUpload} disabled={!selectedFile || isUploading}>
                                                                Upload Video
                                                        </button>
                                                        {isUploading && (
                                                                <div className="mt-3">
                                                                        <div className="progress">
                                                                                <div className="progress-bar" role="progressbar" style={{ width: `${uploadProgress}%` }} aria-valuenow={uploadProgress} aria-valuemin="0" aria-valuemax="100">{uploadProgress}%</div>
                                                                        </div>
                                                                </div>
                                                        )}
                                                </div>
                                        </div>
                                </div>
                        </div>
                </div>
        );
    }

export default VideoUpload;