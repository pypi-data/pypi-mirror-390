import requests
import logging
from kestra import Kestra
from typing import Optional, List, Dict, Any

logger = Kestra.logger()

class AirbyteClient:
    """
    A client for interacting with the Airbyte API.

    :param client_id: The client ID for authentication.
    :param client_secret: The client secret for authentication.
    :param base_url: The base URL for the Airbyte API.
    """
    def __init__(self, client_id: str, client_secret: str, base_url: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.access_token: Optional[str] = None

    def get_access_token(self) -> None:
        """
        Obtain an access token using the client credentials.

        :raises: Exception if the token cannot be obtained.
        """
        url = f"{self.base_url}/v1/applications/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            logger.info("Access token obtained successfully.")
        else:
            logger.error(f"Failed to obtain access token: {response.status_code} - {response.text}")

    def make_authenticated_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make an authenticated request to the Airbyte API.

        :param endpoint: The API endpoint to call.
        :param method: The HTTP method to use (default is 'GET').
        :param data: The data to send with the request (for POST requests).
        :return: The response object from the request.
        """
        if not self.access_token:
            self.get_access_token()

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=headers, json=data)
        
        if response.status_code == 401:
            # Token might have expired, try to refresh it
            self.get_access_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.request(method, url, headers=headers, json=data)
        
        return response

    def list_connections(self, workspace_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        List connections from all workspaces or specific workspaces if workspace_ids are provided.

        :param workspace_ids: Optional list of workspace IDs to filter connections.
        :return: JSON response containing the list of connections.
        :rtype: dict
        """
        endpoint = "/v1/connections"
        if workspace_ids:
            workspace_ids_param = ','.join(workspace_ids)
            endpoint += f"?workspaceIds={workspace_ids_param}"
        
        response = self.make_authenticated_request(endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to list connections: {response.status_code} - {response.text}")
            return None

    def create_job(self, connection_id: str, job_type: str = 'sync') -> Optional[Dict[str, Any]]:
        """
        Trigger a sync or reset job for a connection.

        :param connection_id: The ID of the connection for which to create the job.
        :param job_type: The type of job to create ('sync' or 'reset').
        :return: JSON response containing the job details.
        :rtype: dict
        """
        endpoint = "/v1/jobs"
        payload = {
            "connectionId": connection_id,
            "jobType": job_type
        }
        
        response = self.make_authenticated_request(endpoint, method='POST', data=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to create job: {response.status_code} - {response.text}")
            return None

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status and details of a specific job.

        :param job_id: The ID of the job to retrieve.
        :return: JSON response containing the job status and details.
        :rtype: dict
        """
        endpoint = f"/v1/jobs/{job_id}"
        
        response = self.make_authenticated_request(endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get job status: {response.status_code} - {response.text}")
            return None



def main(client_id: str, client_secret: str, base_url: str, connection_id: str, wait_time: int) -> None:
    """
    Main function to create a job and monitor its status.

    :param client_id: The client ID for Airbyte.
    :param client_secret: The client secret for Airbyte.
    :param base_url: The base URL for the Airbyte API.
    :param connection_id: The ID of the connection for which to create the job.
    :param wait_time: Time in seconds to wait between status checks.
    """
    import time
    # Initialize Airbyte client
    airbyte_client = AirbyteClient(client_id=client_id, client_secret=client_secret, base_url=base_url)

    # Create a job
    job = airbyte_client.create_job(connection_id)

    if job:
        job_id = job.get("jobId")
        logger.info(f"Job created with ID: {job_id}")

        # Check job status until successful sync
        while True:
            job_status = airbyte_client.get_job_status(job_id)
            if job_status:
                status = job_status.get("status")
                if status in ["succeeded", "failed"]:
                    if status == "succeeded":
                        logger.info("Job completed successfully.")
                    else:
                        logger.error("Job failed.")
                    break
            else:
                logger.error("Failed to retrieve job status.")
                break

            time.sleep(wait_time)  # Wait before checking the status again

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Airbyte Job Status Checker")
    parser.add_argument("--client_id", required=True, help="Airbyte client ID")
    parser.add_argument("--client_secret", required=True, help="Airbyte client secret")
    parser.add_argument("--base_url", required=False, help="Base URL for Airbyte API",default="https://api.airbyte.com")
    parser.add_argument("--connection_id", required=True, help="Connection ID for the job")
    parser.add_argument("--wait_time",required=False,help="how ofter should status of job be checked",default=5)

    args = parser.parse_args()

    main(args.client_id,args.client_secret,args.base_url,args.connection_id,args.wait_time)
