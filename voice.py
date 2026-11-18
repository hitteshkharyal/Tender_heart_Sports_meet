"""
Text-to-speech voice engine for Sports Meet 2026.
Designed to work reliably inside Streamlit's re-run model.
Each speak() call runs pyttsx3 in a fresh daemon thread to avoid
engine-reuse issues that occur when Streamlit caches objects across re-runs.
"""
import threading
import time


class VoiceGreeter:
    def __init__(self, enabled=True, rate=155, volume=1.0, cooldown=4.0):
        self.enabled = enabled
        self.rate = rate
        self.volume = volume
        self.cooldown = cooldown
        self._last_spoken = 0.0
        self._lock = threading.Lock()
        self._speaking = False

    def speak(self, text):
        """Speak text in a background thread. Safe to call from Streamlit."""
        if not self.enabled:
            return

        now = time.time()
        with self._lock:
            # Cooldown: don't overlap or rapid-fire speech
            if now - self._last_spoken < self.cooldown:
                return
            if self._speaking:
                return
            self._last_spoken = now
            self._speaking = True

        t = threading.Thread(target=self._do_speak, args=(text,), daemon=True)
        t.start()

    def _do_speak(self, text):
        """Create a fresh pyttsx3 engine, speak, then dispose."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            # Pick a clear English voice
            try:
                voices = engine.getProperty("voices")
                if voices:
                    for v in voices:
                        name_lower = v.name.lower()
                        if "david" in name_lower or "zira" in name_lower or "english" in name_lower:
                            engine.setProperty("voice", v.id)
                            break
            except Exception:
                pass

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[voice] TTS error: {e}")
        finally:
            with self._lock:
                self._speaking = False

    def play_chime(self):
        """Play a short celebratory chime (Windows only). Non-blocking."""
        def _beep():
            try:
                import winsound
                winsound.Beep(988, 120)
                winsound.Beep(1318, 180)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()

    def toggle(self):
        """Toggle voice on/off. Returns the new state."""
        self.enabled = not self.enabled
        return self.enabled

    def stop(self):
        """No-op for compatibility — threads are daemon and self-terminate."""
        pass
