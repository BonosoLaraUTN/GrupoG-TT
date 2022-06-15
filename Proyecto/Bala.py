import pygame

from Utilidades import *
from Explosion import *

class Bala():
	# direccion constante
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	# estado de la bala
	(ESTADO_REMOVIDO, ESTADO_ACTIVO, ESTADO_EXPLOTANDO) = range(3)

	(PROPIET_JUGAD, PROPIET_ENEMIGO) = range(2)

	def __init__(mismo, nivel, posicion, direccion, danio = 100, velocidad = 5):

		mismo.nivel = nivel
		mismo.direccion = direccion
		mismo.danio = danio
		mismo.owner = None
		mismo.owner_class = None

		# 1-bala normal
		# 2-bala que puede destruir el acero
		mismo.poder = 1

		mismo.image = sprites.subsurface(75*2, 74*2, 3*2, 4*2)

		# posicion es la esquina superior izquierda del jugador,
		# por lo que necesitaremos recalcular un poco. también giramos la imagen en sí.
		if direccion == mismo.DIR_UP:
			mismo.rect = pygame.Rect(posicion[0] + 11, posicion[1] - 8, 6, 8)
		elif direccion == mismo.DIR_RIGHT:
			mismo.image = pygame.transform.rotate(mismo.image, 270)
			mismo.rect = pygame.Rect(posicion[0] + 26, posicion[1] + 11, 8, 6)
		elif direccion == mismo.DIR_DOWN:
			mismo.image = pygame.transform.rotate(mismo.image, 180)
			mismo.rect = pygame.Rect(posicion[0] + 11, posicion[1] + 26, 6, 8)
		elif direccion == mismo.DIR_LEFT:
			mismo.image = pygame.transform.rotate(mismo.image, 90)
			mismo.rect = pygame.Rect(posicion[0] - 8 , posicion[1] + 11, 8, 6)

		mismo.explosion_imagenes = [
			sprites.subsurface(0, 80*2, 32*2, 32*2),
			sprites.subsurface(32*2, 80*2, 32*2, 32*2),
		]

		mismo.velocidad = velocidad

		mismo.estado = mismo.ESTADO_ACTIVO

	def dibujar(mismo, pantalla):
		""" dibujar bala """
		if mismo.estado == mismo.ESTADO_ACTIVO:
			pantalla.blit(mismo.image, mismo.rect.topleft)
		elif mismo.estado == mismo.ESTADO_EXPLOTANDO:
			mismo.explosion.dibujar(pantalla)

	def actualizar(mismo, estatua):

		if mismo.estado == mismo.ESTADO_EXPLOTANDO:
			if not mismo.explosion.active:
				mismo.destruir()
				del mismo.explosion

		if mismo.estado != mismo.ESTADO_ACTIVO:
			return

		""" movimiento de bala """
		if mismo.direccion == mismo.DIR_UP:
			mismo.rect.topleft = [mismo.rect.left, mismo.rect.top - mismo.velocidad]
			if mismo.rect.top < 0:
				if reproducir_sonidos and mismo.owner == mismo.PROPIET_JUGAD:
					sonidos["acero"].play()
				mismo.explotar()
				return
		elif mismo.direccion == mismo.DIR_RIGHT:
			mismo.rect.topleft = [mismo.rect.left + mismo.velocidad, mismo.rect.top]
			if mismo.rect.left > (416 - mismo.rect.width):
				if reproducir_sonidos and mismo.owner == mismo.PROPIET_JUGAD:
					sonidos["acero"].play()
				mismo.explotar()
				return
		elif mismo.direccion == mismo.DIR_DOWN:
			mismo.rect.topleft = [mismo.rect.left, mismo.rect.top + mismo.velocidad]
			if mismo.rect.top > (416 - mismo.rect.height):
				if reproducir_sonidos and mismo.owner == mismo.PROPIET_JUGAD:
					sonidos["acero"].play()
				mismo.explotar()
				return
		elif mismo.direccion == mismo.DIR_LEFT:
			mismo.rect.topleft = [mismo.rect.left - mismo.velocidad, mismo.rect.top]
			if mismo.rect.left < 0:
				if reproducir_sonidos and mismo.owner == mismo.PROPIET_JUGAD:
					sonidos["acero"].play()
				mismo.explotar()
				return

		ha_colicionado = False

		# verifica si hay colisiones con las paredes.
		# una bala puede destruir varias fichas (1 o 2) pero la explosión sigue siendo 1
		rects = mismo.nivel.reacc_obstaculos
		coliciones = mismo.rect.collidelistall(rects)
		if coliciones != []:
			for i in coliciones:
				if mismo.nivel.golpear_baldosa(estatua, rects[i].topleft, mismo.poder, mismo.owner == mismo.PROPIET_JUGAD):
					ha_colicionado = True
		if ha_colicionado:
			mismo.explotar()
			return

		# verifica la colisiones de balas con balas
		for bala in balas:
			if mismo.estado == mismo.ESTADO_ACTIVO and bala.owner != mismo.owner and bala != mismo and mismo.rect.colliderect(bala.rect):
				mismo.destruir()
				mismo.explotar()
				return

		# verifica la colision entre jugadores
		for jugador in jugadores:
			if jugador.estado == jugador.ESTADO_VIDO and mismo.rect.colliderect(jugador.rect):
				if jugador.impacto_bala(mismo.owner == mismo.PROPIET_JUGAD, mismo.danio, mismo.owner_class):
					mismo.destruir()
					return

		# verifica la colision entre enemigos
		for enemigo in enemigos:
			if enemigo.estado == enemigo.ESTADO_VIDO and mismo.rect.colliderect(enemigo.rect):
				if enemigo.impacto_bala(mismo.owner == mismo.PROPIET_ENEMIGO, mismo.danio, mismo.owner_class):
					mismo.destruir()
					return

		# verifica la colision con el estatua
		if estatua.active and mismo.rect.colliderect(estatua.rect):
			estatua.destruir()
			mismo.destruir()
			return

	def explotar(mismo):
		""" las balas explotan """
		global pantalla
		if mismo.estado != mismo.ESTADO_REMOVIDO:
			mismo.estado = mismo.ESTADO_EXPLOTANDO
			mismo.explosion = Explosion([mismo.rect.left-13, mismo.rect.top-13], None, mismo.explosion_imagenes)

	def destruir(mismo):
		mismo.estado = mismo.ESTADO_REMOVIDO