from typing import Dict, Any, List, Optional
import threading
import time
from .virtual_dom import VNode, VTree
from .layout_manager import LayoutManager
from .style_engine import StyleEngine

class RenderEngine:
    """Moteur de rendu principal pour Mibale"""
    
    def __init__(self):
        self.vtree = VTree()
        self.layout_manager = LayoutManager()
        self.style_engine = StyleEngine()
        self.native_renderer = None
        self.is_initialized = False
        self.render_queue = []
        self.render_lock = threading.Lock()
        self.platform = None
        
        # Détection de la plateforme
        self._detect_platform()
    
    def _detect_platform(self):
        """Détecte la plateforme cible"""
        try:
            from ..android.renderer.android_renderer import AndroidRenderer
            self.native_renderer = AndroidRenderer()
            self.platform = "android"
            print(f"🎯 Plateforme détectée: Android")
        except ImportError:
            try:
                from ..ios.renderer.ios_renderer import IOSRenderer
                self.native_renderer = IOSRenderer()
                self.platform = "ios"
                print(f"🎯 Plateforme détectée: iOS")
            except ImportError:
                from .native_renderer import DesktopRenderer
                self.native_renderer = DesktopRenderer()
                self.platform = "desktop"
                print(f"🎯 Plateforme détectée: Desktop (mode développement)")
    
    def initialize(self) -> bool:
        """Initialise le moteur de rendu"""
        if self.native_renderer:
            self.is_initialized = self.native_renderer.initialize()
            if self.is_initialized:
                print("✅ Moteur de rendu initialisé")
            return self.is_initialized
        return False
    
    def render_component(self, component_data: Dict[str, Any]) -> bool:
        """Rend un composant compilé"""
        if not self.is_initialized:
            if not self.initialize():
                return False
        
        try:
            # Extraction des données du composant
            template = component_data.get('template', '')
            template_ast = component_data.get('template_ast')
            style = component_data.get('style', {})
            component_class = component_data.get('component')
            
            # Crée le VNode racine à partir du template
            root_vnode = self._create_vnode_from_template(template, template_ast, component_class)
            
            if not root_vnode:
                print("❌ Impossible de créer le VNode racine")
                return False
            
            # Applique les styles
            self.style_engine.apply_styles(root_vnode, style)
            
            # Calcule le layout
            self.layout_manager.calculate_layout(root_vnode)
            
            # Met à jour l'arbre virtuel
            self.vtree.update(root_vnode)
            
            # Rend sur la plateforme native
            success = self.native_renderer.render(root_vnode)
            
            if success:
                print("✅ Composant rendu avec succès")
            else:
                print("❌ Erreur lors du rendu natif")
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur rendu composant: {e}")
            return False
    
    def _create_vnode_from_template(self, template: str, template_ast: Dict, component_class: Any) -> Optional[VNode]:
        """Crée un VNode à partir d'un template"""
        if template_ast:
            return self._create_vnode_from_ast(template_ast, component_class)
        else:
            # Fallback: parsing basique du template
            return self._parse_template_basic(template, component_class)
    
    def _create_vnode_from_ast(self, ast_node: Dict, component_class: Any) -> VNode:
        """Crée un VNode à partir d'un AST"""
        node_type = ast_node.get('type')
        
        if node_type == 'element':
            vnode = VNode(
                tag=ast_node['tag'],
                props=ast_node.get('attrs', {}),
                children=[],
                directives=ast_node.get('directives', [])
            )
            
            # Traite les enfants
            for child_ast in ast_node.get('children', []):
                child_vnode = self._create_vnode_from_ast(child_ast, component_class)
                if child_vnode:
                    vnode.children.append(child_vnode)
            
            return vnode
        
        elif node_type == 'text':
            return VNode(
                tag='Text',
                props={'text': ast_node['content']},
                children=[],
                directives=[]
            )
        
        return None
    
    def _parse_template_basic(self, template: str, component_class: Any) -> VNode:
        """Parse basique du template (fallback)"""
        lines = [line.strip() for line in template.split('\n') if line.strip()]
        
        if not lines:
            return VNode('View', {}, [])
        
        # Prend la première balise comme racine
        first_line = lines[0]
        if first_line.startswith('<') and first_line.endswith('>'):
            tag_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)(.*?)>', first_line)
            if tag_match:
                tag_name = tag_match.group(1)
                attrs_str = tag_match.group(2)
                
                # Parse les attributs basiques
                attrs = self._parse_attrs_basic(attrs_str)
                
                return VNode(tag_name, attrs, [])
        
        # Fallback: View simple
        return VNode('View', {}, [])
    
    def _parse_attrs_basic(self, attrs_str: str) -> Dict[str, Any]:
        """Parse basique des attributs"""
        attrs = {}
        attr_pattern = re.compile(r'([a-zA-Z-]+)="([^"]*)"')
        
        for match in attr_pattern.finditer(attrs_str):
            key = match.group(1)
            value = match.group(2)
            attrs[key] = value
        
        return attrs
    
    def update_component(self, component_id: str, new_state: Dict[str, Any]):
        """Met à jour un composant existant"""
        with self.render_lock:
            self.render_queue.append(('update', component_id, new_state))
            self._process_render_queue()
    
    def _process_render_queue(self):
        """Traite la file de rendu"""
        if not self.render_queue:
            return
        
        def process():
            while self.render_queue:
                with self.render_lock:
                    if not self.render_queue:
                        return
                    task = self.render_queue.pop(0)
                
                task_type, component_id, data = task
                
                if task_type == 'update':
                    self._handle_component_update(component_id, data)
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def _handle_component_update(self, component_id: str, new_state: Dict[str, Any]):
        """Gère la mise à jour d'un composant"""
        # Implémentation du diffing et mise à jour incrémentale
        old_vnode = self.vtree.get_component(component_id)
        if old_vnode:
            # Crée un nouveau VNode avec l'état mis à jour
            new_vnode = self._create_updated_vnode(old_vnode, new_state)
            
            # Calcule les différences
            changes = self.vtree.diff(old_vnode, new_vnode)
            
            # Applique les changements
            if changes:
                self._apply_changes(changes)
    
    def _create_updated_vnode(self, old_vnode: VNode, new_state: Dict[str, Any]) -> VNode:
        """Crée un VNode mis à jour"""
        # Clone le VNode avec le nouvel état
        new_vnode = VNode(
            tag=old_vnode.tag,
            props=old_vnode.props.copy(),
            children=old_vnode.children[:],
            directives=old_vnode.directives[:]
        )
        
        # Met à jour les bindings avec le nouvel état
        self._update_bindings(new_vnode, new_state)
        
        return new_vnode
    
    def _update_bindings(self, vnode: VNode, state: Dict[str, Any]):
        """Met à jour les bindings dans le VNode"""
        for key, value in vnode.props.items():
            if isinstance(value, dict) and value.get('type') == 'binding':
                # Évalue l'expression de binding
                expr = value['value']
                try:
                    # Évaluation basique (dans un vrai projet, utiliser un parser d'expressions)
                    if expr in state:
                        vnode.props[key] = state[expr]
                except:
                    pass
        
        # Traite récursivement les enfants
        for child in vnode.children:
            if isinstance(child, VNode):
                self._update_bindings(child, state)
    
    def _apply_changes(self, changes: List[Dict[str, Any]]):
        """Applique les changements au rendu natif"""
        for change in changes:
            self.native_renderer.apply_change(change)