from cli.utils.config import get_api_client

def get_auth_headers():
    """Get common authentication headers for API requests."""
    api_client = get_api_client()
    return {
        "x-api-key": f"{api_client['token']}"
    } 