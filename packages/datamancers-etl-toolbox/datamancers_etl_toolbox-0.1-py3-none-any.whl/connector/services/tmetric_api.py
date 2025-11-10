#!/usr/bin/env python3
import os
import json
import requests
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TMetricClient:
    """
    A Python client for the TMetric API.
    Documentation: https://app.tmetric.com/api-docs/
    """
    
    API_BASE_URL = "https://app.tmetric.com/api"
    API_VERSION = "v3"
    
    def __init__(self, api_token: str, account_id: str):
        """
        Initialize the TMetric client.
        
        Args:
            api_token (str): The API token from TMetric
            account_id (str): The TMetric account ID
        """
        self.api_token = api_token
        self.account_id = account_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the TMetric API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body for POST/PUT requests
            
        Returns:
            dict: The API response
            
        Raises:
            Exception: If the API request fails
        """
        try:
            url = f"{self.API_BASE_URL}/{self.API_VERSION}/{endpoint}"
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_time_entries(
        self,
        start_date: str,
        end_date: str,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Dict]:
        """
        Get time entries for the specified period.
        
        Args:
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            end_date (str): End date in ISO format (YYYY-MM-DD)
            user_id (str, optional): Filter by specific user
            project_id (str, optional): Filter by specific project
            task_id (str, optional): Filter by specific task
            include_deleted (bool): Include deleted time entries (default: False)
            
        Returns:
            List[Dict]: List of time entries matching the criteria
        """
        endpoint = f"accounts/{self.account_id}/timeentries"
        
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'includeDeleted': str(include_deleted).lower()
        }
        
        # Add optional filters
        if user_id:
            params['userId'] = user_id
        if project_id:
            params['projectId'] = project_id
        if task_id:
            params['taskId'] = task_id
            
        current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        
        # Get time entries
        time_entries = self._make_request('GET', endpoint, params=params)
        
        # Add extraction timestamp to each entry
        for entry in time_entries:
            entry['extraction_timestamp'] = current_timestamp
            
        return time_entries

# Example usage:
if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta
    
    parser = argparse.ArgumentParser(description='TMetric API client')
    
    # Get credentials from environment variables
    api_token = os.environ.get('TMETRIC_API_TOKEN')
    account_id = os.environ.get('TMETRIC_ACCOUNT_ID')
    
    if not api_token or not account_id:
        logger.error("API token or Account ID not found in environment variables.")
        exit(1)
        
    parser.add_argument('--start_date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--user_id', type=str, help='Filter by user ID')
    parser.add_argument('--project_id', type=str, help='Filter by project ID')
    parser.add_argument('--output', type=str, default='time_entries.json', help='Output file name')
    
    args = parser.parse_args()
    
    try:
        # Initialize client
        client = TMetricClient(api_token, account_id)
        
        # Set default date range to last 7 days if not specified
        if not args.start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            start_date = args.start_date
            
        if not args.end_date:
            end_date = datetime.now().strftime('%Y-%m-d')
        else:
            end_date = args.end_date
            
        # Get time entries
        time_entries = client.get_time_entries(
            start_date=start_date,
            end_date=end_date,
            user_id=args.user_id,
            project_id=args.project_id
        )
        
        # Write results to file in NDJSON format
        with open(args.output, 'w') as json_file:
            for entry in time_entries:
                json_file.write(json.dumps(entry) + '\n')
                
        logger.info(f"Retrieved {len(time_entries)} time entries. Data saved to {args.output}")
            
    except Exception as e:
        logger.error("Error occurred: %s", str(e)) 