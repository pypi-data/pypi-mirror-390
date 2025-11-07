import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile

class AndroidBuilder:
    """Builder pour applications Android"""
    
    def __init__(self):
        self.build_tools_available = self._check_build_tools()
        
    def build_apk(self, config) -> Optional[str]:
        """Construit un APK Android"""
        print("🔨 Début de la construction Android APK...")
        
        try:
            # Étape 1: Préparation de l'environnement
            self._prepare_android_env(config)
            
            # Étape 2: Compilation des composants
            self._compile_components(config)
            
            # Étape 3: Génération des ressources Android
            self._generate_android_resources(config)
            
            # Étape 4: Construction avec Buildozer
            apk_path = self._build_with_buildozer(config)
            
            if apk_path:
                print(f"✅ APK généré avec succès: {apk_path}")
                return apk_path
            else:
                print("❌ Échec de la construction APK")
                return None
                
        except Exception as e:
            print(f"❌ Erreur construction Android: {e}")
            return None
    
    def _prepare_android_env(self, config):
        """Prépare l'environnement de build Android"""
        print("📋 Préparation de l'environnement Android...")
        
        # Crée la structure de dossiers Android
        android_dir = config.temp_dir / "android"
        android_dir.mkdir(exist_ok=True)
        
        # Dossiers nécessaires
        (android_dir / "src").mkdir(exist_ok=True)
        (android_dir / "res").mkdir(exist_ok=True)
        (android_dir / "libs").mkdir(exist_ok=True)
        
        print("✅ Environnement Android préparé")
    
    def _compile_components(self, config):
        """Compile les composants .mb en Python"""
        print("📦 Compilation des composants...")
        
        from ...compiler.mb_compiler import MBCompiler
        
        compiler = MBCompiler()
        
        # Compile tous les composants .mb
        mb_files = list(Path(".").rglob("*.mb"))
        for mb_file in mb_files:
            print(f"  🔨 Compilation de {mb_file}")
            try:
                component_data = compiler.compile_file(mb_file)
                
                # Sauvegarde le composant compilé
                output_file = config.temp_dir / "components" / f"{mb_file.stem}.py"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Crée un module Python à partir du composant
                self._create_python_module(output_file, component_data)
                
            except Exception as e:
                print(f"  ❌ Erreur compilation {mb_file}: {e}")
        
        print("✅ Tous les composants compilés")
    
    def _create_python_module(self, output_file: Path, component_data: Dict[str, Any]):
        """Crée un module Python à partir des données du composant"""
        component_class = component_data.get('component')
        if not component_class:
            return
        
        module_content = f'''
"""
Composant Mibale généré: {output_file.stem}
"""

from mibale.core.component import BaseComponent

class {component_class.__name__}(BaseComponent):
    def __init__(self):
        super().__init__()
    
    def setup(self):
        """Setup du composant"""
        pass
    
    def on_mount(self):
        """Appelé lors du montage"""
        pass
    
    def on_destroy(self):
        """Appelé lors de la destruction"""
        pass

# Export pour l'import
{component_class.__name__} = {component_class.__name__}
'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(module_content)
    
    def _generate_android_resources(self, config):
        """Génère les ressources Android"""
        print("📱 Génération des ressources Android...")
        
        android_dir = config.temp_dir / "android"
        
        # AndroidManifest.xml
        manifest_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.mibale.{config.app_name.lower()}">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.BLUETOOTH" />
    <uses-permission android:name="android.permission.NFC" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{config.app_name}"
        android:theme="@style/AppTheme">
        
        <activity
            android:name=".MainActivity"
            android:label="{config.app_name}"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|locale"
            android:launchMode="singleTop">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
        
        with open(android_dir / "AndroidManifest.xml", "w") as f:
            f.write(manifest_content)
        
        # build.gradle (simplifié)
        gradle_content = f'''
apply plugin: 'com.android.application'

android {{
    compileSdkVersion 30
    buildToolsVersion "30.0.3"
    
    defaultConfig {{
        applicationId "com.mibale.{config.app_name.lower()}"
        minSdkVersion 21
        targetSdkVersion 30
        versionCode {config.version_code}
        versionName "{config.version}"
    }}
    
    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }}
        debug {{
            minifyEnabled false
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation fileTree(dir: 'libs', include: ['*.jar'])
    implementation 'androidx.appcompat:appcompat:1.3.0'
    implementation 'com.google.android.material:material:1.4.0'
}}
'''
        
        with open(android_dir / "build.gradle", "w") as f:
            f.write(gradle_content)
        
        print("✅ Ressources Android générées")
    
    def _build_with_buildozer(self, config) -> Optional[str]:
        """Utilise Buildozer pour construire l'APK"""
        print("🚀 Construction avec Buildozer...")
        
        try:
            # Vérifie que Buildozer est installé
            result = subprocess.run([
                "buildozer", "--version"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Buildozer non trouvé. Installation...")
                self._install_buildozer()
            
            # Crée un spec Buildozer minimal
            self._create_buildozer_spec(config)
            
            # Lance la construction
            build_command = ["buildozer", "android", "debug"]
            if config.mode == "release":
                build_command = ["buildozer", "android", "release"]
            
            print(f"  🛠️  Exécution: {' '.join(build_command)}")
            
            result = subprocess.run(
                build_command,
                cwd=config.temp_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Trouve le fichier APK généré
                apk_files = list((config.temp_dir / "bin").glob("*.apk"))
                if apk_files:
                    apk_path = config.output_dir / apk_files[0].name
                    shutil.copy(apk_files[0], apk_path)
                    return str(apk_path)
            else:
                print(f"❌ Erreur Buildozer: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erreur construction Buildozer: {e}")
        
        return None
    
    def _create_buildozer_spec(self, config):
        """Crée un fichier buildozer.spec"""
        spec_content = f'''
[app]
title = {config.app_name}
package.name = {config.app_name.lower()}
package.domain = com.mibale

source.dir = ../src
version = {config.version}

requirements = python3, kivy, pyjnius

[buildozer]
log_level = 2

[android]
api = 30
minapi = 21
ndk = 21.0.0

# Permissions
android.permissions = INTERNET,CAMERA,ACCESS_FINE_LOCATION,RECORD_AUDIO,BLUETOOTH,NFC,ACCESS_WIFI_STATE,VIBRATE
'''
        
        spec_file = config.temp_dir / "buildozer.spec"
        with open(spec_file, "w") as f:
            f.write(spec_content)
    
    def _install_buildozer(self):
        """Installe Buildozer si nécessaire"""
        try:
            subprocess.run([
                "pip", "install", "buildozer"
            ], check=True)
            print("✅ Buildozer installé")
        except Exception as e:
            print(f"❌ Erreur installation Buildozer: {e}")
            raise
    
    def _check_build_tools(self) -> bool:
        """Vérifie la disponibilité des outils de build"""
        tools = ['adb', 'java', 'javac']
        
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], capture_output=True)
            except FileNotFoundError:
                print(f"⚠️ Outil non trouvé: {tool}")
                return False
        
        return True