from litellm import Reasoning, responses
from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, List, Union


class ClaudeWebSearch(BaseTool):
    """
    Sends an input request to the web search model and returns the results.

    IMPORTANT CONSTRAINTS:
    - You MUST reason about what to search BEFORE calling this tool
    - You can only make 1 web search call per turn (to prevent context window overflow)
    - Results are limited to the top 3 most relevant matches
    - For user-provided URLs or API documentation, use WebFetch tool instead (no limits)
    - Use this tool ONLY for general research when you don't have a specific URL

    Usage:
    - Plan your search query carefully - you only get one shot
    - Keep queries focused and specific
    - For comprehensive API documentation, use WebFetch with specific URLs instead
    """

    query: str = Field(
        ...,
        description="A SINGLE focused search query. You can only search once per turn, so make it count. Think carefully before searching.",
        examples=[
            "How are files uploaded in OpenAI API?",
            "FastAPI integration with agency-swarm framework"
        ]
    )
    links: Optional[List[str]] = Field(
        default=None,
        description="Optional list of up to 3 specific links to prioritize in search results. For fetching full content, use WebFetch tool instead.",
        examples=[
            "https://platform.openai.com/docs/api-reference/files/create",
            "https://agency-swarm.ai/additional-features/fastapi-integration"
        ]
    )

    def run(self):
        """
        Executes a SINGLE focused web search and returns top 3 results.

        Returns:
            str: Search results limited to 3 most relevant matches, or error message
        """
        try:
            # Prepare links context if provided (limit to 3)
            links_context = ""
            if self.links:
                limited_links = self.links[:3]  # Limit to 3 links
                links_context = " Prioritize these links if relevant: " + ", ".join(limited_links)

            response = responses(
                model="anthropic/claude-sonnet-4-20250514",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that searches the web for information. "
                            "IMPORTANT: Only return the TOP 3 MOST RELEVANT results. "
                            "Do not explore more than 3 sources. "
                            "Return the information concisely and exactly as found. "
                            "If the user needs comprehensive documentation, recommend using WebFetch tool with specific URLs."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Search for: {self.query}{links_context}. Return only the TOP 3 most relevant results."
                    }
                ],
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "medium"  # Changed from "high" to "medium" to reduce context usage
                }],
                reasoning=Reasoning(effort="low"),  # Changed from "medium" to "low" to save tokens
                temperature=0,
            )

            # Track search in context (if available)
            if self.context is not None:
                search_count = self.context.get("web_search_count", 0)
                self.context.set("web_search_count", search_count + 1)

            return f"Web search results for: '{self.query}'\n\n{response.output[-1].content[-1].text}"
        except Exception as e:
            return f"Error performing web search: {str(e)}"


# Create alias for Agency Swarm tool loading (expects class name = file name)
claude_web_search = ClaudeWebSearch

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Test the tool
    # Test with current file
    current_file = __file__

    tool = ClaudeWebSearch(queries=["What is the latest version of the agency-swarm framework?", "How does fast API integration work in agency-swarm? Provide a full code example."], links=["https://platform.openai.com/docs/api-reference/files/create", "https://agency-swarm.ai/llms.txt"])
    print(tool.run())
