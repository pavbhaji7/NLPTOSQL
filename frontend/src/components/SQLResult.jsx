import React from 'react';

const SQLResult = ({ sql }) => {
    if (!sql) return null;

    const copyToClipboard = () => {
        navigator.clipboard.writeText(sql);
    };

    return (
        <div className="sql-result-wrapper">
            <h3>Generated SQL</h3>
            <div className="sql-result-container">
                <button className="copy-button" onClick={copyToClipboard}>Copy</button>
                <pre className="sql-code">{sql}</pre>
            </div>
        </div>
    );
};

export default SQLResult;
