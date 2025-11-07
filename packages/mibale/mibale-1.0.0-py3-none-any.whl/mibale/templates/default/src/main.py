"""
Point d'entrée principal de l'application Mibale
"""

from mibale import create_app
from mibale.router import Router, Route, createRouter
from mibale.stores import defineStore, createStore
from mibale.services.http_client import axios

# Import des composants
from .components.HelloWorld import HelloWorld
from .views.HomeView import HomeView
from .views.AboutView import AboutView

# Import des stores
from .stores.user_store import useUserStore

# Import des services
from .services.api import api

def configure_app():
    """Configure l'application Mibale"""
    
    # Configuration des routes
    routes = [
        Route(path='/', component=HomeView, name='home'),
        Route(path='/about', component=AboutView, name='about'),
    ]
    
    # Configuration des stores
    stores = {
        'user': useUserStore
    }
    
    # Configuration de l'application
    app_config = {
        'name': 'Mon App Mibale',
        'version': '1.0.0',
        'routes': routes,
        'stores': stores
    }
    
    return app_config

def setup_services():
    """Configure les services globaux"""
    
    # Configuration d'axios (client HTTP)
    axios.defaults.baseURL = 'https://api.mon-app.com'
    axios.defaults.timeout = 10000
    
    # Intercepteur de requêtes
    def request_interceptor(config):
        print(f"🌐 Requête HTTP: {config.get('method', 'GET')} {config.get('url')}")
        return config
    
    # Intercepteur de réponses
    def response_interceptor(response):
        print(f"🌐 Réponse HTTP: {response.get('status')}")
        return response
    
    axios.interceptors_request(request_interceptor)
    axios.interceptors_response(response_interceptor)
    
    print("✅ Services configurés")

def main():
    """Fonction principale de l'application"""
    print("🚀 Démarrage de l'application Mibale...")
    
    # Configuration
    app_config = configure_app()
    setup_services()
    
    # Création de l'application
    app = create_app(app_config)
    
    # Enregistrement des composants globaux
    app.component('HelloWorld', HelloWorld)
    
    # Montage de l'application
    app.mount()
    
    print("✅ Application Mibale démarrée avec succès!")
    print("📱 Votre application est maintenant en cours d'exécution")
    print("💡 Utilisez mibale dev pour le développement avec hot-reload")
    
    return app

if __name__ == "__main__":
    # Point d'entrée lors de l'exécution directe
    app = main()
    
    # Boucle principale (pour les applications desktop)
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Application arrêtée")