import React, { useState, useEffect } from 'react';

const SchemaViewer = () => {
    const [schema, setSchema] = useState(null);
    const [history, setHistory] = useState({ active: '', available: [] });

    useEffect(() => {
        fetchSchemaData();
        fetchHistoryData();
    }, []);

    const fetchSchemaData = () => {
        fetch('http://localhost:8000/api/schema')
            .then(res => res.json())
            .then(data => setSchema(data))
            .catch(err => console.error("Failed to fetch schema:", err));
    };

    const fetchHistoryData = () => {
        fetch('http://localhost:8000/api/schemas/history')
            .then(res => res.json())
            .then(data => setHistory(data))
            .catch(err => console.error("Failed to fetch history:", err));
    };

    const handleSwitchSchema = async (e) => {
        const selectedName = e.target.value;
        try {
            const res = await fetch('http://localhost:8000/api/schema/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: selectedName })
            });
            if (res.ok) {
                fetchSchemaData();
                fetchHistoryData();
            }
        } catch (err) {
            console.error("Failed to switch schema");
        }
    };

    if (!schema) return <div className="schema-loading">Loading Schema...</div>;

    return (
        <div className="schema-viewer">
            {history.available.length > 1 && (
                <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>
                        ACTIVE DATABASE
                    </label>
                    <select 
                        value={history.active} 
                        onChange={handleSwitchSchema}
                        style={{
                            width: '100%',
                            padding: '0.8rem',
                            borderRadius: '8px',
                            border: '1px solid var(--border-glass)',
                            background: 'rgba(255,255,255,0.8)',
                            fontSize: '1rem',
                            color: 'var(--text-primary)',
                            cursor: 'pointer'
                        }}
                    >
                        {history.available.map(dbName => (
                            <option key={dbName} value={dbName}>{dbName}</option>
                        ))}
                    </select>
                </div>
            )}

            {schema.tables.map(table => (
                <div key={table.name} className="schema-table">
                    <span className="schema-table-name">{table.name}</span>
                    <ul className="schema-columns">
                        {table.columns.map(col => (
                            <li key={col.name} className="schema-column">
                                {col.name}
                                <span className="col-type">({col.datatype})</span>
                                {col.is_pk && <span className="pk-badge">PK</span>}
                                {col.is_fk && <span className="fk-badge">FK</span>}
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
};

export default SchemaViewer;
