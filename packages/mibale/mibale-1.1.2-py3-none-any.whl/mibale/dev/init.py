"""
Module de développement Mibale
Serveur de développement avec hot-reload et outils de build
"""

from .dev_server import MibaleDevServer
from .file_watcher import FileWatcher, MibaleFileHandler
from .hot_reloader import HotReloader, ComponentReloader

__all__ = [
    'MibaleDevServer',
    'FileWatcher',
    'MibaleFileHandler', 
    'HotReloader',
    'ComponentReloader'
]

def start_dev_server(port=3000, host='localhost', platform='auto'):
    """Démarre le serveur de développement"""
    server = MibaleDevServer(port=port, host=host, platform=platform)
    return server.start()