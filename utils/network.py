import asyncio
from typing import Any, Dict, List, Optional, Union
import aiohttp
import logging
logger = logging.getLogger(__name__)
BASE_BLOCKFRONT_URL = "https://blockfrontapi.vuis.dev"
#TODO possibly re-use Clients
async def async_post_request(endpoint:str,data: Optional[Dict[str, Any]] = None,baseurl:str=BASE_BLOCKFRONT_URL,timeout: float = 15.0,is_json:bool= False)->Union[Dict, List, str]:
    async with aiohttp.ClientSession() as client:
        url = f"{baseurl}{endpoint}"
        try:
            if is_json:
                async with client.post(url, json=data,timeout=timeout) as response:
                    if response.ok:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(error_text)
            else:
                # Send as raw text/string
                async with client.post(url, data=data, timeout=timeout) as response:
                    if response.ok:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(error_text)
        except asyncio.TimeoutError as e:
             logger.error(f"POST Request to {url} timed out after {timeout} seconds. Error text : {e.strerror}")
             raise
        except aiohttp.ClientError as e:
            error_msg = f"POST request to {url} failed with client error: {e}"
            logger.error(error_msg)
            raise
        except aiohttp.ClientResponseError as e:
            error_msg = f"POST request to {url} failed with client error: {e}"
            logger.error(error_msg)
            raise
        except Exception as e:
            logger.error(f"POST Request to {url} failed unexpectedly: {e}")
            raise

def post_request(endpoint:str,data: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0,is_json:bool=False):
    '''Syncronous Wrapper for async function'''
    return asyncio.run(async_post_request(endpoint,data,baseurl=baseurl,timeout=timeout,is_json=is_json))


async def async_get_request(endpoint:str,params: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0):
    async with aiohttp.ClientSession() as client:
        url = f"{baseurl}{endpoint}"
        try:
            async with client.get(url, params=params,timeout=timeout) as response:
                if response.ok:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(error_text)

        except asyncio.TimeoutError as e :
             logger.error(f"GET Request to {url} timed out after {timeout} seconds. Error text : {e}")
             raise
        except aiohttp.ClientError as e:
            error_msg = f"GET request to {url} failed with client error: {e}"
            logger.error(error_msg)
        except aiohttp.ClientResponseError as e:
            error_msg = f"GET request to {url} failed with client error: {e}"
            logger.error(error_msg)
            raise
        except Exception as e:
            logger.error(f"GET Request to {url} failed unexpectedly: {e}")
            raise

def get_request(endpoint:str,params: Optional[Dict[str, Any]] = None,baseurl=BASE_BLOCKFRONT_URL,timeout: float = 15.0):
    '''Syncronous Wrapper for async function'''
    return asyncio.run(async_get_request(endpoint,params,baseurl=baseurl,timeout=timeout))