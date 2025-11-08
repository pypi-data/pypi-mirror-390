from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional
import requests
from bs4 import BeautifulSoup


class WebFetch(BaseTool):
    """
    Fetches content from a specified URL and returns it for analysis.

    Usage:
    - Use this tool when the user provides specific URLs to fetch (e.g., API documentation, reference materials)
    - ALWAYS use this tool when studying complete API documentation - this is encouraged and has NO limits
    - The url parameter must be a valid HTTP/HTTPS URL
    - Returns the full text content of the webpage
    - For API documentation, it's recommended to fetch ALL related doc pages to ensure proper implementation
    - This tool has no search limits - fetch as many documentation pages as needed for accurate implementation
    - If fetch fails, an error message will be returned

    Examples:
    - Fetch API documentation: url="https://platform.openai.com/docs/api-reference/files/create"
    - Fetch reference material: url="https://agency-swarm.ai/additional-features/fastapi-integration"
    - Study framework docs: url="https://docs.anthropic.com/claude/docs/tool-use"
    """

    url: str = Field(
        ...,
        description="The URL to fetch content from. Must be a valid HTTP/HTTPS URL.",
        examples=[
            "https://platform.openai.com/docs/api-reference/files/create",
            "https://agency-swarm.ai/additional-features/fastapi-integration",
            "https://docs.anthropic.com/claude/docs/tool-use"
        ]
    )
    timeout: Optional[int] = Field(
        default=30,
        description="Request timeout in seconds (default: 30)",
        ge=5,
        le=120
    )

    def run(self):
        """
        Fetches the content from the specified URL.

        Returns:
            str: The text content of the webpage, or an error message if fetch fails
        """
        try:
            # Validate URL format
            if not self.url.startswith(('http://', 'https://')):
                return f"Error: Invalid URL format. URL must start with http:// or https://. Got: {self.url}"

            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }

            # Fetch the URL
            response = requests.get(self.url, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Track successful fetch in context (if available)
            if self.context is not None:
                fetched_urls = self.context.get("fetched_urls", set())
                fetched_urls.add(self.url)
                self.context.set("fetched_urls", fetched_urls)

            return f"Successfully fetched content from {self.url}:\n\n{text}"

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds for URL: {self.url}"
        except requests.exceptions.ConnectionError:
            return f"Error: Failed to connect to {self.url}. Please check the URL and your internet connection."
        except requests.exceptions.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} error fetching {self.url}: {str(e)}"
        except Exception as e:
            return f"Error fetching URL {self.url}: {str(e)}"


# Create alias for Agency Swarm tool loading (expects class name = file name)
web_fetch = WebFetch

if __name__ == "__main__":
    # Test the tool
    tool = WebFetch(url="https://www.anthropic.com")
    print(tool.run())
