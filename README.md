# Academic PDF Q&A Service

## Setup Instructions

1. In the `.env` file in the root directory and add:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

3. Start the server:
   ```
   uvicorn app.main:app
   ```