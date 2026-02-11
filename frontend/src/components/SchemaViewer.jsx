import React, { useState, useEffect } from 'react';

const SchemaViewer = () => {
    const [schema, setSchema] = useState(null);

    useEffect(() => {
        fetch('http://localhost:8000/api/schema')
            .then(res => res.json())
            .then(data => setSchema(data))
            .catch(err => console.error("Failed to fetch schema:", err));
    }, []);

    if (!schema) return <div className="schema-loading">Loading Schema...</div>;

    return (
        <div className="schema-viewer">
            <h2>Database Schema</h2>
            {schema.tables.map(table => (
                <div key={table.name} className="schema-table">
                    <span className="schema-table-name">{table.name}</span>
                    <ul className="schema-columns">
                        {table.columns.map(col => (
                            <li key={col.name} className="schema-column">
                                {col.name}
                                <span className="col-type">({col.type})</span>
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
