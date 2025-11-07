from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from .reactive import reactive, computed, watch, ref

class BaseComponent(ABC):
    """Classe de base pour tous les composants Mibale"""
    
    def __init__(self):
        self.props = {}
        self.emits = []
        self.slots = {}
        self.setup_state = {}
        self.lifecycle_hooks = {
            'before_create': [],
            'created': [],
            'before_mount': [],
            'mounted': [],
            'before_update': [],
            'updated': [],
            'before_unmount': [],
            'unmounted': []
        }
        
        # État réactif
        self._state = {}
        self._computed = {}
        self._watchers = []
        
        # Initialisation
        self._run_lifecycle('before_create')
        self.setup()
        self._run_lifecycle('created')
    
    def setup(self):
        """Hook setup (similaire à Vue 3 Composition API)"""
        pass
    
    def on_before_create(self, hook: Callable):
        self.lifecycle_hooks['before_create'].append(hook)
    
    def on_created(self, hook: Callable):
        self.lifecycle_hooks['created'].append(hook)
    
    def on_before_mount(self, hook: Callable):
        self.lifecycle_hooks['before_mount'].append(hook)
    
    def on_mounted(self, hook: Callable):
        self.lifecycle_hooks['mounted'].append(hook)
    
    def on_before_update(self, hook: Callable):
        self.lifecycle_hooks['before_update'].append(hook)
    
    def on_updated(self, hook: Callable):
        self.lifecycle_hooks['updated'].append(hook)
    
    def on_before_unmount(self, hook: Callable):
        self.lifecycle_hooks['before_unmount'].append(hook)
    
    def on_unmounted(self, hook: Callable):
        self.lifecycle_hooks['unmounted'].append(hook)
    
    def _run_lifecycle(self, hook_name: str):
        """Exécute les hooks de lifecycle"""
        for hook in self.lifecycle_hooks[hook_name]:
            hook()
    
    def mount(self):
        """Monte le composant"""
        self._run_lifecycle('before_mount')
        self.on_mount()
        self._run_lifecycle('mounted')
    
    def unmount(self):
        """Démonte le composant"""
        self._run_lifecycle('before_unmount')
        self.on_destroy()
        self._run_lifecycle('unmounted')
    
    def update(self):
        """Met à jour le composant"""
        self._run_lifecycle('before_update')
        self.on_update()
        self._run_lifecycle('updated')
    
    # Hooks de lifecycle à surcharger
    def on_mount(self):
        """Appelé quand le composant est monté"""
        pass
    
    def on_destroy(self):
        """Appelé quand le composant est détruit"""
        pass
    
    def on_update(self):
        """Appelé quand le composant est mis à jour"""
        pass
    
    # Méthodes de template
    def render(self) -> Any:
        """Méthode de rendu (à surcharger ou générée par le compilateur)"""
        return None
    
    # Méthodes utilitaires React-like
    def set_state(self, new_state: Dict[str, Any]):
        """Met à jour l'état et déclenche un re-rendu"""
        self._state.update(new_state)
        self.update()
    
    def get_state(self, key: str = None) -> Any:
        """Récupère l'état"""
        if key:
            return self._state.get(key)
        return self._state.copy()

def defineComponent(component_class):
    """Décorateur pour définir un composant (similaire à Vue)"""
    return component_class