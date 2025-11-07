from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from ..core.component import BaseComponent

@dataclass
class Route:
    """Représente une route (similaire à Vue Router)"""
    path: str
    component: Any
    name: Optional[str] = None
    props: Dict = None
    meta: Dict = None
    children: List['Route'] = None

class Router:
    """Routeur Mibale (similaire à Vue Router)"""
    
    def __init__(self, routes: List[Route] = None, mode: str = 'hash'):
        self.routes = routes or []
        self.mode = mode
        self.current_route: Optional[Route] = None
        self.history: List[str] = []
        
        # Guards
        self.before_each_guards: List[Callable] = []
        self.after_each_guards: List[Callable] = []
        
        # Composant RouterView
        self.router_view = None
    
    def add_route(self, route: Route):
        """Ajoute une route au routeur"""
        self.routes.append(route)
    
    def push(self, path: str):
        """Navigation vers une route (comme router.push())"""
        print(f"📍 Navigation vers: {path}")
        
        target_route = self._find_route(path)
        
        if not target_route:
            print(f"❌ Route non trouvée: {path}")
            return False
        
        # Before each guards
        for guard in self.before_each_guards:
            guard_result = guard(self.current_route, target_route)
            if guard_result is False:
                return False
            elif isinstance(guard_result, str):
                # Redirection
                return self.push(guard_result)
        
        # Avant de changer la route
        if self.current_route:
            self._call_component_hook(self.current_route.component, 'before_route_leave')
        
        self._call_component_hook(target_route.component, 'before_route_enter')
        
        # Changement de route
        self.history.append(path)
        old_route = self.current_route
        self.current_route = target_route
        
        # After each guards
        for guard in self.after_each_guards:
            guard(self.current_route, old_route)
        
        # Mise à jour du rendu
        self._render_route()
        
        # Hooks après navigation
        if old_route:
            self._call_component_hook(old_route.component, 'after_route_leave')
        
        self._call_component_hook(target_route.component, 'after_route_enter')
        
        return True
    
    def replace(self, path: str):
        """Remplace la route courante"""
        if self.history:
            self.history.pop()
        return self.push(path)
    
    def back(self):
        """Retour arrière"""
        if len(self.history) > 1:
            self.history.pop()
            previous_path = self.history[-1]
            return self.push(previous_path)
        return False
    
    def forward(self):
        """Avant"""
        # Implémentation simplifiée
        pass
    
    def go(self, n: int):
        """Navigation relative"""
        if n < 0:
            for _ in range(abs(n)):
                self.back()
        else:
            for _ in range(n):
                # Implémentation forward
                pass
    
    def beforeEach(self, guard: Callable):
        """Guard global before each"""
        self.before_each_guards.append(guard)
    
    def afterEach(self, guard: Callable):
        """Guard global after each"""
        self.after_each_guards.append(guard)
    
    def beforeResolve(self, guard: Callable):
        """Guard before resolve"""
        # Similaire à beforeEach mais après les guards de composant
        pass
    
    def onReady(self, callback: Callable):
        """Callback quand le routeur est prêt"""
        # Appelé après la navigation initiale
        if self.current_route:
            callback()
    
    def _find_route(self, path: str) -> Optional[Route]:
        """Trouve une route par son chemin"""
        for route in self.routes:
            if route.path == path:
                return route
            
            # Support des paramètres dynamiques basique
            if ':' in route.path:
                # Conversion simple: /user/:id -> pattern
                pattern = route.path.replace(':', '(?P<').replace('/', '\\/') + '>)'
                import re
                match = re.match(pattern, path)
                if match:
                    return route
        
        return None
    
    def _render_route(self):
        """Affiche la route courante"""
        if self.current_route and self.router_view:
            # Met à jour le RouterView
            self.router_view.current_component = self.current_route.component
            self.router_view.route_params = self._extract_params(self.current_route)
            
            # Déclenche le rendu
            if hasattr(self.router_view, 'update'):
                self.router_view.update()
    
    def _extract_params(self, route: Route) -> Dict[str, Any]:
        """Extrait les paramètres de route"""
        params = {}
        if ':' in route.path:
            # Extraction basique des paramètres
            path_parts = route.path.split('/')
            current_parts = self.current_route.path.split('/')
            
            for i, part in enumerate(path_parts):
                if part.startswith(':'):
                    param_name = part[1:]
                    if i < len(current_parts):
                        params[param_name] = current_parts[i]
        
        return params
    
    def _call_component_hook(self, component_class: Any, hook_name: str):
        """Appelle un hook de route sur un composant"""
        try:
            component_instance = component_class()
            if hasattr(component_instance, hook_name):
                getattr(component_instance, hook_name)()
        except:
            pass
    
    def start(self):
        """Démarre le routeur"""
        if self.routes:
            initial_route = self.routes[0].path
            self.push(initial_route)

class RouterView(BaseComponent):
    """Composant qui affiche la vue routée courante"""
    
    def __init__(self):
        super().__init__()
        self.current_component = None
        self.route_params = {}
        self.router = useRouter()
        
        # Enregistre ce RouterView dans le routeur
        self.router.router_view = self
    
    def render(self):
        if self.current_component:
            component_instance = self.current_component()
            component_instance.props = self.route_params
            return component_instance.render()
        return None
    
    def on_mount(self):
        print("RouterView mounted")
    
    def on_destroy(self):
        print("RouterView destroyed")

# Hooks de composition (similaire à Vue)
def useRouter() -> Router:
    """Hook pour utiliser le routeur dans les composants"""
    from ..core.application import MibaleApp
    app = MibaleApp.get_current_app()
    return app.router

def useRoute() -> Route:
    """Hook pour utiliser la route courante"""
    router = useRouter()
    return router.current_route

# Fonctions utilitaires
def createRouter(options: Dict[str, Any]) -> Router:
    """Crée une instance de routeur (comme createRouter dans Vue)"""
    return Router(
        routes=options.get('routes', []),
        mode=options.get('mode', 'hash')
    )