
from Utilidades import *
from Tanque import *

class Jugador(Tanque):

	def __init__(mismo, nivel, type, posicion = None, direccion = None, filename = None):

		Tanque.__init__(mismo, nivel, type, posicion = None, direccion = None, filename = None)

		if filename == None:
			filename = (0, 0, 16*2, 16*2)

		mismo.comienzo_posicion = posicion
		mismo.comienzo_direccion = direccion

		mismo.lives = 3

		# puntaje total
		mismo.puntaje = 0

		# almacenar cuántos bonos en esta etapa ha recolectado este jugador
		mismo.trophies = {
			"bonus" : 0,
			"enemigo0" : 0,
			"enemigo1" : 0,
			"enemigo2" : 0,
			"enemigo3" : 0
		}

		mismo.image = sprites.subsurface(filename)
		mismo.imagen_arrib = mismo.image;
		mismo.imagen_izquierda = pygame.transform.rotate(mismo.image, 90)
		mismo.imagen_abajo = pygame.transform.rotate(mismo.image, 180)
		mismo.imagen_derecha = pygame.transform.rotate(mismo.image, 270)

		if direccion == None:
			mismo.rotate(mismo.DIR_UP, False)
		else:
			mismo.rotate(direccion, False)

	def move(mismo, direccion):
		""" mover jugador si es posible """

		if mismo.estado == mismo.ESTADO_EXPLOTANDO:
			if not mismo.explosion.active:
				mismo.estado = mismo.ESTADO_MUERTO
				del mismo.explosion

		if mismo.estado != mismo.ESTADO_VIDO:
			return

		# rotar jugador
		if mismo.direccion != direccion:
			mismo.rotate(direccion)

		if mismo.paralizado:
			return

		# mover jugador
		if direccion == mismo.DIR_UP:
			new_posicion = [mismo.rect.left, mismo.rect.top - mismo.velocidad]
			if new_posicion[1] < 0:
				return
		elif direccion == mismo.DIR_RIGHT:
			new_posicion = [mismo.rect.left + mismo.velocidad, mismo.rect.top]
			if new_posicion[0] > (416 - 26):
				return
		elif direccion == mismo.DIR_DOWN:
			new_posicion = [mismo.rect.left, mismo.rect.top + mismo.velocidad]
			if new_posicion[1] > (416 - 26):
				return
		elif direccion == mismo.DIR_LEFT:
			new_posicion = [mismo.rect.left - mismo.velocidad, mismo.rect.top]
			if new_posicion[0] < 0:
				return

		jugador_rect = pygame.Rect(new_posicion, [26, 26])

		# coliciones con baldosas
		if jugador_rect.collidelist(mismo.nivel.reacc_obstaculos) != -1:
			return

		# coliciones con otros jugadores
		for jugador in jugadores:
			if jugador != mismo and jugador.estado == jugador.ESTADO_VIDO and jugador_rect.colliderect(jugador.rect) == True:
				return

		# coliciones con enemigos
		for enemigo in enemigos:
			if jugador_rect.colliderect(enemigo.rect) == True:
				return

		# coliciones con bonus
		for bonus in bonuses:
			if jugador_rect.colliderect(bonus.rect) == True:
				mismo.bonus = bonus

		#si no hay colicion, mover jugador
		mismo.rect.topleft = (new_posicion[0], new_posicion[1])

	def reiniciar(mismo):
		""" reiniciar jugador """
		mismo.rotate(mismo.comienzo_direccion, False)
		mismo.rect.topleft = mismo.comienzo_posicion
		mismo.superPoderes = 0
		mismo.max_balas_activas = 1
		mismo.vida = 100
		mismo.paralizado = False
		mismo.pausado = False
		mismo.presionado = [False] * 4
		mismo.estado = mismo.ESTADO_VIDO