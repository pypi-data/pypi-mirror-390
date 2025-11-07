"""
Store utilisateur pour la gestion de l'état global de l'utilisateur
"""

from mibale.stores import defineStore

def useUserStore():
    """Store pour la gestion des données utilisateur"""
    return defineStore('user', {
        # State initial
        'state': {
            'isLoggedIn': False,
            'name': None,
            'email': None,
            'avatar': None,
            'preferences': {
                'theme': 'light',
                'language': 'fr',
                'notifications': True
            },
            'lastLogin': None
        },
        
        # Getters (computed properties)
        'getters': {
            'isAuthenticated': lambda state: state['isLoggedIn'],
            'displayName': lambda state: state['name'] or 'Invité',
            'initials': lambda state: ''.join([name[0].upper() for name in (state['name'] or '??').split()[:2]]),
            'preferencesSummary': lambda state: f"Theme: {state['preferences']['theme']}, Lang: {state['preferences']['language']}"
        },
        
        # Actions (méthodes)
        'actions': {
            'async login'(state, username, email=None):
                """Connexion de l'utilisateur"""
                print(f"🔐 Tentative de connexion: {username}")
                
                # Simulation d'une requête API
                try:
                    # Ici, normalement on appellerait une API
                    # user_data = await api.login(username, password)
                    
                    # Données simulées
                    user_data = {
                        'name': username,
                        'email': email or f"{username}@example.com",
                        'avatar': f"https://ui-avatars.com/api/?name={username}&background=667eea&color=fff"
                    }
                    
                    # Mise à jour du state
                    state['isLoggedIn'] = True
                    state['name'] = user_data['name']
                    state['email'] = user_data['email']
                    state['avatar'] = user_data['avatar']
                    state['lastLogin'] = 'now'  # En vrai: datetime.now().isoformat()
                    
                    print(f"✅ Utilisateur connecté: {username}")
                    return True
                    
                except Exception as e:
                    print(f"❌ Erreur connexion: {e}")
                    return False
            
            'logout'(state):
                """Déconnexion de l'utilisateur"""
                print(f"🚪 Déconnexion de: {state['name']}")
                
                # Réinitialisation du state
                state['isLoggedIn'] = False
                state['name'] = None
                state['email'] = None
                state['avatar'] = None
                state['lastLogin'] = None
                
                print("✅ Utilisateur déconnecté")
            
            'updateProfile'(state, updates):
                """Mise à jour du profil utilisateur"""
                print(f"📝 Mise à jour profil: {updates}")
                
                for key, value in updates.items():
                    if key in state:
                        state[key] = value
                
                print("✅ Profil mis à jour")
            
            'updatePreference'(state, key, value):
                """Mise à jour d'une préférence"""
                print(f"⚙️ Mise à jour préférence: {key} = {value}")
                
                if key in state['preferences']:
                    state['preferences'][key] = value
                    print(f"✅ Préférence {key} mise à jour")
                else:
                    print(f"⚠️ Préférence inconnue: {key}")
            
            'async loadUserData'(state):
                """Chargement des données utilisateur"""
                print("📥 Chargement des données utilisateur...")
                
                if not state['isLoggedIn']:
                    print("⚠️ Utilisateur non connecté")
                    return False
                
                try:
                    # Simulation de chargement depuis une API
                    # user_data = await api.getUserProfile()
                    
                    # Données simulées
                    user_data = {
                        'preferences': {
                            'theme': 'dark',
                            'language': 'fr',
                            'notifications': True
                        }
                    }
                    
                    state['preferences'].update(user_data['preferences'])
                    print("✅ Données utilisateur chargées")
                    return True
                    
                except Exception as e:
                    print(f"❌ Erreur chargement données: {e}")
                    return False
            
            'toggleTheme'(state):
                """Bascule entre les thèmes clair/sombre"""
                current_theme = state['preferences']['theme']
                new_theme = 'dark' if current_theme == 'light' else 'light'
                
                state['preferences']['theme'] = new_theme
                print(f"🎨 Thème changé: {current_theme} → {new_theme}")
            
            'setLanguage'(state, language):
                """Définit la langue de l'application"""
                supported_languages = ['fr', 'en', 'es', 'de']
                
                if language in supported_languages:
                    state['preferences']['language'] = language
                    print(f"🌐 Langue changée: {language}")
                else:
                    print(f"❌ Langue non supportée: {language}")
        }
    })

# Export pour une utilisation facile
user_store = useUserStore()

# Exemple d'utilisation :
if __name__ == "__main__":
    # Test du store
    store = useUserStore()
    
    print("🧪 Test du store utilisateur:")
    print(f"État initial: {store.state}")
    
    # Connexion
    store.login("John Doe", "john@example.com")
    print(f"Après connexion: {store.state}")
    
    # Test des getters
    print(f"Authentifié: {store.isAuthenticated}")
    print(f"Nom affiché: {store.displayName}")
    print(f"Initiales: {store.initials}")
    
    # Mise à jour des préférences
    store.updatePreference('theme', 'dark')
    store.toggleTheme()
    
    # Déconnexion
    store.logout()
    print(f"Après déconnexion: {store.state}")