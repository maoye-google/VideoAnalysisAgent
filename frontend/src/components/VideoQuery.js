import React, { useState } from 'react';
import axios from 'axios';

function VideoQuery({ selectedVideoId, onQueryResults }) {
    const [queryText, setQueryText] = useState('');

    const handleQuerySubmit = async () => {
        if (!selectedVideoId) {
            alert('Please select a video first.');
            return;
        }
        if (!queryText) {
            alert('Please enter your query.');
            return;
        }

        try {
            const response = await axios.post(`/api/videos/${selectedVideoId}/query`, {
                query: queryText,
            });
            console.log('Query results:', response.data);
            onQueryResults(response.data); // Pass results to parent component
        } catch (error) {
            console.error('Error submitting query:', error);
            alert('Failed to submit query.');
            onQueryResults({ frames: [], message: "Error processing query." }); // Handle error case
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleQuerySubmit();
        }
    };

    return (
        <div>
            <h2>Video Query</h2>
            {selectedVideoId ? (
                <div>
                    <p>Selected Video ID: {selectedVideoId}</p>
                    <input
                        type="text"
                        placeholder="Enter your query (e.g., find person in red coat)"
                        value={queryText}
                        onChange={(e) => setQueryText(e.target.value)}
                        onKeyPress={handleKeyPress}
                    />
                    <button onClick={handleQuerySubmit}>Search</button>
                </div>
            ) : (
                <p>Please select a video from the list to query.</p>
            )}
        </div>
    );
}

export default VideoQuery;