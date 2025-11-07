from typing import Dict, Any, List, Optional
from .native_components import NativeComponent

class ARComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.permissions = ['CAMERA']
        self.is_tracking = False
        self.planes_detected = []
        self.anchors = {}
        
    def initialize(self) -> bool:
        """Initialise la réalité augmentée"""
        if not self.check_permissions():
            print("🔄 Demande des permissions caméra AR...")
            if not self.request_permissions():
                print("❌ Permissions caméra AR refusées")
                return False
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.ar_initialize()
            
            if success:
                self.emit('ar_ready')
                print("✅ Réalité augmentée initialisée")
            return success
            
        except Exception as e:
            print(f"❌ Erreur initialisation AR: {e}")
            return False
    
    def start_ar_session(self, surface_view: Any = None):
        """Démarre une session AR"""
        if not self.ensure_initialized():
            return
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.ar_start_session(surface_view)
            self.is_tracking = True
            self.emit('session_started')
            print("🎯 Session AR démarrée")
        except Exception as e:
            print(f"❌ Erreur démarrage session AR: {e}")
    
    def stop_ar_session(self):
        """Arrête la session AR"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.ar_stop_session()
            self.is_tracking = False
            self.planes_detected.clear()
            self.anchors.clear()
            self.emit('session_stopped')
            print("🎯 Session AR arrêtée")
        except Exception as e:
            print(f"❌ Erreur arrêt session AR: {e}")
    
    def add_3d_model(self, model_url: str, position: Dict[str, float]) -> str:
        """Ajoute un modèle 3D"""
        if not self.is_tracking:
            print("❌ Session AR non active")
            return ""
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            model_id = bridge.ar_add_model(model_url, position)
            
            if model_id:
                self.anchors[model_id] = position
                self.emit('model_added', {
                    'id': model_id,
                    'url': model_url,
                    'position': position
                })
                print(f"🧊 Modèle 3D ajouté: {model_id}")
                return model_id
                
        except Exception as e:
            print(f"❌ Erreur ajout modèle 3D: {e}")
        
        return ""
    
    def remove_3d_model(self, model_id: str):
        """Supprime un modèle 3D"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.ar_remove_model(model_id)
            
            if model_id in self.anchors:
                del self.anchors[model_id]
            
            self.emit('model_removed', model_id)
            print(f"🧊 Modèle 3D supprimé: {model_id}")
        except Exception as e:
            print(f"❌ Erreur suppression modèle 3D: {e}")
    
    def move_3d_model(self, model_id: str, new_position: Dict[str, float]):
        """Déplace un modèle 3D"""
        if model_id in self.anchors:
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                bridge.ar_move_model(model_id, new_position)
                
                self.anchors[model_id] = new_position
                self.emit('model_moved', {
                    'id': model_id,
                    'position': new_position
                })
                print(f"🧊 Modèle 3D déplacé: {model_id}")
            except Exception as e:
                print(f"❌ Erreur déplacement modèle 3D: {e}")
    
    def on_plane_detected(self, callback: Callable):
        """Callback quand un plan est détecté"""
        def plane_callback(plane_data):
            self.planes_detected.append(plane_data)
            callback(plane_data)
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.ar_set_plane_callback(plane_callback)
            print("📐 Écouteur plans AR ajouté")
        except Exception as e:
            print(f"❌ Erreur ajout écouteur plans AR: {e}")
    
    def on_anchor_updated(self, callback: Callable):
        """Callback quand un anchor est mis à jour"""
        self.on('anchor_updated', callback)
    
    def get_detected_planes(self) -> List[Dict[str, Any]]:
        """Retourne la liste des plans détectés"""
        return self.planes_detected.copy()
    
    def get_anchors(self) -> Dict[str, Dict[str, float]]:
        """Retourne la liste des anchors"""
        return self.anchors.copy()
    
    def hit_test(self, screen_x: float, screen_y: float) -> Optional[Dict[str, float]]:
        """Test de collision avec les objets AR"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.ar_hit_test(screen_x, screen_y)
        except Exception as e:
            print(f"❌ Erreur hit test AR: {e}")
            return None
    
    def cleanup(self):
        """Nettoie les ressources AR"""
        self.stop_ar_session()
        self.emit('ar_cleaned')
        print("🎯 Réalité augmentée nettoyée")

class VRComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.is_initialized = False
        self.current_mode = 'cardboard'
        
    def initialize(self) -> bool:
        """Initialise la réalité virtuelle"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.is_initialized = bridge.vr_initialize()
            
            if self.is_initialized:
                self.emit('vr_ready')
                print("✅ Réalité virtuelle initialisée")
            return self.is_initialized
            
        except Exception as e:
            print(f"❌ Erreur initialisation VR: {e}")
            return False
    
    def initialize_vr_view(self, surface_view: Any) -> bool:
        """Initialise la vue VR"""
        if not self.ensure_initialized():
            return False
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.vr_initialize_view(surface_view)
            
            if success:
                self.emit('vr_view_ready')
                print("👁️ Vue VR initialisée")
            return success
            
        except Exception as e:
            print(f"❌ Erreur initialisation vue VR: {e}")
            return False
    
    def load_vr_video(self, video_url: str):
        """Charge une vidéo VR"""
        if not self.ensure_initialized():
            return
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.vr_load_video(video_url)
            self.emit('vr_video_loaded', video_url)
            print(f"🎥 Vidéo VR chargée: {video_url}")
        except Exception as e:
            print(f"❌ Erreur chargement vidéo VR: {e}")
    
    def load_vr_scene(self, scene_url: str):
        """Charge une scène VR"""
        if not self.ensure_initialized():
            return
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.vr_load_scene(scene_url)
            self.emit('vr_scene_loaded', scene_url)
            print(f"🏞️ Scène VR chargée: {scene_url}")
        except Exception as e:
            print(f"❌ Erreur chargement scène VR: {e}")
    
    def set_vr_mode(self, mode: str):
        """Définit le mode VR (cardboard, daydream, etc.)"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.vr_set_mode(mode)
            self.current_mode = mode
            self.emit('vr_mode_changed', mode)
            print(f"👓 Mode VR changé: {mode}")
        except Exception as e:
            print(f"❌ Erreur changement mode VR: {e}")
    
    def start_vr_session(self):
        """Démarre une session VR"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.vr_start_session()
            self.emit('vr_session_started')
            print("👁️ Session VR démarrée")
        except Exception as e:
            print(f"❌ Erreur démarrage session VR: {e}")
    
    def stop_vr_session(self):
        """Arrête la session VR"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.vr_stop_session()
            self.emit('vr_session_stopped')
            print("👁️ Session VR arrêtée")
        except Exception as e:
            print(f"❌ Erreur arrêt session VR: {e}")
    
    def on_vr_click(self, callback: Callable):
        """Callback pour les clics en VR"""
        self.on('vr_click', callback)
    
    def on_vr_gaze(self, callback: Callable):
        """Callback pour le regard en VR"""
        self.on('vr_gaze', callback)
    
    def set_vr_controller_enabled(self, enabled: bool):
        """Active/désactive le contrôleur VR"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.vr_set_controller_enabled(enabled)
            self.emit('vr_controller_changed', enabled)
            print(f"🎮 Contrôleur VR: {'activé' if enabled else 'désactivé'}")
        except Exception as e:
            print(f"❌ Erreur contrôleur VR: {e}")
    
    def cleanup(self):
        """Nettoie les ressources VR"""
        self.stop_vr_session()
        self.emit('vr_cleaned')
        print("👁️ Réalité virtuelle nettoyée")