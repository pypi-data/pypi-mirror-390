import requests
import asyncio
from typing import Dict, Any, Optional, List, Callable
import json

class HttpClient:
    """Client HTTP similaire à Axios"""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Headers par défaut
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mibale/1.0'
        })
        
        # Intercepteurs
        self.request_interceptors: List[Callable] = []
        self.response_interceptors: List[Callable] = []
        
        # Configuration par défaut
        self.defaults = {
            'timeout': timeout,
            'baseURL': base_url
        }
    
    # Méthodes principales
    async def get(self, url: str, params: Dict = None, **kwargs) -> Dict[str, Any]:
        return await self._request('GET', url, params=params, **kwargs)
    
    async def post(self, url: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        return await self._request('POST', url, data=data, **kwargs)
    
    async def put(self, url: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        return await self._request('PUT', url, data=data, **kwargs)
    
    async def patch(self, url: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        return await self._request('PATCH', url, data=data, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        return await self._request('DELETE', url, **kwargs)
    
    async def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Exécute une requête HTTP"""
        full_url = self.base_url + url
        
        # Configuration fusionnée
        config = {
            'method': method,
            'url': full_url,
            'timeout': self.timeout,
            **kwargs
        }
        
        # Intercepteurs de requête
        for interceptor in self.request_interceptors:
            config = interceptor(config) or config
        
        try:
            # Exécution dans un thread séparé pour l'async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.session.request(
                    method=config['method'],
                    url=config['url'],
                    params=config.get('params'),
                    json=config.get('data'),
                    headers=config.get('headers'),
                    timeout=config.get('timeout')
                )
            )
            
            # Intercepteurs de réponse
            for interceptor in self.response_interceptors:
                response = interceptor(response) or response
            
            return self._handle_response(response, config)
            
        except requests.RequestException as e:
            return self._handle_error(e, config)
    
    def _handle_response(self, response: requests.Response, config: Dict) -> Dict[str, Any]:
        """Gère la réponse HTTP"""
        try:
            response.raise_for_status()
            
            # Essaye de parser le JSON
            try:
                data = response.json()
            except ValueError:
                data = response.text
            
            result = {
                'data': data,
                'status': response.status_code,
                'statusText': response.reason,
                'headers': dict(response.headers),
                'config': config,
                'request': {'url': response.url}
            }
            
            return result
            
        except requests.HTTPError as e:
            return self._handle_error(e, config)
    
    def _handle_error(self, error: Exception, config: Dict) -> Dict[str, Any]:
        """Gère les erreurs HTTP"""
        if isinstance(error, requests.HTTPError):
            response = error.response
            return {
                'error': str(error),
                'data': response.json() if response else None,
                'status': response.status_code if response else None,
                'statusText': response.reason if response else str(error),
                'headers': dict(response.headers) if response else {},
                'config': config
            }
        else:
            return {
                'error': str(error),
                'data': None,
                'status': None,
                'statusText': str(error),
                'headers': {},
                'config': config
            }
    
    # Méthodes utilitaires Axios-like
    def create(self, config: Dict[str, Any]) -> 'HttpClient':
        """Crée une nouvelle instance avec configuration"""
        instance = HttpClient(
            base_url=config.get('baseURL', ''),
            timeout=config.get('timeout', self.timeout)
        )
        
        if 'headers' in config:
            instance.session.headers.update(config['headers'])
        
        return instance
    
    def set_token(self, token: str):
        """Définit le token d'authentification"""
        self.session.headers['Authorization'] = f'Bearer {token}'
    
    def remove_token(self):
        """Supprime le token d'authentification"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    # Intercepteurs
    def interceptors_request(self, interceptor: Callable):
        """Ajoute un intercepteur de requête"""
        self.request_interceptors.append(interceptor)
    
    def interceptors_response(self, interceptor: Callable):
        """Ajoute un intercepteur de réponse"""
        self.response_interceptors.append(interceptor)
    
    # Méthodes statiques
    @staticmethod
    async def all(requests: List):
        """Exécute plusieurs requêtes en parallèle (comme axios.all)"""
        return await asyncio.gather(*requests)
    
    @staticmethod
    def spread(callback: Callable):
        """Spread les résultats (comme axios.spread)"""
        def wrapper(results):
            return callback(*results)
        return wrapper

# Instance globale (comme axios par défaut)
axios = HttpClient()

# Fonctions utilitaires
def createAxiosInstance(config: Dict[str, Any]) -> HttpClient:
    """Crée une instance Axios personnalisée"""
    return HttpClient(
        base_url=config.get('baseURL', ''),
        timeout=config.get('timeout', 30)
    )