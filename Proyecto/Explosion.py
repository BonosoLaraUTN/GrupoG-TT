from Utilidades import *

class Explosion():
	def __init__(mismo, posicion, interval = None, imagenes = None):

		mismo.posicion = [posicion[0]-16, posicion[1]-16]
		mismo.active = True

		if interval == None:
			interval = 100

		if imagenes == None:
			imagenes = [
				sprites.subsurface(0, 80*2, 32*2, 32*2),
				sprites.subsurface(32*2, 80*2, 32*2, 32*2),
				sprites.subsurface(64*2, 80*2, 32*2, 32*2)
			]

		imagenes.reverse()

		mismo.imagenes = [] + imagenes

		mismo.image = mismo.imagenes.pop()

		gtemporizador.add(interval, lambda :mismo.actualizar(), len(mismo.imagenes) + 1)

	def dibujar(mismo, pantalla):
		""" dibujar cuadro de explosión actual """
		pantalla.blit(mismo.image, mismo.posicion)

	def actualizar(mismo):
		""" Avanzar a la siguiente imagen """
		if len(mismo.imagenes) > 0:
			mismo.image = mismo.imagenes.pop()
		else:
			mismo.active = False
