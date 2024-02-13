import pygame.mixer as mixer
import math


class Player:
    """
    Simple facade for pygame mixer, defiining functionality for playing an audio file
    """

    def __init__(self):
        self.__len = None
        self.__is_paused = False
        mixer.init()

    def play(self, path):
        sound = mixer.Sound(path)
        self.__len = sound.get_length()
        mixer.music.load(path)
        mixer.music.play()

    def stop(self):
        mixer.music.stop()
        self.__len = None

    def pause(self):
        if mixer.music.get_busy():
            mixer.music.pause()
            self.__is_paused = True
        elif mixer.music.get_pos() > 0:
            mixer.music.unpause()
            self.__is_paused = False

    def get_pos(self):
        return mixer.music.get_pos() // 1000

    def get_len(self):
        if self.__len:
            return math.trunc(self.__len)
        return 0

    def is_paused(self):
        return self.__is_paused