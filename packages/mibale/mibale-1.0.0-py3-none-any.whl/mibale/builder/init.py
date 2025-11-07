"""
Système de build Mibale
Construction d'applications Android APK et iOS IPA
"""

from .app_builder import AppBuilder
from .android_builder import AndroidBuilder
from .ios_builder import IOSBuilder

__all__ = [
    'AppBuilder',
    'AndroidBuilder', 
    'IOSBuilder'
]

def build_project(platform: str = "android", mode: str = "debug") -> str:
    """Fonction utilitaire pour builder un projet"""
    builder = AppBuilder(platform, mode)
    
    if platform == "android":
        return builder.build_apk()
    elif platform == "ios":
        return builder.build_ipa()
    else:
        raise ValueError(f"Plateforme non supportée: {platform}")