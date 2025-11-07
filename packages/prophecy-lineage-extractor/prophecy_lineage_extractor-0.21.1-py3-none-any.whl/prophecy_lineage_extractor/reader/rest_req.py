
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

from prophecy_lineage_extractor.constants import PROPHECY_URL, PROPHECY_PAT
from prophecy_lineage_extractor.utils import safe_env_variable


def hit_knowledge_graph_api(project_id, branch, pipeline_id_list):
    """
    Get lineage SQL data with retry functionality
    """
    base_url = safe_env_variable(PROPHECY_URL)
    auth_token = safe_env_variable(PROPHECY_PAT)

    # Setup retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    # Create session with retry
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    # API endpoint
    if base_url.endswith("/"):
        url = f"{base_url}api/lineage/sql/project"
    else:
        url = f"{base_url}/api/lineage/sql/project"

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-TOKEN': auth_token
    }

    # Request payload
    payload = {
        "projectId": project_id,
        "branch": branch,
        # "pipeline_list":pipeline_id_list
    }

    # Make request with retry
    response = session.get(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        response_post = session.post(url, headers=headers, json=payload)
        if response_post.status_code == 200:
            return response_post.json()
        else:
            raise Exception("The Post API is not returning valid content. Please check Knowledge Graph API")
    else:
        raise Exception("The Get API is not returning valid content. Please check Knowledge Graph API")