# Perceive Search 🚀

**Privacy-respecting metasearch engine with integrated AI summaries powered by local open-source LLMs.**

Perceive Search proxies Google/Bing results (ad/tracker-free) + generates concise AI insights for queries. Fully self-hosted, lightweight, and offline-capable after setup.

![ezgif-78d8fa326aab7b0c](https://github.com/user-attachments/assets/0bcfa42f-1a8d-4534-90d3-9dcb52d85c75)

## How It's Done

This project is built by forking the original [Whoogle Search](https://github.com/benbusby/whoogle-search) code and enhancing it with modern AI capabilities. I kept the privacy-focused core of Whoogle but added a lightweight open-source Large Language Model (LLM) **Qwen2.5-0.5B-Instruct**.

### How It Works

1.  **Search Proxy**: When you search, the backend (Python/Flask) fetches results from Google without passing your personal data (IP, cookies, etc.).
2.  **AI Summarization**: The top search results are fed into the local Qwen2.5 model running on your CPU. The model reads the snippets and generates a concise answer to your query.
3.  **Modern UI**: A custom React frontend displays the results and the AI summary in a clean, "Perceive" themed interface.

<img width="1723" height="1060" alt="image" src="https://github.com/user-attachments/assets/7f5d8bf8-c3e5-4212-80f5-308ef9d5aebb" />

## Installation

Follow these steps to set up Perceive Search on your own system.

### Prerequisites

*   **Python**
*   **Node.js & npm**

### 1. Clone the Repository

First, download the code to your machine:

```bash
git clone git clone https://github.com/yourusername/perceive-search.git
cd perceive-search
```

### 2. Backend Setup

Set up the Python backend and download the AI model.

```bash
cd backend

# Install required Python libraries
pip install -r requirements.txt

# Download the AI model (Qwen2.5-0.5B-Instruct)
# This saves the model locally so it runs offline later. This is a lightweight model that runs on most CPUs as well.
python3 download_model.py

# Return to root
cd ..
```

### 3. Frontend Setup

Install the dependencies for the user interface.

```bash
cd frontend

# Install Node.js packages
npm install

# Return to root
cd ..
```

### 4. Run Perceive Search

I have included a simple script to start everything at once.

```bash
# Make the script executable (only needed once)
chmod +x start.sh

# Start the application
./start.sh
```

You will see output indicating that the backend (port 5001) and frontend (port 5173) are starting.

Open your browser to: **http://localhost:5173**

## Features

*   **Privacy First**: No ads, no tracking, no cookies, no IP logging.
*   **AI Powered**: Instant summaries for your queries using a local LLM.
*   **Lightweight**: Runs efficiently on standard CPUs (no GPU required).
*   **Modern Design**: A beautiful, dark-themed interface with 3D elements and smooth animations.
*   **Self-Hosted**: You own the data and the infrastructure.

## Credits & License

This project is **inspired by and enhanced from [Whoogle Search](https://github.com/benbusby/whoogle-search) by Ben Busby**.

*   **Original Author**: Ben Busby
*   **Original License**: [MIT License] © 2020 Ben Busby
*   **My Enhancements**: LLM integration (Qwen2.5-0.5B-Instruct) Frontend (React) Backend (Python/Flask)
*   **My License**: [MIT License] © 2025 Vikram Lingam 
