from typing import Dict, Any, Callable, List
from abc import ABC, abstractmethod

class NativeComponent(ABC):
    """Classe de base pour tous les composants natifs"""
    
    def __init__(self):
        self.permissions = []
        self.event_listeners = {}
        self._is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialise le composant natif"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Nettoie les ressources"""
        pass
    
    def check_permissions(self) -> bool:
        """Vérifie les permissions nécessaires"""
        # Implémentation cross-platform
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.check_permissions(self.permissions)
        except ImportError:
            try:
                from ..ios.bridge import IOSBridge
                bridge = IOSBridge.get_instance()
                return bridge.check_permissions(self.permissions)
            except ImportError:
                # Mode développement - toujours vrai
                return True
    
    def request_permissions(self) -> bool:
        """Demande les permissions"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.request_permissions(self.permissions)
        except ImportError:
            try:
                from ..ios.bridge import IOSBridge
                bridge = IOSBridge.get_instance()
                return bridge.request_permissions(self.permissions)
            except ImportError:
                # Mode développement - toujours vrai
                return True
    
    def on(self, event: str, callback: Callable):
        """Ajoute un écouteur d'événement"""
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        self.event_listeners[event].append(callback)
    
    def emit(self, event: str, data: Any = None):
        """Émet un événement"""
        if event in self.event_listeners:
            for callback in self.event_listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Erreur dans l'écouteur {event}: {e}")
    
    def is_initialized(self) -> bool:
        """Vérifie si le composant est initialisé"""
        return self._is_initialized
    
    def ensure_initialized(self) -> bool:
        """S'assure que le composant est initialisé"""
        if not self._is_initialized:
            return self.initialize()
        return True