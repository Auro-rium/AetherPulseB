from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Create FastAPI app
app = FastAPI(
    title="AetherPulseB API",
    description="Reddit Data Analysis and Streaming API with NLP Processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AetherPulseB - Reddit Data Analysis</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-800 mb-2">AetherPulseB</h1>
                <p class="text-gray-600">Reddit Data Analysis & NLP Processing Platform</p>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Server Status</h2>
                <p class="text-green-600 text-lg">✅ FastAPI Server is Running!</p>
                <p class="text-gray-600 mt-2">The server started successfully without loading NLP models.</p>
            </div>
            
            <div class="mt-8 text-center">
                <p class="text-gray-600 mb-2">API Documentation:</p>
                <a href="/docs" class="text-blue-500 hover:text-blue-600 mr-4">Swagger UI</a>
                <a href="/redoc" class="text-blue-500 hover:text-blue-600">ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "AetherPulseB API", "message": "Server running without NLP models"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080) 