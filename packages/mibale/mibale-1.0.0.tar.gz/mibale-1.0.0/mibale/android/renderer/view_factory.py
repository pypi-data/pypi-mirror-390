import jnius
from typing import Any, Dict
from ...render.virtual_dom import VNode

class AndroidViewFactory:
    """Factory pour créer des vues Android natives"""
    
    def __init__(self, context):
        self.context = context
    
    def create_view(self, vnode: VNode) -> Any:
        """Crée une vue Android native basée sur le VNode"""
        tag = vnode.tag.lower()
        
        try:
            from jnius import autoclass, cast
            
            if tag in ['view', 'div', 'container']:
                return self._create_view(vnode)
            elif tag in ['linearlayout', 'vstack']:
                return self._create_linear_layout(vnode, vertical=True)
            elif tag in ['hstack']:
                return self._create_linear_layout(vnode, vertical=False)
            elif tag in ['framelayout', 'zstack']:
                return self._create_frame_layout(vnode)
            elif tag in ['textview', 'text', 'label']:
                return self._create_text_view(vnode)
            elif tag in ['button', 'btn']:
                return self._create_button(vnode)
            elif tag in ['imageview', 'image', 'img']:
                return self._create_image_view(vnode)
            elif tag in ['edittext', 'input', 'textfield']:
                return self._create_edit_text(vnode)
            elif tag in ['scrollview', 'scroll']:
                return self._create_scroll_view(vnode)
            elif tag in ['recyclerview', 'list']:
                return self._create_recycler_view(vnode)
            elif tag in ['webview']:
                return self._create_web_view(vnode)
            elif tag in ['mapview']:
                return self._create_map_view(vnode)
            elif tag in ['surfaceview']:
                return self._create_surface_view(vnode)
            else:
                # Vue générique
                return self._create_view(vnode)
                
        except Exception as e:
            print(f"❌ Erreur création vue Android {tag}: {e}")
            return None
    
    def _create_view(self, vnode: VNode) -> Any:
        """Crée une View générique"""
        from jnius import autoclass
        View = autoclass('android.view.View')
        return View(self.context)
    
    def _create_linear_layout(self, vnode: VNode, vertical: bool = True) -> Any:
        """Crée un LinearLayout"""
        from jnius import autoclass
        LinearLayout = autoclass('android.widget.LinearLayout')
        
        layout = LinearLayout(self.context)
        
        if vertical:
            layout.setOrientation(LinearLayout.VERTICAL)
        else:
            layout.setOrientation(LinearLayout.HORIZONTAL)
        
        return layout
    
    def _create_frame_layout(self, vnode: VNode) -> Any:
        """Crée un FrameLayout"""
        from jnius import autoclass
        FrameLayout = autoclass('android.widget.FrameLayout')
        return FrameLayout(self.context)
    
    def _create_text_view(self, vnode: VNode) -> Any:
        """Crée un TextView"""
        from jnius import autoclass
        TextView = autoclass('android.widget.TextView')
        
        text_view = TextView(self.context)
        text_view.setText(vnode.get_prop('text', ''))
        
        # Style par défaut
        text_view.setTextSize(16.0)
        
        return text_view
    
    def _create_button(self, vnode: VNode) -> Any:
        """Crée un Button"""
        from jnius import autoclass
        Button = autoclass('android.widget.Button')
        
        button = Button(self.context)
        button.setText(vnode.get_prop('text', 'Button'))
        
        # Style par défaut
        button.setTextSize(16.0)
        
        return button
    
    def _create_image_view(self, vnode: VNode) -> Any:
        """Crée une ImageView"""
        from jnius import autoclass
        ImageView = autoclass('android.widget.ImageView')
        return ImageView(self.context)
    
    def _create_edit_text(self, vnode: VNode) -> Any:
        """Crée un EditText"""
        from jnius import autoclass
        EditText = autoclass('android.widget.EditText')
        
        edit_text = EditText(self.context)
        edit_text.setHint(vnode.get_prop('placeholder', ''))
        
        return edit_text
    
    def _create_scroll_view(self, vnode: VNode) -> Any:
        """Crée un ScrollView"""
        from jnius import autoclass
        ScrollView = autoclass('android.widget.ScrollView')
        return ScrollView(self.context)
    
    def _create_recycler_view(self, vnode: VNode) -> Any:
        """Crée un RecyclerView"""
        from jnius import autoclass
        RecyclerView = autoclass('androidx.recyclerview.widget.RecyclerView')
        return RecyclerView(self.context)
    
    def _create_web_view(self, vnode: VNode) -> Any:
        """Crée un WebView"""
        from jnius import autoclass
        WebView = autoclass('android.webkit.WebView')
        
        web_view = WebView(self.context)
        web_view.getSettings().setJavaScriptEnabled(True)
        
        return web_view
    
    def _create_map_view(self, vnode: VNode) -> Any:
        """Crée une MapView"""
        from jnius import autoclass
        try:
            MapView = autoclass('com.google.android.gms.maps.MapView')
            return MapView(self.context)
        except:
            print("❌ Google Maps non disponible")
            return self._create_view(vnode)
    
    def _create_surface_view(self, vnode: VNode) -> Any:
        """Crée une SurfaceView"""
        from jnius import autoclass
        SurfaceView = autoclass('android.view.SurfaceView')
        return SurfaceView(self.context)