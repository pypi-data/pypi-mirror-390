import http.server
import socketserver
import threading
import webbrowser
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from .file_watcher import FileWatcher
from .hot_reloader import HotReloader

class MibaleDevServer:
    """Serveur de développement Mibale avec hot-reload"""
    
    def __init__(self, port=3000, host='localhost', platform="auto"):
        self.port = port
        self.host = host
        self.platform = platform
        self.is_running = False
        self.current_app = None
        self.render_engine = None
        self.file_watcher = None
        self.hot_reloader = None
        self.dev_console_logs = []
        
        # Statistiques
        self.stats = {
            'start_time': time.time(),
            'reload_count': 0,
            'components_loaded': 0,
            'last_reload': None
        }
        
        print(f"🚀 Serveur de développement Mibale initialisé")
        print(f"📍 Adresse: http://{host}:{port}")
        print(f"📱 Plateforme: {platform}")
    
    def start(self):
        """Démarre le serveur de développement"""
        print("🛠️  Démarrage du serveur de développement...")
        
        try:
            # Initialise le moteur de rendu
            self._init_render_engine()
            
            # Initialise le hot-reloader
            self.hot_reloader = HotReloader(self)
            
            # Initialise le file watcher
            self.file_watcher = FileWatcher(self._on_file_changed)
            self.file_watcher.start()
            
            # Charge l'application initiale
            self._load_initial_app()
            
            # Démarre le serveur HTTP
            self._start_http_server()
            
            # Ouvre le navigateur
            self._open_browser()
            
            print("✅ Serveur de développement démarré avec succès!")
            print("👁️  Surveillance des fichiers activée")
            print("🔄 Hot-reload prêt")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage serveur dev: {e}")
            return False
    
    def _init_render_engine(self):
        """Initialise le moteur de rendu pour la plateforme cible"""
        from ..render.render_engine import RenderEngine
        
        self.render_engine = RenderEngine()
        
        # Détermine la plateforme
        if self.platform == "auto":
            # Détection automatique
            pass
        elif self.platform == "android":
            from ..android.renderer.android_renderer import AndroidRenderer
            self.render_engine.native_renderer = AndroidRenderer()
            self.render_engine.platform = "android"
        elif self.platform == "ios":
            from ..ios.renderer.ios_renderer import IOSRenderer
            self.render_engine.native_renderer = IOSRenderer()
            self.render_engine.platform = "ios"
        
        # Initialise le moteur
        if not self.render_engine.initialize():
            print("❌ Impossible d'initialiser le moteur de rendu")
    
    def _load_initial_app(self):
        """Charge l'application initiale"""
        try:
            from ..compiler.mb_compiler import MBCompiler
            from ..core.application import MibaleApp
            
            compiler = MBCompiler()
            project_data = compiler.compile_project(Path('.'))
            
            # Crée l'application
            self.current_app = MibaleApp(project_data)
            self.stats['components_loaded'] = len(project_data.get('components', {}))
            
            # Rend l'application
            if self.render_engine:
                success = self.render_engine.render_component(project_data)
                if success:
                    print("✅ Application rendue avec succès")
                else:
                    print("❌ Erreur lors du rendu initial")
            
            self._log_dev("🔧 Application chargée initialement")
            
        except Exception as e:
            self._log_dev(f"❌ Erreur chargement application: {e}")
            print(f"❌ Erreur chargement application: {e}")
    
    def _start_http_server(self):
        """Démarre le serveur HTTP pour l'interface de dev"""
        handler = self._create_request_handler()
        
        def run_server():
            with socketserver.TCPServer((self.host, self.port), handler) as httpd:
                self.is_running = True
                print(f"🌐 Serveur HTTP démarré sur http://{self.host}:{self.port}")
                httpd.serve_forever()
        
        # Démarre dans un thread séparé
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def _create_request_handler(self):
        """Crée le gestionnaire de requêtes HTTP"""
        class DevRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.dev_server = self.server.dev_server
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                # Routes spéciales du serveur de dev
                if self.path == '/__mibale_dev':
                    self._serve_dev_console()
                elif self.path == '/__mibale_health':
                    self._serve_health_check()
                elif self.path == '/__mibale_reload':
                    self._handle_hot_reload()
                elif self.path == '/__mibale_logs':
                    self._serve_logs()
                elif self.path.startswith('/__mibale_component/'):
                    self._serve_component_preview()
                else:
                    # Servir les fichiers statiques
                    super().do_GET()
            
            def do_POST(self):
                if self.path == '/__mibale_build':
                    self._handle_build_request()
                elif self.path == '/__mibale_restart':
                    self._handle_restart_request()
                else:
                    self.send_error(404)
            
            def _serve_dev_console(self):
                """Sert la console de développement"""
                html = self._generate_dev_console()
                self._send_html_response(200, html)
            
            def _serve_health_check(self):
                """Endpoint de santé"""
                health_data = {
                    'status': 'running',
                    'platform': self.dev_server.platform,
                    'uptime': time.time() - self.dev_server.stats['start_time'],
                    'reloads': self.dev_server.stats['reload_count'],
                    'components': self.dev_server.stats['components_loaded'],
                    'last_reload': self.dev_server.stats['last_reload']
                }
                self._send_json_response(200, health_data)
            
            def _handle_hot_reload(self):
                """Force un rechargement à chaud"""
                self.dev_server.hot_reloader.trigger_reload()
                self._send_json_response(200, {'reloaded': True})
            
            def _serve_logs(self):
                """Retourne les logs de développement"""
                self._send_json_response(200, self.dev_server.dev_console_logs)
            
            def _serve_component_preview(self):
                """Aperçu d'un composant individuel"""
                component_name = self.path.split('/')[-1]
                html = self._generate_component_preview(component_name)
                self._send_html_response(200, html)
            
            def _handle_build_request(self):
                """Gère une demande de build"""
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                build_config = json.loads(post_data)
                
                # Déclenche le build
                success = self.dev_server._trigger_build(build_config)
                self._send_json_response(200, {'building': success})
            
            def _handle_restart_request(self):
                """Redémarre le serveur"""
                self.dev_server._restart_server()
                self._send_json_response(200, {'restarting': True})
            
            def _generate_dev_console(self):
                """Génère l'interface de console de développement"""
                return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mibale Dev Console</title>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a; color: #ffffff; line-height: 1.6;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem; text-align: center; 
        }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ opacity: 0.9; font-size: 1.1rem; }}
        
        .stats {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem; padding: 1.5rem; background: #2d2d2d;
        }}
        .stat-card {{ 
            background: #3a3a3a; padding: 1rem; border-radius: 8px;
            text-align: center; 
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 0.9rem; opacity: 0.7; }}
        
        .controls {{ 
            padding: 1.5rem; background: #252525; border-bottom: 1px solid #333;
        }}
        .btn {{ 
            background: #667eea; color: white; border: none; padding: 0.75rem 1.5rem;
            border-radius: 6px; margin-right: 0.5rem; cursor: pointer; font-size: 1rem;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #5a6fd8; }}
        .btn.danger {{ background: #e74c3c; }}
        .btn.danger:hover {{ background: #c0392b; }}
        .btn.success {{ background: #27ae60; }}
        .btn.success:hover {{ background: #219a52; }}
        
        .logs {{ 
            padding: 1.5rem; max-height: 400px; overflow-y: auto;
            background: #1a1a1a; font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
        }}
        .log-entry {{ 
            padding: 0.5rem; border-bottom: 1px solid #333; 
            display: flex; align-items: center;
        }}
        .log-time {{ color: #666; margin-right: 1rem; min-width: 80px; }}
        .log-message {{ flex: 1; }}
        .log-level.info {{ color: #3498db; }}
        .log-level.success {{ color: #27ae60; }}
        .log-level.warning {{ color: #f39c12; }}
        .log-level.error {{ color: #e74c3c; }}
        
        .components {{ 
            padding: 1.5rem; background: #2d2d2d; margin: 1rem;
            border-radius: 8px;
        }}
        .components h3 {{ margin-bottom: 1rem; color: #667eea; }}
        .component-list {{ display: grid; gap: 0.5rem; }}
        .component-item {{ 
            background: #3a3a3a; padding: 0.75rem; border-radius: 4px;
            display: flex; justify-content: space-between; align-items: center;
        }}
        .component-actions {{ display: flex; gap: 0.5rem; }}
        .component-btn {{ 
            background: #555; color: white; border: none; padding: 0.25rem 0.5rem;
            border-radius: 3px; cursor: pointer; font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Mibale Dev Console</h1>
        <p>Plateforme: {self.dev_server.platform} | Port: {self.dev_server.port}</p>
    </div>
    
    <div class="stats" id="stats">
        <!-- Les stats seront mises à jour par JavaScript -->
    </div>
    
    <div class="controls">
        <button class="btn" onclick="reloadApp()">🔄 Recharger</button>
        <button class="btn success" onclick="buildApp()">🔨 Construire</button>
        <button class="btn" onclick="openPreview()">👁️ Aperçu</button>
        <button class="btn danger" onclick="restartServer()">🔄 Redémarrer</button>
    </div>
    
    <div class="logs" id="logs">
        <!-- Les logs seront injectés ici -->
    </div>
    
    <div class="components">
        <h3>📦 Composants Chargés</h3>
        <div class="component-list" id="components">
            <!-- Liste des composants -->
        </div>
    </div>

    <script>
        // Mise à jour en temps réel
        function updateStats() {{
            fetch('/__mibale_health')
                .then(r => r.json())
                .then(data => {{
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${{Math.floor(data.uptime)}}s</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{data.reloads}}</div>
                            <div class="stat-label">Rechargements</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{data.components}}</div>
                            <div class="stat-label">Composants</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{data.platform}}</div>
                            <div class="stat-label">Plateforme</div>
                        </div>
                    `;
                }});
        }}
        
        function updateLogs() {{
            fetch('/__mibale_logs')
                .then(r => r.json())
                .then(logs => {{
                    const logsHtml = logs.map(log => `
                        <div class="log-entry">
                            <div class="log-time">${{new Date(log.timestamp).toLocaleTimeString()}}</div>
                            <div class="log-message ${{log.level ? 'log-level ' + log.level : ''}}">
                                ${{log.message}}
                            </div>
                        </div>
                    `).join('');
                    document.getElementById('logs').innerHTML = logsHtml;
                    document.getElementById('logs').scrollTop = document.getElementById('logs').scrollHeight;
                }});
        }}
        
        function reloadApp() {{
            fetch('/__mibale_reload', {{ method: 'POST' }})
                .then(() => addLog('🔁 Rechargement manuel déclenché', 'info'));
        }}
        
        function buildApp() {{
            fetch('/__mibale_build', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ platform: '{self.dev_server.platform}', mode: 'debug' }})
            }}).then(() => addLog('🔨 Construction déclenchée', 'info'));
        }}
        
        function restartServer() {{
            fetch('/__mibale_restart', {{ method: 'POST' }})
                .then(() => addLog('🔄 Redémarrage serveur...', 'warning'));
        }}
        
        function openPreview() {{
            window.open('/__mibale_component/preview', '_blank');
        }}
        
        function addLog(message, level = 'info') {{
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <div class="log-time">${{new Date().toLocaleTimeString()}}</div>
                <div class="log-message log-level ${{level}}">${{message}}</div>
            `;
            document.getElementById('logs').appendChild(logEntry);
            document.getElementById('logs').scrollTop = document.getElementById('logs').scrollHeight;
        }}
        
        // Polling automatique
        setInterval(updateStats, 2000);
        setInterval(updateLogs, 1000);
        
        // Initialisation
        updateStats();
        updateLogs();
        addLog('✅ Console de développement connectée', 'success');
    </script>
</body>
</html>
"""
            
            def _generate_component_preview(self, component_name):
                """Génère un aperçu de composant"""
                return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Aperçu: {component_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 2rem; }}
        .preview-container {{ border: 2px dashed #ccc; padding: 2rem; }}
    </style>
</head>
<body>
    <h1>👁️ Aperçu: {component_name}</h1>
    <div class="preview-container">
        <p>Aperçu du composant <strong>{component_name}</strong></p>
        <p><em>L'aperçu en temps réel sera implémenté ici</em></p>
    </div>
</body>
</html>
"""
            
            def _send_html_response(self, code, html):
                self.send_response(code)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            
            def _send_json_response(self, code, data):
                self.send_response(code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
        
        # Patch pour passer le serveur dev au handler
        class PatchedTCPServer(socketserver.TCPServer):
            def __init__(self, *args, **kwargs):
                self.dev_server = self
                super().__init__(*args, **kwargs)
        
        # Monkey patch pour passer la référence
        import types
        handler_class = types.new_class('MibaleDevHandler', (DevRequestHandler,))
        return handler_class
    
    def _on_file_changed(self, file_path: Path):
        """Callback appelé quand un fichier est modifié"""
        self._log_dev(f"📁 Fichier modifié: {file_path}")
        
        if self.hot_reloader:
            self.hot_reloader.handle_file_change(file_path)
    
    def _trigger_build(self, build_config: Dict[str, Any]) -> bool:
        """Déclenche un build de l'application"""
        try:
            from ..builder.app_builder import AppBuilder
            
            platform = build_config.get('platform', self.platform)
            mode = build_config.get('mode', 'debug')
            
            builder = AppBuilder(platform, mode)
            
            if platform == "android":
                result = builder.build_apk()
            elif platform == "ios":
                result = builder.build_ipa()
            else:
                result = None
            
            if result:
                self._log_dev(f"✅ Build réussi: {result}", "success")
                return True
            else:
                self._log_dev("❌ Échec du build", "error")
                return False
                
        except Exception as e:
            self._log_dev(f"❌ Erreur build: {e}", "error")
            return False
    
    def _restart_server(self):
        """Redémarre le serveur de développement"""
        self._log_dev("🔄 Redémarrage du serveur...", "warning")
        # Implémentation du redémarrage
        print("🔄 Redémarrage du serveur de développement...")
    
    def _open_browser(self):
        """Ouvre le navigateur sur la console de dev"""
        def open():
            time.sleep(1)  # Attendre que le serveur démarre
            webbrowser.open(f"http://{self.host}:{self.port}/__mibale_dev")
        
        threading.Thread(target=open, daemon=True).start()
    
    def _log_dev(self, message: str, level: str = "info"):
        """Ajoute un log à la console de développement"""
        log_entry = {
            'timestamp': time.time(),
            'message': message,
            'level': level
        }
        self.dev_console_logs.append(log_entry)
        
        # Garder seulement les 100 derniers logs
        if len(self.dev_console_logs) > 100:
            self.dev_console_logs.pop(0)
        
        # Afficher dans la console aussi
        level_icons = {
            'info': 'ℹ️',
            'success': '✅', 
            'warning': '⚠️',
            'error': '❌'
        }
        print(f"{level_icons.get(level, '📝')} {message}")
    
    def stop(self):
        """Arrête le serveur de développement"""
        self.is_running = False
        if self.file_watcher:
            self.file_watcher.stop()
        if self.hot_reloader:
            self.hot_reloader.cleanup()
        
        self._log_dev("🛑 Serveur de développement arrêté", "warning")
        print("🛑 Serveur de développement arrêté")