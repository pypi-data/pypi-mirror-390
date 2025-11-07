import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class ComponentState:
    """État d'un composant pour le hot-reload"""
    file_path: Path
    last_hash: str
    last_modified: float
    is_loaded: bool = False
    load_count: int = 0
    error_count: int = 0

class ComponentReloader:
    """Gère le rechargement des composants individuels"""
    
    def __init__(self, dev_server):
        self.dev_server = dev_server
        self.components: Dict[str, ComponentState] = {}
        self.reload_queue = []
        self.reload_lock = threading.Lock()
        self.is_processing = False
        
        print("🔄 ComponentReloader initialisé")
    
    def register_component(self, file_path: Path) -> str:
        """Enregistre un composant pour le hot-reload"""
        component_id = self._generate_component_id(file_path)
        
        if component_id not in self.components:
            self.components[component_id] = ComponentState(
                file_path=file_path,
                last_hash=self._compute_file_hash(file_path),
                last_modified=file_path.stat().st_mtime
            )
            print(f"📦 Composant enregistré: {file_path}")
        
        return component_id
    
    def handle_file_change(self, file_path: Path):
        """Gère le changement d'un fichier"""
        component_id = self._find_component_id(file_path)
        
        if component_id:
            self._queue_component_reload(component_id, file_path)
        else:
            # Fichier non enregistré - peut-être un nouveau composant
            print(f"🆕 Nouveau fichier détecté: {file_path}")
            self._handle_new_component(file_path)
    
    def _queue_component_reload(self, component_id: str, file_path: Path):
        """Ajoute un composant à la file de rechargement"""
        with self.reload_lock:
            # Évite les doublons
            for item in self.reload_queue:
                if item['component_id'] == component_id:
                    return
            
            self.reload_queue.append({
                'component_id': component_id,
                'file_path': file_path,
                'timestamp': time.time()
            })
        
        # Démarre le traitement si pas déjà en cours
        if not self.is_processing:
            self._process_reload_queue()
    
    def _process_reload_queue(self):
        """Traite la file de rechargement"""
        def process():
            self.is_processing = True
            
            while True:
                # Récupère le prochain élément
                with self.reload_lock:
                    if not self.reload_queue:
                        self.is_processing = False
                        break
                    
                    item = self.reload_queue.pop(0)
                
                # Traite le rechargement
                self._reload_component(item['component_id'], item['file_path'])
                
                # Petit délai entre les rechargements
                time.sleep(0.1)
        
        # Traite dans un thread séparé
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def _reload_component(self, component_id: str, file_path: Path):
        """Recharge un composant spécifique"""
        try:
            component_state = self.components[component_id]
            
            # Vérifie si le fichier a vraiment changé
            current_hash = self._compute_file_hash(file_path)
            if current_hash == component_state.last_hash:
                print(f"📦 Composant inchangé: {file_path.name}")
                return
            
            # Met à jour l'état
            component_state.last_hash = current_hash
            component_state.last_modified = file_path.stat().st_mtime
            
            # Recompile le composant
            from ..compiler.mb_compiler import MBCompiler
            compiler = MBCompiler()
            component_data = compiler.compile_file(file_path)
            
            if component_data and component_data.get('component'):
                # Met à jour l'application
                component_name = file_path.stem
                if self.dev_server.current_app:
                    self.dev_server.current_app.update_component(component_name, component_data)
                
                component_state.load_count += 1
                component_state.is_loaded = True
                
                self.dev_server._log_dev(
                    f"🔄 Composant rechargé: {file_path.name} (v{component_state.load_count})", 
                    "success"
                )
                
                # Met à jour les statistiques
                self.dev_server.stats['reload_count'] += 1
                self.dev_server.stats['last_reload'] = time.time()
                
            else:
                component_state.error_count += 1
                self.dev_server._log_dev(
                    f"❌ Erreur rechargement: {file_path.name}", 
                    "error"
                )
            
        except Exception as e:
            if component_id in self.components:
                self.components[component_id].error_count += 1
            
            self.dev_server._log_dev(
                f"❌ Erreur rechargement {file_path.name}: {e}", 
                "error"
            )
            print(f"❌ Erreur rechargement composant: {e}")
    
    def _handle_new_component(self, file_path: Path):
        """Gère un nouveau composant détecté"""
        try:
            # Enregistre le composant
            component_id = self.register_component(file_path)
            
            # Recompile le projet entier
            from ..compiler.mb_compiler import MBCompiler
            compiler = MBCompiler()
            project_data = compiler.compile_project(Path('.'))
            
            # Met à jour l'application
            if self.dev_server.current_app:
                self.dev_server.current_app.configure(project_data)
                self.dev_server.stats['components_loaded'] = len(project_data.get('components', {}))
            
            self.dev_server._log_dev(
                f"🆕 Nouveau composant détecté: {file_path.name}", 
                "success"
            )
            
        except Exception as e:
            self.dev_server._log_dev(
                f"❌ Erreur nouveau composant {file_path.name}: {e}", 
                "error"
            )
    
    def _generate_component_id(self, file_path: Path) -> str:
        """Génère un ID unique pour un composant"""
        path_str = str(file_path.absolute())
        return hashlib.md5(path_str.encode()).hexdigest()[:8]
    
    def _find_component_id(self, file_path: Path) -> Optional[str]:
        """Trouve l'ID d'un composant par son chemin"""
        target_id = self._generate_component_id(file_path)
        return target_id if target_id in self.components else None
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Calcule le hash d'un fichier"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""

class HotReloader:
    """Système principal de hot-reload pour Mibale"""
    
    def __init__(self, dev_server):
        self.dev_server = dev_server
        self.component_reloader = ComponentReloader(dev_server)
        self.project_reloader = ProjectReloader(dev_server)
        self.is_enabled = True
        
        print("🔥 HotReloader initialisé")
    
    def handle_file_change(self, file_path: Path):
        """Gère le changement d'un fichier"""
        if not self.is_enabled:
            return
        
        file_suffix = file_path.suffix.lower()
        
        if file_suffix == '.mb':
            # Composant individuel
            self.component_reloader.handle_file_change(file_path)
        elif file_suffix == '.py' and 'routes' in file_path.name:
            # Configuration des routes
            self.project_reloader.handle_routes_change(file_path)
        elif file_suffix == '.py' and 'store' in file_path.name:
            # Store
            self.project_reloader.handle_store_change(file_path)
        elif file_path.name == 'mibale.config.py':
            # Configuration du projet
            self.project_reloader.handle_config_change(file_path)
        else:
            # Autres fichiers Python - rechargement complet
            self.trigger_full_reload()
    
    def trigger_reload(self):
        """Déclenche un rechargement manuel"""
        self.dev_server._log_dev("🔁 Rechargement manuel déclenché", "info")
        self.trigger_full_reload()
    
    def trigger_full_reload(self):
        """Déclenche un rechargement complet du projet"""
        try:
            self.dev_server._log_dev("🔄 Rechargement complet du projet...", "warning")
            
            # Recompile tout le projet
            from ..compiler.mb_compiler import MBCompiler
            compiler = MBCompiler()
            project_data = compiler.compile_project(Path('.'))
            
            # Recrée l'application
            from ..core.application import MibaleApp
            self.dev_server.current_app = MibaleApp(project_data)
            
            # Remet à jour les statistiques
            self.dev_server.stats['components_loaded'] = len(project_data.get('components', {}))
            self.dev_server.stats['reload_count'] += 1
            self.dev_server.stats['last_reload'] = time.time()
            
            # Re-rend l'application
            if self.dev_server.render_engine:
                success = self.dev_server.render_engine.render_component(project_data)
                if success:
                    self.dev_server._log_dev("✅ Rechargement complet réussi", "success")
                else:
                    self.dev_server._log_dev("❌ Erreur rendu après rechargement", "error")
            
        except Exception as e:
            self.dev_server._log_dev(f"❌ Erreur rechargement complet: {e}", "error")
    
    def enable(self):
        """Active le hot-reload"""
        self.is_enabled = True
        self.dev_server._log_dev("🔥 Hot-reload activé", "success")
    
    def disable(self):
        """Désactive le hot-reload"""
        self.is_enabled = False
        self.dev_server._log_dev("❄️ Hot-reload désactivé", "warning")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du hot-reload"""
        return {
            'enabled': self.is_enabled,
            'components_registered': len(self.component_reloader.components),
            'reload_queue_size': len(self.component_reloader.reload_queue),
            'total_reloads': self.dev_server.stats['reload_count']
        }
    
    def cleanup(self):
        """Nettoie les ressources du hot-reload"""
        self.component_reloader.reload_queue.clear()
        self.components.clear()

class ProjectReloader:
    """Gère le rechargement de la configuration du projet"""
    
    def __init__(self, dev_server):
        self.dev_server = dev_server
    
    def handle_routes_change(self, file_path: Path):
        """Gère le changement des routes"""
        self.dev_server._log_dev("🛣️ Routes modifiées - rechargement...", "info")
        self.dev_server.hot_reloader.trigger_full_reload()
    
    def handle_store_change(self, file_path: Path):
        """Gère le changement des stores"""
        self.dev_server._log_dev("🏪 Store modifié - rechargement...", "info")
        self.dev_server.hot_reloader.trigger_full_reload()
    
    def handle_config_change(self, file_path: Path):
        """Gère le changement de configuration"""
        self.dev_server._log_dev("⚙️ Configuration modifiée - rechargement...", "info")
        self.dev_server.hot_reloader.trigger_full_reload()