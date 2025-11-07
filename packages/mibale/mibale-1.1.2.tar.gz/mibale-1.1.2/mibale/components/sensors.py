from typing import Dict, List, Any, Callable
from .native_components import NativeComponent

class SensorComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.available_sensors = {}
        self.active_sensors = {}
        self.sensor_listeners = {}
        
    def initialize(self):
        """Initialise le gestionnaire de capteurs"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.available_sensors = bridge.sensors_get_available()
            self.emit('sensors_ready', self.available_sensors)
            print("📡 Gestionnaire de capteurs initialisé")
            return True
        except Exception as e:
            print(f"❌ Erreur initialisation capteurs: {e}")
            return False
    
    def get_available_sensors(self) -> Dict[str, Any]:
        """Retourne la liste des capteurs disponibles"""
        return self.available_sensors
    
    def start_sensor(self, sensor_type: str, interval: int = 100000) -> bool:
        """Démarre un capteur"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            success = bridge.sensor_start(sensor_type, interval)
            if success:
                self.active_sensors[sensor_type] = interval
                self.emit('sensor_started', sensor_type)
                print(f"📡 Capteur {sensor_type} démarré")
                return True
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur démarrage capteur {sensor_type}: {e}")
        
        return False
    
    def stop_sensor(self, sensor_type: str):
        """Arrête un capteur"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            bridge.sensor_stop(sensor_type)
            if sensor_type in self.active_sensors:
                del self.active_sensors[sensor_type]
            self.emit('sensor_stopped', sensor_type)
            print(f"📡 Capteur {sensor_type} arrêté")
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur arrêt capteur {sensor_type}: {e}")
    
    def on_sensor_data(self, sensor_type: str, callback: Callable):
        """Écoute les données d'un capteur"""
        def sensor_callback(data):
            callback({
                'sensor': sensor_type,
                'data': data,
                'timestamp': data.get('timestamp', 0)
            })
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.sensor_set_listener(sensor_type, sensor_callback)
            
            if sensor_type not in self.sensor_listeners:
                self.sensor_listeners[sensor_type] = []
            self.sensor_listeners[sensor_type].append(callback)
            
            print(f"📡 Écouteur ajouté pour {sensor_type}")
        except Exception as e:
            print(f"❌ Erreur ajout écouteur {sensor_type}: {e}")
    
    def get_sensor_data(self, sensor_type: str) -> Dict[str, Any]:
        """Retourne les données actuelles d'un capteur"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.sensor_get_data(sensor_type)
        except Exception as e:
            print(f"❌ Erreur lecture données {sensor_type}: {e}")
            return {}
    
    def cleanup(self):
        """Nettoie tous les capteurs"""
        for sensor_type in list(self.active_sensors.keys()):
            self.stop_sensor(sensor_type)
        self.emit('sensors_cleaned')
        print("📡 Tous les capteurs nettoyés")

class AccelerometerSensor:
    """Capteur accéléromètre"""
    
    def __init__(self, sensor_component: SensorComponent):
        self.sensor = sensor_component
        self.type = 'accelerometer'
    
    def start(self, interval: int = 100000):
        """Démarre l'accéléromètre"""
        return self.sensor.start_sensor(self.type, interval)
    
    def stop(self):
        """Arrête l'accéléromètre"""
        self.sensor.stop_sensor(self.type)
    
    def on_data(self, callback: Callable):
        """Écoute les données de l'accéléromètre"""
        self.sensor.on_sensor_data(self.type, callback)
    
    def get_current_acceleration(self) -> Dict[str, float]:
        """Retourne l'accélération actuelle"""
        data = self.sensor.get_sensor_data(self.type)
        return {
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'z': data.get('z', 0)
        }

class GyroscopeSensor:
    """Capteur gyroscope"""
    
    def __init__(self, sensor_component: SensorComponent):
        self.sensor = sensor_component
        self.type = 'gyroscope'
    
    def start(self, interval: int = 100000):
        """Démarre le gyroscope"""
        return self.sensor.start_sensor(self.type, interval)
    
    def stop(self):
        """Arrête le gyroscope"""
        self.sensor.stop_sensor(self.type)
    
    def on_data(self, callback: Callable):
        """Écoute les données du gyroscope"""
        self.sensor.on_sensor_data(self.type, callback)
    
    def get_current_rotation(self) -> Dict[str, float]:
        """Retourne la rotation actuelle"""
        data = self.sensor.get_sensor_data(self.type)
        return {
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'z': data.get('z', 0)
        }

class GPSComponent(NativeComponent):
    """Composant GPS"""
    
    def __init__(self):
        super().__init__()
        self.permissions = ['ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION']
        self.is_tracking = False
        self.update_interval = 1000
        self.min_distance = 0
        self.last_location = None
        
    def initialize(self) -> bool:
        """Initialise le GPS"""
        if not self.check_permissions():
            print("📍 Demande des permissions GPS...")
            if not self.request_permissions():
                print("❌ Permissions GPS refusées")
                return False
        return True
    
    def start_tracking(self, interval: int = 1000, min_distance: float = 0):
        """Démarre le tracking GPS"""
        if not self.initialize():
            return False
        
        self.update_interval = interval
        self.min_distance = min_distance
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            success = bridge.gps_start_tracking(interval, min_distance)
            if success:
                self.is_tracking = True
                self.emit('gps_started')
                print("📍 Tracking GPS démarré")
                return True
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur démarrage GPS: {e}")
        
        return False
    
    def stop_tracking(self):
        """Arrête le tracking GPS"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            bridge.gps_stop_tracking()
            self.is_tracking = False
            self.emit('gps_stopped')
            print("📍 Tracking GPS arrêté")
        except Exception as e:
            self.emit('error', str(e))
            print(f"❌ Erreur arrêt GPS: {e}")
    
    def on_location_update(self, callback: Callable):
        """Écoute les mises à jour de position"""
        def location_callback(data):
            self.last_location = {
                'latitude': data.get('latitude', 0),
                'longitude': data.get('longitude', 0),
                'altitude': data.get('altitude', 0),
                'accuracy': data.get('accuracy', 0),
                'speed': data.get('speed', 0),
                'bearing': data.get('bearing', 0),
                'timestamp': data.get('timestamp', 0)
            }
            callback(self.last_location)
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.gps_set_listener(location_callback)
            print("📍 Écouteur GPS ajouté")
        except Exception as e:
            print(f"❌ Erreur ajout écouteur GPS: {e}")
    
    def get_last_location(self) -> Dict[str, Any]:
        """Retourne la dernière position connue"""
        if self.last_location:
            return self.last_location
        
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.gps_get_last_location()
        except Exception as e:
            print(f"❌ Erreur lecture position GPS: {e}")
            return {}
    
    def get_satellite_info(self) -> Dict[str, Any]:
        """Retourne les informations sur les satellites"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.gps_get_satellite_info()
        except Exception as e:
            print(f"❌ Erreur lecture info satellites: {e}")
            return {}
    
    def cleanup(self):
        """Nettoie les ressources GPS"""
        if self.is_tracking:
            self.stop_tracking()
        self.emit('gps_cleaned')
        print("📍 GPS nettoyé")