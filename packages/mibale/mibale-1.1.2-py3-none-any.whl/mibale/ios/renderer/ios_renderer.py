from typing import Dict, Any, List, Optional
from ...render.virtual_dom import VNode

class IOSRenderer:
    """Renderer natif pour iOS via PyObjC/UIKit"""
    
    def __init__(self):
        self.bridge = None
        self.root_view = None
        self.registered_views = {}
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialise le renderer iOS"""
        try:
            from ..bridge import IOSBridge
            self.bridge = IOSBridge.get_instance()
            
            if not self.bridge.initialized:
                if not self.bridge.initialize():
                    return False
            
            self.initialized = True
            print("✅ Renderer iOS initialisé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation renderer iOS: {e}")
            return False
    
    def render(self, root_vnode: VNode) -> bool:
        """Rend un VNode en vues iOS natives"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        try:
            # Crée la vue racine
            self.root_view = self._create_native_view(root_vnode)
            
            if not self.root_view:
                print("❌ Impossible de créer la vue racine iOS")
                return False
            
            # Ajoute à la hiérarchie de vues
            root_vc = self.bridge.root_view_controller
            if root_vc:
                root_vc.view().addSubview_(self.root_view)
                
                # Configure Auto Layout pour la vue racine
                self._setup_root_view_constraints(self.root_view, root_vc.view())
            
            print("✅ Vue iOS rendue avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur rendu iOS: {e}")
            return False
    
    def _create_native_view(self, vnode: VNode) -> Any:
        """Crée récursivement une vue iOS à partir d'un VNode"""
        from .view_factory import IOSViewFactory
        
        factory = IOSViewFactory(self.bridge)
        
        # Crée la vue native
        native_view = factory.create_view(vnode)
        
        if not native_view:
            return None
        
        # Applique les styles
        self._apply_ios_styles(native_view, vnode)
        
        # Applique les propriétés
        self._apply_ios_props(native_view, vnode)
        
        # Crée les enfants récursivement
        if vnode.children:
            for child in vnode.children:
                if isinstance(child, VNode):
                    child_view = self._create_native_view(child)
                    if child_view:
                        self._add_child_to_parent(native_view, child_view, vnode.tag)
        
        # Enregistre la vue
        if vnode.key:
            self.registered_views[vnode.key] = native_view
        
        return native_view
    
    def _add_child_to_parent(self, parent_view, child_view, parent_tag: str):
        """Ajoute une vue enfant à son parent iOS"""
        try:
            # Pour iOS, on ajoute simplement la vue enfant
            parent_view.addSubview_(child_view)
            
            # Configure Auto Layout basique
            self._setup_child_constraints(child_view, parent_view, parent_tag)
            
        except Exception as e:
            print(f"❌ Erreur ajout enfant iOS: {e}")
    
    def _setup_root_view_constraints(self, root_view, parent_view):
        """Configure les contraintes pour la vue racine"""
        try:
            from UIKit import NSLayoutConstraint
            
            root_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
            
            constraints = [
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    root_view, 7, 0, parent_view, 7, 1.0, 0  # leading, leading
                ),
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    root_view, 8, 0, parent_view, 8, 1.0, 0  # trailing, trailing
                ),
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    root_view, 3, 0, parent_view, 3, 1.0, 0  # top, top
                ),
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    root_view, 4, 0, parent_view, 4, 1.0, 0  # bottom, bottom
                )
            ]
            
            NSLayoutConstraint.activateConstraints_(constraints)
            
        except Exception as e:
            print(f"❌ Erreur contraintes racine iOS: {e}")
    
    def _setup_child_constraints(self, child_view, parent_view, parent_tag: str):
        """Configure les contraintes pour une vue enfant"""
        try:
            from UIKit import NSLayoutConstraint
            
            child_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
            
            # Contraintes basiques - remplir le parent
            constraints = [
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    child_view, 7, 0, parent_view, 7, 1.0, 0  # leading
                ),
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    child_view, 8, 0, parent_view, 8, 1.0, 0  # trailing
                ),
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    child_view, 3, 0, parent_view, 3, 1.0, 0  # top
                ),
                NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                    child_view, 4, 0, parent_view, 4, 1.0, 0  # bottom
                )
            ]
            
            NSLayoutConstraint.activateConstraints_(constraints)
            
        except Exception as e:
            print(f"❌ Erreur contraintes enfant iOS: {e}")
    
    def _apply_ios_styles(self, native_view, vnode: VNode):
        """Applique les styles iOS à une vue native"""
        try:
            style = vnode.style or {}
            layout = vnode.layout or {}
            
            # Couleur de fond
            if 'background_color' in style:
                color_value = self._parse_ios_color(style['background_color'])
                if color_value:
                    native_view.setBackgroundColor_(color_value)
            
            # Coin arrondi
            if 'border_radius' in style:
                radius = float(style['border_radius'])
                native_view.layer().setCornerRadius_(radius)
                native_view.layer().setMasksToBounds_(True)
            
            # Opacité
            if 'opacity' in style:
                opacity = float(style['opacity'])
                native_view.setAlpha_(opacity)
                
        except Exception as e:
            print(f"❌ Erreur application styles iOS: {e}")
    
    def _apply_ios_props(self, native_view, vnode: VNode):
        """Applique les propriétés aux vues iOS"""
        try:
            props = vnode.props or {}
            
            # UILabel
            if vnode.tag.lower() in ['textview', 'text', 'label']:
                if 'text' in props:
                    native_view.setText_(str(props['text']))
                
                if 'text_color' in props:
                    color_value = self._parse_ios_color(props['text_color'])
                    if color_value:
                        native_view.setTextColor_(color_value)
                
                if 'font_size' in props:
                    from UIKit import UIFont
                    font_size = float(props['font_size'])
                    font = UIFont.systemFontOfSize_(font_size)
                    native_view.setFont_(font)
            
            # UIButton
            elif vnode.tag.lower() in ['button', 'btn']:
                if 'text' in props:
                    native_view.setTitle_forState_(str(props['text']), 0)  # Normal state
                
                if 'on_click' in props:
                    # Le gestionnaire est déjà configuré dans la factory
                    pass
            
            # UIImageView
            elif vnode.tag.lower() in ['imageview', 'image', 'img']:
                if 'src' in props:
                    self._set_ios_image(native_view, props['src'])
                    
        except Exception as e:
            print(f"❌ Erreur application props iOS: {e}")
    
    def _set_ios_image(self, image_view, image_src: str):
        """Charge une image dans une UIImageView"""
        try:
            # Pour les images locales
            if not image_src.startswith('http'):
                from UIKit import UIImage
                image = UIImage.imageNamed_(image_src)
                if image:
                    image_view.setImage_(image)
            else:
                # Pour les URLs - nécessiterait un loader d'image
                print(f"📥 Chargement image URL iOS: {image_src}")
                
        except Exception as e:
            print(f"❌ Erreur chargement image iOS: {e}")
    
    def _parse_ios_color(self, color_value: Any) -> Any:
        """Parse une couleur en UIColor"""
        try:
            if isinstance(color_value, str):
                if color_value.startswith('#'):
                    # Conversion hex vers UIColor
                    return self.bridge.get_color('system_blue')  # Simplifié
                elif color_value in ['red', 'blue', 'green', 'black', 'white']:
                    return self.bridge.get_color(color_value)
            
            return self.bridge.get_color('black')  # Couleur par défaut
            
        except Exception as e:
            print(f"❌ Erreur parsing couleur iOS: {e}")
            return self.bridge.get_color('black')
    
    def apply_change(self, change: Dict[str, Any]):
        """Applique un changement incrémental au rendu iOS"""
        change_type = change.get('type')
        
        if change_type == 'UPDATE_PROPS':
            self._update_view_props(change)
        elif change_type == 'UPDATE_STYLES':
            self._update_view_styles(change)
    
    def _update_view_props(self, change: Dict[str, Any]):
        """Met à jour les propriétés d'une vue iOS"""
        node = change.get('node')
        if node and node.key in self.registered_views:
            view = self.registered_views[node.key]
            self._apply_ios_props(view, node)
    
    def _update_view_styles(self, change: Dict[str, Any]):
        """Met à jour les styles d'une vue iOS"""
        node = change.get('node')
        if node and node.key in self.registered_views:
            view = self.registered_views[node.key]
            self._apply_ios_styles(view, node)