import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

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
        
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:4000] if text else "No content found at the URL."
    except Exception as e:
        return f"Error extracting content from URL {url}: {str(e)}"

@tool
def send_email(to_email: str, subject: str, content: str) -> str:
    """Useful for sending emails. Provide the destination email, subject, and text content."""
    try:
        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            return "Error: SENDGRID_API_KEY is not configured."
            
        message = Mail(
            from_email='agentcore@tu-dominio.com',
            to_emails=to_email,
            subject=subject,
            html_content=content)
            
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return f"Email sent successfully to {to_email}. Status code: {response.status_code}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@tool
def analyze_image(image_url: str, prompt: str) -> str:
    """Useful for analyzing an image from a URL. Provide the image URL and a prompt asking what you want to know about it."""
    try:
        llm_vision = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.environ.get("GEMINI_API_KEY")
        )
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": image_url}
            ]
        )
        response = llm_vision.invoke([message])
        return response.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

agent_tools = [web_search, extract_url_content, send_email, analyze_image]
