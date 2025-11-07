"""
Configuration Mibale - similaire à vue.config.js
"""

import os
from pathlib import Path

class MibaleConfig:
    """Configuration principale de l'application Mibale"""
    
    def __init__(self):
        # Informations de base de l'application
        self.app_name = "Mon App Mibale"
        self.version = "1.0.0"
        self.description = "Une application Mibale géniale"
        self.author = "Votre Nom"
        self.license = "MIT"
        
        # Configuration du build
        self.build = {
            # Dossiers
            'assets_dir': 'static',
            'output_dir': 'dist',
            'temp_dir': 'build',
            
            # Android
            'android': {
                'package_name': 'com.mibale.myapp',
                'version_code': 1,
                'min_sdk': 21,
                'target_sdk': 30,
                'permissions': [
                    'INTERNET',
                    'CAMERA', 
                    'ACCESS_FINE_LOCATION',
                    'ACCESS_COARSE_LOCATION',
                    'RECORD_AUDIO',
                    'BLUETOOTH',
                    'NFC',
                    'ACCESS_WIFI_STATE',
                    'VIBRATE'
                ],
                'features': [
                    'android.hardware.camera',
                    'android.hardware.location',
                    'android.hardware.sensor.accelerometer'
                ]
            },
            
            # iOS
            'ios': {
                'bundle_identifier': 'com.mibale.MyApp',
                'version': '1.0.0',
                'deployment_target': '13.0',
                'device_family': ['iphone', 'ipad'],
                'capabilities': [
                    'camera',
                    'location',
                    'bluetooth',
                    'nfc'
                ]
            }
        }
        
        # Configuration du serveur de développement
        self.dev_server = {
            'port': 3000,
            'host': 'localhost',
            'hot_reload': True,
            'open_browser': True,
            'cors': True,
            'https': False
        }
        
        # Options du compilateur
        self.compiler = {
            'minify': False,  # À activer en production
            'source_map': True,
            'hot_reload': True,
            'cache': True
        }
        
        # Configuration du routeur
        self.router = {
            'mode': 'hash',  # 'hash' ou 'history'
            'base': '/',
            'scroll_behavior': 'smooth'
        }
        
        # Configuration des stores
        self.stores = {
            'persist': True,
            'storage_key': 'mibale_stores'
        }
        
        # Configuration des services
        self.services = {
            'api': {
                'base_url': 'https://api.mon-app.com',
                'timeout': 10000,
                'retry_attempts': 3
            },
            'analytics': {
                'enabled': True,
                'provider': 'google'  # 'google', 'amplitude', 'mixpanel'
            }
        }
        
        # Configuration UI/UX
        self.ui = {
            'theme': {
                'primary': '#667eea',
                'secondary': '#764ba2',
                'accent': '#f093fb',
                'error': '#f56565',
                'warning': '#ed8936',
                'info': '#4299e1',
                'success': '#48bb78'
            },
            'typography': {
                'font_family': 'System',
                'font_sizes': {
                    'xs': 12,
                    'sm': 14,
                    'base': 16,
                    'lg': 18,
                    'xl': 20,
                    '2xl': 24,
                    '3xl': 30
                }
            },
            'spacing': {
                'xs': 4,
                'sm': 8,
                'md': 16,
                'lg': 24,
                'xl': 32,
                '2xl': 48
            },
            'border_radius': {
                'sm': 4,
                'md': 8,
                'lg': 12,
                'xl': 16,
                'full': 9999
            }
        }
        
        # Plugins et extensions
        self.plugins = [
            # 'mibale-plugin-analytics',
            # 'mibale-plugin-push',
            # 'mibale-plugin-database'
        ]
        
        # Configuration de développement
        self.development = {
            'debug': True,
            'logger': {
                'level': 'debug',  # 'debug', 'info', 'warn', 'error'
                'colors': True
            },
            'dev_tools': True
        }
        
        # Configuration de production
        self.production = {
            'debug': False,
            'logger': {
                'level': 'warn',
                'colors': False
            },
            'dev_tools': False
        }
    
    def get_build_config(self, platform: str) -> dict:
        """Retourne la configuration de build pour une plateforme spécifique"""
        return self.build.get(platform, {})
    
    def get_current_config(self) -> dict:
        """Retourne la configuration actuelle basée sur l'environnement"""
        import os
        is_prod = os.getenv('MIBALE_ENV') == 'production'
        
        base_config = {
            'app': {
                'name': self.app_name,
                'version': self.version,
                'description': self.description
            },
            'build': self.build,
            'compiler': self.compiler,
            'router': self.router,
            'stores': self.stores,
            'services': self.services,
            'ui': self.ui
        }
        
        # Merge avec la configuration d'environnement
        env_config = self.production if is_prod else self.development
        base_config.update(env_config)
        
        return base_config
    
    def validate(self) -> bool:
        """Valide la configuration"""
        try:
            # Validation des champs requis
            required_fields = ['app_name', 'version']
            for field in required_fields:
                if not getattr(self, field):
                    print(f"❌ Champ requis manquant: {field}")
                    return False
            
            # Validation de la configuration Android
            android_config = self.build.get('android', {})
            if not android_config.get('package_name'):
                print("❌ Package name Android manquant")
                return False
            
            # Validation de la configuration iOS
            ios_config = self.build.get('ios', {})
            if not ios_config.get('bundle_identifier'):
                print("❌ Bundle identifier iOS manquant")
                return False
            
            print("✅ Configuration valide")
            return True
            
        except Exception as e:
            print(f"❌ Erreur validation configuration: {e}")
            return False

# Instance de configuration exportée
config = MibaleConfig()

# Fonctions utilitaires
def get_config():
    """Retourne la configuration actuelle"""
    return config.get_current_config()

def is_development():
    """Vérifie si on est en mode développement"""
    import os
    return os.getenv('MIBALE_ENV') != 'production'

def is_production():
    """Vérifie si on est en mode production"""
    return not is_development()

# Exemple d'utilisation
if __name__ == "__main__":
    print("🧪 Test de configuration Mibale:")
    print(f"📱 Application: {config.app_name} v{config.version}")
    print(f"🔧 Environnement: {'Production' if is_production() else 'Développement'}")
    
    # Validation
    if config.validate():
        current_config = get_config()
        print("✅ Configuration chargée avec succès")
    else:
        print("❌ Configuration invalide")