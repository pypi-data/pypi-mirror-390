import os
from pathlib import Path

class MibaleConfig:
    """Configuration Mibale (similaire à vue.config.js)"""
    
    def __init__(self):
        self.app_name = "Mon App Mibale"
        self.version = "1.0.0"
        self.description = "Une application Mibale géniale"
        
        # Build configuration
        self.build = {
            'assets_dir': 'static',
            'output_dir': 'dist',
            'android': {
                'package_name': 'com.mibale.app',
                'version_code': 1,
                'permissions': [
                    'INTERNET',
                    'CAMERA',
                    'ACCESS_FINE_LOCATION',
                    'ACCESS_COARSE_LOCATION',
                    'RECORD_AUDIO'
                ]
            },
            'ios': {
                'bundle_identifier': 'com.mibale.app',
                'version': '1.0.0',
                'deployment_target': '13.0'
            }
        }
        
        # Dev server
        self.dev_server = {
            'port': 3000,
            'host': 'localhost',
            'hot_reload': True,
            'open_browser': True
        }
        
        # Compiler options
        self.compiler = {
            'minify': False,
            'source_map': True,
            'hot_reload': True
        }
        
        # Router configuration
        self.router = {
            'mode': 'hash',
            'base': '/'
        }

# Configuration exportée
config = MibaleConfig()