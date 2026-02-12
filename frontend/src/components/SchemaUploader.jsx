import React, { useState } from 'react';

function SchemaUploader({ onSchemaUpdate }) {
    const [jsonInput, setJsonInput] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleUpload = async () => {
        setError(null);
        setSuccess(null);
        try {
            const schemaData = JSON.parse(jsonInput);

            const response = await fetch('http://localhost:8000/api/schema/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(schemaData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update schema');
            }

            setSuccess('Schema updated successfully!');
            if (onSchemaUpdate) {
                onSchemaUpdate();
            }
        } catch (err) {
            if (err instanceof SyntaxError) {
                setError('Invalid JSON format');
            } else {
                setError(err.message);
            }
        }
    };

    return (
        <div className="schema-uploader">
            <h3>Upload Custom Schema</h3>
            <textarea
                rows="10"
                placeholder={`Paste your Database Schema JSON here...
Example:
{
  "database": "MyDB",
  "tables": [
    {
      "name": "Users",
      "columns": [
        { "name": "id", "datatype": "int", "is_pk": true },
        { "name": "username", "datatype": "text" }
      ]
    }
  ]
}`}
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                style={{ width: '100%', fontFamily: 'monospace' }}
            />
            <button onClick={handleUpload} style={{ marginTop: '10px' }}>
                Load Schema
            </button>
            {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
            {success && <div style={{ color: 'green', marginTop: '10px' }}>{success}</div>}
        </div>
    );
}

export default SchemaUploader;
