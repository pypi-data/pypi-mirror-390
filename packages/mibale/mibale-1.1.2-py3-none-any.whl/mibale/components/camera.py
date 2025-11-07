import base64
from typing import Optional, Dict, Any, List
from .native_components import NativeComponent

class CameraComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.permissions = ['CAMERA', 'WRITE_EXTERNAL_STORAGE']
        self.is_initialized = False
        self.camera_instance = None
        self.current_quality = 'high'
        self.available_resolutions = []
        
    def initialize(self) -> bool:
        """Initialise la caméra"""
        if not self.check_permissions():
            print("📷 Demande des permissions caméra...")
            if not self.request_permissions():
                print("❌ Permissions caméra refusées")
                return False
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            self.camera_instance = bridge.create_camera()
            self.available_resolutions = bridge.camera_get_supported_resolutions()
            self.is_initialized = True
            
            self.emit('camera_ready')
            print("✅ Caméra initialisée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation caméra: {e}")
            return False
    
    def take_picture(self, quality: str = None) -> Optional[str]:
        """Prend une photo et retourne en base64"""
        if not self.ensure_initialized():
            return None
        
        quality = quality or self.current_quality
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            picture_data = bridge.camera_take_picture(quality)
            
            if picture_data:
                picture_base64 = base64.b64encode(picture_data).decode('utf-8')
                self.emit('picture_taken', {
                    'data': picture_base64,
                    'format': 'jpeg',
                    'quality': quality
                })
                return picture_base64
            
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur prise de photo: {e}")
        
        return None
    
    def start_preview(self, surface_view: Any = None):
        """Démarre la prévisualisation"""
        if not self.ensure_initialized():
            return
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.camera_start_preview(surface_view)
            self.emit('preview_started')
            print("📹 Prévisualisation caméra démarrée")
        except Exception as e:
            print(f"❌ Erreur démarrage prévisualisation: {e}")
    
    def stop_preview(self):
        """Arrête la prévisualisation"""
        if self.is_initialized:
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                bridge.camera_stop_preview()
                self.emit('preview_stopped')
                print("📹 Prévisualisation caméra arrêtée")
            except Exception as e:
                print(f"❌ Erreur arrêt prévisualisation: {e}")
    
    def switch_camera(self, facing: str = 'back'):
        """Change de caméra (front/back)"""
        if self.ensure_initialized():
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                bridge.camera_switch(facing)
                self.emit('camera_switched', facing)
                print(f"📷 Caméra changée: {facing}")
            except Exception as e:
                print(f"❌ Erreur changement caméra: {e}")
    
    def set_quality(self, quality: str):
        """Définit la qualité de la caméra"""
        self.current_quality = quality
        if self.is_initialized:
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                bridge.camera_set_quality(quality)
            except Exception as e:
                print(f"❌ Erreur réglage qualité: {e}")
    
    def get_supported_resolutions(self) -> List[Dict]:
        """Retourne les résolutions supportées"""
        return self.available_resolutions
    
    def start_recording(self, output_file: str = None):
        """Démarre l'enregistrement vidéo"""
        if self.ensure_initialized():
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                bridge.camera_start_recording(output_file)
                self.emit('recording_started', output_file)
                print("🎥 Enregistrement vidéo démarré")
            except Exception as e:
                print(f"❌ Erreur démarrage enregistrement: {e}")
    
    def stop_recording(self) -> Optional[str]:
        """Arrête l'enregistrement vidéo"""
        if self.is_initialized:
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                video_file = bridge.camera_stop_recording()
                self.emit('recording_stopped', video_file)
                print("🎥 Enregistrement vidéo arrêté")
                return video_file
            except Exception as e:
                print(f"❌ Erreur arrêt enregistrement: {e}")
        return None
    
    def cleanup(self):
        """Nettoie les ressources de la caméra"""
        self.stop_preview()
        self.stop_recording()
        
        if self.is_initialized:
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                bridge.camera_release()
                self.is_initialized = False
                self.emit('camera_released')
                print("📷 Caméra libérée")
            except Exception as e:
                print(f"❌ Erreur libération caméra: {e}")