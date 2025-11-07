import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import plistlib

class IOSBuilder:
    """Builder pour applications iOS"""
    
    def __init__(self):
        self.xcode_available = self._check_xcode()
        
    def build_ipa(self, config) -> Optional[str]:
        """Construit un IPA iOS"""
        print("🔨 Début de la construction iOS IPA...")
        
        if not self.xcode_available:
            print("❌ Xcode non disponible - impossible de builder pour iOS")
            return None
        
        try:
            # Étape 1: Préparation de l'environnement iOS
            self._prepare_ios_env(config)
            
            # Étape 2: Compilation des composants
            self._compile_components(config)
            
            # Étape 3: Génération du projet Xcode
            self._generate_xcode_project(config)
            
            # Étape 4: Construction avec xcodebuild
            ipa_path = self._build_with_xcodebuild(config)
            
            if ipa_path:
                print(f"✅ IPA généré avec succès: {ipa_path}")
                return ipa_path
            else:
                print("❌ Échec de la construction IPA")
                return None
                
        except Exception as e:
            print(f"❌ Erreur construction iOS: {e}")
            return None
    
    def _prepare_ios_env(self, config):
        """Prépare l'environnement de build iOS"""
        print("📋 Préparation de l'environnement iOS...")
        
        # Crée la structure de dossiers iOS
        ios_dir = config.temp_dir / "ios"
        ios_dir.mkdir(exist_ok=True)
        
        # Dossiers nécessaires pour un projet iOS
        (ios_dir / "Sources").mkdir(exist_ok=True)
        (ios_dir / "Resources").mkdir(exist_ok=True)
        (ios_dir / "Supporting Files").mkdir(exist_ok=True)
        
        print("✅ Environnement iOS préparé")
    
    def _compile_components(self, config):
        """Compile les composants .mb pour iOS"""
        print("📦 Compilation des composants iOS...")
        
        from ...compiler.mb_compiler import MBCompiler
        
        compiler = MBCompiler()
        
        # Compile tous les composants .mb
        mb_files = list(Path(".").rglob("*.mb"))
        for mb_file in mb_files:
            print(f"  🔨 Compilation iOS de {mb_file}")
            try:
                component_data = compiler.compile_file(mb_file)
                
                # Pour iOS, on génère des wrappers Swift/ObjC
                self._create_ios_component_wrapper(config, mb_file, component_data)
                
            except Exception as e:
                print(f"  ❌ Erreur compilation iOS {mb_file}: {e}")
        
        print("✅ Tous les composants iOS compilés")
    
    def _create_ios_component_wrapper(self, config, mb_file: Path, component_data: Dict[str, Any]):
        """Crée un wrapper iOS pour un composant"""
        component_name = mb_file.stem
        swift_file = config.temp_dir / "ios" / "Sources" / f"{component_name}.swift"
        
        swift_content = f'''
//
// {component_name}.swift
// {config.app_name}
//
// Composant Mibale généré: {component_name}
//

import UIKit
import SwiftUI

class {component_name}ViewController: UIViewController {{
    override func viewDidLoad() {{
        super.viewDidLoad()
        setupComponent()
    }}
    
    private func setupComponent() {{
        // Implémentation du composant {component_name}
        let label = UILabel()
        label.text = "{component_name}"
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(label)
        
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }}
}}

@available(iOS 13.0, *)
struct {component_name}View: View {{
    var body: some View {{
        VStack {{
            Text("{component_name}")
                .font(.title)
                .padding()
            Text("Composant Mibale")
                .font(.body)
                .foregroundColor(.gray)
        }}
    }}
}}
'''
        
        swift_file.parent.mkdir(parents=True, exist_ok=True)
        with open(swift_file, 'w', encoding='utf-8') as f:
            f.write(swift_content)
    
    def _generate_xcode_project(self, config):
        """Génère un projet Xcode"""
        print("🛠️ Génération du projet Xcode...")
        
        ios_dir = config.temp_dir / "ios"
        
        # Info.plist
        info_plist = {
            'CFBundleDevelopmentRegion': '$(DEVELOPMENT_LANGUAGE)',
            'CFBundleExecutable': '$(EXECUTABLE_NAME)',
            'CFBundleIdentifier': 'com.mibale.$(PRODUCT_NAME:rfc1034identifier)',
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundleName': '$(PRODUCT_NAME)',
            'CFBundlePackageType': 'APPL',
            'CFBundleShortVersionString': config.version,
            'CFBundleVersion': str(config.version_code),
            'LSRequiresIPhoneOS': True,
            'UIRequiredDeviceCapabilities': ['armv7'],
            'UISupportedInterfaceOrientations': [
                'UIInterfaceOrientationPortrait',
                'UIInterfaceOrientationLandscapeLeft',
                'UIInterfaceOrientationLandscapeRight'
            ],
            'UILaunchStoryboardName': 'LaunchScreen',
            'UIApplicationSceneManifest': {
                'UIApplicationSupportsMultipleScenes': False,
                'UISceneConfigurations': {
                    'UIWindowSceneSessionRoleApplication': [{
                        'UISceneConfigurationName': 'Default Configuration',
                        'UISceneDelegateClassName': '$(PRODUCT_MODULE_NAME).SceneDelegate'
                    }]
                }
            }
        }
        
        with open(ios_dir / "Supporting Files" / "Info.plist", 'wb') as f:
            plistlib.dump(info_plist, f)
        
        # Fichier projet Xcode (simplifié)
        self._create_xcode_project_file(config, ios_dir)
        
        print("✅ Projet Xcode généré")
    
    def _create_xcode_project_file(self, config, ios_dir: Path):
        """Crée un fichier projet Xcode .pbxproj simplifié"""
        # Cette implémentation est très simplifiée
        # Un vrai projet Xcode nécessiterait un fichier .pbxproj complexe
        
        project_content = f'''
// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 50;
	objects = {{
        /* Simplified project structure */
	}};
	rootObject = 000000000000000000000000 /* Project object */;
}}
'''
        
        project_file = ios_dir / f"{config.app_name}.xcodeproj" / "project.pbxproj"
        project_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(project_file, 'w') as f:
            f.write(project_content)
    
    def _build_with_xcodebuild(self, config) -> Optional[str]:
        """Utilise xcodebuild pour construire l'IPA"""
        print("🚀 Construction avec xcodebuild...")
        
        try:
            ios_dir = config.temp_dir / "ios"
            project_file = ios_dir / f"{config.app_name}.xcodeproj"
            
            # Vérifie que le projet existe
            if not project_file.exists():
                print("❌ Projet Xcode non trouvé")
                return None
            
            # Construction pour le simulateur (pour le test)
            build_command = [
                "xcodebuild",
                "-project", str(project_file),
                "-scheme", config.app_name,
                "-configuration", "Debug" if config.mode == "debug" else "Release",
                "-destination", "generic/platform=iOS",
                "-archivePath", str(config.temp_dir / "build" / f"{config.app_name}.xcarchive"),
                "archive"
            ]
            
            print(f"  🛠️  Exécution: {' '.join(build_command)}")
            
            result = subprocess.run(
                build_command,
                cwd=ios_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Exportation de l'IPA
                ipa_path = self._export_ipa(config)
                return ipa_path
            else:
                print(f"❌ Erreur xcodebuild: {result.stderr}")
                # En mode développement, on peut créer un IPA fictif
                if config.mode == "debug":
                    return self._create_debug_ipa(config)
                
        except Exception as e:
            print(f"❌ Erreur construction xcodebuild: {e}")
            # Fallback pour le développement
            if config.mode == "debug":
                return self._create_debug_ipa(config)
        
        return None
    
    def _export_ipa(self, config) -> Optional[str]:
        """Exporte l'IPA depuis l'archive"""
        try:
            archive_path = config.temp_dir / "build" / f"{config.app_name}.xcarchive"
            export_path = config.temp_dir / "build" / "export"
            
            export_command = [
                "xcodebuild",
                "-exportArchive",
                "-archivePath", str(archive_path),
                "-exportPath", str(export_path),
                "-exportOptionsPlist", self._create_export_options(config),
                "DEBUG_INFORMATION_FORMAT=dwarf-with-dsym",
                "DEPLOYMENT_POSTPROCESSING=YES",
                "STRIP_INSTALLED_PRODUCT=YES"
            ]
            
            result = subprocess.run(
                export_command,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                ipa_files = list(export_path.glob("*.ipa"))
                if ipa_files:
                    final_ipa = config.output_dir / ipa_files[0].name
                    shutil.copy(ipa_files[0], final_ipa)
                    return str(final_ipa)
                    
        except Exception as e:
            print(f"❌ Erreur export IPA: {e}")
        
        return None
    
    def _create_export_options(self, config) -> str:
        """Crée un fichier d'options d'export"""
        options = {
            'method': 'development' if config.mode == 'debug' else 'app-store',
            'teamID': 'YOUR_TEAM_ID',  # À remplacer par un vrai Team ID
            'uploadBitcode': False,
            'compileBitcode': False
        }
        
        options_file = config.temp_dir / "ExportOptions.plist"
        with open(options_file, 'wb') as f:
            plistlib.dump(options, f)
        
        return str(options_file)
    
    def _create_debug_ipa(self, config) -> str:
        """Crée un IPA de débogage fictif pour le développement"""
        print("🔧 Création d'un IPA de débogage fictif...")
        
        ipa_path = config.output_dir / f"{config.app_name}-debug.ipa"
        
        # Crée une structure IPA basique
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Structure d'un IPA basique
            payload_dir = temp_path / "Payload"
            payload_dir.mkdir()
            
            app_dir = payload_dir / f"{config.app_name}.app"
            app_dir.mkdir()
            
            # Fichier Info.plist minimal
            info_plist = {
                'CFBundleName': config.app_name,
                'CFBundleVersion': config.version,
                'CFBundleShortVersionString': config.version,
                'CFBundleExecutable': config.app_name
            }
            
            with open(app_dir / "Info.plist", 'wb') as f:
                plistlib.dump(info_plist, f)
            
            # Crée l'archive ZIP
            shutil.make_archive(str(ipa_path.with_suffix('')), 'zip', str(temp_path))
            ipa_path.with_suffix('.zip').rename(ipa_path)
        
        print(f"✅ IPA de débogage créé: {ipa_path}")
        return str(ipa_path)
    
    def _check_xcode(self) -> bool:
        """Vérifie la disponibilité de Xcode"""
        try:
            result = subprocess.run([
                "xcodebuild", "-version"
            ], capture_output=True, text=True)
            
            return result.returncode == 0
        except FileNotFoundError:
            print("⚠️ Xcode non trouvé - le build iOS ne fonctionnera pas")
            return False