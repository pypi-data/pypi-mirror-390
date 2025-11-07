from typing import Dict, Any
from .virtual_dom import VNode

class DesktopRenderer:
    """Renderer de secours pour le développement desktop"""
    
    def __init__(self):
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialise le renderer desktop"""
        print("🖥️ Renderer Desktop initialisé (mode développement)")
        self.initialized = True
        return True
    
    def render(self, root_vnode: VNode) -> bool:
        """Rend un VNode en mode desktop"""
        if not self.initialized:
            self.initialize()
        
        print("🎨 Rendu Desktop:")
        self._print_vnode_tree(root_vnode)
        return True
    
    def _print_vnode_tree(self, node: VNode, depth=0):
        """Affiche l'arbre VNode pour le débogage"""
        indent = "  " * depth
        print(f"{indent}└── {node.tag} (key: {node.key})")
        
        if node.props:
            for key, value in node.props.items():
                print(f"{indent}    ├── {key}: {value}")
        
        if node.style:
            print(f"{indent}    ├── Style: {node.style}")
        
        if node.layout:
            print(f"{indent}    ├── Layout: {node.layout}")
        
        for child in node.children:
            if isinstance(child, VNode):
                self._print_vnode_tree(child, depth + 1)
    
    def apply_change(self, change: Dict[str, Any]):
        """Applique un changement au rendu desktop"""
        print(f"🔄 Application changement: {change.get('type')}")