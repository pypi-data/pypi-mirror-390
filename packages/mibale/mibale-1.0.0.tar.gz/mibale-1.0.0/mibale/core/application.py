from typing import Dict, Any, List, Optional, Callable
from .component import BaseComponent
from ..router import Router
from ..stores import Store

class MibaleApp:
    """Application Mibale principale (similaire à Vue app)"""
    
    _current_instance = None
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.router = Router()
        self.store = Store()
        self.components: Dict[str, Any] = {}
        self.directives: Dict[str, Any] = {}
        self.plugins: List[Any] = []
        self._is_mounted = False
        
        # Instance globale
        MibaleApp._current_instance = self
        
        # Initialisation
        self._init_router()
        self._init_store()
        self._init_plugins()
    
    @classmethod
    def get_current_app(cls) -> 'MibaleApp':
        """Retourne l'instance courante de l'app"""
        return cls._current_instance
    
    def _init_router(self):
        """Initialise le routeur"""
        if 'routes' in self.config:
            for route_config in self.config['routes']:
                self.router.add_route(route_config)
    
    def _init_store(self):
        """Initialise le store"""
        if 'stores' in self.config:
            for store_name, store_config in self.config['stores'].items():
                self.store.define_store(store_name, store_config)
    
    def _init_plugins(self):
        """Initialise les plugins"""
        for plugin in self.plugins:
            if hasattr(plugin, 'install'):
                plugin.install(self)
    
    def component(self, name: str, component: Any):
        """Enregistre un composant global"""
        self.components[name] = component
    
    def directive(self, name: str, directive: Any):
        """Enregistre une directive globale"""
        self.directives[name] = directive
    
    def use(self, plugin: Any):
        """Utilise un plugin"""
        self.plugins.append(plugin)
        if hasattr(plugin, 'install'):
            plugin.install(self)
    
    def mount(self, selector: str = None):
        """Monte l'application (comme app.mount() dans Vue)"""
        print("🚀 Montage de l'application Mibale...")
        
        # Démarre le routeur
        self.router.start()
        
        # Rend l'écran initial
        if self.router.current_route:
            self._render_current_route()
        
        self._is_mounted = True
        print("✅ Application Mibale montée!")
    
    def _render_current_route(self):
        """Rend la route courante"""
        from ..render.render_engine import RenderEngine
        
        if not hasattr(self, '_render_engine'):
            self._render_engine = RenderEngine()
            self._render_engine.initialize()
        
        route = self.router.current_route
        if route and route.component:
            # Trouve le composant
            component_class = self.components.get(route.component.__name__, route.component)
            
            # Crée l'instance du composant
            component_instance = component_class()
            
            # Rend le composant
            success = self._render_engine.render_component(component_instance)
            
            if success:
                print(f"📍 Route rendue: {route.path}")
            else:
                print(f"❌ Erreur rendu route: {route.path}")
    
    def unmount(self):
        """Démonte l'application"""
        self._is_mounted = False
        print("🛑 Application Mibale démontée")

def create_app(config: Dict[str, Any] = None) -> MibaleApp:
    """Crée une application Mibale (comme createApp() dans Vue)"""
    return MibaleApp(config)