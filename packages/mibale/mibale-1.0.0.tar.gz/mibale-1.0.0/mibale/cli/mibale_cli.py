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
        
        # Chemin du template
        template_dir = Path(__file__).parent.parent.parent / "templates" / "default"
        project_dir = Path.cwd() / project_name
        
        if project_dir.exists():
            print(f"❌ Le dossier {project_name} existe déjà!")
            return False
        
        # Copie du template
        shutil.copytree(template_dir, project_dir)
        
        # Met à jour la configuration
        self._update_project_config(project_dir, project_name)
        
        print(f"✅ Projet {project_name} créé avec succès!")
        print(f"📁 Dossier: {project_dir}")
        print("\nPour démarrer:")
        print(f"  cd {project_name}")
        print("  pip install -r requirements.txt")
        print("  mibale dev")
        
        return True
    
    def run_dev(self, platform="android", port=3000, host="localhost"):
        """mibale dev --platform android --port 3000"""
        print(f"🛠️  Démarrage du serveur de développement Mibale...")
        print(f"📱 Plateforme: {platform}")
        print(f"📍 Port: {port}")
        
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
    
    def run_build(self, platform="android", mode="debug"):
        """mibale build [android|ios] --mode debug"""
        print(f"🔨 Construction pour {platform} ({mode})...")
        
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
    
    def run_serve(self):
        """mibale serve - Serveur de production"""
        print("🌐 Démarrage du serveur de production...")
        # Implémentation du serveur production
        pass
    
    def add_component(self, component_name):
        """mibale add ComponentName"""
        print(f"➕ Ajout du composant: {component_name}")
        
        component_content = f'''<template>
<View class="container">
    <Text class="title">{component_name}</Text>
    <Text class="content">Nouveau composant créé avec Mibale</Text>
</View>
</template>

<script>
from mibale import BaseComponent

class {component_name}(BaseComponent):
    def __init__(self):
        super().__init__()
        self.message = "Hello from {component_name}"
    
    def on_mount(self):
        print("Component {component_name} mounted")
    
    def on_destroy(self):
        print("Component {component_name} destroyed")
</script>

<style scoped>
.container {{
    padding: 16px;
    background-color: #ffffff;
}}

.title {{
    font-size: 24px;
    font-weight: bold;
    color: #333333;
    margin-bottom: 8px;
}}

.content {{
    font-size: 16px;
    color: #666666;
}}
</style>
'''
        
        component_path = Path("src/components") / f"{component_name}.mb"
        component_path.parent.mkdir(exist_ok=True)
        
        with open(component_path, 'w', encoding='utf-8') as f:
            f.write(component_content)
        
        print(f"✅ Composant créé: {component_path}")
    
    def generate(self, resource_type, name):
        """mibale generate [component|store|view] Name"""
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
        store_content = f'''from mibale.stores import defineStore

def use{store_name.capitalize()}Store():
    return defineStore('{store_name.lower()}', {{
        # State
        'state': {{
            'data': None,
            'loading': False,
            'error': None
        }},
        
        # Getters
        'getters': {{
            'hasData': lambda state: state['data'] is not None,
            'isLoading': lambda state: state['loading']
        }},
        
        # Actions  
        'actions': {{
            'async fetchData'(state) {{
                state['loading'] = True
                state['error'] = None
                
                try:
                    # Implémentez votre logique ici
                    # state['data'] = await api.fetch{store_name.capitalize()}()
                    pass
                except Exception as e:
                    state['error'] = str(e)
                finally:
                    state['loading'] = False
            }},
            
            'clearData'(state) {{
                state['data'] = None
                state['error'] = None
            }}
        }}
    }})
'''
        
        store_path = Path("src/stores") / f"{store_name.lower()}_store.py"
        store_path.parent.mkdir(exist_ok=True)
        
        with open(store_path, 'w', encoding='utf-8') as f:
            f.write(store_content)
        
        print(f"✅ Store créé: {store_path}")
    
    def _generate_view(self, view_name):
        """Génère une vue"""
        view_content = f'''<template>
<View class="container">
    <Text class="title">{view_name}</Text>
    <Text class="content">Ceci est la vue {view_name}</Text>
</View>
</template>

<script>
from mibale import BaseComponent

class {view_name}(BaseComponent):
    def __init__(self):
        super().__init__()
        self.message = "Welcome to {view_name}"
    
    def on_mount(self):
        print("View {view_name} mounted")
</script>

<style scoped>
.container {{
    flex: 1;
    padding: 16px;
    background-color: #f5f5f5;
}}

.title {{
    font-size: 28px;
    font-weight: bold;
    color: #333333;
    margin-bottom: 16px;
    text-align: center;
}}

.content {{
    font-size: 16px;
    color: #666666;
    text-align: center;
}}
</style>
'''
        
        view_path = Path("src/views") / f"{view_name}.mb"
        view_path.parent.mkdir(exist_ok=True)
        
        with open(view_path, 'w', encoding='utf-8') as f:
            f.write(view_content)
        
        print(f"✅ Vue créée: {view_path}")
    
    def _update_project_config(self, project_dir, project_name):
        """Met à jour la configuration du projet"""
        config_file = project_dir / "mibale.config.py"
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
            
            content = content.replace("Mon App Mibale", project_name)
            
            with open(config_file, 'w') as f:
                f.write(content)

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