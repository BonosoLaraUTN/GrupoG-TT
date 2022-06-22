import pygame, random

from Utilidades import sprites

class Bonus():
	""" Varios poderes Cuando se genera la bonificación, 
		comienza a parpadear y después de un tiempo desaparece

	Bonos disponibles:
		granada: recoger el poder de la granada elimina instantáneamente a todos los enemigos presentes en la pantalla, incluidos los tanques blindados, independientemente de cuántas veces los hayas golpeado. Sin embargo, no obtiene crédito por destruirlos durante los puntos de bonificación de la etapa final.
		casco: El encendido del casco te otorga un campo de fuerza temporal que te hace invulnerable a los disparos enemigos, igual que con el que comienzas cada etapa.
		Pala: El encendido de la pala convierte las paredes alrededor de tu fortaleza de ladrillo en piedra. Esto hace que sea imposible que el enemigo penetre la pared y destruya tu fortaleza, terminando el juego prematuramente. Sin embargo, el efecto es solo temporal y desaparecerá con el tiempo.
		estrella: El poder de la estrella otorga a tu tanque un nuevo poder ofensivo cada vez que recoges uno, hasta tres veces. La primera estrella te permite disparar tus balas tan rápido como lo hacen los tanques de energía. La segunda estrella te permite disparar hasta dos balas en la pantalla a la vez. Y la tercera estrella permite que tus balas destruyan las paredes de acero irrompibles. Llevas este poder contigo a cada nueva etapa hasta que pierdes una vida.
		tanque: El encendido del tanque te otorga una vida extra. La única otra forma de obtener una vida extra es obtener 20000 puntos.
		Temporizador: el encendido del temporizador congela temporalmente el tiempo, lo que te permite acercarte a todos los tanques sin causar daño y destruirlos hasta que desaparezca el tiempo congelado.
"""

	# tipos de bonus
	(BONUS_GRANADA, BONUS_CASCO, BONUS_PALA, BONUS_ESTRELLA, BONUS_TANQUES, BONUS_TIEMPO) = range(6)

	def __init__(mismo, nivel):

		# para saber donde colocar
		mismo.nivel = nivel

		# tiempo limitado para los bonus
		mismo.active = True

		# estado intermitente
		mismo.visible = True

		mismo.rect = pygame.Rect(random.randint(0, 416-32), random.randint(0, 416-32), 32, 32)

		mismo.bonus = random.choice([
			mismo.BONUS_GRANADA,
			mismo.BONUS_CASCO,
			mismo.BONUS_PALA,
			mismo.BONUS_ESTRELLA,
			mismo.BONUS_TANQUES,
			mismo.BONUS_TIEMPO
		])

		mismo.image = sprites.subsurface(16*2*mismo.bonus, 32*2, 16*2, 15*2)

	def dibujar(mismo, pantalla):
		""" dibujar bonus """
		if mismo.visible:
			pantalla.blit(mismo.image, mismo.rect.topleft)

	def alternarVisibilidad(mismo):
		""" Alternar visibilidad de bonificación """
		mismo.visible = not mismo.visible