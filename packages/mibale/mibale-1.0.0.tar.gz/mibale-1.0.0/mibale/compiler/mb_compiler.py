import re
import ast
from typing import Dict, Any, List, Optional
from pathlib import Path

class MBCompiler:
    """Compilateur pour les fichiers .mb (similaire à Vue SFC compiler)"""
    
    def __init__(self):
        self.template_pattern = re.compile(r'<template>(.*?)</template>', re.DOTALL)
        self.script_pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL)
        self.style_pattern = re.compile(r'<style(?:\s+scoped)?>(.*?)</style>', re.DOTALL)
        self.directive_pattern = re.compile(r'v-([a-z-]+)(?::([a-z-]+))?(?:="(.*?)")?')
        
    def compile_project(self, project_dir: Path) -> Dict[str, Any]:
        """Compile un projet Mibale entier"""
        app_data = {
            'name': 'Mibale App',
            'version': '1.0.0',
            'routes': [],
            'stores': {},
            'components': {},
            'main_component': None
        }
        
        # Compile tous les composants .mb
        for mb_file in project_dir.rglob("*.mb"):
            component_data = self.compile_file(mb_file)
            component_name = mb_file.stem
            app_data['components'][component_name] = component_data
        
        # Charge la configuration
        app_data.update(self._load_project_config(project_dir))
        
        return app_data
    
    def compile_file(self, file_path: Path) -> Dict[str, Any]:
        """Compile un fichier .mb individuel"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.compile(content, str(file_path))
    
    def compile(self, content: str, filename: str = None) -> Dict[str, Any]:
        """Compile le contenu d'un fichier .mb"""
        template = self._extract_template(content)
        script = self._extract_script(content)
        style = self._extract_style(content)
        
        # Parse le template en AST
        template_ast = self._parse_template(template)
        
        # Compile le script
        component_class = self._compile_script(script, filename)
        
        # Compile les styles
        compiled_style = self._compile_style(style)
        
        return {
            'filename': filename,
            'template': template,
            'template_ast': template_ast,
            'script': script,
            'component': component_class,
            'style': compiled_style,
            'custom_blocks': self._extract_custom_blocks(content)
        }
    
    def _extract_template(self, content: str) -> str:
        """Extrait la section template"""
        match = self.template_pattern.search(content)
        return match.group(1).strip() if match else ""
    
    def _extract_script(self, content: str) -> str:
        """Extrait la section script"""
        match = self.script_pattern.search(content)
        return match.group(1).strip() if match else ""
    
    def _extract_style(self, content: str) -> str:
        """Extrait la section style"""
        match = self.style_pattern.search(content)
        return match.group(1).strip() if match else ""
    
    def _extract_custom_blocks(self, content: str) -> Dict[str, str]:
        """Extrait les blocs personnalisés"""
        blocks = {}
        custom_pattern = re.compile(r'<([a-z-]+)>(.*?)</\\1>', re.DOTALL)
        
        for match in custom_pattern.finditer(content):
            block_name = match.group(1)
            block_content = match.group(2).strip()
            blocks[block_name] = block_content
        
        return blocks
    
    def _parse_template(self, template: str) -> Dict[str, Any]:
        """Parse le template en AST"""
        # Implémentation simplifiée du parser de template
        lines = template.strip().split('\n')
        ast_nodes = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<!--'):
                node = self._parse_template_line(line)
                if node:
                    ast_nodes.append(node)
        
        return {
            'type': 'root',
            'children': ast_nodes
        }
    
    def _parse_template_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne du template"""
        # Détection des balises
        tag_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)(.*?)(?:>(.*)</\\1>|\\s*/>)', line, re.DOTALL)
        if not tag_match:
            return None
        
        tag_name = tag_match.group(1)
        attrs_str = tag_match.group(2)
        content = tag_match.group(3) if tag_match.group(3) else ""
        
        # Parse les attributs
        attrs = self._parse_attributes(attrs_str)
        
        # Parse les directives
        directives = self._parse_directives(attrs)
        
        # Parse le contenu
        children = []
        if content:
            child_lines = content.strip().split('\n')
            for child_line in child_lines:
                child_node = self._parse_template_line(child_line.strip())
                if child_node:
                    children.append(child_node)
                elif child_line.strip():
                    children.append({
                        'type': 'text',
                        'content': child_line.strip()
                    })
        
        return {
            'type': 'element',
            'tag': tag_name,
            'attrs': attrs,
            'directives': directives,
            'children': children
        }
    
    def _parse_attributes(self, attrs_str: str) -> Dict[str, Any]:
        """Parse les attributs HTML"""
        attrs = {}
        attr_pattern = re.compile(r'([a-zA-Z-:@]+)="(.*?)"')
        
        for match in attr_pattern.finditer(attrs_str):
            key = match.group(1)
            value = match.group(2)
            
            # Détection des bindings
            if key.startswith(':'):
                attrs[key[1:]] = {
                    'type': 'binding',
                    'value': value
                }
            elif key.startswith('@'):
                attrs[key[1:]] = {
                    'type': 'event',
                    'value': value
                }
            else:
                attrs[key] = {
                    'type': 'literal',
                    'value': value
                }
        
        return attrs
    
    def _parse_directives(self, attrs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse les directives Vue-like"""
        directives = []
        
        for key, value in attrs.items():
            if key.startswith('v-'):
                directive_parts = key[2:].split(':')
                directive_name = directive_parts[0]
                directive_arg = directive_parts[1] if len(directive_parts) > 1 else None
                
                directives.append({
                    'name': directive_name,
                    'arg': directive_arg,
                    'value': value['value'],
                    'raw': key
                })
        
        return directives
    
    def _compile_script(self, script_content: str, filename: str = None) -> Any:
        """Compile la section script en classe Python"""
        if not script_content:
            return None
        
        try:
            # Extraction de la classe du composant
            class_name = self._extract_component_class_name(script_content)
            
            # Création d'un environnement d'exécution
            exec_globals = {
                '__file__': filename,
                'BaseComponent': None,
                'reactive': None,
                'ref': None,
                'computed': None,
                'watch': None
            }
            
            # Import des dépendances Mibale
            from ..core.component import BaseComponent
            from ..core.reactive import reactive, ref, computed, watch
            
            exec_globals.update({
                'BaseComponent': BaseComponent,
                'reactive': reactive,
                'ref': ref,
                'computed': computed,
                'watch': watch
            })
            
            # Exécution du script
            exec(script_content, exec_globals)
            
            # Récupération de la classe du composant
            if class_name in exec_globals:
                return exec_globals[class_name]
            else:
                # Recherche de toute classe qui hérite de BaseComponent
                for name, obj in exec_globals.items():
                    if (isinstance(obj, type) and 
                        issubclass(obj, BaseComponent) and 
                        obj != BaseComponent):
                        return obj
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur compilation script {filename}: {e}")
            return None
    
    def _extract_component_class_name(self, script_content: str) -> Optional[str]:
        """Extrait le nom de la classe du composant"""
        try:
            tree = ast.parse(script_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    return node.name
        except:
            pass
        return None
    
    def _compile_style(self, style_content: str) -> Dict[str, Any]:
        """Compile la section style"""
        if not style_content:
            return {}
        
        # Parse le CSS-like en objets
        styles = {}
        current_selector = None
        current_rules = {}
        
        for line in style_content.split('\n'):
            line = line.strip()
            
            if line.endswith('{'):
                if current_selector:
                    styles[current_selector] = current_rules
                current_selector = line[:-1].strip()
                current_rules = {}
            
            elif ':' in line and not line.endswith('}'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().rstrip(';')
                current_rules[key] = self._parse_css_value(value)
            
            elif line == '}':
                if current_selector:
                    styles[current_selector] = current_rules
                current_selector = None
                current_rules = {}
        
        return styles
    
    def _parse_css_value(self, value: str) -> Any:
        """Parse une valeur CSS"""
        # Couleurs
        if value.startswith('#') or value.startswith('rgb'):
            return value
        # Dimensions
        elif value.endswith(('px', 'dp', 'sp')):
            return float(value[:-2])
        # Nombres
        elif value.replace('.', '').isdigit():
            return float(value)
        # Chaînes
        else:
            return value
    
    def _load_project_config(self, project_dir: Path) -> Dict[str, Any]:
        """Charge la configuration du projet"""
        config = {
            'routes': [],
            'stores': {}
        }
        
        # Charge les routes
        routes_file = project_dir / 'src' / 'router' / 'routes.py'
        if routes_file.exists():
            try:
                spec = importlib.util.spec_from_file_location("routes", routes_file)
                routes_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(routes_module)
                
                if hasattr(routes_module, 'routes'):
                    config['routes'] = routes_module.routes
            except Exception as e:
                print(f"❌ Erreur chargement routes: {e}")
        
        return config

# Fonction d'export
def compile_mb(content: str, filename: str = None) -> Dict[str, Any]:
    """Fonction utilitaire pour compiler du contenu .mb"""
    compiler = MBCompiler()
    return compiler.compile(content, filename)