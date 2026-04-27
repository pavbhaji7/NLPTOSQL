# System Architecture Diagrams

*The following 8 diagrams outline the architectural evolution of the G-SQL project across its two core development sprints. These diagrams use standard Mermaid syntax but are heavily styled for premium, publication-ready rendering on GitHub.*

---

## 1. Sprint I: Core G-SQL Engine (Backend)

### 1.1 Backend Use Case Diagram

```mermaid
graph LR
    classDef actor fill:#1e293b,stroke:#fff,stroke-width:2px,color:#fff,shape:circle;
    classDef usecase fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff,shape:pill;
    classDef sys fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px,stroke-dasharray: 5 5;

    Dev(("👤 Developer")):::actor
    
    subgraph "G-SQL Core Engine"
        direction TB
        UC1(["Submit NLQ String"]):::usecase
        UC2(["Parse & Lemmatize Tokens"]):::usecase
        UC3(["Assign Semantic Tags"]):::usecase
        UC4(["Infer Graph Joins (BFS)"]):::usecase
        UC5(["Generate SQL Syntax"]):::usecase
    end
    
    Dev --> UC1
    UC1 -. "<< includes >>" .-> UC2
    UC2 -. "<< includes >>" .-> UC3
    UC3 -. "<< includes >>" .-> UC4
    UC4 -. "<< includes >>" .-> UC5
    
    class "G-SQL Core Engine" sys;
```

### 1.2 Backend Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant API as 🌐 server.py (FastAPI)
    participant NLP as 🧠 nlp.py (spaCy)
    participant Tag as 🏷️ tagger.py
    participant Lnk as 🔗 linker.py (BFS)
    participant Gen as ⚙️ generator.py
    
    API->>NLP: process("List actors in Titanic")
    activate NLP
    Note right of NLP: Tokenize, Lemmatize, POS
    NLP-->>API: Return [Tokens, Lemmas, POS]
    deactivate NLP
    
    API->>Tag: tag(Tokens)
    activate Tag
    Tag-->>API: Return [Meta, Value, Cond]
    deactivate Tag
    
    API->>Lnk: link(Tagged_Tokens)
    activate Lnk
    Note over Lnk: Execute Graph BFS<br/>Map to DB Schema
    Lnk-->>API: Return Query_Structure (JSON)
    deactivate Lnk
    
    API->>Gen: generate(Query_Structure)
    activate Gen
    Gen-->>API: Return "SELECT name FROM..."
    deactivate Gen
    
    Note left of API: Format Final JSON Response
```

### 1.3 Backend Component Diagram

```mermaid
graph TD
    classDef module fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef db fill:#475569,stroke:#fff,stroke-width:2px,color:#fff,shape:cylinder;
    classDef api fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff;

    subgraph "G-SQL Backend Architecture"
        Server["🌐 server.py (REST API)"]:::api
        
        subgraph "Core Library (gsql/)"
            NLP["nlp.py"]:::module
            Tagger["tagger.py"]:::module
            Linker["linker.py"]:::module
            Generator["generator.py"]:::module
            Schema["schema.py"]:::module
        end
        
        subgraph "Data Dictionaries"
            SynList[("Synonyms Map")]:::db
            AggList[("Aggregations Map")]:::db
        end
    end
    
    Server ==> NLP & Tagger & Linker & Generator
    Tagger -. "Dictionary Lookup" .-> SynList & AggList
    Linker -. "Validates against" .-> Schema
```

### 1.4 Backend Deployment Diagram

```mermaid
graph TD
    classDef hardware fill:#e2e8f0,stroke:#64748b,stroke-width:2px;
    classDef software fill:#334155,stroke:#fff,stroke-width:2px,color:#fff;
    classDef external fill:#f59e0b,stroke:#fff,stroke-width:2px,color:#fff,shape:circle;

    Clients(("🌐 HTTP Clients")):::external

    subgraph "Local Development Machine"
        subgraph "Python 3.8+ Virtual Environment"
            Spacy[("spaCy en_core_web_sm")]:::software
            
            subgraph "Uvicorn ASGI Server"
                FastAPI["FastAPI Engine (Port 8000)"]:::software
            end
        end
    end
    
    Clients == "POST /api/translate" ==> FastAPI
    FastAPI -. "Loads Model into RAM" .-> Spacy
    
    class "Local Development Machine" hardware;
    class "Python 3.8+ Virtual Environment" hardware;
```

---

## 2. Sprint II: Interactive Visualization Interface (Frontend)

### 2.1 Frontend Use Case Diagram

```mermaid
graph LR
    classDef actor fill:#1e293b,stroke:#fff,stroke-width:2px,color:#fff,shape:circle;
    classDef usecase fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff,shape:pill;

    User(("👤 End User")):::actor
    
    subgraph "React Dashboard Interface"
        direction TB
        V1(["View Database Schema"]):::usecase
        V2(["Input Natural Language Query"]):::usecase
        V3(["Audit Pipeline Visual Chips"]):::usecase
        V4(["Copy Generated SQL"]):::usecase
    end
    
    User --> V1 & V2 & V3 & V4
    V2 -. "<< triggers >>" .-> V3
```

### 2.2 Frontend Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 End User
    participant App as ⚛️ App.jsx
    participant Input as ⌨️ QueryInput.jsx
    participant Viz as 🎨 PipelineVisualizer.jsx
    participant API as 🌐 FastAPI Backend
    
    User->>Input: Types query & clicks "Translate"
    activate Input
    Input->>App: handleQuerySubmit(text)
    deactivate Input
    
    activate App
    App->>API: HTTP POST /api/translate
    API-->>App: JSON {sql, tokens, structure}
    
    App->>Viz: Pass JSON tokens as props
    activate Viz
    Note over Viz: Render color-coded<br/>Meta & Value Chips
    Viz-->>User: Display Interactive Pipeline
    deactivate Viz
    
    App->>User: Render syntax-highlighted SQL
    deactivate App
```

### 2.3 Frontend Component Diagram

```mermaid
graph TD
    classDef comp fill:#61dafb,stroke:#000,stroke-width:2px,color:#000;
    classDef css fill:#f472b6,stroke:#fff,stroke-width:2px,color:#fff;

    subgraph "Vite + React Single Page Application"
        App["App.jsx (Main Container)"]:::comp
        
        SchemaViewer["SchemaViewer.jsx"]:::comp
        QueryInput["QueryInput.jsx"]:::comp
        PipelineViz["PipelineVisualizer.jsx"]:::comp
        SQLResult["SQLResult.jsx"]:::comp
        
        CSS["🎨 index.css (Global Styles)"]:::css
    end
    
    App ==> SchemaViewer & QueryInput & PipelineViz & SQLResult
    PipelineViz -. "Imports custom chip classes" .-> CSS
```

### 2.4 Frontend Deployment Diagram

```mermaid
graph TD
    classDef client fill:#f8fafc,stroke:#94a3b8,stroke-width:2px;
    classDef server fill:#1e293b,stroke:#fff,stroke-width:2px,color:#fff;
    classDef backend fill:#059669,stroke:#fff,stroke-width:2px,color:#fff;

    subgraph "Client Device"
        Browser["🌐 Web Browser (Chrome/Firefox)"]:::client
        SPA["⚛️ React App (Client-Side)"]:::client
        Browser --- SPA
    end
    
    subgraph "Local Development Node"
        Vite["📦 Vite Dev Server (Port 5173)"]:::server
    end
    
    subgraph "Backend Node"
        FastAPI["🐍 FastAPI Engine (Port 8000)"]:::backend
    end
    
    Browser == "Fetches JS/CSS payload" ==> Vite
    SPA == "AJAX Fetch (CORS Enabled)" ==> FastAPI
```
