"""
Service API pour les appels HTTP et la communication avec le backend
"""

from mibale.services.http_client import axios, createAxiosInstance
import json
from typing import Dict, Any, Optional, List

class ApiService:
    """Service principal pour les appels API"""
    
    def __init__(self, base_url: str = None):
        self.client = createAxiosInstance({
            'baseURL': base_url or 'https://jsonplaceholder.typicode.com',
            'timeout': 10000,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        })
        
        # Configuration des intercepteurs
        self._setup_interceptors()
        
        print(f"🌐 ApiService initialisé: {base_url}")
    
    def _setup_interceptors(self):
        """Configure les intercepteurs Axios"""
        
        # Intercepteur de requêtes
        def request_interceptor(config):
            # Ajoute un token d'authentification si disponible
            from mibale.stores import useStore
            
            try:
                user_store = useStore('user')
                if user_store.isLoggedIn:
                    # En vrai, on récupérerait le token du store
                    # config.headers['Authorization'] = f'Bearer {user_store.token}'
                    config.headers['X-User-ID'] = user_store.name
            except:
                pass
            
            print(f"🌐 → {config.get('method', 'GET').upper()} {config.get('url')}")
            return config
        
        # Intercepteur de réponses
        def response_interceptor(response):
            print(f"🌐 ← {response.get('status')} {response.get('config', {}).get('url')}")
            return response
        
        # Intercepteur d'erreurs
        def error_interceptor(error):
            error_data = getattr(error, 'response', {})
            print(f"🌐 ❌ Erreur {error_data.get('status', 'Unknown')}: {error_data.get('data', str(error))}")
            
            # Gestion des erreurs spécifiques
            if error_data.get('status') == 401:
                print("🔐 Session expirée - déconnexion...")
                # Déconnexion automatique
                # user_store.logout()
            
            return error
        
        self.client.interceptors_request(request_interceptor)
        self.client.interceptors_response(response_interceptor)
        self.client.interceptors_response(error_interceptor)
    
    # === METHODES CRUD ===
    
    async def get(self, endpoint: str, params: Dict = None) -> Optional[Dict[str, Any]]:
        """Requête GET"""
        try:
            response = await self.client.get(endpoint, params=params)
            return response.get('data')
        except Exception as e:
            print(f"❌ Erreur GET {endpoint}: {e}")
            return None
    
    async def post(self, endpoint: str, data: Dict = None) -> Optional[Dict[str, Any]]:
        """Requête POST"""
        try:
            response = await self.client.post(endpoint, data=data)
            return response.get('data')
        except Exception as e:
            print(f"❌ Erreur POST {endpoint}: {e}")
            return None
    
    async def put(self, endpoint: str, data: Dict = None) -> Optional[Dict[str, Any]]:
        """Requête PUT"""
        try:
            response = await self.client.put(endpoint, data=data)
            return response.get('data')
        except Exception as e:
            print(f"❌ Erreur PUT {endpoint}: {e}")
            return None
    
    async def delete(self, endpoint: str) -> bool:
        """Requête DELETE"""
        try:
            response = await self.client.delete(endpoint)
            return response.get('status', 0) == 200
        except Exception as e:
            print(f"❌ Erreur DELETE {endpoint}: {e}")
            return False
    
    # === METHODES SPÉCIFIQUES ===
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Récupère la liste des utilisateurs"""
        return await self.get('/users') or []
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur spécifique"""
        return await self.get(f'/users/{user_id}')
    
    async def get_posts(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Récupère les posts"""
        params = {}
        if user_id:
            params['userId'] = user_id
        
        return await self.get('/posts', params=params) or []
    
    async def create_post(self, title: str, body: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Crée un nouveau post"""
        data = {
            'title': title,
            'body': body,
            'userId': user_id
        }
        return await self.post('/posts', data=data)
    
    async def update_post(self, post_id: int, title: str, body: str) -> Optional[Dict[str, Any]]:
        """Met à jour un post"""
        data = {
            'title': title,
            'body': body
        }
        return await self.put(f'/posts/{post_id}', data=data)
    
    async def delete_post(self, post_id: int) -> bool:
        """Supprime un post"""
        return await self.delete(f'/posts/{post_id}')
    
    async def get_comments(self, post_id: int = None) -> List[Dict[str, Any]]:
        """Récupère les commentaires"""
        params = {}
        if post_id:
            params['postId'] = post_id
        
        return await self.get('/comments', params=params) or []
    
    # === METHODES AUTH ===
    
    async def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Connexion utilisateur"""
        # Note: Ceci est une simulation - en vrai, on utiliserait un endpoint d'authentification
        data = {
            'username': username,
            'password': password
        }
        
        # Simulation d'une réponse d'authentification
        mock_response = {
            'user': {
                'id': 1,
                'name': username,
                'email': f'{username}@example.com',
                'token': 'mock_jwt_token_here'
            },
            'expires_in': 3600
        }
        
        # En vrai: return await self.post('/auth/login', data=data)
        return mock_response
    
    async def register(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Inscription utilisateur"""
        return await self.post('/auth/register', data=user_data)
    
    async def logout(self) -> bool:
        """Déconnexion utilisateur"""
        try:
            # En vrai: await self.post('/auth/logout')
            print("🔐 Déconnexion API")
            return True
        except:
            return False
    
    async def get_profile(self) -> Optional[Dict[str, Any]]:
        """Récupère le profil utilisateur"""
        return await self.get('/auth/profile')

# Instance globale
api = ApiService()

# Export des fonctions utilitaires
async def fetch_users():
    """Récupère tous les utilisateurs"""
    return await api.get_users()

async def fetch_user_posts(user_id: int):
    """Récupère les posts d'un utilisateur"""
    return await api.get_posts(user_id)

async def create_new_post(title: str, content: str, author_id: int):
    """Crée un nouveau post"""
    return await api.create_post(title, content, author_id)

# Exemple d'utilisation
if __name__ == "__main__":
    import asyncio
    
    async def test_api():
        print("🧪 Test de l'API Service:")
        
        # Test des utilisateurs
        users = await api.get_users()
        print(f"👥 Utilisateurs: {len(users)} trouvés")
        
        if users:
            # Test des posts du premier utilisateur
            user_id = users[0]['id']
            posts = await api.get_posts(user_id)
            print(f"📝 Posts de l'utilisateur {user_id}: {len(posts)} trouvés")
            
            # Test de création de post
            new_post = await api.create_post(
                title="Test Post",
                body="Ceci est un test",
                user_id=user_id
            )
            if new_post:
                print(f"✅ Post créé: {new_post['id']}")
        
        # Test des commentaires
        comments = await api.get_comments()
        print(f"💬 Commentaires: {len(comments)} trouvés")
    
    # Exécution du test
    asyncio.run(test_api())