#!/usr/bin/env python3
"""
Whoogle Search - NiceGUI Interface 
A modern, custom GUI wrapper for Whoogle Search using NiceGUI built on Whoogle by Vikram Lingam
"""

import subprocess
import time
import atexit
import httpx
from bs4 import BeautifulSoup
from nicegui import ui, app
import asyncio
from typing import Optional

# Configuration
WHOOGLE_PORT = 5001
WHOOGLE_URL = f"http://localhost:{WHOOGLE_PORT}"
GUI_PORT = 8080

# Global process holder
whoogle_process: Optional[subprocess.Popen] = None


def start_whoogle_backend():
    """Start the Whoogle backend server as a subprocess"""
    global whoogle_process
    
    if whoogle_process is not None:
        return
    
    try:
        # Start Whoogle server
        whoogle_process = subprocess.Popen(
            ['python3', '-um', 'app', '--host', '0.0.0.0', '--port', str(WHOOGLE_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='/Users/vikramlingam/Desktop/Whoogle_AI'
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = httpx.get(WHOOGLE_URL, timeout=5)
            if response.status_code == 200:
                print(f"✅ Whoogle backend started successfully on port {WHOOGLE_PORT}")
        except Exception as e:
            print(f"⚠️ Whoogle backend may not be ready: {e}")
            
    except Exception as e:
        print(f"❌ Failed to start Whoogle backend: {e}")


def stop_whoogle_backend():
    """Stop the Whoogle backend server"""
    global whoogle_process
    
    if whoogle_process:
        whoogle_process.terminate()
        try:
            whoogle_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            whoogle_process.kill()
        print("🛑 Whoogle backend stopped")


async def perform_search(query: str):
    """Perform a search using the Whoogle backend"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{WHOOGLE_URL}/search",
                params={'q': query},
                follow_redirects=True
            )
            
            if response.status_code == 200:
                return parse_search_results(response.text)
            else:
                return [{"error": f"Search failed with status code: {response.status_code}"}]
                
    except Exception as e:
        return [{"error": f"Search error: {str(e)}"}]


def parse_search_results(html: str):
    """Parse search results from Whoogle HTML response"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # Try finding results with the observed structure (ZINbbc class)
    # This is common in Whoogle/Google mobile views
    result_divs = soup.find_all('div', class_='ZINbbc')
    
    if not result_divs:
        # Fallback to 'result' class if ZINbbc not found (older versions/themes)
        result_divs = soup.find_all('div', class_='result')
    
    for div in result_divs:
        try:
            # Look for the link
            # The structure often is: div.ZINbbc -> div.kCrYT -> a
            link_elem = div.find('a')
            if not link_elem:
                continue
                
            # Check if it has a title (h3)
            title_elem = link_elem.find('h3')
            if not title_elem:
                # Try finding h3 anywhere in the div
                title_elem = div.find('h3')
                if not title_elem:
                    continue
            
            title = title_elem.get_text(strip=True)
            link = link_elem.get('href', '')
            
            # Clean up link if it's a google redirect
            if link.startswith('/url?q='):
                link = link.split('/url?q=')[1].split('&')[0]
            
            # Extract snippet
            # Try to find the snippet container (usually the second kCrYT div)
            snippet = ""
            inner_divs = div.find_all('div', class_='kCrYT')
            if len(inner_divs) >= 2:
                snippet_div = inner_divs[1]
                snippet = snippet_div.get_text(strip=True)
            else:
                # Fallback: get all text and remove title
                full_text = div.get_text(strip=True)
                snippet = full_text.replace(title, "").strip()
            
            # Extract displayed URL
            display_url = link
            
            # Avoid duplicates or empty results
            if not title or not link:
                continue
                
            results.append({
                'title': title,
                'link': link,
                'snippet': snippet[:300] + "..." if len(snippet) > 300 else snippet,
                'display_url': display_url
            })
        except Exception as e:
            print(f"Error parsing result: {e}")
            continue
    
    return results if results else [{"error": "No results found"}]


# Create the NiceGUI interface
@ui.page('/')
async def main_page():
    """Main search interface"""
    
    # State
    search_results = []
    
    # Custom CSS for modern styling
    ui.add_head_html('''
        <style>
            .search-container {
                max-width: 800px;
                margin: 0 auto;
                width: 100%;
            }
            .result-card {
                background: white;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: box-shadow 0.2s;
            }
            .result-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .result-title {
                color: #1a0dab;
                font-size: 20px;
                font-weight: 400;
                margin-bottom: 4px;
            }
            .result-url {
                color: #006621;
                font-size: 14px;
                margin-bottom: 8px;
            }
            .result-snippet {
                color: #545454;
                font-size: 14px;
                line-height: 1.5;
            }
        </style>
    ''')
    
    # Main container - centered vertically and horizontally
    with ui.column().classes('w-full min-h-screen items-center justify-center p-4'):
        
        # Header/Title
        ui.label('Perceive').classes('text-6xl font-bold text-gray-800 mb-8')
        
        # Search container
        with ui.column().classes('search-container'):
            # Search input
            search_input = ui.input(
                placeholder='Search...',
                validation={'Too short': lambda value: len(value) >= 2}
            ).classes('w-full text-lg').props('outlined rounded')
            
            # Loading indicator
            loading = ui.spinner('dots', size='lg', color='gray')
            loading.visible = False
            
            # Results container
            results_container = ui.column().classes('w-full mt-8')
            
            async def handle_search():
                """Handle search button click"""
                query = search_input.value
                
                if not query or len(query) < 2:
                    ui.notify('Please enter a search query', type='warning')
                    return
                
                # Show loading
                loading.visible = True
                results_container.clear()
                
                # Perform search
                results = await perform_search(query)
                
                # Hide loading
                loading.visible = False
                
                # Display results
                with results_container:
                    if results and 'error' in results[0]:
                        ui.label(results[0]['error']).classes('text-red-500 text-lg')
                    elif results:
                        ui.label(f'Found {len(results)} results').classes('text-gray-600 mb-4')
                        
                        for result in results:
                            with ui.card().classes('result-card w-full'):
                                # Title (clickable)
                                ui.link(
                                    result['title'],
                                    result['link'],
                                    new_tab=True
                                ).classes('result-title no-underline hover:underline')
                                
                                # URL
                                ui.label(result['display_url']).classes('result-url')
                                
                                # Snippet
                                if result['snippet']:
                                    ui.label(result['snippet']).classes('result-snippet')
                    else:
                        ui.label('No results found').classes('text-gray-500 text-lg')
            
            # Allow Enter key to search
            search_input.on('keydown.enter', handle_search)


# Startup and shutdown handlers
@app.on_startup
async def on_startup():
    """Start Whoogle backend on app startup"""
    print("🚀 Starting Perceive...")
    start_whoogle_backend()


@app.on_shutdown
async def on_shutdown():
    """Stop Whoogle backend on app shutdown"""
    print("👋 Shutting down Perceive...")
    stop_whoogle_backend()


# Register cleanup on exit
atexit.register(stop_whoogle_backend)


if __name__ in {"__main__", "__mp_main__"}:
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                   Perceive Search                        ║
╚══════════════════════════════════════════════════════════╝

🌐 GUI Interface: http://localhost:{GUI_PORT}
🔧 Backend API:   {WHOOGLE_URL}

Starting servers...
    """)
    
    ui.run(
        port=GUI_PORT,
        title='Perceive',
        favicon='👁️',
        reload=False,
        show=True  # Automatically open browser
    )
