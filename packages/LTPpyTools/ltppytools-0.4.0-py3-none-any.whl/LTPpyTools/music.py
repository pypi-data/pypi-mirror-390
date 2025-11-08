import wave
import threading
import os

class music:
    @classmethod
    def __init__(self):
        self.is_playing = False
        self.thread = None
        self.initialized = False
        self.lock = threading.Lock()
    @classmethod
    def init(self):
        print("Tools.music loaded")
        self.initialized = True
    @classmethod
    def load(self, file_path):
        if not self.initialized:
            raise RuntimeError("Please call init() before using the music.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.lower().endswith('.wav'):
            raise ValueError(f"Unsupported file format: {file_path}. Only .wav files are supported.")
        self.file_path = file_path
        print(f"Loaded: {file_path}")
    @classmethod
    def play_audio(self, loop):
        try:
            with wave.open(self.file_path, 'rb') as wf:
                chunk = 1024
                while loop > 0 or loop == -1:
                    wf.rewind()
                    data = wf.readframes(chunk)
                    while data:
                        data = wf.readframes(chunk)
                    if loop > 0:
                        loop -= 1
            self.is_playing = False
        except Exception as e:
            print(f"Error playing audio: {e}")
    @classmethod
    def play(self, loop=1):
        if not self.initialized:
            raise RuntimeError("Please call init() before using the music.")
        if not hasattr(self, 'file_path'):
            raise RuntimeError("No file loaded. Use `load()` first.")
        with self.lock:
            if self.is_playing:
                print("Error: Already playing.")
                return
            self.is_playing = True
            self.thread = threading.Thread(target=self.play_audio, args=(loop,))
            self.thread.start()
    @classmethod
    def stop(self):
        if not self.initialized:
            raise RuntimeError("Please call init() before using the music.")
        if self.is_playing:
            self.is_playing = False
            if self.thread and self.thread.is_alive():
                self.thread.join()
            print("Playback stopped.")
        else:
            print("Error: No audio is currently playing.")
