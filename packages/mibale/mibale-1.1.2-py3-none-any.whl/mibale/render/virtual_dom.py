from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import uuid

@dataclass
class VNode:
    """Nœud du DOM Virtuel"""
    tag: str
    props: Dict[str, Any]
    children: List[Any]
    directives: List[Dict[str, Any]] = field(default_factory=list)
    key: str = None
    component_id: str = None
    native_view: Any = None
    style: Dict[str, Any] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.key:
            self.key = str(uuid.uuid4())[:8]
    
    def add_child(self, child: 'VNode'):
        self.children.append(child)
    
    def set_prop(self, key: str, value: Any):
        self.props[key] = value
    
    def get_prop(self, key: str, default: Any = None) -> Any:
        return self.props.get(key, default)
    
    def add_directive(self, directive: Dict[str, Any]):
        self.directives.append(directive)
    
    def find_by_tag(self, tag: str) -> List['VNode']:
        """Trouve tous les nœuds avec le tag spécifié"""
        results = []
        if self.tag == tag:
            results.append(self)
        
        for child in self.children:
            if isinstance(child, VNode):
                results.extend(child.find_by_tag(tag))
        
        return results
    
    def find_by_id(self, element_id: str) -> Optional['VNode']:
        """Trouve un nœud par son ID"""
        if self.get_prop('id') == element_id:
            return self
        
        for child in self.children:
            if isinstance(child, VNode):
                result = child.find_by_id(element_id)
                if result:
                    return result
        
        return None

class VTree:
    """Arbre du DOM Virtuel"""
    
    def __init__(self):
        self.root: Optional[VNode] = None
        self.nodes: Dict[str, VNode] = {}
        self.components: Dict[str, VNode] = {}
    
    def update(self, new_root: VNode):
        """Met à jour l'arbre avec une nouvelle racine"""
        if self.root:
            changes = self.diff(self.root, new_root)
            self._apply_changes(changes)
        else:
            self.root = new_root
            self._index_node(new_root)
    
    def diff(self, old_node: VNode, new_node: VNode) -> List[Dict[str, Any]]:
        """Calcule les différences entre deux arbres"""
        changes = []
        self._diff_nodes(old_node, new_node, changes, 'root')
        return changes
    
    def _diff_nodes(self, old_node: VNode, new_node: VNode, changes: List, path: str):
        """Compare récursivement deux nœuds"""
        if old_node.tag != new_node.tag:
            changes.append({
                'type': 'REPLACE_NODE',
                'path': path,
                'old_node': old_node,
                'new_node': new_node
            })
            return
        
        # Diff des propriétés
        prop_changes = self._diff_props(old_node, new_node)
        if prop_changes:
            changes.append({
                'type': 'UPDATE_PROPS',
                'path': path,
                'node': old_node,
                'changes': prop_changes
            })
        
        # Diff des styles
        style_changes = self._diff_styles(old_node, new_node)
        if style_changes:
            changes.append({
                'type': 'UPDATE_STYLES',
                'path': path,
                'node': old_node,
                'changes': style_changes
            })
        
        # Diff des enfants
        self._diff_children(old_node, new_node, changes, path)
    
    def _diff_props(self, old_node: VNode, new_node: VNode) -> Dict[str, Any]:
        """Diff des propriétés"""
        changes = {}
        
        # Propriétés modifiées ou ajoutées
        for key, new_value in new_node.props.items():
            old_value = old_node.get_prop(key)
            if old_value != new_value:
                changes[key] = {'old': old_value, 'new': new_value}
        
        # Propriétés supprimées
        for key in old_node.props:
            if key not in new_node.props:
                changes[key] = {'old': old_node.get_prop(key), 'new': None}
        
        return changes
    
    def _diff_styles(self, old_node: VNode, new_node: VNode) -> Dict[str, Any]:
        """Diff des styles"""
        changes = {}
        old_style = old_node.style or {}
        new_style = new_node.style or {}
        
        # Styles modifiés ou ajoutés
        for key, new_value in new_style.items():
            old_value = old_style.get(key)
            if old_value != new_value:
                changes[key] = {'old': old_value, 'new': new_value}
        
        # Styles supprimés
        for key in old_style:
            if key not in new_style:
                changes[key] = {'old': old_style.get(key), 'new': None}
        
        return changes
    
    def _diff_children(self, old_node: VNode, new_node: VNode, changes: List, path: str):
        """Diff des enfants"""
        old_children = [c for c in old_node.children if isinstance(c, VNode)]
        new_children = [c for c in new_node.children if isinstance(c, VNode)]
        
        # Algorithme de diffing basique par index
        max_children = max(len(old_children), len(new_children))
        
        for i in range(max_children):
            child_path = f"{path}.children[{i}]"
            
            if i < len(old_children) and i < len(new_children):
                # Les deux existent - diff récursif
                self._diff_nodes(old_children[i], new_children[i], changes, child_path)
            elif i < len(old_children):
                # Enfant supprimé
                changes.append({
                    'type': 'REMOVE_CHILD',
                    'path': path,
                    'index': i,
                    'node': old_children[i]
                })
            else:
                # Nouvel enfant
                changes.append({
                    'type': 'ADD_CHILD',
                    'path': path,
                    'index': i,
                    'node': new_children[i]
                })
    
    def _apply_changes(self, changes: List[Dict[str, Any]]):
        """Applique les changements (sera implémenté par le renderer natif)"""
        # Cette méthode sera appelée par le renderer natif
        pass
    
    def _index_node(self, node: VNode):
        """Indexe un nœud et ses enfants"""
        self.nodes[node.key] = node
        if node.component_id:
            self.components[node.component_id] = node
        
        for child in node.children:
            if isinstance(child, VNode):
                self._index_node(child)
    
    def get_component(self, component_id: str) -> Optional[VNode]:
        """Récupère un composant par son ID"""
        return self.components.get(component_id)
    
    def get_node(self, key: str) -> Optional[VNode]:
        """Récupère un nœud par sa clé"""
        return self.nodes.get(key)
    
    def traverse(self, callback):
        """Parcourt l'arbre et applique un callback à chaque nœud"""
        def _traverse_node(node, depth=0):
            callback(node, depth)
            for child in node.children:
                if isinstance(child, VNode):
                    _traverse_node(child, depth + 1)
        
        if self.root:
            _traverse_node(self.root)