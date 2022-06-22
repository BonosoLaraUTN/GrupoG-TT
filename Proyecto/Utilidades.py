import pygame

from Temporizador import *

# cargar sprites (version funky )
#sprites = pygame.transform.scale2x(pygame.image.load("imagenes/sprites.gif"))
# cargar sprites (version pixely )
sprites = pygame.transform.scale(pygame.image.load("imagenes/sprites.gif"), [192, 224])
#pantalla.set_colorkey((0,138,104))

jugadores = []
enemigos = []
balas = []
bonuses = []
etiquetas = []

reproducir_sonidos = True
sonidos = {}

gtemporizador = Temporizador()