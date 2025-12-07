### Python Backend Setup

1.  **Environment Setup:**
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

2.  **Environment Variables (`.env có sẵn trong repo`):**
    ```env
    PINECONE_API_KEY=your_key
    GOOGLE_API_KEY=your_gemini_key
    GEMINI_API_KEY=your_gemini_key
    ```

3.  **Run Server:**
    ```bash
    python -m app.main
    # Server: http://localhost:8000
    ```

### 📱 Flutter App Setup

1.  **Install & Run:**
    ```bash
    flutter pub get
    flutter run
    ```

2.  **Network Configuration:**
    *   Emulator: `http://10.0.2.2:8000`
    *   Physical Device: IP của máy đang chạy backend
