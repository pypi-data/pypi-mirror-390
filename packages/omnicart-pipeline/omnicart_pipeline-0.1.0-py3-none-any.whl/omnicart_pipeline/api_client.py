from .config import ConfigManager
from .logging_config import setup_logger
import requests

logger = setup_logger(__name__)

class APIClient:
    # CONFIG_FILE = "pipeline.cfg"
    CONFIGMANAGER = ConfigManager()
    
    def __init__(self):
        self.base_url = APIClient.CONFIGMANAGER.get("API", "base_url")
        self.limit = int(APIClient.CONFIGMANAGER.get("PAGINATION", "limit"))
    
    
    def _paginate(self, data: list[dict], limit: int) -> list[dict]:
        """
        Simulated pagination
        Args:
            data : A response from my api call
            limit (int): An integer simulating a chunk of data from a page

        Returns:
            list[dict]: all products data 
        """
        if not isinstance(limit, int):
            logger.exception("Limit must be an integer")
            raise TypeError("Limit must be an Integer")
        
        if limit <= 0:
            logger.exception("Limit must be greater than zero")
            raise ValueError("Limit must be greater than Zero")
        
        paginated_data = []
        page = 1
        
        for skip in range(0, len(data), limit):
            chunk = data[skip: skip + limit]
            
            # Add a logger here instead
            logger.info(f"Processing Page {page}: {len(chunk)} items")
            # print(f"Processing Page {page}: {len(chunk)} items")
            paginated_data.extend(chunk)
            page += 1
        
        return paginated_data
        
        
    def get_all_products(self) -> list[dict]:
        """
        Returns:
            list[dict]: A list of dictionary containing all of my products
        """
        try:
            response = requests.get(f"{self.base_url}/products")
            response.raise_for_status()
            all_products = response.json()
            
            return self._paginate(all_products, self.limit)
            
        except Exception as e:
            #TODO: Set my logger here
            logger.exception(f"An error occurred here: {e}")
            # print(f"An error occurred here: {e}")
            
            
    def get_all_users(self):
        try:
            response = requests.get(f"{self.base_url}/users")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            # TODO: ADD MY LOGGGER HERE
            logger.exception(f"An error occurred here: {e}")
            # print(f"An error occured here: {e}")
            
    
    @property    
    def get_config_settings(self):
        """
        returns my settings in the config file
        Returns:
            _dict
        """
        return APIClient.CONFIGMANAGER.settings()
    

# client = APIClient()
# print(client.get_config_settings)