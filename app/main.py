from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pathlib import Path

from app.api.endpoints import query, stream

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

# Include API routers
app.include_router(query.router, prefix="/api/v1")
app.include_router(stream.router, prefix="/api/v1")

# Create static files directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AetherPulseB - Reddit Data Analysis</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-800 mb-2">AetherPulseB</h1>
                <p class="text-gray-600">Reddit Data Analysis & NLP Processing Platform</p>
            </div>

            <!-- System Status -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">System Status</h3>
                    <div id="systemStatus" class="text-2xl font-bold text-green-600">Loading...</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Total Posts</h3>
                    <div id="totalPosts" class="text-2xl font-bold text-blue-600">-</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Total Comments</h3>
                    <div id="totalComments" class="text-2xl font-bold text-purple-600">-</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Subreddits</h3>
                    <div id="subredditsCount" class="text-2xl font-bold text-orange-600">-</div>
                </div>
            </div>

            <!-- Controls -->
            <div class="bg-white rounded-lg shadow p-6 mb-8">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Controls</h2>
                <div class="flex flex-wrap gap-4">
                    <button onclick="startStreaming()" class="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg">
                        Start Streaming
                    </button>
                    <button onclick="getStats()" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg">
                        Refresh Stats
                    </button>
                    <button onclick="getAnalytics()" class="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg">
                        Get Analytics
                    </button>
                    <input type="text" id="subredditInput" placeholder="Enter subreddit name" class="border border-gray-300 px-4 py-2 rounded-lg">
                    <button onclick="fetchSubreddit()" class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg">
                        Fetch Subreddit
                    </button>
                </div>
            </div>

            <!-- Recent Data -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Recent Data</h2>
                <div class="overflow-x-auto">
                    <table class="min-w-full table-auto">
                        <thead>
                            <tr class="bg-gray-50">
                                <th class="px-4 py-2 text-left">Type</th>
                                <th class="px-4 py-2 text-left">Subreddit</th>
                                <th class="px-4 py-2 text-left">Author</th>
                                <th class="px-4 py-2 text-left">Content</th>
                                <th class="px-4 py-2 text-left">Score</th>
                            </tr>
                        </thead>
                        <tbody id="recentData">
                            <tr>
                                <td colspan="5" class="px-4 py-2 text-center text-gray-500">Loading recent data...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- API Links -->
            <div class="mt-8 text-center">
                <p class="text-gray-600 mb-2">API Documentation:</p>
                <a href="/docs" class="text-blue-500 hover:text-blue-600 mr-4">Swagger UI</a>
                <a href="/redoc" class="text-blue-500 hover:text-blue-600">ReDoc</a>
            </div>
        </div>

        <script>
            const API_BASE = '/api/v1';

            document.addEventListener('DOMContentLoaded', function() {
                getStats();
                getRecentData();
                
                setInterval(() => {
                    getStats();
                    getRecentData();
                }, 30000);
            });

            async function getStats() {
                try {
                    const response = await axios.get(`${API_BASE}/stats`);
                    const stats = response.data;
                    
                    document.getElementById('totalPosts').textContent = stats.total_posts.toLocaleString();
                    document.getElementById('totalComments').textContent = stats.total_comments.toLocaleString();
                    document.getElementById('subredditsCount').textContent = stats.subreddits_count;
                    document.getElementById('systemStatus').textContent = 'Operational';
                    document.getElementById('systemStatus').className = 'text-2xl font-bold text-green-600';
                } catch (error) {
                    console.error('Error fetching stats:', error);
                    document.getElementById('systemStatus').textContent = 'Error';
                    document.getElementById('systemStatus').className = 'text-2xl font-bold text-red-600';
                }
            }

            async function startStreaming() {
                try {
                    const response = await axios.post(`${API_BASE}/stream/start`);
                    alert('Streaming started successfully!');
                    getStats();
                } catch (error) {
                    console.error('Error starting streaming:', error);
                    alert('Failed to start streaming: ' + error.response?.data?.message || error.message);
                }
            }

            async function fetchSubreddit() {
                const subreddit = document.getElementById('subredditInput').value.trim();
                if (!subreddit) {
                    alert('Please enter a subreddit name');
                    return;
                }

                try {
                    const response = await axios.post(`${API_BASE}/stream/fetch?subreddit=${subreddit}`);
                    alert(`Successfully fetched data from r/${subreddit}!`);
                    getStats();
                    getRecentData();
                } catch (error) {
                    console.error('Error fetching subreddit:', error);
                    alert('Failed to fetch subreddit: ' + error.response?.data?.message || error.message);
                }
            }

            async function getAnalytics() {
                try {
                    const response = await axios.get(`${API_BASE}/stream/analytics`);
                    const analytics = response.data.data;
                    console.log('Analytics:', analytics);
                    alert('Analytics retrieved! Check console for details.');
                } catch (error) {
                    console.error('Error getting analytics:', error);
                    alert('Failed to get analytics: ' + error.response?.data?.message || error.message);
                }
            }

            async function getRecentData() {
                try {
                    const response = await axios.get(`${API_BASE}/recent?limit=10`);
                    const data = response.data;
                    
                    const tbody = document.getElementById('recentData');
                    tbody.innerHTML = '';
                    
                    data.forEach(item => {
                        const row = document.createElement('tr');
                        row.className = 'border-b';
                        
                        const content = item.title ? 
                            (item.title + (item.body ? ' - ' + item.body.substring(0, 50) + '...' : '')) :
                            (item.body ? item.body.substring(0, 100) + '...' : 'No content');
                        
                        row.innerHTML = `
                            <td class="px-4 py-2">
                                <span class="px-2 py-1 rounded text-xs ${item.type === 'post' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}">
                                    ${item.type}
                                </span>
                            </td>
                            <td class="px-4 py-2">r/${item.subreddit}</td>
                            <td class="px-4 py-2">${item.author}</td>
                            <td class="px-4 py-2">${content}</td>
                            <td class="px-4 py-2">${item.score}</td>
                        `;
                        
                        tbody.appendChild(row);
                    });
                } catch (error) {
                    console.error('Error fetching recent data:', error);
                    document.getElementById('recentData').innerHTML = 
                        '<tr><td colspan="5" class="px-4 py-2 text-center text-red-500">Error loading recent data</td></tr>';
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "AetherPulseB API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
