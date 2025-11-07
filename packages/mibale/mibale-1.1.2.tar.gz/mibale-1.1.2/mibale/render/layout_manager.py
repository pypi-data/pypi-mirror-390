from typing import Dict, Any
from .virtual_dom import VNode

class LayoutManager:
    """Gestionnaire de layout pour le calcul des positions et dimensions"""
    
    def __init__(self):
        self.screen_width = 1080  # Valeurs par défaut
        self.screen_height = 1920
    
    def calculate_layout(self, root: VNode):
        """Calcule le layout pour l'arbre entier"""
        self._calculate_node_layout(root, 0, 0, self.screen_width, self.screen_height)
    
    def _calculate_node_layout(self, node: VNode, x: float, y: float, width: float, height: float):
        """Calcule récursivement le layout d'un nœud"""
        style = node.style or {}
        
        # Applique le modèle de box
        margin = style.get('margin', 0)
        padding = style.get('padding', 0)
        border = style.get('border_width', 0)
        
        # Dimensions calculées
        content_width = width - (margin * 2 + padding * 2 + border * 2)
        content_height = height - (margin * 2 + padding * 2 + border * 2)
        
        # Position calculée
        node.layout = {
            'x': x + margin,
            'y': y + margin,
            'width': max(0, content_width),
            'height': max(0, content_height),
            'margin': margin,
            'padding': padding,
            'border': border,
            'absolute_x': x,
            'absolute_y': y
        }
        
        # Layout des enfants selon le type de container
        if node.tag.lower() in ['linearlayout', 'vstack']:
            self._layout_linear_children(node, x, y, width, height, 'vertical')
        elif node.tag.lower() in ['hstack']:
            self._layout_linear_children(node, x, y, width, height, 'horizontal')
        elif node.tag.lower() in ['framelayout', 'zstack']:
            self._layout_frame_children(node, x, y, width, height)
        else:
            self._layout_simple_children(node, x, y, width, height)
    
    def _layout_linear_children(self, node: VNode, x: float, y: float, width: float, height: float, orientation: str):
        """Layout pour les containers linéaires"""
        children = [c for c in node.children if isinstance(c, VNode)]
        if not children:
            return
        
        child_x, child_y = x, y
        
        for i, child in enumerate(children):
            if isinstance(child, VNode):
                if orientation == 'vertical':
                    child_height = height / len(children)
                    self._calculate_node_layout(child, child_x, child_y, width, child_height)
                    child_y += child_height
                else:  # horizontal
                    child_width = width / len(children)
                    self._calculate_node_layout(child, child_x, child_y, child_width, height)
                    child_x += child_width
    
    def _layout_frame_children(self, node: VNode, x: float, y: float, width: float, height: float):
        """Layout pour les containers empilés"""
        for child in node.children:
            if isinstance(child, VNode):
                # Tous les enfants prennent tout l'espace
                self._calculate_node_layout(child, x, y, width, height)
    
    def _layout_simple_children(self, node: VNode, x: float, y: float, width: float, height: float):
        """Layout simple pour les vues feuilles"""
        # Les vues feuilles n'ont généralement pas d'enfants à layout
        pass
    
    def set_screen_size(self, width: float, height: float):
        """Définit la taille de l'écran"""
        self.screen_width = width
        self.screen_height = height