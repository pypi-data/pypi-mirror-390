import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .android_builder import AndroidBuilder
from .ios_builder import IOSBuilder

@dataclass
class BuildConfig:
    """Configuration de build"""
    platform: str
    mode: str  # debug, release
    output_dir: Path
    temp_dir: Path
    app_name: str
    version: str
    version_code: int

class AppBuilder:
    """Builder principal d'applications Mibale"""
    
    def __init__(self, platform: str = "android", mode: str = "debug"):
        self.platform = platform
        self.mode = mode
        self.config = self._load_build_config()
        self.builders = {
            'android': AndroidBuilder(),
            'ios': IOSBuilder()
        }
        
        print(f"🔨 AppBuilder initialisé: {platform}/{mode}")
    
    def build_apk(self) -> Optional[str]:
        """Construit un APK Android"""
        if self.platform != "android":
            print("❌ Build APK demandé mais plateforme n'est pas Android")
            return None
        
        try:
            builder = self.builders['android']
            return builder.build_apk(self.config)
        except Exception as e:
            print(f"❌ Erreur build APK: {e}")
            return None
    
    def build_ipa(self) -> Optional[str]:
        """Construit un IPA iOS"""
        if self.platform != "ios":
            print("❌ Build IPA demandé mais plateforme n'est pas iOS")
            return None
        
        try:
            builder = self.builders['ios']
            return builder.build_ipa(self.config)
        except Exception as e:
            print(f"❌ Erreur build IPA: {e}")
            return None
    
    def clean(self):
        """Nettoie les dossiers de build"""
        try:
            if self.config.output_dir.exists():
                shutil.rmtree(self.config.output_dir)
                print(f"🧹 Dossier de sortie nettoyé: {self.config.output_dir}")
            
            if self.config.temp_dir.exists():
                shutil.rmtree(self.config.temp_dir)
                print(f"🧹 Dossier temporaire nettoyé: {self.config.temp_dir}")
                
        except Exception as e:
            print(f"❌ Erreur nettoyage: {e}")
    
    def _load_build_config(self) -> BuildConfig:
        """Charge la configuration de build"""
        # Charge la configuration du projet
        project_config = self._load_project_config()
        
        # Crée les dossiers
        output_dir = Path("dist")
        temp_dir = Path("build")
        
        output_dir.mkdir(exist_ok=True)
        temp_dir.mkdir(exist_ok=True)
        
        return BuildConfig(
            platform=self.platform,
            mode=self.mode,
            output_dir=output_dir,
            temp_dir=temp_dir,
            app_name=project_config.get('app_name', 'MibaleApp'),
            version=project_config.get('version', '1.0.0'),
            version_code=project_config.get('version_code', 1)
        )
    
    def _load_project_config(self) -> Dict[str, Any]:
        """Charge la configuration du projet"""
        try:
            # Essaye de charger mibale.config.py
            config_file = Path("mibale.config.py")
            if config_file.exists():
                # Exécute le fichier de configuration
                config_globals = {}
                exec(config_file.read_text(), config_globals)
                
                if 'config' in config_globals:
                    config_obj = config_globals['config']
                    return {
                        'app_name': getattr(config_obj, 'app_name', 'MibaleApp'),
                        'version': getattr(config_obj, 'version', '1.0.0'),
                        'version_code': 1
                    }
            
            # Fallback: charge depuis pyproject.toml ou setup.py
            return self._load_fallback_config()
            
        except Exception as e:
            print(f"⚠️ Erreur chargement configuration: {e}")
            return {
                'app_name': 'MibaleApp',
                'version': '1.0.0',
                'version_code': 1
            }
    
    def _load_fallback_config(self) -> Dict[str, Any]:
        """Charge la configuration de fallback"""
        # Essaye pyproject.toml
        pyproject_file = Path("pyproject.toml")
        if pyproject_file.exists():
            try:
                import tomli
                with open(pyproject_file, 'rb') as f:
                    data = tomli.load(f)
                
                tool_config = data.get('tool', {}).get('mibale', {})
                if tool_config:
                    return tool_config
            except:
                pass
        
        # Essaye setup.py
        setup_file = Path("setup.py")
        if setup_file.exists():
            # Extraction basique depuis setup.py
            content = setup_file.read_text()
            if 'name=' in content:
                import re
                name_match = re.search(r"name=['\"]([^'\"]+)['\"]", content)
                version_match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
                
                return {
                    'app_name': name_match.group(1) if name_match else 'MibaleApp',
                    'version': version_match.group(1) if version_match else '1.0.0',
                    'version_code': 1
                }
        
        # Configuration par défaut
        return {
            'app_name': 'MibaleApp',
            'version': '1.0.0', 
            'version_code': 1
        }
    
    def get_build_info(self) -> Dict[str, Any]:
        """Retourne les informations de build"""
        return {
            'platform': self.platform,
            'mode': self.mode,
            'app_name': self.config.app_name,
            'version': self.config.version,
            'output_dir': str(self.config.output_dir),
            'temp_dir': str(self.config.temp_dir)
        }