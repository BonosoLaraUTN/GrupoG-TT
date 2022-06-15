from Utilidades import sprites
from Explosion import *

class Estatua():
	""" Estatua del jugador """

	(STATE_STANDING, STATE_destruirED, ESTADO_EXPLOTANDO) = range(3)

	def __init__(mismo):

		# imagenes
		mismo.img_undaniod = sprites.subsurface(0, 15*2, 16*2, 16*2)
		mismo.img_destruired = sprites.subsurface(16*2, 15*2, 16*2, 16*2)

		# posicion inicial
		mismo.rect = pygame.Rect(12*16, 24*16, 32, 32)

		# comienzo con un estatua sano 
		mismo.rebuild()

	def dibujar(mismo, pantalla):
		""" Dibujar estatua """

		pantalla.blit(mismo.image, mismo.rect.topleft)

		if mismo.estado == mismo.ESTADO_EXPLOTANDO:
			if not mismo.explosion.active:
				mismo.estado = mismo.STATE_destruirED
				del mismo.explosion
			else:
				mismo.explosion.dibujar(pantalla)

	def rebuild(mismo):
		""" Restablecer estatua """
		mismo.estado = mismo.STATE_STANDING
		mismo.image = mismo.img_undaniod
		mismo.active = True

	def destruir(mismo):
		"""Destruir estatua """
		mismo.estado = mismo.ESTADO_EXPLOTANDO
		mismo.explosion = Explosion(mismo.rect.topleft)
		mismo.image = mismo.img_destruired
		mismo.active = False