import re
from typing import Dict, Any
from .virtual_dom import VNode

class StyleEngine:
    """Moteur d'application des styles CSS-like"""
    
    def __init__(self):
        self.stylesheets = {}
    
    def apply_styles(self, node: VNode, styles: Dict[str, Any]):
        """Applique les styles à un nœud et ses enfants"""
        if styles:
            self._apply_styles_to_node(node, styles)
    
    def _apply_styles_to_node(self, node: VNode, styles: Dict[str, Dict[str, Any]]):
        """Applique récursivement les styles à un nœud"""
        # Applique les styles par ID
        node_id = node.get_prop('id')
        if node_id and f'#{node_id}' in styles:
            node_style = styles[f'#{node_id}']
            node.style.update(node_style)
        
        # Applique les styles par classe
        node_class = node.get_prop('class')
        if node_class:
            classes = node_class.split()
            for cls in classes:
                if f'.{cls}' in styles:
                    node_style = styles[f'.{cls}']
                    node.style.update(node_style)
        
        # Applique les styles par tag
        tag_selector = node.tag.lower()
        if tag_selector in styles:
            node_style = styles[tag_selector]
            node.style.update(node_style)
        
        # Applique aux enfants
        for child in node.children:
            if isinstance(child, VNode):
                self._apply_styles_to_node(child, styles)
    
    def parse_styles(self, style_content: str) -> Dict[str, Dict[str, Any]]:
        """Parse le CSS-like en objets style"""
        styles = {}
        current_selector = None
        current_rules = {}
        
        for line in style_content.split('\n'):
            line = line.strip()
            
            # Sélecteur
            if line.endswith('{'):
                if current_selector:
                    styles[current_selector] = current_rules
                current_selector = line[:-1].strip()
                current_rules = {}
            
            # Règle
            elif ':' in line and not line.endswith('}'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().rstrip(';')
                current_rules[key] = self._parse_value(value)
            
            # Fin du bloc
            elif line == '}':
                if current_selector:
                    styles[current_selector] = current_rules
                current_selector = None
                current_rules = {}
        
        return styles
    
    def _parse_value(self, value: str) -> Any:
        """Parse une valeur CSS en valeur Python"""
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