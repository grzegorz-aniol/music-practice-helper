import pygame.mixer as mixer
import math


class Player:
    """
    Simple facade for pygame mixer, defiining functionality for playing an audio file
    """

    def __init__(self):
        self.len = None
        mixer.init()

    def play(self, path):
        sound = mixer.Sound(path)
        self.len = sound.get_length()
        mixer.music.load(path)
        mixer.music.play()

    def stop(self):
        mixer.music.stop()
        self.len = None

    def get_pos(self):
        return mixer.music.get_pos() // 1000

    def get_len(self):
        return math.trunc(self.len)
