import asyncio
from typing import Any, Dict, List, Optional, Union
import aiohttp
import logging
logger = logging.getLogger(__name__)
BASE_BLOCKFRONT_URL = "https://blockfrontapi.vuis.dev"
#TODO possibly re-use Clients
async def async_post_request(endpoint:str,data: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0)->Union[Dict, List, str]:
    async with aiohttp.ClientSession() as client:
        url = f"{baseurl}/{endpoint}"
        try:
            async with client.post(url, json=data,timeout=timeout) as response:
                if response.ok:
                    return await response.json()
                else:
                    error_text = response.text
                    logger.error(f"Request to {url} failed: {error_text}")
                    raise Exception(f"Request to {url} failed: {error_text}")
        except aiohttp.RequestError as e:
            logger.error(f"Request to {url} failed: {e}")
            raise
        except aiohttp.TimeoutException as e:
            logger.error(f"Request to {url} timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"Request to {url} failed unexpectedly: {e}")
            raise

def post_request(endpoint:str,data: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0):
    '''Syncronous Wrapper for async function'''
    return asyncio.run(async_post_request(endpoint,data,baseurl=baseurl,timeout=timeout))


async def async_get_request(endpoint:str,params: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0):
    async with aiohttp.ClientSession() as client:
        url = f"{baseurl}{endpoint}"
        try:
            async with client.get(url, params=params,timeout=timeout) as response:
                if response.ok:
                    return await response.json()
                else:
                    error_text = response.text
                    logger.error(f"Request to {url} failed: {error_text}")
                    raise Exception(f"Request to {url} failed: {error_text}")

                
        except aiohttp.RequestError as e:
            logger.error(f"Request to {url} failed: {e}")
            raise
        except aiohttp.TimeoutException as e:
            logger.error(f"Request to {url} timed out: {e}")
            raise Exception(f"Request to {url} timed out: {e}")
        except Exception as e:
            logger.error(f"Request to {url} failed unexpectedly: {e}")
            raise

def get_request(endpoint:str,params: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0):
    '''Syncronous Wrapper for async function'''
    return asyncio.run(async_get_request(endpoint,params,baseurl=baseurl,timeout=timeout))