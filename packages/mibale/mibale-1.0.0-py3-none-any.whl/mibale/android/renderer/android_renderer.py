import jnius
from typing import Dict, Any, List, Optional
from ...render.virtual_dom import VNode

class AndroidRenderer:
    """Renderer natif pour Android"""
    
    def __init__(self):
        self.context = None
        self.activity = None
        self.view_factory = None
        self.registered_views = {}
        
    def initialize(self) -> bool:
        """Initialise le renderer Android"""
        try:
            from jnius import autoclass, cast
            
            # Récupère le contexte Android via Kivy/Pyjnius
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.activity = PythonActivity.mActivity
            self.context = self.activity.getApplicationContext()
            
            # Initialise la factory de vues
            from .view_factory import AndroidViewFactory
            self.view_factory = AndroidViewFactory(self.context)
            
            print("✅ Renderer Android initialisé")
            return True
            
        except Exception as e:
            print(f"❌ Initialisation Android échouée: {e}")
            return False
    
    def render(self, root_vnode: VNode) -> bool:
        """Rend un VNode en vues Android natives"""
        if not self.context or not self.view_factory:
            return False
        
        try:
            # Crée la vue racine
            root_view = self._create_native_view(root_vnode)
            
            if root_view:
                # Définit comme content view
                self.activity.setContentView(root_view)
                
                # Enregistre la vue racine
                self.registered_views['root'] = root_view
                
                print("✅ Vue Android rendue avec succès")
                return True
                
        except Exception as e:
            print(f"❌ Rendu Android échoué: {e}")
        
        return False
    
    def _create_native_view(self, vnode: VNode) -> Any:
        """Crée récursivement une vue Android à partir d'un VNode"""
        if not self.view_factory:
            return None
        
        # Crée la vue native
        native_view = self.view_factory.create_view(vnode)
        
        if not native_view:
            return None
        
        # Applique les styles
        self._apply_android_styles(native_view, vnode)
        
        # Applique les propriétés
        self._apply_android_props(native_view, vnode)
        
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
        """Ajoute une vue enfant à son parent selon le type de layout"""
        from jnius import autoclass
        
        try:
            if parent_tag.lower() in ['linearlayout', 'vstack']:
                # Pour LinearLayout vertical
                LayoutParams = autoclass('android.widget.LinearLayout$LayoutParams')
                params = LayoutParams(
                    LayoutParams.MATCH_PARENT,
                    LayoutParams.WRAP_CONTENT
                )
                parent_view.addView(child_view, params)
            
            elif parent_tag.lower() in ['hstack']:
                # Pour LinearLayout horizontal
                LayoutParams = autoclass('android.widget.LinearLayout$LayoutParams')
                params = LayoutParams(
                    LayoutParams.WRAP_CONTENT,
                    LayoutParams.MATCH_PARENT
                )
                parent_view.addView(child_view, params)
            
            elif parent_tag.lower() in ['framelayout', 'zstack']:
                # Pour FrameLayout
                LayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')
                params = LayoutParams(
                    LayoutParams.MATCH_PARENT,
                    LayoutParams.MATCH_PARENT
                )
                parent_view.addView(child_view, params)
            
            else:
                # Layout par défaut
                parent_view.addView(child_view)
                
        except Exception as e:
            print(f"❌ Erreur ajout enfant Android: {e}")
    
    def _apply_android_styles(self, native_view, vnode: VNode):
        """Applique les styles Android à une vue native"""
        from jnius import autoclass
        
        try:
            style = vnode.style or {}
            layout = vnode.layout or {}
            
            # Applique les dimensions
            if 'width' in layout:
                width = int(layout['width'])
                native_view.getLayoutParams().width = width
            
            if 'height' in layout:
                height = int(layout['height'])
                native_view.getLayoutParams().height = height
            
            # Applique les marges
            if 'margin' in layout:
                margin = int(layout['margin'])
                params = native_view.getLayoutParams()
                if hasattr(params, 'setMargins'):
                    params.setMargins(margin, margin, margin, margin)
            
            # Applique la couleur de fond
            if 'background_color' in style:
                Color = autoclass('android.graphics.Color')
                try:
                    color_value = self._parse_android_color(style['background_color'])
                    native_view.setBackgroundColor(color_value)
                except:
                    pass
            
            # Applique le padding
            if 'padding' in style:
                padding = int(style['padding'])
                native_view.setPadding(padding, padding, padding, padding)
                
        except Exception as e:
            print(f"❌ Erreur application styles Android: {e}")
    
    def _apply_android_props(self, native_view, vnode: VNode):
        """Applique les propriétés aux vues Android"""
        try:
            props = vnode.props or {}
            
            # TextView
            if vnode.tag.lower() == 'textview':
                if 'text' in props:
                    native_view.setText(str(props['text']))
                
                if 'text_size' in props:
                    native_view.setTextSize(float(props['text_size']))
                
                if 'text_color' in props:
                    Color = autoclass('android.graphics.Color')
                    color_value = self._parse_android_color(props['text_color'])
                    native_view.setTextColor(color_value)
            
            # Button
            elif vnode.tag.lower() == 'button':
                if 'text' in props:
                    native_view.setText(str(props['text']))
                
                if 'on_click' in props:
                    self._set_android_click_listener(native_view, props['on_click'])
            
            # ImageView
            elif vnode.tag.lower() == 'imageview':
                if 'src' in props:
                    self._set_android_image(native_view, props['src'])
                    
        except Exception as e:
            print(f"❌ Erreur application props Android: {e}")
    
    def _set_android_click_listener(self, native_view, click_handler):
        """Définit un click listener Android"""
        from jnius import PythonJavaClass, java_method, autoclass
        
        class ClickListener(PythonJavaClass):
            __javainterfaces__ = ['android/view/View$OnClickListener']
            
            def __init__(self, handler):
                self.handler = handler
            
            @java_method('(Landroid/view/View;)V')
            def onClick(self, view):
                try:
                    self.handler()
                except Exception as e:
                    print(f"❌ Erreur handler click: {e}")
        
        listener = ClickListener(click_handler)
        native_view.setOnClickListener(listener)
    
    def _set_android_image(self, image_view, image_src: str):
        """Charge une image dans une ImageView"""
        from jnius import autoclass
        
        try:
            # Pour les images locales
            if image_src.startswith('@drawable/'):
                Resources = autoclass('android.content.res.Resources')
                Drawable = autoclass('android.graphics.drawable.Drawable')
                
                resource_name = image_src.replace('@drawable/', '')
                resources = self.context.getResources()
                resource_id = resources.getIdentifier(resource_name, 'drawable', self.context.getPackageName())
                
                if resource_id != 0:
                    drawable = resources.getDrawable(resource_id)
                    image_view.setImageDrawable(drawable)
            
            # Pour les URLs (nécessiterait une lib de chargement d'image)
            elif image_src.startswith('http'):
                print(f"📥 Chargement image URL: {image_src}")
                # Implémentation avec Glide/Picasso serait nécessaire
                
        except Exception as e:
            print(f"❌ Erreur chargement image Android: {e}")
    
    def _parse_android_color(self, color_value: Any) -> int:
        """Parse une couleur en valeur Android"""
        from jnius import autoclass
        Color = autoclass('android.graphics.Color')
        
        try:
            if isinstance(color_value, str):
                if color_value.startswith('#'):
                    return Color.parseColor(color_value)
                elif color_value in ['red', 'blue', 'green', 'black', 'white']:
                    color_map = {
                        'red': Color.RED,
                        'blue': Color.BLUE,
                        'green': Color.GREEN,
                        'black': Color.BLACK,
                        'white': Color.WHITE
                    }
                    return color_map.get(color_value, Color.BLACK)
            
            return Color.BLACK  # Couleur par défaut
            
        except:
            return Color.BLACK
    
    def apply_change(self, change: Dict[str, Any]):
        """Applique un changement incrémental au rendu"""
        change_type = change.get('type')
        
        if change_type == 'UPDATE_PROPS':
            self._update_view_props(change)
        elif change_type == 'UPDATE_STYLES':
            self._update_view_styles(change)
        elif change_type == 'REPLACE_NODE':
            self._replace_view(change)
    
    def _update_view_props(self, change: Dict[str, Any]):
        """Met à jour les propriétés d'une vue"""
        node = change.get('node')
        if node and node.key in self.registered_views:
            view = self.registered_views[node.key]
            self._apply_android_props(view, node)
    
    def _update_view_styles(self, change: Dict[str, Any]):
        """Met à jour les styles d'une vue"""
        node = change.get('node')
        if node and node.key in self.registered_views:
            view = self.registered_views[node.key]
            self._apply_android_styles(view, node)
    
    def _replace_view(self, change: Dict[str, Any]):
        """Remplace une vue"""
        # Implémentation complexe nécessitant la gestion du parent
        print("🔄 Remplacement de vue (non implémenté)")