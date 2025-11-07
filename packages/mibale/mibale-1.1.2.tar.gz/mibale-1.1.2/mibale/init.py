"""
Mibale Framework - Vue.js-like mobile framework in Python
"""

__version__ = "1.0.0"
__author__ = "Mibale Team"

from .core.application import create_app, MibaleApp
from .core.component import BaseComponent, defineComponent
from .router import Router, Route, useRouter, useRoute
from .stores import createStore, useStore, defineStore
from .services.http_client import axios
from .directives import v_model, v_show, v_if, v_for, v_on, v_bind
from .compiler import compile_mb, MBCompiler

# Exports principaux
__all__ = [
    'create_app',
    'MibaleApp', 
    'BaseComponent',
    'defineComponent',
    'Router',
    'Route', 
    'useRouter',
    'useRoute',
    'createStore',
    'useStore',
    'defineStore',
    'axios',
    'v_model',
    'v_show', 
    'v_if',
    'v_for',
    'v_on',
    'v_bind',
    'compile_mb',
    'MBCompiler'
]

# Initialisation globale
def init():
    """Initialise le framework Mibale"""
    from .core.application import MibaleApp
    from .render.render_engine import RenderEngine
    print("🚀 Mibale Framework initialisé")