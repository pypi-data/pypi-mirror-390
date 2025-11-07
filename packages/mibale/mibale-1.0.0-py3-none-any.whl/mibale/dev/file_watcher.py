import time
from pathlib import Path
from typing import Callable, List, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import threading

class MibaleFileHandler(FileSystemEventHandler):
    """Gestionnaire d'événements de fichiers pour Mibale"""
    
    def __init__(self, callback: Callable, ignored_dirs: List[str] = None):
        self.callback = callback
        self.ignored_dirs = ignored_dirs or [
            '__pycache__', '.git', 'node_modules', 'build', 'dist', 
            '.mypy_cache', '.pytest_cache', '.idea', '.vscode'
        ]
        self.debounce_timers: Dict[str, threading.Timer] = {}
        self.debounce_interval = 0.3  # 300ms pour éviter les multiples déclenchements
    
    def on_modified(self, event: FileSystemEvent):
        """Appelé quand un fichier est modifié"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Ignore les fichiers cachés et les dossiers ignorés
        if self._should_ignore_file(file_path):
            return
        
        # Débouncing pour éviter les multiples rechargements
        self._debounce_file_change(file_path)
    
    def on_created(self, event: FileSystemEvent):
        """Appelé quand un fichier est créé"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if self._should_ignore_file(file_path):
            return
        
        print(f"📄 Nouveau fichier détecté: {file_path}")
        self._debounce_file_change(file_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Appelé quand un fichier est supprimé"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        if self._should_ignore_file(file_path):
            return
        
        print(f"🗑️ Fichier supprimé: {file_path}")
        # Pas de debounce pour les suppressions
        self.callback(file_path)
    
    def on_moved(self, event: FileSystemEvent):
        """Appelé quand un fichier est déplacé"""
        if event.is_directory:
            return
        
        old_path = Path(event.src_path)
        new_path = Path(event.dest_path)
        
        print(f"📂 Fichier déplacé: {old_path} -> {new_path}")
        
        # Traite comme une suppression + création
        if not self._should_ignore_file(new_path):
            self.callback(new_path)
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être ignoré"""
        # Ignore les fichiers cachés
        if file_path.name.startswith('.'):
            return True
        
        # Ignore les dossiers spécifiques
        for part in file_path.parts:
            if part in self.ignored_dirs:
                return True
        
        # Ne surveille que les fichiers .mb et .py
        if file_path.suffix not in ['.mb', '.py', '.json', '.xml']:
            return True
        
        return False
    
    def _debounce_file_change(self, file_path: Path):
        """Implémente le debouncing pour les changements de fichiers"""
        file_key = str(file_path)
        
        # Annule le timer existant pour ce fichier
        if file_key in self.debounce_timers:
            self.debounce_timers[file_key].cancel()
        
        # Crée un nouveau timer
        timer = threading.Timer(self.debounce_interval, self._trigger_callback, [file_path])
        self.debounce_timers[file_key] = timer
        timer.start()
    
    def _trigger_callback(self, file_path: Path):
        """Déclenche le callback après le debounce"""
        # Nettoie le timer
        file_key = str(file_path)
        if file_key in self.debounce_timers:
            del self.debounce_timers[file_key]
        
        # Appelle le callback
        self.callback(file_path)

class FileWatcher:
    """Service de surveillance des fichiers pour le hot-reload"""
    
    def __init__(self, change_callback: Callable, watch_paths: List[str] = None):
        self.change_callback = change_callback
        self.watch_paths = watch_paths or ['.']
        self.observer = Observer()
        self.event_handler = MibaleFileHandler(change_callback)
        self.is_watching = False
        
        print(f"👁️ FileWatcher initialisé pour: {', '.join(self.watch_paths)}")
    
    def start(self):
        """Démarre la surveillance des fichiers"""
        if self.is_watching:
            print("⚠️ FileWatcher déjà en cours d'exécution")
            return
        
        try:
            # Ajoute les chemins à surveiller
            for path in self.watch_paths:
                watch_path = Path(path)
                if watch_path.exists():
                    self.observer.schedule(
                        self.event_handler, 
                        str(watch_path), 
                        recursive=True
                    )
                    print(f"📁 Surveillance de: {watch_path}")
                else:
                    print(f"⚠️ Chemin non trouvé: {watch_path}")
            
            # Démarre l'observateur
            self.observer.start()
            self.is_watching = True
            
            print("✅ Surveillance des fichiers démarrée")
            
        except Exception as e:
            print(f"❌ Erreur démarrage FileWatcher: {e}")
    
    def stop(self):
        """Arrête la surveillance des fichiers"""
        if self.is_watching:
            try:
                self.observer.stop()
                self.observer.join()
                self.is_watching = False
                print("🛑 Surveillance des fichiers arrêtée")
            except Exception as e:
                print(f"❌ Erreur arrêt FileWatcher: {e}")
    
    def add_watch_path(self, path: str):
        """Ajoute un chemin à surveiller"""
        watch_path = Path(path)
        if watch_path.exists():
            self.observer.schedule(
                self.event_handler,
                str(watch_path),
                recursive=True
            )
            print(f"📁 Ajouté à la surveillance: {watch_path}")
        else:
            print(f"⚠️ Chemin non trouvé: {watch_path}")
    
    def remove_watch_path(self, path: str):
        """Retire un chemin de la surveillance"""
        # Note: watchdog ne supporte pas facilement la suppression de watch
        # On redémarre simplement l'observateur avec les nouveaux chemins
        print(f"📁 Retrait de la surveillance: {path}")
        self.stop()
        self.watch_paths = [p for p in self.watch_paths if p != path]
        self.start()
    
    def get_watch_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de surveillance"""
        return {
            'watching_paths': self.watch_paths,
            'is_running': self.is_watching,
            'handler_type': type(self.event_handler).__name__
        }