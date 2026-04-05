# API Reference - Islamic AI Agent

The **Noor** Backend is a Flask Unified API providing a bridge between the React frontend and the AgentScope-based specialized agents.

## 🔑 Authentication & Headers
- **Base URL**: `http://localhost:5010` (default)
- **Headers**: `Content-Type: application/json`

---

## 💬 Core Chat Endpoints

### `POST /api/chat`
**Purpose**: Direct interaction with the **Noor** single-agent (IslamicAIAgent).
- **Request Body**:
    ```json
    { "message": "What is the virtue of Tahajjud?", "user_gender": "not_specified" }
    ```
- **Response**:
    ```json
    { "response": "Tahajjud is...", "timestamp": "...", "agent": "Noor" }
    ```

### `POST /api/multi-chat`
**Purpose**: Targeted scholar consultation (targeted Specialist).
- **Request Body**:
    ```json
    { "message": "Analyze this hadith reference...", "specialist": "Sheikha Aisha" }
    ```
- **Response**:
    ```json
    { "response": "Sheikha Aisha says...", "specialist": "Sheikha Aisha", "timestamp": "..." }
    ```

### `POST /api/collaborative`
**Purpose**: Full scholarly deliberation (multi-scholar synthesis).
- **Request Body**:
    ```json
    { "message": "What is the ruling on Zakat on cryptocurrencies?" }
    ```
- **Response**:
    ```json
    { "response": "Consultation Summary...", "timestamp": "...", "agent": "Imam Hassan (Coordinator)" }
    ```

---

## 🛠 Utility Endpoints

### `POST /api/prayer-times`
**Purpose**: Get GPS-accurate prayer times.
- **Request Body**:
    ```json
    { "latitude": 24.4686, "longitude": 39.6142 }
    ```

### `POST /api/qibla`
**Purpose**: Get Qibla bearing and direction.
- **Request Body**:
    ```json
    { "latitude": 24.4686, "longitude": 39.6142 }
    ```

### `POST /api/zakat/calculate`
**Purpose**: Precise Zakat calculation across multiple assets.
- **Request Body**:
    ```json
    { "cash": 5000, "gold_grams": 100, "investments": 2000, "debts": 500 }
    ```

---

## 📂 Knowledge Base Management

### `POST /api/knowledge/upload`
**Purpose**: Upload a PDF or TXT to the authentic digital library.
- **Form Data**: `file: (Binary)`

### `DELETE /api/knowledge/delete?filename=example.pdf`
**Purpose**: Remove a document from the local store.

---

> [!NOTE]
> All endpoints are CORS-enabled and support interactive development on the 3001 (React) port.
