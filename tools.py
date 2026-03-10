import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def web_search(query: str) -> str:
    """Useful for searching the internet for current information."""
    try:
        tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
        search_result = tavily.search(query=query, search_depth="basic")
        
        formatted_results = []
        for result in search_result.get("results", []):
            formatted_results.append(f"Title: {result.get('title')}\nURL: {result.get('url')}\nContent: {result.get('content')}\n---")
        
        return "\n".join(formatted_results) if formatted_results else "No relevant results found."
    except Exception as e:
        return f"Error using Tavily search: {str(e)}"

@tool
def extract_url_content(url: str) -> str:
    """Useful for reading and extracting the text content of a specific URL."""
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing whitespace
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit content to avoid token limits
        return text[:4000] if text else "No content found at the URL."
    except Exception as e:
        return f"Error extracting content from URL {url}: {str(e)}"

# Export tools as a list
agent_tools = [web_search, extract_url_content]
