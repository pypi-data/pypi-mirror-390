"""
Configuration des routes de l'application Mibale
"""

from mibale.router import Route

# Import des composants de vue
from ..views.HomeView import HomeView
from ..views.AboutView import AboutView

# Définition des routes de l'application
routes = [
    # Route d'accueil
    Route(
        path='/',
        component=HomeView,
        name='home',
        meta={
            'title': 'Accueil',
            'requiresAuth': False,
            'transition': 'slide'
        }
    ),
    
    # Page À propos
    Route(
        path='/about',
        component=AboutView,
        name='about',
        meta={
            'title': 'À propos',
            'requiresAuth': False,
            'transition': 'fade'
        }
    ),
    
    # Exemple de route avec paramètres dynamiques
    # Route(
    #     path='/user/:id',
    #     component=UserView,
    #     name='user',
    #     meta={
    #         'title': 'Profil Utilisateur',
    #         'requiresAuth': True
    #     }
    # ),
    
    # Exemple de route avec enfants (nested routes)
    # Route(
    #     path='/settings',
    #     component=SettingsView,
    #     name='settings',
    #     children=[
    #         Route(
    #             path='profile',
    #             component=ProfileSettings,
    #             name='settings-profile'
    #         ),
    #         Route(
    #             path='security',
    #             component=SecuritySettings,
    #             name='settings-security'
    #         )
    #     ]
    # )
]

# Guards de route globaux
def create_route_guards(router):
    """
    Crée et configure les guards de route globaux
    """
    
    def auth_guard(to_route, from_route):
        """
        Guard pour vérifier l'authentification
        """
        if to_route.meta and to_route.meta.get('requiresAuth'):
            from mibale.stores import useStore
            
            user_store = useStore('user')
            if not user_store.isLoggedIn:
                print("🔐 Route protégée - redirection vers la connexion")
                # Rediriger vers la page de connexion
                # return '/login'
                return False
        
        return True
    
    def logging_guard(to_route, from_route):
        """
        Guard pour le logging des navigations
        """
        from_name = from_route.name if from_route else 'null'
        to_name = to_route.name if to_route else 'null'
        
        print(f"🛣️ Navigation: {from_name} → {to_name}")
        return True
    
    def analytics_guard(to_route, from_route):
        """
        Guard pour l'analytics (ex: Google Analytics)
        """
        if to_route and to_route.name:
            print(f"📊 Analytics: page_view - {to_route.name}")
            # Ici on enverrait l'événement à Google Analytics
            # analytics.track_page_view(to_route.name)
        
        return True
    
    # Application des guards
    router.beforeEach(auth_guard)
    router.beforeEach(logging_guard)
    router.afterEach(analytics_guard)
    
    print("✅ Guards de route configurés")

# Configuration du router
router_config = {
    'routes': routes,
    'mode': 'hash',  # ou 'history' pour les URLs propres
    'base': '/',     # base URL pour l'application
}

# Export pour une utilisation facile
def get_router_config():
    """Retourne la configuration du router"""
    return router_config

def get_routes():
    """Retourne la liste des routes"""
    return routes

# Exemple d'utilisation avancée
if __name__ == "__main__":
    print("🧪 Test de configuration des routes:")
    
    for route in routes:
        print(f"📍 {route.name}: {route.path}")
        if route.meta:
            print(f"   📝 Meta: {route.meta}")