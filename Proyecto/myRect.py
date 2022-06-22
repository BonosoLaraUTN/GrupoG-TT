import pygame

class myRect(pygame.Rect):
	""" Añadir tipo de propiedad """
	def __init__(mismo, left, top, width, height, type):
		pygame.Rect.__init__(mismo, left, top, width, height)
		mismo.type = type