"""
Module iOS pour Mibale Framework
Support pour le rendu natif iOS via PyObjC
"""

from .bridge import IOSBridge
from .renderer.ios_renderer import IOSRenderer
from .renderer.view_factory import IOSViewFactory

__all__ = [
    'IOSBridge',
    'IOSRenderer', 
    'IOSViewFactory'
]

def is_ios_available():
    """Vérifie si l'environnement iOS est disponible"""
    try:
        import objc
        return True
    except ImportError:
        return False

def initialize_ios():
    """Initialise le module iOS"""
    if is_ios_available():
        print("✅ Module iOS initialisé")
        return True
    else:
        print("❌ PyObjC non disponible - mode iOS désactivé")
        return False