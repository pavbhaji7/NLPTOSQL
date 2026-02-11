import React, { useState } from 'react';
import SchemaViewer from './components/SchemaViewer';
import QueryInput from './components/QueryInput';
import PipelineVisualizer from './components/PipelineVisualizer';
import SQLResult from './components/SQLResult';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (query) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Failed to translate query. Please ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <SchemaViewer />
      </div>

      <main className="main-content">
        <header>
          <h1>G-SQL Interface</h1>
          <p className="subtitle">Rule-Guided Natural Language to SQL Translation</p>
        </header>

        <QueryInput onSearch={handleSearch} isLoading={loading} />

        {error && <div className="error-message" style={{ color: '#ff4d4f' }}>{error}</div>}

        {result && (
          <>
            <PipelineVisualizer data={result} />
            <SQLResult sql={result.sql} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
