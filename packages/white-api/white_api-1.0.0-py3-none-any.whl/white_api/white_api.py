# white_api/white_api.py
import requests
import json

__version__ = "1.0.0"

class BaseWhiteAPI:
    """Базовый класс для White API"""
    def __init__(self, api_key, base_url="https://api.wscode.ru"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint, data=None):
        """Базовый метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json=data or {},
                timeout=30
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON response"}

class WhiteGiftAPI(BaseWhiteAPI):
    """API для работы с подарками"""
    
    def floor_gift(self, name):
        """Получить минимальную цену для конкретного подарка"""
        return self._make_request('/api/floor_gift', {'name': name})
    
    def floor_gift_all(self):
        """Получить минимальные цены для всех доступных подарков"""
        return self._make_request('/api/floor_gift_all')
    
    def floor_models_gift(self, name):
        """Получить цены моделей для конкретного подарка"""
        return self._make_request('/api/floor_models_gift', {'name': name})
    
    def floor_gift_backdrop(self, name, backdrop):
        """Получить цену подарка с определенным фоном"""
        return self._make_request('/api/floor_gift_backdrop', {
            'name': name,
            'backdrop': backdrop
        })
    
    def find_floor_gift(self, name, backdrop=None, model=None, symbol=None, id=None):
        """Расширенный поиск с фильтрами"""
        params = {'name': name}
        if backdrop: params['backdrop'] = backdrop
        if model: params['model'] = model
        if symbol: params['symbol'] = symbol
        if id: params['id'] = id
        
        return self._make_request('/api/find_floor_gift', params)

class WhiteStickerAPI(BaseWhiteAPI):
    """API для работы со стикерами Palace"""
    
    def get_floor_sticker(self, collection=None, model=None, ID=None):
        """Получить минимальные цены для стикеров"""
        params = {}
        if collection: params['collection'] = collection
        if model: params['model'] = model
        if ID: params['ID'] = ID
        
        return self._make_request('/api/get_floor_sticker', params)
    
    def get_supply_sticker(self, collection=None, model=None, ID=None):
        """Получить информацию о саплае"""
        params = {}
        if collection: params['collection'] = collection
        if model: params['model'] = model
        if ID: params['ID'] = ID
        
        return self._make_request('/api/get_supply_sticker', params)

class WhiteStickerToolsAPI(BaseWhiteAPI):
    """API для работы с платформой Stickertools"""
    
    def total_stats(self):
        """Получить общую статистику платформы Stickertools"""
        return self._make_request('/api/stickertools/total_stats')
    
    def collections_list(self):
        """Получить список всех коллекций Stickertools"""
        return self._make_request('/api/stickertools/collections_list')
    
    def collection_by_id(self, collection_id):
        """Получить данные коллекции по ID"""
        return self._make_request('/api/stickertools/collection_by_id', {
            'collection_id': collection_id
        })
    
    def collection_by_name(self, collection_name):
        """Получить коллекцию по названию"""
        return self._make_request('/api/stickertools/collection_by_name', {
            'collection_name': collection_name
        })
    
    def collection_stickers(self, collection_id):
        """Получить все стикеры коллекции"""
        return self._make_request('/api/stickertools/collection_stickers', {
            'collection_id': collection_id
        })
    
    def sticker_by_id(self, collection_id, sticker_id):
        """Получить конкретный стикер по ID"""
        return self._make_request('/api/stickertools/sticker_by_id', {
            'collection_id': collection_id,
            'sticker_id': sticker_id
        })
    
    def stickers_by_name(self, sticker_name):
        """Найти все стикеры по названию"""
        return self._make_request('/api/stickertools/stickers_by_name', {
            'sticker_name': sticker_name
        })
    
    def top_collections_by_volume(self, limit=10):
        """Топ коллекций по объему торгов"""
        return self._make_request('/api/stickertools/top_collections_by_volume', {
            'limit': limit
        })
    
    def top_stickers_by_price(self, limit=10):
        """Топ стикеров по текущей медианной цене"""
        return self._make_request('/api/stickertools/top_stickers_by_price', {
            'limit': limit
        })
    
    def burned_stickers(self):
        """Получить список сожженных стикеров"""
        return self._make_request('/api/stickertools/burned_stickers')
    
    def sticker_price_history(self, collection_id, sticker_id, period='current'):
        """Получить историю цен стикера за период"""
        return self._make_request('/api/stickertools/sticker_price_history', {
            'collection_id': collection_id,
            'sticker_id': sticker_id,
            'period': period
        })
    
    def sticker_volume_history(self, collection_id, sticker_id, period='current'):
        """Получить историю объема торгов стикера за период"""
        return self._make_request('/api/stickertools/sticker_volume_history', {
            'collection_id': collection_id,
            'sticker_id': sticker_id,
            'period': period
        })
    
    def platform_overview(self):
        """Быстрый обзор платформы Stickertools"""
        return self._make_request('/api/stickertools/platform_overview')
    
    def search_stickers(self, keyword):
        """Поиск стикеров по ключевому слову в названии"""
        return self._make_request('/api/stickertools/search_stickers', {
            'keyword': keyword
        })
    
    def sticker_full_info(self, collection_id, sticker_id):
        """Получить полную информацию о стикере"""
        return self._make_request('/api/stickertools/sticker_full_info', {
            'collection_id': collection_id,
            'sticker_id': sticker_id
        })

class WhiteAPI:
    """Основной класс для работы со всеми API White"""
    
    def __init__(self, api_key, base_url="https://api.wscode.ru"):
        self.gift = WhiteGiftAPI(api_key, base_url)
        self.sticker = WhiteStickerAPI(api_key, base_url)
        self.stickertools = WhiteStickerToolsAPI(api_key, base_url)
        self.api_key = api_key
        self.base_url = base_url
    
    def api_methods(self):
        """Получить все методы API"""
        url = f"{self.base_url}/api/methods"
        try:
            response = requests.get(url)
            return response.json() if response.status_code == 200 else None
        except:
            return None