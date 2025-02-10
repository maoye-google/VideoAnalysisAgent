import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AnalysisProgress({ selectedVideoId }) {
    const [progress, setProgress] = useState(0);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisStatus, setAnalysisStatus] = useState(''); // e.g., "Analyzing", "Completed", "Cancelled", "Error"

    useEffect(() => {
        if (selectedVideoId) {
            startProgressCheck();
        }
        return () => stopProgressCheck(); // Cleanup on unmount
    }, [selectedVideoId]);
// }, [selectedVideoId, isAnalyzing]);

    const progressCheckInterval = React.useRef(null);

    const startProgressCheck = () => {
        console.log('Start Progress Check !')
        setIsAnalyzing(true)
        setAnalysisStatus("Analyzing");
        progressCheckInterval.current = setInterval(async () => {
            try {
                const response = await axios.get(`/api/videos/${selectedVideoId}/analysis-progress`);
                setProgress(response.data.progress || 0);
                setAnalysisStatus(response.data.status || "Analyzing"); // Update status from backend

                if (response.data.status === 'Completed' || response.data.status === 'Error' || response.data.status === 'Cancelled') {
                    stopProgressCheck();
                    setIsAnalyzing(false);
                    if (response.data.status === 'Completed') {
                        alert("Video analysis completed successfully!");
                    } else if (response.data.status === 'Error') {
                        alert("Video analysis encountered an error.");
                    } else if (response.data.status === 'Cancelled') {
                        alert("Video analysis was cancelled.");
                    }
                }
            } catch (error) {
                console.error('Error fetching analysis progress:', error);
                stopProgressCheck();
                setIsAnalyzing(false);
                setAnalysisStatus("Error");
                alert("Error fetching analysis progress.");
            }
        }, 2000); // Check progress every 2 seconds
    };

    const stopProgressCheck = () => {
        console.log("Stop Progress Check");
        clearInterval(progressCheckInterval.current);
    };

    const handleCancelAnalysis = async () => {
        if (selectedVideoId && isAnalyzing) {
            try {
                await axios.post(`/api/videos/${selectedVideoId}/cancel-analysis`);
                console.log('Analysis cancellation requested for video:', selectedVideoId);
                stopProgressCheck();
                setIsAnalyzing(false);
                setAnalysisStatus("Cancelled");
                alert("Analysis cancellation requested.");
            } catch (error) {
                console.error('Error cancelling analysis:', error);
                alert('Failed to cancel analysis.');
            }
        }
    };

    if (!selectedVideoId) {
        return <p>Select a video to see analysis progress.</p>;
    }

    return (
        <div>
            <h2>Video Analysis Progress</h2>
            {isAnalyzing && analysisStatus === "Analyzing" ? (
                <div>
                    <p>Analysis Status: {analysisStatus}</p>
                    <progress value={progress} max="100" /> {progress}%
                    <button onClick={handleCancelAnalysis}>Cancel Analysis</button>
                </div>
            ) : (
                <p>Analysis Status: {analysisStatus || "Not Started"}</p>
            )}
        </div>
    );
}

export default AnalysisProgress;