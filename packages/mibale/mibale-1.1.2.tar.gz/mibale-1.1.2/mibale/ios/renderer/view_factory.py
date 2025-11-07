from typing import Any, Dict
from ...render.virtual_dom import VNode

class IOSViewFactory:
    """Factory pour créer des vues iOS natives"""
    
    def __init__(self, bridge):
        self.bridge = bridge
    
    def create_view(self, vnode: VNode) -> Any:
        """Crée une vue iOS native basée sur le VNode"""
        tag = vnode.tag.lower()
        
        try:
            if tag in ['view', 'div', 'container']:
                return self._create_view(vnode)
            elif tag in ['vstack', 'vertical']:
                return self._create_vertical_stack(vnode)
            elif tag in ['hstack', 'horizontal']:
                return self._create_horizontal_stack(vnode)
            elif tag in ['textview', 'text', 'label']:
                return self._create_label(vnode)
            elif tag in ['button', 'btn']:
                return self._create_button(vnode)
            elif tag in ['imageview', 'image', 'img']:
                return self._create_image_view(vnode)
            elif tag in ['scrollview', 'scroll']:
                return self._create_scroll_view(vnode)
            elif tag in ['mapview']:
                return self._create_map_view(vnode)
            elif tag in ['webview']:
                return self._create_web_view(vnode)
            else:
                # Vue générique
                return self._create_view(vnode)
                
        except Exception as e:
            print(f"❌ Erreur création vue iOS {tag}: {e}")
            return None
    
    def _create_view(self, vnode: VNode) -> Any:
        """Crée une UIView générique"""
        return self.bridge.create_view()
    
    def _create_vertical_stack(self, vnode: VNode) -> Any:
        """Crée un conteneur vertical (UIStackView)"""
        try:
            from UIKit import UIStackView
            from CoreGraphics import CGRectMake
            
            stack = UIStackView.alloc().initWithFrame_(CGRectMake(0, 0, 100, 100))
            stack.setAxis_(1)  # UILayoutConstraintAxisVertical
            stack.setDistribution_(0)  # UIStackViewDistributionFill
            stack.setAlignment_(0)  # UIStackViewAlignmentFill
            stack.setSpacing_(0)
            
            return stack
        except Exception as e:
            print(f"❌ Erreur création stack vertical: {e}")
            return self._create_view(vnode)
    
    def _create_horizontal_stack(self, vnode: VNode) -> Any:
        """Crée un conteneur horizontal (UIStackView)"""
        try:
            from UIKit import UIStackView
            from CoreGraphics import CGRectMake
            
            stack = UIStackView.alloc().initWithFrame_(CGRectMake(0, 0, 100, 100))
            stack.setAxis_(0)  # UILayoutConstraintAxisHorizontal
            stack.setDistribution_(0)  # UIStackViewDistributionFill
            stack.setAlignment_(0)  # UIStackViewAlignmentFill
            stack.setSpacing_(0)
            
            return stack
        except Exception as e:
            print(f"❌ Erreur création stack horizontal: {e}")
            return self._create_view(vnode)
    
    def _create_label(self, vnode: VNode) -> Any:
        """Crée un UILabel"""
        label = self.bridge.create_label()
        
        if label:
            # Configuration basique
            label.setNumberOfLines_(0)  # Multi-lignes
            label.setLineBreakMode_(0)  # NSLineBreakByWordWrapping
            
            # Texte par défaut
            props = vnode.props or {}
            default_text = props.get('text', 'Label')
            label.setText_(default_text)
        
        return label
    
    def _create_button(self, vnode: VNode) -> Any:
        """Crée un UIButton"""
        button = self.bridge.create_button()
        
        if button:
            # Configuration basique
            props = vnode.props or {}
            default_title = props.get('text', 'Button')
            button.setTitle_forState_(default_title, 0)  # Normal state
            
            # Style par défaut
            button.setTitleColor_forState_(
                self.bridge.get_color('system_blue'), 
                0  # Normal state
            )
        
        return button
    
    def _create_image_view(self, vnode: VNode) -> Any:
        """Crée un UIImageView"""
        props = vnode.props or {}
        image_name = props.get('src')
        return self.bridge.create_image_view(image_name)
    
    def _create_scroll_view(self, vnode: VNode) -> Any:
        """Crée un UIScrollView"""
        try:
            from UIKit import UIScrollView
            from CoreGraphics import CGRectMake
            
            scroll_view = UIScrollView.alloc().initWithFrame_(CGRectMake(0, 0, 100, 100))
            scroll_view.setScrollEnabled_(True)
            scroll_view.setBounces_(True)
            
            return scroll_view
        except Exception as e:
            print(f"❌ Erreur création scroll view: {e}")
            return self._create_view(vnode)
    
    def _create_map_view(self, vnode: VNode) -> Any:
        """Crée un MKMapView"""
        try:
            from MapKit import MKMapView
            from CoreGraphics import CGRectMake
            
            map_view = MKMapView.alloc().initWithFrame_(CGRectMake(0, 0, 100, 100))
            map_view.setShowsUserLocation_(True)
            
            return map_view
        except Exception as e:
            print(f"❌ Erreur création map view: {e}")
            return self._create_view(vnode)
    
    def _create_web_view(self, vnode: VNode) -> Any:
        """Crée un WKWebView"""
        try:
            from WebKit import WKWebView, WKWebViewConfiguration
            from CoreGraphics import CGRectMake
            
            config = WKWebViewConfiguration.alloc().init()
            web_view = WKWebView.alloc().initWithFrame_configuration_(
                CGRectMake(0, 0, 100, 100), 
                config
            )
            
            return web_view
        except Exception as e:
            print(f"❌ Erreur création web view: {e}")
            return self._create_view(vnode)