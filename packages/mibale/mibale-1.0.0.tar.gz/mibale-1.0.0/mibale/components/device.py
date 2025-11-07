from typing import Dict, Any
from .native_components import NativeComponent

class DeviceComponent(NativeComponent):
    """Composant pour les informations device"""
    
    def __init__(self):
        super().__init__()
    
    def initialize(self):
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Retourne les informations du device"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            info = bridge.device_get_info()
            self.emit('device_info', info)
            return info
        except Exception as e:
            print(f"❌ Erreur lecture info device: {e}")
            return {
                'model': 'Unknown',
                'manufacturer': 'Unknown',
                'platform': 'unknown'
            }
    
    def get_battery_info(self) -> Dict[str, Any]:
        """Retourne les informations de la batterie"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.device_get_battery_info()
        except Exception as e:
            print(f"❌ Erreur lecture info batterie: {e}")
            return {
                'level': 100,
                'status': 'unknown',
                'health': 'good'
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Retourne les informations réseau"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.device_get_network_info()
        except Exception as e:
            print(f"❌ Erreur lecture info réseau: {e}")
            return {
                'type': 'unknown',
                'connected': False,
                'ssid': None
            }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Retourne les informations de stockage"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.device_get_storage_info()
        except Exception as e:
            print(f"❌ Erreur lecture info stockage: {e}")
            return {
                'total': 0,
                'available': 0,
                'used': 0
            }
    
    def vibrate(self, duration: int = 100):
        """Fait vibrer le device"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.device_vibrate(duration)
            self.emit('vibrated', duration)
            print(f"📳 Vibration de {duration}ms")
        except Exception as e:
            print(f"❌ Erreur vibration: {e}")
    
    def set_brightness(self, level: float):
        """Définit la luminosité de l'écran (0.0 à 1.0)"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.device_set_brightness(level)
            self.emit('brightness_changed', level)
            print(f"💡 Luminosité réglée à {level}")
        except Exception as e:
            print(f"❌ Erreur réglage luminosité: {e}")