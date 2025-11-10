from linkedin_api import Linkedin
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import logging

load_dotenv()

mcp = FastMCP("LinkedIn-MCP")
logger = logging.getLogger(__name__)

def get_creds():
    return Linkedin(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD"), debug=True)

@mcp.tool()
def get_profile():
    """
    Retrieves the User Profile
    """
    linkedin = get_creds()
    profile = linkedin.get_profile()
    return profile
@mcp.tool()
def get_feed_posts(limit: int = 10, offset: int = 0) -> str:
    """
    Retrieve LinkedIn feed posts.

    :return: List of feed post details
    """
    linkedin = get_creds()
    try:
        post_urns = linkedin.get_feed_posts(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error: {e}"
    
    posts = ""
    for urn in post_urns:
        posts += f"Post by {urn["author_name"]}: {urn["content"]}\n"

    return posts

def main():
    """Main entry point for the LinkedIn MCP server"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()