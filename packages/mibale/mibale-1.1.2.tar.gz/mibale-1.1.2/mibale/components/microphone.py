import base64
from typing import Optional, Dict, Any, List
from .native_components import NativeComponent

class MicrophoneComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.permissions = ['RECORD_AUDIO']
        self.is_recording = False
        self.audio_format = 'mp3'
        self.audio_source = 'mic'
        self.sample_rate = 44100
        self.bit_rate = 128000
        
    def initialize(self) -> bool:
        """Initialise le microphone"""
        if not self.check_permissions():
            print("🎤 Demande des permissions microphone...")
            if not self.request_permissions():
                print("❌ Permissions microphone refusées")
                return False
        return True
    
    def start_recording(self, file_path: str = None) -> bool:
        """Démarre l'enregistrement audio"""
        if not self.initialize():
            return False
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            success = bridge.audio_start_recording(
                file_path, 
                self.audio_format, 
                self.audio_source,
                self.sample_rate,
                self.bit_rate
            )
            
            if success:
                self.is_recording = True
                self.emit('recording_started', {
                    'file_path': file_path,
                    'format': self.audio_format,
                    'sample_rate': self.sample_rate
                })
                print("🎤 Enregistrement audio démarré")
                return True
                
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur démarrage enregistrement: {e}")
        
        return False
    
    def stop_recording(self) -> Optional[str]:
        """Arrête l'enregistrement et retourne le fichier"""
        if not self.is_recording:
            return None
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            audio_file = bridge.audio_stop_recording()
            self.is_recording = False
            
            if audio_file:
                # Lecture du fichier en base64
                with open(audio_file, 'rb') as f:
                    audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                self.emit('recording_stopped', {
                    'file_path': audio_file,
                    'data': audio_base64,
                    'format': self.audio_format
                })
                
                print("🎤 Enregistrement audio arrêté")
                return audio_base64
                
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur arrêt enregistrement: {e}")
        
        return None
    
    def get_audio_level(self) -> float:
        """Retourne le niveau audio actuel (0.0 à 1.0)"""
        if self.is_recording:
            try:
                from ..android.bridge import AndroidBridge
                bridge = AndroidBridge.get_instance()
                return bridge.audio_get_level()
            except Exception as e:
                print(f"❌ Erreur lecture niveau audio: {e}")
        return 0.0
    
    def set_audio_format(self, format: str):
        """Définit le format audio"""
        supported_formats = ['mp3', 'aac', 'wav', 'flac']
        if format in supported_formats:
            self.audio_format = format
    
    def set_audio_source(self, source: str):
        """Définit la source audio"""
        self.audio_source = source
    
    def set_sample_rate(self, sample_rate: int):
        """Définit le taux d'échantillonnage"""
        self.sample_rate = sample_rate
    
    def set_bit_rate(self, bit_rate: int):
        """Définit le débit binaire"""
        self.bit_rate = bit_rate
    
    def get_supported_formats(self) -> List[str]:
        """Retourne les formats audio supportés"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.audio_get_supported_formats()
        except:
            return ['mp3', 'aac', 'wav']
    
    def cleanup(self):
        """Nettoie les ressources"""
        if self.is_recording:
            self.stop_recording()
        self.emit('microphone_released')
        print("🎤 Microphone libéré")