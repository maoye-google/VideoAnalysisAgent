import React, { useState } from 'react';
import VideoUpload from './components/VideoUpload';
import VideoList from './components/VideoList';
import VideoQuery from './components/VideoQuery';
import QueryResults from './components/QueryResults';
import AnalysisProgress from './components/AnalysisProgress';

function App() {
    const [selectedVideoId, setSelectedVideoId] = useState(null);
    const [queryResults, setQueryResults] = useState(null);
    const [refreshVideoList, setRefreshVideoList] = useState(false); // State to trigger video list refresh

    const handleVideoSelected = (videoId) => {
        setSelectedVideoId(videoId);
        setQueryResults(null); // Clear previous results when video changes
    };

    const handleQueryResults = (results) => {
        setQueryResults(results);
    };

    const handleVideoUploadedOrDeleted = () => {
        setRefreshVideoList(!refreshVideoList); // Toggle state to trigger refresh in VideoList
    };


    return (
        <div className="App">
            <h1>Video Analysis Agent</h1>
            <VideoUpload onVideoUploaded={handleVideoUploadedOrDeleted} />
            <VideoList onVideoSelected={handleVideoSelected} onVideoDeleted={handleVideoUploadedOrDeleted} refresh={refreshVideoList}/>
            <AnalysisProgress selectedVideoId={selectedVideoId} />
            <VideoQuery selectedVideoId={selectedVideoId} onQueryResults={handleQueryResults} />
            <QueryResults results={queryResults} />
        </div>
    );
}

export default App;