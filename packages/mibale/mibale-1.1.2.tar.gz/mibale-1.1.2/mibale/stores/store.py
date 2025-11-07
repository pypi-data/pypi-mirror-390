from typing import Dict, Any, List, Callable, Optional
import threading

class Store:
    """Store global Mibale (similaire à Pinia)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.stores: Dict[str, Dict[str, Any]] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.actions: Dict[str, Dict[str, Callable]] = {}
        self.getters: Dict[str, Dict[str, Callable]] = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def define_store(self, name: str, config: Dict[str, Any]):
        """Définit un store"""
        # State initial
        self.stores[name] = config.get('state', {}).copy()
        
        # Getters
        self.getters[name] = config.get('getters', {})
        
        # Actions
        self.actions[name] = config.get('actions', {})
        
        # Initialise les subscribers
        self.subscribers[name] = []
    
    def get_state(self, store_name: str, key: str = None) -> Any:
        """Récupère le state d'un store"""
        if store_name not in self.stores:
            raise ValueError(f"Store {store_name} non trouvé")
        
        store_state = self.stores[store_name]
        
        if key:
            return store_state.get(key)
        return store_state.copy()
    
    def set_state(self, store_name: str, new_state: Dict[str, Any]):
        """Met à jour le state d'un store"""
        if store_name not in self.stores:
            raise ValueError(f"Store {store_name} non trouvé")
        
        old_state = self.stores[store_name].copy()
        self.stores[store_name].update(new_state)
        
        # Notifie les subscribers
        self._notify_subscribers(store_name, old_state, self.stores[store_name])
    
    def dispatch(self, store_name: str, action: str, *args, **kwargs) -> Any:
        """Dispatch une action"""
        if (store_name not in self.actions or 
            action not in self.actions[store_name]):
            raise ValueError(f"Action {action} non trouvée dans store {store_name}")
        
        action_fn = self.actions[store_name][action]
        state = self.stores[store_name]
        
        # Exécute l'action
        result = action_fn(state, *args, **kwargs)
        
        # Notifie les subscribers
        self._notify_subscribers(store_name, state.copy(), state)
        
        return result
    
    def subscribe(self, store_name: str, callback: Callable):
        """Abonnement aux changements d'un store"""
        if store_name not in self.subscribers:
            self.subscribers[store_name] = []
        
        self.subscribers[store_name].append(callback)
    
    def unsubscribe(self, store_name: str, callback: Callable):
        """Désabonnement"""
        if store_name in self.subscribers:
            if callback in self.subscribers[store_name]:
                self.subscribers[store_name].remove(callback)
    
    def _notify_subscribers(self, store_name: str, old_state: Dict, new_state: Dict):
        """Notifie tous les subscribers d'un store"""
        if store_name in self.subscribers:
            for callback in self.subscribers[store_name]:
                try:
                    callback(old_state, new_state)
                except Exception as e:
                    print(f"Erreur dans le subscriber: {e}")
    
    def reset(self, store_name: str):
        """Réinitialise un store à son état initial"""
        # Implémentation de la réinitialisation
        pass

# API Pinia-like
def defineStore(store_id: str, options: Dict[str, Any]) -> Callable:
    """Définit un store (similaire à defineStore de Pinia)"""
    def useStore():
        store = Store.get_instance()
        
        # S'assure que le store est défini
        if store_id not in store.stores:
            store.define_store(store_id, options)
        
        class StoreAPI:
            def __init__(self):
                self._store = store
                self._store_id = store_id
            
            @property
            def state(self):
                return self._store.get_state(self._store_id)
            
            def __getattr__(self, name):
                # Getters
                if (self._store_id in self._store.getters and 
                    name in self._store.getters[self._store_id]):
                    getter_fn = self._store.getters[self._store_id][name]
                    return getter_fn(self.state)
                
                # Actions
                if (self._store_id in self._store.actions and 
                    name in self._store.actions[self._store_id]):
                    action_fn = self._store.actions[self._store_id][name]
                    
                    def wrapped_action(*args, **kwargs):
                        return self._store.dispatch(self._store_id, name, *args, **kwargs)
                    
                    return wrapped_action
                
                # State
                if name in self.state:
                    return self.state[name]
                
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
            
            def __setattr__(self, name, value):
                if name in ['_store', '_store_id']:
                    super().__setattr__(name, value)
                else:
                    # Mutation directe du state
                    self._store.set_state(self._store_id, {name: value})
            
            def $subscribe(self, callback: Callable):
                """Abonnement aux changements"""
                self._store.subscribe(self._store_id, callback)
            
            def $reset(self):
                """Réinitialisation du store"""
                self._store.reset(self._store_id)
            
            def $patch(self, partial_state: Dict[str, Any]):
                """Patch partiel du state"""
                self._store.set_state(self._store_id, partial_state)
        
        return StoreAPI()
    
    return useStore

def createStore(options: Dict[str, Any]) -> Callable:
    """Crée un store (alias de defineStore)"""
    return defineStore(options.get('id', 'default'), options)

def useStore(store_id: str = None):
    """Utilise un store (hook de composition)"""
    if store_id is None:
        # Retourne le store global
        return Store.get_instance()
    
    # Retourne un store spécifique
    store = Store.get_instance()
    if store_id in store.stores:
        # Crée une API pour ce store
        class StoreAccessor:
            def __init__(self):
                self._store = store
                self._store_id = store_id
            
            @property
            def state(self):
                return self._store.get_state(self._store_id)
            
            def dispatch(self, action: str, *args, **kwargs):
                return self._store.dispatch(self._store_id, action, *args, **kwargs)
        
        return StoreAccessor()
    
    raise ValueError(f"Store {store_id} non trouvé")