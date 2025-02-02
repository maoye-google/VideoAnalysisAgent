import React from 'react';

function QueryResults({ results }) {
    if (!results) {
        return <p>No query submitted yet.</p>;
    }

    if (results.message) {
        return <p>{results.message}</p>; // Display error or "no results" messages
    }

    if (!results.frames || results.frames.length === 0) {
        return <p>Sorry, no relevant video frames found for your query.</p>;
    }

    return (
        <div>
            <h2>Query Results</h2>
            {results.frames.map((frame, index) => (
                <div key={index} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
                    <img src={frame.frame_url} alt={`Frame ${index}`} style={{ maxWidth: '300px' }} />
                    <p>Timeframe: {frame.timeframe}</p>
                    <p>Video Link: <a href={frame.video_link} target="_blank" rel="noopener noreferrer">View Video</a></p>
                    <p>Confidence: To-Be-Calculated</p>
                    {frame.detected_objects && frame.detected_objects.length > 0 && (
                        <div>
                            <p>Detected Objects:</p>
                            <ul>
                                {frame.detected_objects.map((obj, objIndex) => (
                                    <li key={objIndex}>Type: {obj.object_type}    Color: {obj.object_color}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

export default QueryResults;