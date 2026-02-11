import React, { useState } from 'react';

const QueryInput = ({ onSearch, isLoading }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <div className="query-input-container">
            <form onSubmit={handleSubmit}>
                <textarea
                    className="query-input"
                    placeholder="Ask a question in natural language (e.g., 'Show me movies released after 2000')"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isLoading}
                />
                <button type="submit" className="query-button" disabled={isLoading || !query.trim()}>
                    {isLoading ? 'Translating...' : 'Translate to SQL'}
                </button>
            </form>
        </div>
    );
};

export default QueryInput;
