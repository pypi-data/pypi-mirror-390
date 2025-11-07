#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path

class MibaleCLI:
    def __init__(self):
        self.commands = {
            'create': self.create_project,
            'dev': self.run_dev,
            'build': self.run_build,
            'serve': self.run_serve,
            'add': self.add_component,
            'generate': self.generate
        }
    
    def create_project(self, project_name):
        """mibale create my-app"""
        print(f"🚀 Création du projet Mibale: {project_name}")
        
        # Plusieurs emplacements possibles pour les templates
        template_dirs = [
            # 1. Dans l'installation du package
            Path(__file__).parent.parent / "templates" / "default",
            # 2. Dans le dossier courant (pour le développement)
            Path(".") / "mibale" / "templates" / "default",
            # 3. Dans le home directory
            Path.home() / ".mibale" / "templates" / "default",
        ]
        
        template_dir = None
        for dir_candidate in template_dirs:
            if dir_candidate.exists():
                template_dir = dir_candidate
                print(f"📁 Template trouvé dans: {template_dir}")
                break
        
        project_dir = Path.cwd() / project_name
        
        if project_dir.exists():
            print(f"❌ Le dossier {project_name} existe déjà!")
            return False
        
        if template_dir and template_dir.exists():
            # Copie du template
            try:
                shutil.copytree(template_dir, project_dir)
                print("✅ Template copié avec succès")
            except Exception as e:
                print(f"❌ Erreur lors de la copie du template: {e}")
                print("🔄 Création d'une structure basique...")
                return self._create_basic_structure(project_dir, project_name)
        else:
            print("❌ Template par défaut non trouvé.")
            print("🔄 Création d'une structure basique...")
            return self._create_basic_structure(project_dir, project_name)
        
        # Met à jour la configuration
        self._update_project_config(project_dir, project_name)
        
        print(f"✅ Projet {project_name} créé avec succès!")
        print(f"📁 Dossier: {project_dir}")
        print("\nPour démarrer:")
        print(f"  cd {project_name}")
        print("  pip install -r requirements.txt")
        print("  mibale dev")
        
        return True
    
    def _create_basic_structure(self, project_dir, project_name):
        """Crée une structure de projet basique si le template n'est pas trouvé"""
        try:
            # Crée la structure de dossiers
            directories = [
                "src",
                "src/components", 
                "src/views",
                "src/stores",
                "src/router",
                "src/services",
                "static",
                "static/images"
            ]
            
            for directory in directories:
                (project_dir / directory).mkdir(parents=True, exist_ok=True)
            
            # Crée les fichiers essentiels
            self._create_basic_files(project_dir, project_name)
            
            print(f"✅ Structure basique créée pour: {project_name}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur création structure basique: {e}")
            return False
    
    def _create_basic_files(self, project_dir, project_name):
        """Crée les fichiers de base pour un nouveau projet"""
        
        # requirements.txt
        requirements_content = """mibale>=1.0.0
requests>=2.25.0
watchdog>=2.1.0
"""
        (project_dir / "requirements.txt").write_text(requirements_content)
        
        # mibale.config.py
        config_content = f'''import os
from pathlib import Path

class MibaleConfig:
    def __init__(self):
        self.app_name = "{project_name}"
        self.version = "1.0.0"
        
        self.build = {{
            'assets_dir': 'static',
            'output_dir': 'dist',
            'android': {{
                'package_name': 'com.mibale.{project_name.lower()}',
                'version_code': 1,
                'permissions': ['INTERNET', 'CAMERA']
            }},
            'ios': {{
                'bundle_identifier': 'com.mibale.{project_name.lower()}',
                'version': '1.0.0'
            }}
        }}
        
        self.dev_server = {{
            'port': 3000,
            'host': 'localhost',
            'hot_reload': True
        }}

config = MibaleConfig()
'''
        (project_dir / "mibale.config.py").write_text(config_content)
        
        # main.py
        main_content = f'''from mibale import create_app
from mibale.router import Router, Route

# Import des vues
from .views.HomeView import HomeView

# Configuration des routes
routes = [
    Route(path='/', component=HomeView, name='home'),
]

# Création de l'application
app = create_app({{
    'name': '{project_name}',
    'version': '1.0.0',
    'routes': routes
}})

if __name__ == "__main__":
    app.mount()
    print("🚀 Application {project_name} démarrée!")
'''
        (project_dir / "src" / "main.py").write_text(main_content)
        
        # HomeView.mb
        homeview_content = '''<template>
<View class="container">
    <Text class="title">Bienvenue dans votre app Mibale!</Text>
    <Text class="subtitle">Commencez à développer vos composants .mb</Text>
</View>
</template>

<script>
from mibale import BaseComponent

class HomeView(BaseComponent):
    def on_mount(self):
        print("📍 Vue d'accueil montée")
</script>

<style scoped>
.container {
    flex: 1;
    padding: 20px;
    background-color: #ffffff;
    align-items: center;
    justify-content: center;
}

.title {
    font-size: 24px;
    font-weight: bold;
    color: #333333;
    text-align: center;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 16px;
    color: #666666;
    text-align: center;
}
</style>
'''
        (project_dir / "src" / "views" / "HomeView.mb").write_text(homeview_content)
        
        # routes.py
        routes_content = '''from mibale.router import Route
from ..views.HomeView import HomeView

routes = [
    Route(path='/', component=HomeView, name='home'),
]

__all__ = ['routes']
'''
        (project_dir / "src" / "router" / "routes.py").write_text(routes_content)
        
        # README.md - Utilisation de format() au lieu de f-string pour éviter les problèmes
        readme_lines = [
            f"# {project_name}",
            "",
            "Application créée avec Mibale Framework.",
            "",
            "## Développement",
            "",
            "```bash",
            "# Installer les dépendances",
            "pip install -r requirements.txt",
            "",
            "# Lancer le serveur de développement",
            "mibale dev",
            "",
            "# Construire l'application",
            "mibale build android",
            "```",
            "",
            "## Structure",
            "",
            "- `src/main.py` - Point d'entrée",
            "- `src/views/` - Vues de l'application",
            "- `src/components/` - Composants réutilisables",
            "- `src/stores/` - State management",
            "- `src/router/` - Configuration des routes",
        ]
        readme_content = "\n".join(readme_lines)
        (project_dir / "README.md").write_text(readme_content)
    
    def _update_project_config(self, project_dir, project_name):
        """Met à jour la configuration du projet"""
        config_file = project_dir / "mibale.config.py"
        if config_file.exists():
            try:
                content = config_file.read_text()
                content = content.replace("Mon App Mibale", project_name)
                content = content.replace("com.mibale.app", f"com.mibale.{project_name.lower()}")
                config_file.write_text(content)
            except Exception as e:
                print(f"⚠️ Impossible de mettre à jour la configuration: {e}")
    
    def run_dev(self, platform="android", port=3000, host="localhost"):
        """mibale dev --platform android --port 3000"""
        print(f"🛠️  Démarrage du serveur de développement Mibale...")
        print(f"📱 Plateforme: {platform}")
        print(f"📍 Port: {port}")
        
        try:
            from ..dev.dev_server import MibaleDevServer
            server = MibaleDevServer(port=port, platform=platform, host=host)
            
            print("\n🌐 Interfaces disponibles:")
            print(f"   • Console de dev: http://{host}:{port}")
            print(f"   • App native: Rendue sur {platform} device/émulateur")
            print(f"   • Health check: http://{host}:{port}/__mibale_health")
            
            print("\n📋 Commandes utiles:")
            print("   • Ctrl+C pour arrêter")
            print("   • Modifiez un fichier .mb pour voir le hot-reload")
            
            server.start()
        except ImportError as e:
            print(f"❌ Impossible d'importer le serveur de développement: {e}")
            print("💡 Assurez-vous que Mibale est correctement installé")
        except Exception as e:
            print(f"❌ Erreur démarrage serveur dev: {e}")
    
    def run_build(self, platform="android", mode="debug"):
        """mibale build [android|ios] --mode debug"""
        print(f"🔨 Construction pour {platform} ({mode})...")
        
        try:
            from ..builder.app_builder import AppBuilder
            builder = AppBuilder(platform, mode)
            
            if platform == "android":
                output = builder.build_apk()
                if output:
                    print(f"✅ APK généré: {output}")
                else:
                    print("❌ Erreur lors de la construction")
            elif platform == "ios":
                output = builder.build_ipa()
                if output:
                    print(f"✅ IPA généré: {output}")
                else:
                    print("❌ Erreur lors de la construction")
            else:
                print("❌ Plateforme non supportée")
        except ImportError as e:
            print(f"❌ Impossible d'importer le système de build: {e}")
            print("💡 Assurez-vous que Mibale est correctement installé")
        except Exception as e:
            print(f"❌ Erreur lors du build: {e}")
    
    def run_serve(self):
        """mibale serve - Serveur de production"""
        print("🌐 Démarrage du serveur de production...")
        # Implémentation du serveur production
        pass
    
    def add_component(self, component_name):
        """mibale add ComponentName"""
        print(f"➕ Ajout du composant: {component_name}")
        
        # Vérifie si on est dans un projet Mibale
        if not Path("src").exists():
            print("❌ Vous devez être dans un projet Mibale pour ajouter un composant")
            print("💡 Exécutez cette commande depuis la racine de votre projet")
            return
        
        # Utilisation de format() au lieu de f-string multiligne
        component_lines = [
            "<template>",
            "<View class=\"container\">",
            f"    <Text class=\"title\">{component_name}</Text>",
            "    <Text class=\"content\">Nouveau composant créé avec Mibale</Text>",
            "</View>",
            "</template>",
            "",
            "<script>",
            "from mibale import BaseComponent",
            "",
            f"class {component_name}(BaseComponent):",
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.message = \"Hello from {component_name}\"",
            "",
            "    def on_mount(self):",
            f"        print(\"Component {component_name} mounted\")",
            "",
            "    def on_destroy(self):",
            f"        print(\"Component {component_name} destroyed\")",
            "</script>",
            "",
            "<style scoped>",
            ".container {",
            "    padding: 16px;",
            "    background-color: #ffffff;",
            "}",
            "",
            ".title {",
            "    font-size: 24px;",
            "    font-weight: bold;",
            "    color: #333333;",
            "    margin-bottom: 8px;",
            "}",
            "",
            ".content {",
            "    font-size: 16px;",
            "    color: #666666;",
            "}",
            "</style>",
        ]
        component_content = "\n".join(component_lines)
        
        component_path = Path("src/components") / f"{component_name}.mb"
        component_path.parent.mkdir(exist_ok=True)
        
        with open(component_path, 'w', encoding='utf-8') as f:
            f.write(component_content)
        
        print(f"✅ Composant créé: {component_path}")
    
    def generate(self, resource_type, name):
        """mibale generate [component|store|view] Name"""
        # Vérifie si on est dans un projet Mibale
        if not Path("src").exists():
            print("❌ Vous devez être dans un projet Mibale pour générer des ressources")
            print("💡 Exécutez cette commande depuis la racine de votre projet")
            return
            
        if resource_type == "component":
            self.add_component(name)
        elif resource_type == "store":
            self._generate_store(name)
        elif resource_type == "view":
            self._generate_view(name)
        else:
            print(f"❌ Type de ressource inconnu: {resource_type}")
    
    def _generate_store(self, store_name):
        """Génère un store"""
        # Utilisation de format() au lieu de f-string multiligne
        store_lines = [
            "from mibale.stores import defineStore",
            "",
            f"def use{store_name.capitalize()}Store():",
            f"    return defineStore('{store_name.lower()}', {{",
            "        # State",
            "        'state': {",
            "            'data': None,",
            "            'loading': False,",
            "            'error': None",
            "        },",
            "        ",
            "        # Getters",
            "        'getters': {",
            "            'hasData': lambda state: state['data'] is not None,",
            "            'isLoading': lambda state: state['loading']",
            "        },",
            "        ",
            "        # Actions  ",
            "        'actions': {",
            "            'async fetchData'(state) {",
            "                state['loading'] = True",
            "                state['error'] = None",
            "                ",
            "                try:",
            "                    # Implémentez votre logique ici",
            f"                    # state['data'] = await api.fetch{store_name.capitalize()}()",
            "                    pass",
            "                except Exception as e:",
            "                    state['error'] = str(e)",
            "                finally:",
            "                    state['loading'] = False",
            "            },",
            "            ",
            "            'clearData'(state) {",
            "                state['data'] = None",
            "                state['error'] = None",
            "            }",
            "        }",
            "    })",
        ]
        store_content = "\n".join(store_lines)
        
        store_path = Path("src/stores") / f"{store_name.lower()}_store.py"
        store_path.parent.mkdir(exist_ok=True)
        
        with open(store_path, 'w', encoding='utf-8') as f:
            f.write(store_content)
        
        print(f"✅ Store créé: {store_path}")
    
    def _generate_view(self, view_name):
        """Génère une vue"""
        # Utilisation de format() au lieu de f-string multiligne
        view_lines = [
            "<template>",
            "<View class=\"container\">",
            f"    <Text class=\"title\">{view_name}</Text>",
            f"    <Text class=\"content\">Ceci est la vue {view_name}</Text>",
            "</View>",
            "</template>",
            "",
            "<script>",
            "from mibale import BaseComponent",
            "",
            f"class {view_name}(BaseComponent):",
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.message = \"Welcome to {view_name}\"",
            "",
            "    def on_mount(self):",
            f"        print(\"View {view_name} mounted\")",
            "</script>",
            "",
            "<style scoped>",
            ".container {",
            "    flex: 1;",
            "    padding: 16px;",
            "    background-color: #f5f5f5;",
            "}",
            "",
            ".title {",
            "    font-size: 28px;",
            "    font-weight: bold;",
            "    color: #333333;",
            "    margin-bottom: 16px;",
            "    text-align: center;",
            "}",
            "",
            ".content {",
            "    font-size: 16px;",
            "    color: #666666;",
            "    text-align: center;",
            "}",
            "</style>",
        ]
        view_content = "\n".join(view_lines)
        
        view_path = Path("src/views") / f"{view_name}.mb"
        view_path.parent.mkdir(exist_ok=True)
        
        with open(view_path, 'w', encoding='utf-8') as f:
            f.write(view_content)
        
        print(f"✅ Vue créée: {view_path}")


def _get_platform_specific_requirements(self):
    """Retourne les requirements spécifiques à la plateforme"""
    import platform
    
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        return [
            "pyobjc>=9.0.0",
            "pyobjc-framework-cocoa>=9.0.0", 
            "pyobjc-framework-webkit>=9.0.0",
            "pyobjc-framework-mapkit>=9.0.0"
        ]
    else:
        return []

def main():
    cli = MibaleCLI()
    parser = argparse.ArgumentParser(description="Mibale CLI - Framework Vue.js-like en Python")
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # create
    create_parser = subparsers.add_parser('create', help='Créer un nouveau projet')
    create_parser.add_argument('project_name', help='Nom du projet')
    
    # dev
    dev_parser = subparsers.add_parser('dev', help='Lancer le serveur de développement')
    dev_parser.add_argument('--platform', default='android', choices=['android', 'ios'],
                          help='Plateforme cible (android/ios)')
    dev_parser.add_argument('--port', type=int, default=3000, help='Port du serveur de développement')
    dev_parser.add_argument('--host', default='localhost', help='Hôte du serveur de développement')
    
    # build
    build_parser = subparsers.add_parser('build', help='Construire l\'application')
    build_parser.add_argument('platform', nargs='?', default='android', 
                            choices=['android', 'ios'], help='Plateforme cible')
    build_parser.add_argument('--mode', default='debug', choices=['debug', 'release'],
                            help='Mode de construction')
    
    # add
    add_parser = subparsers.add_parser('add', help='Ajouter un composant')
    add_parser.add_argument('component_name', help='Nom du composant')
    
    # generate
    generate_parser = subparsers.add_parser('generate', help='Générer une ressource')
    generate_parser.add_argument('resource_type', choices=['component', 'store', 'view'],
                               help='Type de ressource à générer')
    generate_parser.add_argument('name', help='Nom de la ressource')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        cli.create_project(args.project_name)
    elif args.command == 'dev':
        cli.run_dev(args.platform, args.port, args.host)
    elif args.command == 'build':
        cli.run_build(args.platform, args.mode)
    elif args.command == 'add':
        cli.add_component(args.component_name)
    elif args.command == 'generate':
        cli.generate(args.resource_type, args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()