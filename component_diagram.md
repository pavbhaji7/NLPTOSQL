# Natural Language to SQL Component Architecture

This component architecture diagram integrates the structure of your existing rule-based NLP pipeline (from the local `frontend` and `gsql` Python codebase) with your requested Cloud implementation (Vercel, API Gateway, Cloud Functions with LangChain/LLM, and Database).

```mermaid
flowchart LR
    %% Styling
    classDef frontend fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef gateway fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef serverless fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef database fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;

    %% Client Layer
    subgraph FrontendLayer ["💻 React / Vercel"]
        direction TB
        UI_QueryInput["QueryInput.jsx"]
        UI_PipelineVisual["PipelineVisualizer.jsx"]
        UI_SQLResult["SQLResult.jsx"]
        UI_SchemaViewer["SchemaViewer.jsx"]

        UI_QueryInput --> UI_PipelineVisual --> UI_SQLResult
    end
    class FrontendLayer frontend;

    %% Routing
    APIGateway{"🚀 API Gateway"}
    class APIGateway gateway;

    %% Backend Layer
    subgraph BackendLayer ["⚡ Python Cloud Function"]
        direction TB
        LLM["LangChain / LLM Text-to-SQL"]
        
        subgraph Pipeline ["Structural Post-Processing"]
            direction TB
            NLP["NLP & Semantic Tagging"]
            Linker["Schema Mapping & Inference"]
            Generator["SQL Generation"]
            NLP --> Linker --> Generator
        end
        LLM -. "Fallback / Augmentation" .-> Pipeline
    end
    class BackendLayer serverless;

    %% Data Layer
    Database[("🗄️ Database\n(Schema & Data)")]
    class Database database;

    %% Connections
    FrontendLayer -- "1. NL Query" --> APIGateway
    APIGateway -- "2. Route Request" --> BackendLayer
    
    BackendLayer -- "3. Fetch Schema" --> Database
    Database -- "4. Return Schema" --> BackendLayer
    
    BackendLayer -- "5. Return Results" --> APIGateway
    APIGateway -- "6. Dispatch to UI" --> FrontendLayer

    style UI_QueryInput fill:#1e293b,stroke:#3b82f6
    style UI_SchemaViewer fill:#1e293b,stroke:#3b82f6
    style UI_PipelineVisual fill:#1e293b,stroke:#3b82f6
    style UI_SQLResult fill:#1e293b,stroke:#3b82f6
```

### Component Breakdown
1. **Frontend (React / Vercel)**: Inherits the architecture from your current `frontend/` folder. It uses `QueryInput` for capturing user sentences, `SchemaViewer` for depicting the database design, `PipelineVisualizer` to illustrate the NLP pipeline visually with color-coded chips, and `SQLResult` to show the final query. It is statically hosted on Vercel.
2. **API Gateway**: Serves as the networking router that securely captures HTTP requests from the React frontend and directs them to the backend serverless functions.
3. **Cloud Function (Python)**: Replaces the local FastAPI `server.py` setup. It uses the proposed **LangChain/LLM** approach to convert text to SQL, alongside the structured pipeline elements (Tokenization, Semantic Tagging, Schema Linking) to provide the necessary payload for the front end's visual token breakdown.
4. **Database**: The definitive target where tables and relationships reside, acting as the ground-truth for schema inferences and actual data querying.
