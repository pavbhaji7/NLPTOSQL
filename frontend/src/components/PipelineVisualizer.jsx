import React from 'react';

const PipelineVisualizer = ({ data }) => {
    if (!data) return null;

    return (
        <div className="pipeline-visualizer">
            <div className="pipeline-step">
                <h3>1. NLP & Tagging</h3>
                <div className="tokens-container">
                    {data.tokens.map((token, index) => {
                        let className = "token-chip";
                        if (token.gsql_tag === "Meta") className += " meta";
                        if (token.gsql_tag === "Value") className += " value";

                        return (
                            <div key={index} className={className}>
                                <span className="token-text">{token.text}</span>
                                <span className="token-tag">{token.gsql_tag}</span>
                                {token.meta_match && (
                                    <span className="token-meta-detail">
                                        {token.meta_match.type === 'column'
                                            ? `${token.meta_match.table}.${token.meta_match.name}`
                                            : token.meta_match.name}
                                    </span>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="pipeline-step">
                <h3>2. Logic & Linking</h3>
                <p><strong>Intent:</strong> Select {data.query_structure.select.join(", ") || "*"}</p>
                <p><strong>From:</strong> {data.query_structure.from.join(", ")}</p>
                {data.query_structure.where.length > 0 && (
                    <p><strong>Conditions:</strong> {data.query_structure.where.join(" AND ")}</p>
                )}
                {data.query_structure.joins.length > 0 && (
                    <div className="joins-list">
                        <strong>Joins Inferred:</strong>
                        <ul>
                            {data.query_structure.joins.map((join, i) => (
                                <li key={i}>{join}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PipelineVisualizer;
