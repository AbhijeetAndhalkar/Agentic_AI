# ChatBot Project Setup & Run Instructions

## Prerequisites
1.  **Python 3.11**: Ensure Python 3.11 is installed and available as `py -3.11` or `python`.
2.  **API Keys**: You need API keys for:
    *   **Groq** (LLM inference)
    *   **Pinecone** (Vector Database)
    *   **Gmail App Password** (For sending emails)

## Installation

1.  **Create Virtual Environment**
    Open a terminal in the project directory and run:
    ```bash
    py -3.11 -m venv .venv
    ```

2.  **Activate Environment**
    *   Windows:
        ```bash
        .\.venv\Scripts\activate
        ```
    *   Mac/Linux:
        ```bash
        source .venv/bin/activate
        ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Environment Variables**
    Open the `.env` file and fill in your details:
    ```ini
    GROQ_API_KEY=your_groq_api_key
    PINECONE_API_KEY=your_pinecone_api_key
    PINECONE_ENV=your_pinecone_environment (e.g., us-east-1)
    PINECONE_INDEX_NAME=chatbot
    EMAIL_USER=your-email@gmail.com
    EMAIL_PASS=your-app-password
    ```

2.  **Data Source**
    Create a file named `linkcode.txt` in the project root.
    Add the text content you want the chatbot to know about, one sentence/paragraph per line.
    Example `linkcode.txt`:
    ```text
    EduPro LMS is a leading learning platform.
    We offer courses in Python, Data Science, and Machine Learning.
    Contact support at support@edupro.com.
    ```

## Running the Project

1.  **Ingest Data** (Populate the database)
    Run this once or whenever you update `linkcode.txt`:
    ```bash
    python ingest.py
    ```

2.  **Start the Server**
    ```bash
    python app.py
    ```

3.  **Access the Application**
    Open your browser and navigate to:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Troubleshooting
*   **Import Errors**: Ensure you have activated the virtual environment (`.\.venv\Scripts\activate`) before running python commands.
*   **Ingestion Issues**: Check `linkcode.txt` exists and has content. specific errors might be printed to the console.
