from Utilidades import *

class Etiqueta():
	def __init__(mismo, posicion, text = "", duration = None):

		mismo.posicion = posicion

		mismo.active = True

		mismo.text = text

		mismo.font = pygame.font.SysFont("Arial", 13)

		if duration != None:
			gtemporizador.add(duration, lambda :mismo.destruir(), 1)

	def dibujar(mismo, pantalla):
		""" dibujar etiqueta """
		pantalla.blit(mismo.font.render(mismo.text, False, (200,200,200)), [mismo.posicion[0]+4, mismo.posicion[1]+8])

	def destruir(mismo):
		mismo.active = False