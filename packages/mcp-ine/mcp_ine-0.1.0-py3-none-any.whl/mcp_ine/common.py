import os, logging, requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_ine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('mcp_ine')

# Load environment variables
load_dotenv()

# Configuration
INE_LANGUAGE = os.getenv('INE_LANGUAGE', 'ES')
INE_DEFAULT_PERIODS = int(os.getenv('INE_DEFAULT_PERIODS', '12'))
INE_BASE_URL = "https://servicios.ine.es/wstempus/js"

# Validate language
if INE_LANGUAGE not in ['ES', 'EN', 'FR', 'CA']:
    logger.warning(f"Invalid language {INE_LANGUAGE}, using ES")
    INE_LANGUAGE = 'ES'

# Initialize MCP server
mcp = FastMCP(
    name="mcp_ine",
    instructions="This server provides tools to interact with INE (Spanish Statistical Office) public data API. "
                 "Access to 109+ statistical operations including IPC (CPI), EPA (Labor Force Survey), "
                 "Population data, and economic indicators."
)

# HTTP Client helper
def ine_request(function: str, input_param: Optional[str] = None, 
                params: Optional[Dict] = None) -> Any:
    """Execute INE API request
    
    Args:
        function: API function (OPERACIONES_DISPONIBLES, DATOS_TABLA, etc)
        input_param: Optional input parameter (table_id, series_code, etc)
        params: Optional query parameters (nult, tip, date, det)
    
    Returns:
        JSON response from INE API or error dict
    """
    url_parts = [INE_BASE_URL, INE_LANGUAGE, function]
    if input_param:
        url_parts.append(str(input_param))
    
    url = '/'.join(url_parts)
    
    try:
        logger.info(f"INE API request: {url} | params: {params}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"INE API error: {e}")
        return {"error": str(e)}
    except ValueError as e:
        logger.error(f"JSON parse error: {e}")
        return {"error": f"Invalid JSON response: {str(e)}"}
