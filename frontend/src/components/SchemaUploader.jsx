import React, { useState } from 'react';

function SchemaUploader({ onSchemaUpdate }) {
    const [mode, setMode] = useState('sql'); // 'sql', 'csv', or 'json'
    const [jsonInput, setJsonInput] = useState('');
    const [fileHandle, setFileHandle] = useState(null);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleJsonUpload = async () => {
        setError(null);
        setSuccess(null);
        try {
            const schemaData = JSON.parse(jsonInput);
            const response = await fetch('http://localhost:8000/api/schema/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(schemaData),
            });
            if (!response.ok) throw new Error((await response.json()).detail || 'Failed to update schema');
            
            setSuccess('Schema updated successfully!');
            if (onSchemaUpdate) onSchemaUpdate();
        } catch (err) {
            setError(err instanceof SyntaxError ? 'Invalid JSON format' : err.message);
        }
    };

    const handleFileUpload = async (endpoint) => {
        setError(null);
        setSuccess(null);
        if (!fileHandle) {
            setError('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileHandle);

        try {
            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error((await response.json()).detail || 'Failed to upload file');

            const data = await response.json();
            setSuccess(data.message || 'Imported successfully!');
            setFileHandle(null);
            
            const fileInput = document.getElementById('file-input');
            if (fileInput) fileInput.value = '';

            if (onSchemaUpdate) onSchemaUpdate();
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="schema-uploader">
            <div style={{ display: 'flex', gap: '5px', marginBottom: '1rem', flexWrap: 'wrap' }}>
                <button 
                    style={{ flex: 1, padding: '0.5rem', opacity: mode === 'sql' ? 1 : 0.5, fontSize: '0.85rem' }} 
                    onClick={() => { setMode('sql'); setError(null); setSuccess(null); }}
                >
                    SQL
                </button>
                <button 
                    style={{ flex: 1, padding: '0.5rem', opacity: mode === 'csv' ? 1 : 0.5, fontSize: '0.85rem' }} 
                    onClick={() => { setMode('csv'); setError(null); setSuccess(null); }}
                >
                    CSV
                </button>
                <button 
                    style={{ flex: 1, padding: '0.5rem', opacity: mode === 'json' ? 1 : 0.5, fontSize: '0.85rem' }} 
                    onClick={() => { setMode('json'); setError(null); setSuccess(null); }}
                >
                    JSON
                </button>
            </div>

            {mode === 'json' ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <textarea
                        rows="6"
                        placeholder={'{"database": "DB", "tables": []}'}
                        value={jsonInput}
                        onChange={(e) => setJsonInput(e.target.value)}
                        style={{ width: '100%', fontFamily: 'monospace' }}
                    />
                    <button onClick={handleJsonUpload}>Import JSON</button>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div className="file-input-wrapper">
                        <input 
                            id="file-input"
                            type="file" 
                            accept={mode === 'sql' ? ".sql" : ".csv"} 
                            onChange={(e) => setFileHandle(e.target.files[0])} 
                            style={{ 
                                padding: '10px', 
                                border: '1px dashed rgba(0,0,0,0.2)', 
                                borderRadius: '8px',
                                width: '100%',
                                boxSizing: 'border-box'
                            }}
                        />
                    </div>
                    <button onClick={() => handleFileUpload(mode === 'sql' ? '/api/schema/upload_sql' : '/api/schema/upload_csv')}>
                        Import {mode.toUpperCase()}
                    </button>
                </div>
            )}

            {error && <div style={{ color: '#e11d48', marginTop: '10px', fontSize: '0.9rem' }}><b>Error:</b> {error}</div>}
            {success && <div style={{ color: '#16a34a', marginTop: '10px', fontSize: '0.9rem' }}>{success}</div>}
        </div>
    );
}

export default SchemaUploader;
