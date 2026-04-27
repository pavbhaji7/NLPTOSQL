# System Architecture Diagrams

*The following 8 diagrams outline the architectural evolution of the G-SQL project across its two core development sprints. These diagrams use the standard Mermaid `flowchart` and `sequenceDiagram` syntax, which ensures compatibility with GitHub and Mermaid Live.*

---

## 1. Sprint I: Core G-SQL Engine (Backend)

During Sprint I, development focused entirely on the Python backend, the deterministic NLP pipeline, and the REST API.

### 1.1 Backend Use Case Diagram
*Illustrates the functional capabilities exposed by the backend engine.*

```mermaid
flowchart LR
    actor Developer[["Developer / System Client"]]
    
    subgraph CoreEngine ["G-SQL Core Engine"]
        UC1(["Submit NLQ String"])
        UC2(["Parse & Lemmatize Tokens"])
        UC3(["Assign Semantic Tags"])
        UC4(["Infer Graph Joins (BFS)"])
        UC5(["Generate SQL Syntax"])
    end
    
    Developer --> UC1
    UC1 -. "includes" .-> UC2
    UC2 -. "includes" .-> UC3
    UC3 -. "includes" .-> UC4
    UC4 -. "includes" .-> UC5
```

### 1.2 Backend Sequence Diagram
*Traces the chronological execution path of a single query through the Python modules.*

```mermaid
sequenceDiagram
    participant API as server.py (FastAPI)
    participant NLP as nlp.py (spaCy)
    participant Tag as tagger.py
    participant Lnk as linker.py (Schema)
    participant Gen as generator.py
    
    API->>NLP: process("List actors in Titanic")
    activate NLP
    NLP-->>API: Return [Tokens, Lemmas, POS]
    deactivate NLP
    
    API->>Tag: tag(Tokens)
    activate Tag
    Tag-->>API: Return [Meta, Value, Cond]
    deactivate Tag
    
    API->>Lnk: link(Tagged_Tokens)
    activate Lnk
    Note over Lnk: Perform BFS Graph Search<br/>for Multi-Table Joins
    Lnk-->>API: Return Query_Structure (JSON)
    deactivate Lnk
    
    API->>Gen: generate(Query_Structure)
    activate Gen
    Gen-->>API: Return "SELECT name FROM..."
    deactivate Gen
    
    API-->>API: Format Final JSON Response
```

### 1.3 Backend Component Diagram
*Shows the structural relationships between the core Python modules.*

```mermaid
flowchart TD
    subgraph GSQL_Backend ["G-SQL Backend Subsystem"]
        Server["server.py (REST API)"]
        
        subgraph Lib ["gsql Library"]
            NLP["nlp.py"]
            Tagger["tagger.py"]
            Linker["linker.py"]
            Generator["generator.py"]
            Schema["schema.py"]
        end
        
        subgraph Dicts ["Dictionaries"]
            SynList[("Synonyms List")]
            AggList[("Aggregations List")]
        end
    end
    
    Server --> NLP
    Server --> Tagger
    Server --> Linker
    Server --> Generator
    
    Tagger -. "Lookup" .-> SynList
    Linker -. "Maps tags to DB schema" .-> Schema
```

### 1.4 Backend Deployment Diagram
*Illustrates the localized hosting environment for the Python application.*

```mermaid
flowchart TD
    subgraph LocalMachine ["Local Development Machine"]
        subgraph PythonEnv ["Python 3.8+ Environment"]
            SpacyModel[("spaCy en_core_web_sm")]
            
            subgraph Uvicorn ["Uvicorn ASGI Server"]
                FastAPI["FastAPI Application"]
            end
        end
    end
    
    Clients(("External Clients"))
    
    FastAPI -. "Loads in memory" .-> SpacyModel
    Clients -- "HTTP POST /api/translate (Port 8000)" --> FastAPI
```

---

## 2. Sprint II: Interactive Visualization Interface (Frontend)

During Sprint II, development shifted to decoupling the user interface from the backend, focusing on building a modern React dashboard to visualize the pipeline.

### 2.1 Frontend Use Case Diagram
*Illustrates what the end-user can accomplish within the React application.*

```mermaid
flowchart LR
    actor User[["End User"]]
    
    subgraph Dashboard ["React Dashboard"]
        V1(["View Database Schema"])
        V2(["Input Natural Language"])
        V3(["View Pipeline Chips"])
        V4(["Copy Generated SQL"])
    end
    
    User --> V1
    User --> V2
    User --> V3
    User --> V4
    
    V2 -. "Triggers" .-> V3
```

### 2.2 Frontend Sequence Diagram
*Traces the asynchronous communication between the React components and the Python API.*

```mermaid
sequenceDiagram
    actor User
    participant UI as React App (Main)
    participant Input as QueryInput.jsx
    participant Viz as PipelineVisualizer.jsx
    participant API as FastAPI Backend
    
    User->>Input: Types query & clicks "Translate"
    activate Input
    Input->>UI: handleQuerySubmit(text)
    deactivate Input
    
    activate UI
    UI->>API: HTTP POST /api/translate
    API-->>UI: JSON {sql, tokens, structure}
    
    UI->>Viz: Pass JSON tokens as props
    activate Viz
    Note over Viz: Render color-coded<br/>Meta & Value Chips
    Viz-->>User: Display Visual Pipeline
    deactivate Viz
    
    UI->>User: Render syntax-highlighted SQL
    deactivate UI
```

### 2.3 Frontend Component Diagram
*Breaks down the React component hierarchy.*

```mermaid
flowchart TD
    subgraph SPA ["Vite + React SPA"]
        App["App.jsx (Container)"]
        
        SchemaViewer["SchemaViewer.jsx"]
        QueryInput["QueryInput.jsx"]
        PipelineViz["PipelineVisualizer.jsx"]
        SQLResult["SQLResult.jsx"]
        
        CSS[("index.css (Stylesheet)")]
    end
    
    App --> SchemaViewer
    App --> QueryInput
    App --> PipelineViz
    App --> SQLResult
    
    PipelineViz -. "Applies Chip Colors" .-> CSS
```

### 2.4 Frontend Deployment Diagram
*Shows the dual-node interaction between the browser, the frontend server, and the backend engine.*

```mermaid
flowchart TD
    subgraph Device ["Client Device"]
        subgraph Browser ["Web Browser"]
            ClientApp["React SPA (Client-Side Rendered)"]
        end
    end
    
    subgraph DevServer ["Development Server"]
        subgraph NodeEnv ["Node.js Environment"]
            Vite["Vite Dev Server"]
        end
    end
    
    subgraph BackendServ ["Backend Server"]
        Backend["FastAPI Engine (Port 8000)"]
    end
    
    ClientApp -- "Fetches static assets (JS/CSS)" --> Vite
    ClientApp -- "AJAX / Fetch API (CORS enabled)" --> Backend
```
