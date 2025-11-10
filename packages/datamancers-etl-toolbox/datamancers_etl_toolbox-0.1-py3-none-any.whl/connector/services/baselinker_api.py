#!/usr/bin/env python3
import os
import json
import requests
import logging
from datetime import datetime
import time
from typing import Dict, List, Optional, Union

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseLinkerClient:
    """
    A Python client for the BaseLinker API.
    Documentation: https://api.baselinker.com/
    """
    
    API_URL = "https://api.baselinker.com/connector.php"
    REQUEST_LIMIT = 100  # requests per minute
    
    def __init__(self, api_token: str):
        """
        Initialize the BaseLinker client.
        
        Args:
            api_token (str): The API token from BaseLinker panel 
                           (Account & other -> My account -> API)
        """
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            'X-BLToken': api_token,
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def _make_request(self, method: str, parameters: Optional[Dict] = None) -> Dict:
        """
        Make a request to the BaseLinker API.
        
        Args:
            method (str): The API method to call
            parameters (dict, optional): The parameters to send with the request
            
        Returns:
            dict: The API response
            
        Raises:
            Exception: If the API request fails
        """
        try:
            data = {
                'method': method,
                'parameters': json.dumps(parameters or {})
            }
            
            response = self.session.post(self.API_URL, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if 'status' in result and result['status'] == 'ERROR':
                error_msg = f"API Error: {result.get('error_message', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    # Product Catalog Methods
    def get_inventories(self) -> Dict:
        """Get a list of catalogs available in BaseLinker storage."""
        return self._make_request('getInventories')
    
    def get_inventory_products_data(self, inventory_id: int, products: List[int]) -> Dict:
        """
        Get detailed data for selected products from BaseLinker catalogue.
        
        Args:
            inventory_id (int): ID of the inventory
            products (List[int]): List of product IDs
            
        Returns:
            dict: Product details
        """
        parameters = {
            'inventory_id': inventory_id,
            'products': products
        }
        return self._make_request('getInventoryProductsData', parameters)

    def get_inventory_products_list(
        self,
        inventory_id: int,
        filter_id: Optional[str] = None,
        filter_category_id: Optional[int] = None,
        filter_ean: Optional[str] = None,
        filter_sku: Optional[str] = None,
        filter_name: Optional[str] = None,
        filter_price_from: Optional[float] = None,
        filter_price_to: Optional[float] = None,
        filter_quantity_from: Optional[int] = None,
        filter_quantity_to: Optional[int] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict:
        """
        Get a list of products from BaseLinker catalogue with optional filters.
        
        Args:
            inventory_id (int): ID of the inventory
            filter_id (str, optional): Filter by product ID
            filter_category_id (int, optional): Filter by category ID
            filter_ean (str, optional): Filter by EAN
            filter_sku (str, optional): Filter by SKU
            filter_name (str, optional): Filter by product name
            filter_price_from (float, optional): Filter by minimum price
            filter_price_to (float, optional): Filter by maximum price
            filter_quantity_from (int, optional): Filter by minimum quantity
            filter_quantity_to (int, optional): Filter by maximum quantity
            page (int): Page number for pagination
            limit (int): Number of products per page
            
        Returns:
            dict: List of products matching the filters
        """
        parameters = {
            'inventory_id': inventory_id,
            'page': page,
            'limit': limit
        }
        
        # Add optional filters
        if filter_id:
            parameters['filter_id'] = filter_id
        if filter_category_id:
            parameters['filter_category_id'] = filter_category_id
        if filter_ean:
            parameters['filter_ean'] = filter_ean
        if filter_sku:
            parameters['filter_sku'] = filter_sku
        if filter_name:
            parameters['filter_name'] = filter_name
        if filter_price_from:
            parameters['filter_price_from'] = filter_price_from
        if filter_price_to:
            parameters['filter_price_to'] = filter_price_to
        if filter_quantity_from:
            parameters['filter_quantity_from'] = filter_quantity_from
        if filter_quantity_to:
            parameters['filter_quantity_to'] = filter_quantity_to
            
        return self._make_request('getInventoryProductsList', parameters)

    def update_inventory_products_stock(
        self,
        inventory_id: int,
        products: List[Dict[str, Union[int, Dict[str, int]]]]
    ) -> Dict:
        """
        Update stock levels for products in BaseLinker catalogue.
        
        Args:
            inventory_id (int): ID of the inventory
            products (List[Dict]): List of products to update, each containing:
                - product_id: ID of the product
                - stock: New stock value or dict of variant stocks
                
        Returns:
            dict: Update result
        """
        parameters = {
            'inventory_id': inventory_id,
            'products': products
        }
        return self._make_request('updateInventoryProductsStock', parameters)

    # Order Methods
    def get_orders(
        self,
        order_id: Optional[int] = None,
        date_confirmed_from: Optional[int] = None,
        date_from: Optional[int] = None,
        id_from: Optional[int] = None,
        get_unconfirmed_orders: bool = False,
        include_custom_extra_fields: bool = False,
        status_id: Optional[int] = None,
        filter_email: Optional[str] = None,
        filter_order_source: Optional[str] = None,
        filter_order_source_id: Optional[int] = None
    ) -> Dict:
        """
        Get orders from BaseLinker order manager. Maximum 100 orders are returned at a time.
        
        Args:
            order_id (int, optional): Order identifier to get a specific order
            date_confirmed_from (int, optional): Get orders confirmed from this date (unix timestamp)
            date_from (int, optional): Get orders created from this date (unix timestamp)
            id_from (int, optional): Get orders from this ID onwards
            get_unconfirmed_orders (bool): Include unconfirmed orders (default: False)
            include_custom_extra_fields (bool): Include custom extra fields (default: False)
            status_id (int, optional): Get orders with specific status ID
            filter_email (str, optional): Filter orders by customer email
            filter_order_source (str, optional): Filter by order source (e.g., "ebay", "amazon")
            filter_order_source_id (int, optional): Filter by order source ID (requires filter_order_source)
            
        Returns:
            dict: List of orders matching the criteria. Each order contains detailed information
                 including customer details, delivery info, products, etc.
                 
        Note:
            It's recommended to download only confirmed orders (get_unconfirmed_orders=False) as
            unconfirmed orders may be incomplete or in the process of being created.
            
            For downloading ongoing orders, it's best to:
            1. Set date_confirmed_from to start date
            2. Process received orders (max 100 at a time)
            3. Use the last order's date_confirmed + 1 second as new date_confirmed_from
            4. Repeat until receiving less than 100 orders
        """
        parameters = {}
        
        # Add optional parameters
        if order_id is not None:
            parameters['order_id'] = order_id
        if date_confirmed_from is not None:
            parameters['date_confirmed_from'] = date_confirmed_from
        if date_from is not None:
            parameters['date_from'] = date_from
        if id_from is not None:
            parameters['id_from'] = id_from
        if get_unconfirmed_orders:
            parameters['get_unconfirmed_orders'] = get_unconfirmed_orders
        if include_custom_extra_fields:
            parameters['include_custom_extra_fields'] = include_custom_extra_fields
        if status_id is not None:
            parameters['status_id'] = status_id
        if filter_email:
            parameters['filter_email'] = filter_email
        if filter_order_source:
            parameters['filter_order_source'] = filter_order_source
            if filter_order_source_id is not None:
                parameters['filter_order_source_id'] = filter_order_source_id
                
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        records_cnt=100
        orders=[]
        # Paginate through results while we have 100 records (max per request)
        while records_cnt == 100:
            response = self._make_request('getOrders', parameters)
            records_cnt = len(response['orders'])
            logger.info(f"Retrieved {records_cnt} orders, checking for more...")
            # Add extraction timestamp to each order record in human readable format
            
            orders_extracted = response['orders']
            last_order = orders_extracted[-1]
            for order in orders_extracted:
                order['extraction_timestamp'] = current_timestamp
                
            orders.extend(orders_extracted)
                
                
                
            if 'date_confirmed' in last_order and last_order['date_confirmed']:
                # Add 1 second to avoid duplicate records
                new_date_confirmed_from = int(last_order['date_confirmed']) + 1
                parameters['date_confirmed_from'] = new_date_confirmed_from
            
            else:
                # Break the loop if no orders in the response
                break
            
        return orders

# Example usage:
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='BaseLinker API client')
    
    # Get API token from environment variable
    api_token = os.environ.get('BASELINKER_API_TOKEN')
    if api_token is None:
        logger.error("API token not found in environment variables.")
        exit(1)
        
    parser.add_argument('--method', type=str, help='Method to call')

    parser.add_argument('--date_from', type=str, help='Get orders from date (unix timestamp)')
    args = parser.parse_args()
    
    try:
        # Initialize client
        client = BaseLinkerClient(api_token)
        
        # Example: Get orders from last 24 hours
        if args.date_from:
            date_from = datetime.strptime(args.date_from, "%Y-%m-%d").timestamp()
        else:
            date_from = int(time.time()) - (24 * 60 * 60)  # 24 hours ago
            
        orders = client.get_orders(date_confirmed_from=int(date_from))
        with open('orders.json', 'w') as json_file:
            # Write each order as a separate line in NDJSON format
            for order in orders:
                json_file.write(json.dumps(order) + '\n')
            
    except Exception as e:
        logger.error("Error occurred: %s", str(e)) 