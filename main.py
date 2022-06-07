import pygame, sys, os


pygame.init

if __name__ == "__main__":

	gtemporizador = Temporizador()

	sprites = None
	pantalla = None
	jugadores = []
	enemigos = []
	balas = []
	bonuses = []
	etiquetas = []

	reproducir_sonidos = True
	sonidos = {}

	game = Juego()
	castillo = Castillo()
	game.mostrarMenu()