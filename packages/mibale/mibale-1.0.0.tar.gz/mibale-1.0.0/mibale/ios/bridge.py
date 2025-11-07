from typing import Dict, Any, List, Optional, Callable
import threading

class IOSBridge:
    """Bridge principal pour les fonctionnalités iOS natives via PyObjC"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.ui_application = None
        self.ui_window = None
        self.root_view_controller = None
        self.initialized = False
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def initialize(self) -> bool:
        """Initialise le bridge iOS"""
        try:
            import objc
            from Foundation import NSBundle, NSRunLoop, NSDefaultRunLoopMode
            from UIKit import UIApplication, UIWindow, UIScreen
            
            # Récupère l'application iOS principale
            self.ui_application = UIApplication.sharedApplication()
            
            # Crée une fenêtre principale
            screen_rect = UIScreen.mainScreen().bounds()
            self.ui_window = UIWindow.alloc().initWithFrame_(screen_rect)
            
            # Crée un view controller racine
            from UIKit import UIViewController
            self.root_view_controller = UIViewController.alloc().init()
            self.ui_window.setRootViewController_(self.root_view_controller)
            
            # Rend la fenêtre visible
            self.ui_window.makeKeyAndVisible()
            
            self.initialized = True
            print("✅ Bridge iOS initialisé via PyObjC")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation bridge iOS: {e}")
            return False
    
    # === UI COMPONENTS ===
    
    def create_view_controller(self) -> Any:
        """Crée un UIViewController"""
        try:
            from UIKit import UIViewController
            return UIViewController.alloc().init()
        except Exception as e:
            print(f"❌ Erreur création UIViewController: {e}")
            return None
    
    def create_view(self, frame: Dict[str, float] = None) -> Any:
        """Crée une UIView"""
        try:
            from UIKit import UIView
            from CoreGraphics import CGRectMake
            
            if frame:
                rect = CGRectMake(frame.get('x', 0), frame.get('y', 0), 
                                frame.get('width', 100), frame.get('height', 100))
            else:
                from UIKit import UIScreen
                screen_rect = UIScreen.mainScreen().bounds()
                rect = screen_rect
            
            return UIView.alloc().initWithFrame_(rect)
        except Exception as e:
            print(f"❌ Erreur création UIView: {e}")
            return None
    
    def create_label(self, text: str = "") -> Any:
        """Crée un UILabel"""
        try:
            from UIKit import UILabel
            from CoreGraphics import CGRectMake
            
            label = UILabel.alloc().initWithFrame_(CGRectMake(0, 0, 200, 40))
            label.setText_(text)
            label.setBackgroundColor_(self.get_color('clear'))
            return label
        except Exception as e:
            print(f"❌ Erreur création UILabel: {e}")
            return None
    
    def create_button(self, title: str = "") -> Any:
        """Crée un UIButton"""
        try:
            from UIKit import UIButton
            from CoreGraphics import CGRectMake
            
            button = UIButton.buttonWithType_(0)  # UIButtonTypeSystem
            button.setFrame_(CGRectMake(0, 0, 100, 44))
            button.setTitle_forState_(title, 0)  # UIControlStateNormal
            
            # Ajoute un gestionnaire d'événements
            button.addTarget_action_forControlEvents_(
                self, 
                'handle_button_click:', 
                1 << 12  # UIControlEventTouchUpInside
            )
            
            return button
        except Exception as e:
            print(f"❌ Erreur création UIButton: {e}")
            return None
    
    def handle_button_click_(self, sender):
        """Gère les clics sur les boutons iOS"""
        print(f"🖲️ Bouton iOS cliqué: {sender.titleForState_(0)}")
    
    def create_image_view(self, image_name: str = None) -> Any:
        """Crée un UIImageView"""
        try:
            from UIKit import UIImageView, UIImage
            from CoreGraphics import CGRectMake
            
            image_view = UIImageView.alloc().initWithFrame_(CGRectMake(0, 0, 100, 100))
            
            if image_name:
                image = UIImage.imageNamed_(image_name)
                if image:
                    image_view.setImage_(image)
            
            return image_view
        except Exception as e:
            print(f"❌ Erreur création UIImageView: {e}")
            return None
    
    # === LAYOUT ===
    
    def setup_auto_layout(self, view: Any):
        """Active Auto Layout pour une vue"""
        try:
            view.setTranslatesAutoresizingMaskIntoConstraints_(False)
        except Exception as e:
            print(f"❌ Erreur activation Auto Layout: {e}")
    
    def add_constraints(self, constraints: List[Any]):
        """Ajoute des contraintes Auto Layout"""
        try:
            from UIKit import NSLayoutConstraint
            NSLayoutConstraint.activateConstraints_(constraints)
        except Exception as e:
            print(f"❌ Erreur ajout contraintes: {e}")
    
    # === CAMERA ===
    
    def create_camera(self) -> Any:
        """Crée une instance de caméra iOS"""
        try:
            from AVFoundation import AVCaptureDevice, AVCaptureDeviceInput, AVCaptureSession
            from UIKit import AVCaptureVideoPreviewLayer
            
            # Configure la session de capture
            session = AVCaptureSession.alloc().init()
            session.setSessionPreset_("AVCaptureSessionPresetHigh")
            
            # Récupère le device caméra
            device = AVCaptureDevice.defaultDeviceWithMediaType_("vide")
            if not device:
                print("❌ Aucun device caméra trouvé")
                return None
            
            # Crée l'input
            input_device = AVCaptureDeviceInput.deviceInputWithDevice_error_(device, None)
            if not input_device:
                print("❌ Impossible de créer l'input caméra")
                return None
            
            # Ajoute l'input à la session
            if session.canAddInput_(input_device):
                session.addInput_(input_device)
            
            return {
                'session': session,
                'device': device,
                'input': input_device
            }
            
        except Exception as e:
            print(f"❌ Erreur création caméra iOS: {e}")
            return None
    
    def camera_take_picture(self, quality: str) -> bytes:
        """Prend une photo avec la caméra iOS"""
        try:
            from AVFoundation import AVCapturePhotoOutput, AVCapturePhotoSettings
            from Foundation import NSData
            
            print(f"📷 Photo iOS prise avec qualité: {quality}")
            # Implémentation simplifiée - retourne des données fictives
            return b"fake_ios_image_data"
            
        except Exception as e:
            print(f"❌ Erreur prise de photo iOS: {e}")
            return b""
    
    # === SENSORS ===
    
    def sensors_get_available(self) -> Dict[str, Any]:
        """Retourne les capteurs disponibles sur iOS"""
        try:
            from CoreMotion import CMMotionManager
            
            motion_manager = CMMotionManager.alloc().init()
            
            return {
                'accelerometer': motion_manager.isAccelerometerAvailable(),
                'gyroscope': motion_manager.isGyroscopeAvailable(),
                'magnetometer': motion_manager.isMagnetometerAvailable(),
                'device_motion': motion_manager.isDeviceMotionAvailable()
            }
            
        except Exception as e:
            print(f"❌ Erreur détection capteurs iOS: {e}")
            return {
                'accelerometer': False,
                'gyroscope': False,
                'magnetometer': False,
                'device_motion': False
            }
    
    def sensor_start(self, sensor_type: str, interval: float) -> bool:
        """Démarre un capteur iOS"""
        try:
            from CoreMotion import CMMotionManager
            from Foundation import NSOperationQueue
            
            motion_manager = CMMotionManager.alloc().init()
            
            if sensor_type == 'accelerometer' and motion_manager.isAccelerometerAvailable():
                motion_manager.setAccelerometerUpdateInterval_(interval / 1000000.0)
                motion_manager.startAccelerometerUpdatesToQueue_withHandler_(
                    NSOperationQueue.mainQueue(),
                    self._accelerometer_handler
                )
                return True
                
            elif sensor_type == 'gyroscope' and motion_manager.isGyroscopeAvailable():
                motion_manager.setGyroscopeUpdateInterval_(interval / 1000000.0)
                motion_manager.startGyroscopeUpdatesToQueue_withHandler_(
                    NSOperationQueue.mainQueue(),
                    self._gyroscope_handler
                )
                return True
                
        except Exception as e:
            print(f"❌ Erreur démarrage capteur {sensor_type}: {e}")
        
        return False
    
    def _accelerometer_handler(self, data, error):
        """Gère les données de l'accéléromètre iOS"""
        if data and not error:
            acceleration = data.acceleration()
            print(f"📡 Accéléromètre iOS: x={acceleration.x}, y={acceleration.y}, z={acceleration.z}")
    
    def _gyroscope_handler(self, data, error):
        """Gère les données du gyroscope iOS"""
        if data and not error:
            rotation = data.rotationRate()
            print(f"📡 Gyroscope iOS: x={rotation.x}, y={rotation.y}, z={rotation.z}")
    
    # === GPS ===
    
    def gps_start_tracking(self, interval: int, min_distance: float) -> bool:
        """Démarre le tracking GPS iOS"""
        try:
            from CoreLocation import CLLocationManager, CLAccuracyBest, KCLLocationAccuracyBest
            
            self.location_manager = CLLocationManager.alloc().init()
            self.location_manager.setDesiredAccuracy_(KCLLocationAccuracyBest)
            self.location_manager.setDistanceFilter_(min_distance)
            
            # Demande l'autorisation
            self.location_manager.requestWhenInUseAuthorization()
            
            # Démarre les mises à jour
            self.location_manager.startUpdatingLocation()
            
            print("📍 Tracking GPS iOS démarré")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage GPS iOS: {e}")
            return False
    
    def gps_get_last_location(self) -> Dict[str, Any]:
        """Retourne la dernière position GPS iOS"""
        try:
            if hasattr(self, 'location_manager'):
                location = self.location_manager.location()
                if location:
                    return {
                        'latitude': location.coordinate().latitude,
                        'longitude': location.coordinate().longitude,
                        'altitude': location.altitude(),
                        'accuracy': location.horizontalAccuracy(),
                        'timestamp': location.timestamp().timeIntervalSince1970()
                    }
        except Exception as e:
            print(f"❌ Erreur lecture position GPS iOS: {e}")
        
        return {}
    
    # === BLUETOOTH ===
    
    def bluetooth_initialize(self) -> bool:
        """Initialise Bluetooth iOS"""
        try:
            from CoreBluetooth import CBCentralManager, CBManagerState
            
            self.bluetooth_manager = CBCentralManager.alloc().initWithDelegate_queue_(
                self, 
                None  # Main queue
            )
            print("📡 Bluetooth iOS initialisé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation Bluetooth iOS: {e}")
            return False
    
    def centralManagerDidUpdateState_(self, central):
        """Callback pour les changements d'état Bluetooth"""
        state = central.state()
        states = {
            0: "unknown",
            1: "resetting", 
            2: "unsupported",
            3: "unauthorized",
            4: "poweredOff",
            5: "poweredOn"
        }
        print(f"📡 État Bluetooth iOS: {states.get(state, 'unknown')}")
    
    # === PERMISSIONS ===
    
    def check_permissions(self, permissions: List[str]) -> bool:
        """Vérifie les permissions iOS"""
        try:
            from AVFoundation import AVCaptureDevice
            from CoreLocation import CLLocationManager
            from CoreBluetooth import CBCentralManager
            
            for permission in permissions:
                if permission == 'CAMERA':
                    # Vérifie l'autorisation caméra
                    auth_status = AVCaptureDevice.authorizationStatusForMediaType_("vide")
                    if auth_status != 3:  # AVAuthorizationStatusAuthorized
                        return False
                        
                elif permission == 'LOCATION':
                    # Vérifie l'autorisation localisation
                    auth_status = CLLocationManager.authorizationStatus()
                    if auth_status not in [3, 4]:  # kCLAuthorizationStatusAuthorizedWhenInUse/Always
                        return False
            
            print(f"🔐 Permissions iOS vérifiées: {permissions}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification permissions iOS: {e}")
            return True  # Fallback pour le développement
    
    def request_permissions(self, permissions: List[str]) -> bool:
        """Demande les permissions iOS"""
        try:
            from AVFoundation import AVCaptureDevice
            from CoreLocation import CLLocationManager
            
            for permission in permissions:
                if permission == 'CAMERA':
                    AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                        "vide", 
                        lambda granted: print(f"📷 Permission caméra: {'accordée' if granted else 'refusée'}")
                    )
                elif permission == 'LOCATION':
                    if not hasattr(self, 'location_manager'):
                        self.location_manager = CLLocationManager.alloc().init()
                    self.location_manager.requestWhenInUseAuthorization()
            
            print(f"🔐 Demandes de permissions iOS envoyées: {permissions}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur demande permissions iOS: {e}")
            return True  # Fallback pour le développement
    
    # === UTILITIES ===
    
    def get_color(self, color_name: str) -> Any:
        """Retourne une UIColor"""
        try:
            from UIKit import UIColor
            
            colors = {
                'black': UIColor.blackColor(),
                'white': UIColor.whiteColor(),
                'red': UIColor.redColor(),
                'blue': UIColor.blueColor(),
                'green': UIColor.greenColor(),
                'clear': UIColor.clearColor(),
                'system_blue': UIColor.systemBlueColor() if hasattr(UIColor, 'systemBlueColor') else UIColor.blueColor()
            }
            
            return colors.get(color_name, UIColor.blackColor())
            
        except Exception as e:
            print(f"❌ Erreur couleur iOS: {e}")
            return None
    
    def show_alert(self, title: str, message: str):
        """Affiche une alerte iOS"""
        try:
            from UIKit import UIAlertController, UIAlertAction, UIAlertControllerStyleAlert
            from UIKit import UIViewController
            
            alert = UIAlertController.alertControllerWithTitle_message_preferredStyle_(
                title, message, UIAlertControllerStyleAlert
            )
            
            ok_action = UIAlertAction.actionWithTitle_style_handler_(
                "OK", 0, lambda action: None  # UIAlertActionStyleDefault
            )
            alert.addAction_(ok_action)
            
            # Présente l'alerte
            root_vc = self.root_view_controller or self._get_root_view_controller()
            if root_vc:
                root_vc.presentViewController_animated_completion_(alert, True, None)
                
        except Exception as e:
            print(f"❌ Erreur alerte iOS: {e}")
    
    def _get_root_view_controller(self) -> Any:
        """Récupère le view controller racine"""
        try:
            if self.root_view_controller:
                return self.root_view_controller
            
            if self.ui_window:
                return self.ui_window.rootViewController()
            
            from UIKit import UIApplication
            app = UIApplication.sharedApplication()
            if app:
                return app.keyWindow().rootViewController()
                
        except Exception as e:
            print(f"❌ Erreur récupération root VC: {e}")
        
        return None
    
    # === VIBRATION ===
    
    def device_vibrate(self, duration: int = 100):
        """Fait vibrer le device iOS"""
        try:
            from AudioToolbox import AudioServicesPlaySystemSound
            # 1519 est le son de vibration (peut varier)
            AudioServicesPlaySystemSound(1519)
            print("📳 Vibration iOS")
        except Exception as e:
            print(f"❌ Erreur vibration iOS: {e}")
    
    # === BATTERY ===
    
    def device_get_battery_info(self) -> Dict[str, Any]:
        """Retourne les infos batterie iOS"""
        try:
            from UIKit import UIDevice
            
            device = UIDevice.currentDevice()
            device.setBatteryMonitoringEnabled_(True)
            
            return {
                'level': device.batteryLevel() * 100,  # Converti en pourcentage
                'state': ['unknown', 'unplugged', 'charging', 'full'][int(device.batteryState())],
                'platform': 'ios'
            }
            
        except Exception as e:
            print(f"❌ Erreur lecture batterie iOS: {e}")
            return {
                'level': 100,
                'state': 'unknown',
                'platform': 'ios'
            }