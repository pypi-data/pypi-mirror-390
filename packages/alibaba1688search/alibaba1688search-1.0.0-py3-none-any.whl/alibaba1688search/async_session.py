import asyncio
import aiohttp
from yarl import URL
from typing import List
import time

from .models import Product, extract_products_from_html
from .utils import prepare_image_request, generate_sign, read_and_encode_image

class Async1688Session:
    def __init__(self, default_timeout: float = 30):
        self._session = None
        self._token = None
        self._token_part = None
        self.app_key = "12574478"
        self.base_url = "https://h5api.m.1688.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
        self._initialized = False
        self.default_timeout = default_timeout
    
    async def __aenter__(self):
        if not self._initialized:
            await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _initialize(self):
        if self._initialized:
            return
        
        await self.start()
        self._initialized = True
    
    async def start(self):
        if self._session:
            await self.close()
        
        self._session = aiohttp.ClientSession()
        
        try:
            test_params = {
                "jsv": "2.7.2",
                "appKey": self.app_key,
                "t": str(int(time.time() * 1000)),
                "api": "mtop.relationrecommend.WirelessRecommend.recommend",
                "v": "2.0",
                "type": "originaljson"
            }
            
            response = await self._session.get(
                self.base_url,
                params=test_params,
                timeout=self.default_timeout
            )
            
            url_obj = URL(self.base_url)
            cookies = self._session.cookie_jar.filter_cookies(url_obj)
            token_cookie = cookies.get('_m_h5_tk')
            
            if token_cookie:
                self._token = token_cookie.value
                self._token_part = self._token.split('_')[0]
                return True
            else:
                raise Exception("Не удалось получить токен")
            
            await response.release()
            
        except Exception as e:
            await self.close()
            raise Exception(f"Ошибка запуска сессии: {e}")
    
    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
            self._token = None
            self._token_part = None
            self._initialized = False
    
    async def _ensure_initialized(self):
        if not self._initialized or not self.is_active:
            await self._initialize()
    
    async def _get_image_id(self, image_path, timeout=None):
        await self._ensure_initialized()
        
        if timeout is None:
            timeout = self.default_timeout
        
        image_b64 = read_and_encode_image(image_path)
        data_string = prepare_image_request(image_b64)
        timestamp = str(int(time.time() * 1000))
        sign = generate_sign(self._token_part, timestamp, self.app_key, data_string)
        
        params = {
            "jsv": "2.7.2",
            "appKey": self.app_key,
            "t": timestamp,
            "sign": sign,
            "api": "mtop.relationrecommend.WirelessRecommend.recommend",
            "ignoreLogin": "true",
            "prefix": "h5api",
            "v": "2.0",
            "type": "originaljson",
            "dataType": "jsonp", 
            "jsonpIncPrefix": "search1688",
            "timeout": "20000"
        }
        
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://s.1688.com",
            "referer": "https://s.1688.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            response = await self._session.post(
                self.base_url,
                params=params,
                data={"data": data_string},
                headers=headers,
                timeout=timeout
            )
            
            if response.status == 200:
                result = await response.json()
                if result.get("data", {}).get("success"):
                    image_id = result["data"].get("imageId")
                    if image_id:
                        return image_id
            
            await response.release()
            return None
            
        except Exception as e:
            raise Exception(f"Ошибка при запросе: {e}")
    
    async def search_by_image(self, image_path: str, timeout: float = None) -> List[Product]:
        await self._ensure_initialized()
        
        if timeout is None:
            timeout = self.default_timeout
        
        image_id = await self._get_image_id(image_path, timeout=timeout)
        
        if not image_id:
            return []
        
        products = await self._search_by_image_id(image_id, timeout=timeout)
        return products
    
    async def _search_by_image_id(self, image_id: str, timeout=None) -> List[Product]:
        await self._ensure_initialized()
        
        if timeout is None:
            timeout = self.default_timeout
        
        search_url = f"https://s.1688.com/youyuan/index.htm"
        params = {
            "tab": "imageSearch",
            "imageId": image_id
        }
        
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "referer": "https://s.1688.com/"
        }
        
        try:
            response = await self._session.get(
                search_url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            
            if response.status == 200:
                html_content = await response.text()
                products = extract_products_from_html(html_content)
                return products
            else:
                return []
                
        except Exception:
            return []
    
    @property
    def is_active(self):
        return self._session is not None and not self._session.closed

    def __await__(self):
        return self._create_initialized().__await__()

    async def _create_initialized(self):
        await self._initialize()
        return self
