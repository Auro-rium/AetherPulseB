
# AetherPulseB Documentation

## Overview

**AetherPulseB** is a Reddit Data Analysis & NLP Processing Platform, built to stream, analyze, and present Reddit data in real-time. The platform combines data acquisition from Reddit with natural language processing capabilities, all exposed via a modern FastAPI backend and a responsive web interface.

---

## Main Features

- **Reddit Streaming**: Continuously fetches posts and comments from specified subreddits.
- **Data Storage**: Organizes and stores Reddit data in a MongoDB database.
- **NLP Processing**: Performs natural language analysis (such as emotion detection) on Reddit content.
- **Web Dashboard**: User-friendly dashboard with system status, controls, and analytics.
- **REST API**: Exposes endpoints for streaming control, analytics, and direct data access.

---

## Architecture

### Key Components

- **FastAPI App (`app/main.py`, `app/main_simple.py`)**
  - Launches the backend server.
  - Serves both the API and the main web interface.
  - Includes health checks and API documentation endpoints.

- **Routers (`app/api/endpoints/`)**
  - `query.py`: Handles data querying endpoints.
  - `stream.py`: Controls data streaming, analytics, and subreddit fetching.
  - `user.py`: User-related endpoints.

- **Web Interface**
  - Provides a status dashboard, controls for starting/stopping streams, and displays recent Reddit data.
  - Built using TailwindCSS for styling and Axios for API interaction.

- **Setup Script (`setup.py`)**
  - Guides users through environment setup.
  - Checks Python dependencies.
  - Creates a `.env` with Reddit API credentials template.
  - Validates configuration before server launch.

- **Database**
  - Uses MongoDB to store and aggregate Reddit data and analytics.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Auro-rium/AetherPulseB
cd AetherPulseB
```

### 2. Install Python Dependencies

A recommended way is to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Setup Script

```bash
python setup.py
```

- This will prompt you to fill in Reddit API credentials in the generated `.env` file.
- Credentials can be obtained from: https://www.reddit.com/prefs/apps

### 4. Start the Server

```bash
python -m app.main
# or for the simple version:
python -m app.main_simple
```

The server will be available at [http://localhost:8080](http://localhost:8080).

---

## Usage

### Main Web Dashboard

- Visit `/` to access the dashboard.
- System status, total posts/comments, and subreddit count are displayed.
- Controls allow you to:
  - Start streaming Reddit data
  - Fetch specific subreddits
  - Get analytics (recent activity, top subreddits, emotion distribution)
  - View recent data entries in tabular form

### API Endpoints

- API is versioned under `/api/v1`
- **Key Endpoints:**
  - `/api/v1/stream/start` — Start streaming Reddit data
  - `/api/v1/stream/fetch?subreddit={name}` — Fetch data from a specific subreddit
  - `/api/v1/stream/analytics` — Retrieve analytics (activity stats, top subreddits, emotion distribution)
  - `/api/v1/query` — Query stored Reddit data
  - `/health` — Health check endpoint

- **API Documentation:**
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`

### Example: Fetching Analytics

```bash
curl http://localhost:8080/api/v1/stream/analytics
```

---

## Core Code Structure

```
AetherPulseB/
├── app/
│   ├── main.py            # Main FastAPI app with web dashboard
│   ├── main_simple.py     # Lightweight FastAPI app (no NLP models)
│   └── api/
│        └── endpoints/
│             ├── stream.py   # Streaming and analytics endpoints
│             ├── query.py    # Data query endpoints
│             └── user.py     # User endpoints
├── requirements.txt
├── setup.py             # Interactive setup script
└── .env                 # Reddit API credentials (user-generated)
```

---

## Additional Notes

- **Customization**: You can modify which subreddits are streamed and how NLP analysis is performed by editing endpoint logic in `stream.py`.
- **Extending Functionality**: Add new endpoints by placing additional routers in `app/api/endpoints/`.
- **Security**: Be sure to keep your `.env` file secure and never expose your Reddit API secrets.

---

## Troubleshooting

- If the server won’t start, ensure all dependencies are installed and `.env` is properly set.
- Use `/health` endpoint for a quick check of server status.
- Refer to API docs at `/docs` or `/redoc` for endpoint details.

---

## License

Currently, no license is specified. Add a `LICENSE` file to clarify usage and contributions.

---

## Author

Developed by [Auro-rium](https://github.com/Auro-rium)
