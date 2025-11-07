from typing import Any, Callable, Dict, List
import inspect

class Ref:
    """Référence réactive (similaire à Vue ref)"""
    
    def __init__(self, value: Any):
        self._value = value
        self._subscribers = []
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = new_value
        self._notify(old_value, new_value)
    
    def _notify(self, old_value, new_value):
        for subscriber in self._subscribers:
            subscriber(new_value, old_value)
    
    def subscribe(self, callback: Callable):
        self._subscribers.append(callback)

def ref(value: Any) -> Ref:
    """Crée une référence réactive"""
    return Ref(value)

def reactive(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Crée un objet réactif (similaire à Vue reactive)"""
    # Implémentation simplifiée de la réactivité
    return obj

def computed(getter: Callable) -> Any:
    """Crée une valeur calculée (similaire à Vue computed)"""
    # Implémentation simplifiée
    return getter()

def watch(source: Any, callback: Callable, immediate: bool = False):
    """Observe les changements (similaire à Vue watch)"""
    # Implémentation simplifiée
    if hasattr(source, 'subscribe'):
        source.subscribe(callback)
    
    if immediate:
        callback(source.value if hasattr(source, 'value') else source)

class Effect:
    """Effet réactif (similaire à Vue effect)"""
    
    def __init__(self, fn: Callable):
        self.fn = fn
        self.dependencies = set()
    
    def run(self):
        # Exécute la fonction et collecte les dépendances
        self.fn()
    
    def track(self, target):
        self.dependencies.add(target)
    
    def trigger(self):
        self.run()

def effect(fn: Callable):
    """Crée un effet réactif"""
    e = Effect(fn)
    e.run()
    return e