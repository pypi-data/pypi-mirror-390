from typing import Dict, Any, List, Optional
from .native_components import NativeComponent

class VideoPlayerComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.current_position = 0
        self.duration = 0
        self.current_video_url = None
        
    def initialize(self) -> bool:
        return True
    
    def load_video(self, video_url: str, surface_view: Any = None) -> bool:
        """Charge une vidéo"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            success = bridge.video_load(video_url, surface_view)
            if success:
                self.current_video_url = video_url
                self.duration = bridge.video_get_duration()
                self.emit('video_loaded', {
                    'url': video_url,
                    'duration': self.duration
                })
                print(f"🎥 Vidéo chargée: {video_url}")
                return True
                
        except Exception as e:
            print(f"❌ Erreur chargement vidéo: {e}")
        
        return False
    
    def play(self):
        """Joue la vidéo"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.video_play()
            self.is_playing = True
            self.emit('video_playing')
            print("▶️ Vidéo en lecture")
        except Exception as e:
            print(f"❌ Erreur lecture vidéo: {e}")
    
    def pause(self):
        """Met en pause"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.video_pause()
            self.is_playing = False
            self.emit('video_paused')
            print("⏸️ Vidéo en pause")
        except Exception as e:
            print(f"❌ Erreur pause vidéo: {e}")
    
    def seek_to(self, position: int):
        """Se positionne à un moment précis"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.video_seek_to(position)
            self.current_position = position
            self.emit('video_seeked', position)
            print(f"⏩ Vidéo avancée à {position}ms")
        except Exception as e:
            print(f"❌ Erreur seek vidéo: {e}")
    
    def set_volume(self, volume: float):
        """Définit le volume (0.0 à 1.0)"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.video_set_volume(volume)
            self.emit('volume_changed', volume)
            print(f"🔊 Volume réglé à {volume}")
        except Exception as e:
            print(f"❌ Erreur réglage volume: {e}")
    
    def get_duration(self) -> int:
        """Retourne la durée totale"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.duration = bridge.video_get_duration()
            return self.duration
        except Exception as e:
            print(f"❌ Erreur lecture durée: {e}")
            return 0
    
    def get_current_position(self) -> int:
        """Retourne la position actuelle"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            self.current_position = bridge.video_get_current_position()
            return self.current_position
        except Exception as e:
            print(f"❌ Erreur lecture position: {e}")
            return 0
    
    def stop(self):
        """Arrête la vidéo"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.video_stop()
            self.is_playing = False
            self.current_position = 0
            self.emit('video_stopped')
            print("⏹️ Vidéo arrêtée")
        except Exception as e:
            print(f"❌ Erreur arrêt vidéo: {e}")
    
    def on_video_completed(self, callback: Callable):
        """Callback quand la vidéo est terminée"""
        self.on('video_completed', callback)
    
    def on_buffering_update(self, callback: Callable):
        """Callback pendant le buffering"""
        self.on('buffering_update', callback)
    
    def cleanup(self):
        """Nettoie les ressources vidéo"""
        self.stop()
        self.emit('video_cleaned')
        print("🎥 Lecteur vidéo nettoyé")

class AudioPlayerComponent(NativeComponent):
    def __init__(self):
        super().__init__()
        self.playlist: List[str] = []
        self.current_index = 0
        self.is_playing = False
        self.is_shuffling = False
        self.is_repeating = False
        
    def load_audio(self, audio_url: str) -> bool:
        """Charge un fichier audio"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            
            success = bridge.audio_load(audio_url)
            if success:
                self.emit('audio_loaded', {'url': audio_url})
                print(f"🎵 Audio chargé: {audio_url}")
                return True
                
        except Exception as e:
            print(f"❌ Erreur chargement audio: {e}")
        
        return False
    
    def play(self):
        """Joue l'audio"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.audio_play()
            self.is_playing = True
            self.emit('audio_playing')
            print("▶️ Audio en lecture")
        except Exception as e:
            print(f"❌ Erreur lecture audio: {e}")
    
    def pause(self):
        """Met en pause"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.audio_pause()
            self.is_playing = False
            self.emit('audio_paused')
            print("⏸️ Audio en pause")
        except Exception as e:
            print(f"❌ Erreur pause audio: {e}")
    
    def stop(self):
        """Arrête l'audio"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.audio_stop()
            self.is_playing = False
            self.emit('audio_stopped')
            print("⏹️ Audio arrêté")
        except Exception as e:
            print(f"❌ Erreur arrêt audio: {e}")
    
    def set_playlist(self, playlist: List[str]):
        """Définit une playlist"""
        self.playlist = playlist
        self.current_index = 0
        self.emit('playlist_loaded', {'count': len(playlist)})
        print(f"🎵 Playlist chargée: {len(playlist)} titres")
    
    def next(self):
        """Piste suivante"""
        if not self.playlist:
            return
        
        if self.is_shuffling:
            import random
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        
        next_track = self.playlist[self.current_index]
        self.load_audio(next_track)
        
        if self.is_playing:
            self.play()
        
        self.emit('track_changed', {
            'index': self.current_index,
            'track': next_track
        })
        print(f"⏭️ Piste suivante: {next_track}")
    
    def previous(self):
        """Piste précédente"""
        if not self.playlist:
            return
        
        self.current_index = (self.current_index - 1) % len(self.playlist)
        prev_track = self.playlist[self.current_index]
        self.load_audio(prev_track)
        
        if self.is_playing:
            self.play()
        
        self.emit('track_changed', {
            'index': self.current_index,
            'track': prev_track
        })
        print(f"⏮️ Piste précédente: {prev_track}")
    
    def set_shuffle(self, shuffle: bool):
        """Active/désactive le mode aléatoire"""
        self.is_shuffling = shuffle
        self.emit('shuffle_changed', shuffle)
        print(f"🔀 Mode aléatoire: {'activé' if shuffle else 'désactivé'}")
    
    def set_repeat(self, repeat: bool):
        """Active/désactive la répétition"""
        self.is_repeating = repeat
        self.emit('repeat_changed', repeat)
        print(f"🔁 Mode répétition: {'activé' if repeat else 'désactivé'}")
    
    def set_volume(self, volume: float):
        """Définit le volume (0.0 à 1.0)"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            bridge.audio_set_volume(volume)
            self.emit('volume_changed', volume)
            print(f"🔊 Volume audio réglé à {volume}")
        except Exception as e:
            print(f"❌ Erreur réglage volume audio: {e}")
    
    def get_current_position(self) -> int:
        """Retourne la position actuelle"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.audio_get_current_position()
        except Exception as e:
            print(f"❌ Erreur lecture position audio: {e}")
            return 0
    
    def get_duration(self) -> int:
        """Retourne la durée totale"""
        try:
            from ..android.bridge import AndroidBridge
            bridge = AndroidBridge.get_instance()
            return bridge.audio_get_duration()
        except Exception as e:
            print(f"❌ Erreur lecture durée audio: {e}")
            return 0
    
    def on_audio_completed(self, callback: Callable):
        """Callback quand l'audio est terminé"""
        self.on('audio_completed', callback)
    
    def cleanup(self):
        """Nettoie les ressources audio"""
        self.stop()
        self.emit('audio_cleaned')
        print("🎵 Lecteur audio nettoyé")