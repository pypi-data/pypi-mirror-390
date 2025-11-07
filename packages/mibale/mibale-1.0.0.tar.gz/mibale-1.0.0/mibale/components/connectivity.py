from typing import Dict, List, Any, Callable
from .native_components import NativeComponent

class BluetoothComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.permissions = ['BLUETOOTH', 'BLUETOOTH_ADMIN', 'ACCESS_FINE_LOCATION']
        self.is_scanning = False
        self.connected_devices = []
        self.discovered_devices = []
        
    def initialize(self) -> bool:
        """Initialise Bluetooth"""
        if not self.check_permissions():
            print("📡 Demande des permissions Bluetooth...")
            if not self.request_permissions():
                print("❌ Permissions Bluetooth refusées")
                return False
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.bluetooth_initialize()
            if success:
                self.emit('bluetooth_ready')
                print("✅ Bluetooth initialisé")
            return success
        except Exception as e:
            print(f"❌ Erreur initialisation Bluetooth: {e}")
            return False
    
    def start_scan(self) -> bool:
        """Démarre le scan des devices Bluetooth"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.is_scanning = bridge.bluetooth_start_scan()
            
            if self.is_scanning:
                self.emit('scan_started')
                print("🔍 Scan Bluetooth démarré")
            return self.is_scanning
        except Exception as e:
            print(f"❌ Erreur démarrage scan Bluetooth: {e}")
            return False
    
    def stop_scan(self):
        """Arrête le scan"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.bluetooth_stop_scan()
            self.is_scanning = False
            self.emit('scan_stopped')
            print("🔍 Scan Bluetooth arrêté")
        except Exception as e:
            print(f"❌ Erreur arrêt scan Bluetooth: {e}")
    
    def get_paired_devices(self) -> List[Dict]:
        """Retourne les devices appairés"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.bluetooth_get_paired_devices()
        except Exception as e:
            print(f"❌ Erreur lecture devices appairés: {e}")
            return []
    
    def connect_device(self, device_address: str) -> bool:
        """Connecte un device"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.bluetooth_connect(device_address)
            
            if success:
                self.connected_devices.append(device_address)
                self.emit('device_connected', device_address)
                print(f"📱 Device Bluetooth connecté: {device_address}")
            return success
        except Exception as e:
            print(f"❌ Erreur connexion device: {e}")
            return False
    
    def send_data(self, data: bytes, device_address: str = None) -> bool:
        """Envoie des données"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.bluetooth_send_data(data, device_address)
            
            if success:
                self.emit('data_sent', {'data': data, 'device': device_address})
            return success
        except Exception as e:
            print(f"❌ Erreur envoi données Bluetooth: {e}")
            return False
    
    def on_device_found(self, callback: Callable):
        """Callback quand un device est trouvé"""
        def discovery_callback(device):
            self.discovered_devices.append(device)
            callback(device)
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.bluetooth_set_discovery_callback(discovery_callback)
            print("📡 Écouteur découverte Bluetooth ajouté")
        except Exception as e:
            print(f"❌ Erreur ajout écouteur découverte: {e}")
    
    def on_data_received(self, callback: Callable):
        """Callback quand des données sont reçues"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.bluetooth_set_data_callback(callback)
            print("📡 Écouteur données Bluetooth ajouté")
        except Exception as e:
            print(f"❌ Erreur ajout écouteur données: {e}")
    
    def cleanup(self):
        """Nettoie les ressources Bluetooth"""
        if self.is_scanning:
            self.stop_scan()
        self.emit('bluetooth_cleaned')
        print("📡 Bluetooth nettoyé")

class NFCComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.permissions = ['NFC']
        self.is_enabled = False
        
    def initialize(self) -> bool:
        """Initialise NFC"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.is_enabled = bridge.nfc_initialize()
            
            if self.is_enabled:
                self.emit('nfc_ready')
                print("✅ NFC initialisé")
            return self.is_enabled
        except Exception as e:
            print(f"❌ Erreur initialisation NFC: {e}")
            return False
    
    def enable_foreground_dispatch(self):
        """Active la détection NFC en foreground"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.nfc_enable_foreground_dispatch()
            self.emit('foreground_enabled')
            print("📲 Détection NFC foreground activée")
        except Exception as e:
            print(f"❌ Erreur activation NFC foreground: {e}")
    
    def disable_foreground_dispatch(self):
        """Désactive la détection NFC"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.nfc_disable_foreground_dispatch()
            self.emit('foreground_disabled')
            print("📲 Détection NFC foreground désactivée")
        except Exception as e:
            print(f"❌ Erreur désactivation NFC foreground: {e}")
    
    def write_tag(self, data: str, tag_type: str = "TEXT") -> bool:
        """Écrit sur un tag NFC"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.nfc_write_tag(data, tag_type)
            
            if success:
                self.emit('tag_written', {'data': data, 'type': tag_type})
                print(f"📝 Tag NFC écrit: {data}")
            return success
        except Exception as e:
            print(f"❌ Erreur écriture tag NFC: {e}")
            return False
    
    def on_tag_discovered(self, callback: Callable):
        """Callback quand un tag NFC est détecté"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.nfc_set_tag_callback(callback)
            print("📡 Écouteur tags NFC ajouté")
        except Exception as e:
            print(f"❌ Erreur ajout écouteur NFC: {e}")
    
    def cleanup(self):
        """Nettoie les ressources NFC"""
        self.disable_foreground_dispatch()
        self.emit('nfc_cleaned')
        print("📲 NFC nettoyé")

class WiFiComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.permissions = ['ACCESS_WIFI_STATE', 'CHANGE_WIFI_STATE', 'ACCESS_FINE_LOCATION']
        self.available_networks = []
        
    def initialize(self) -> bool:
        return True
    
    def scan_networks(self) -> List[Dict]:
        """Scan les réseaux WiFi disponibles"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.available_networks = bridge.wifi_scan_networks()
            self.emit('networks_scanned', self.available_networks)
            print(f"📶 {len(self.available_networks)} réseaux WiFi trouvés")
            return self.available_networks
        except Exception as e:
            print(f"❌ Erreur scan WiFi: {e}")
            return []
    
    def connect_to_network(self, ssid: str, password: str) -> bool:
        """Se connecte à un réseau WiFi"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.wifi_connect(ssid, password)
            
            if success:
                self.emit('wifi_connected', {'ssid': ssid})
                print(f"📶 Connecté au WiFi: {ssid}")
            return success
        except Exception as e:
            print(f"❌ Erreur connexion WiFi: {e}")
            return False
    
    def get_connected_network(self) -> Dict[str, Any]:
        """Retourne les infos du réseau connecté"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.wifi_get_connected_network()
        except Exception as e:
            print(f"❌ Erreur lecture réseau connecté: {e}")
            return {}
    
    def enable_hotspot(self, ssid: str, password: str) -> bool:
        """Active le hotspot"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            success = bridge.wifi_enable_hotspot(ssid, password)
            
            if success:
                self.emit('hotspot_enabled', {'ssid': ssid})
                print(f"📡 Hotspot activé: {ssid}")
            return success
        except Exception as e:
            print(f"❌ Erreur activation hotspot: {e}")
            return False
    
    def disable_hotspot(self):
        """Désactive le hotspot"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.wifi_disable_hotspot()
            self.emit('hotspot_disabled')
            print("📡 Hotspot désactivé")
        except Exception as e:
            print(f"❌ Erreur désactivation hotspot: {e}")