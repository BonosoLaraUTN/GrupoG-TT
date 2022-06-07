import pygame, random

from Utilidades import *
from Bala import *

class Tanque():

	# direcciones posibles
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	# estados
	(ESTADO_APARECIENDO, ESTADO_MUERTO, ESTADO_VIDO, ESTADO_EXPLOTANDO) = range(4)

	# lados
	(LADO_JUGADOR, LADO_ENEMIGO) = range(2)

	def __init__(mismo, nivel, lado, posicion = None, direccion = None, filename = None):

		# saldus, si la salud es 0 significa muerte
		mismo.vida = 100

		# el tanque no se puede mover pero puede rotar y disparar
		mismo.paralizado = False

		# el tanque no puede hacer nada
		mismo.pausado = False

		# el tanque está protegido de las balas
		mismo.blindado = False

		# px por movimiento
		mismo.velocidad = 2

		# cuantas balas puede disparar un tanque simultaneamente
		mismo.max_balas_activas = 1

		# amigo o enemigo
		mismo.lado = lado

		# estado intermitente. 0 apagado, 1 encendido
		mismo.intermitente = 0

		# teclas de navegación: fuego, arriba, derecha, abajo, izquierda
		mismo.controles = [pygame.K_SPACE, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

		# Botones presionados actualmente (solo navegación)
		mismo.presionado = [False] * 4

		mismo.imagenes_escudo = [
			sprites.subsurface(0, 48*2, 16*2, 16*2),
			sprites.subsurface(16*2, 48*2, 16*2, 16*2)
		]
		mismo.imagen_escudo = mismo.imagenes_escudo[0]
		mismo.indice_escudo = 0

		mismo.imagenes_aparecer = [
			sprites.subsurface(32*2, 48*2, 16*2, 16*2),
			sprites.subsurface(48*2, 48*2, 16*2, 16*2)
		]
		mismo.imagen_aparecer = mismo.imagenes_aparecer[0]
		mismo.indice_aparecer = 0

		mismo.nivel = nivel 

		if posicion != None:
			mismo.rect = pygame.Rect(posicion, (26, 26))
		else:
			mismo.rect = pygame.Rect(0, 0, 26, 26)

		if direccion == None:
			mismo.direccion = random.choice([mismo.DIR_RIGHT, mismo.DIR_DOWN, mismo.DIR_LEFT])
		else:
			mismo.direccion = direccion

		mismo.estado = mismo.ESTADO_APARECIENDO

		# animacion de aparecimiento
		mismo.temporizador_uuid_spawn = gtemporizador.add(100, lambda :mismo.alternar_imag_aparecer())

		# duracion del aparecimiento
		mismo.temporizador_uuid_spawn_end = gtemporizador.add(1000, lambda :mismo.terminar_aparecer())

	def terminar_aparecer(mismo):
		""" termina la animacion de aparecer 
		Los jugadores pueden jugar
		"""
		mismo.estado = mismo.ESTADO_VIDO
		gtemporizador.destruir(mismo.temporizador_uuid_spawn_end)


	def alternar_imag_aparecer(mismo):
		""" avanzar a la siguiente imagen de generacion """
		if mismo.estado != mismo.ESTADO_APARECIENDO:
			gtemporizador.destruir(mismo.temporizador_uuid_spawn)
			return
		mismo.indice_aparecer += 1
		if mismo.indice_aparecer >= len(mismo.imagenes_aparecer):
			mismo.indice_aparecer = 0
		mismo.imagen_aparecer = mismo.imagenes_aparecer[mismo.indice_aparecer]

	def alternar_imagen_escudo(mismo):
		""" avanzar a la siguiente imagen del escudo """
		if mismo.estado != mismo.ESTADO_VIDO:
			gtemporizador.destruir(mismo.temporiz_uuid_escudo)
			return
		if mismo.blindado:
			mismo.indice_escudo += 1
			if mismo.indice_escudo >= len(mismo.imagenes_escudo):
				mismo.indice_escudo = 0
			mismo.imagen_escudo = mismo.imagenes_escudo[mismo.indice_escudo]


	def dibujar(mismo, pantalla):
		""" dibujar tanque """

		if mismo.estado == mismo.ESTADO_VIDO:
			pantalla.blit(mismo.image, mismo.rect.topleft)
			if mismo.blindado:
				pantalla.blit(mismo.imagen_escudo, [mismo.rect.left-3, mismo.rect.top-3])
		elif mismo.estado == mismo.ESTADO_EXPLOTANDO:
			mismo.explosion.dibujar(pantalla)
		elif mismo.estado == mismo.ESTADO_APARECIENDO:
			pantalla.blit(mismo.imagen_aparecer, mismo.rect.topleft)

	def explotar(mismo):
		""" empezar la explocion del tanque """
		if mismo.estado != mismo.ESTADO_MUERTO:
			mismo.estado = mismo.ESTADO_EXPLOTANDO
			mismo.explosion = Explosion(mismo.rect.topleft)

	def fuego(mismo, forzado = False):
		""" disparar una bala
		@param boolean forzado. Si es falso, verifica si el tanque ha excedido su cuota de balas. Default: True
		@return boolean True si la bala fuera disparada, false de lo contrario
		"""

		if mismo.estado != mismo.ESTADO_VIDO:
			gtemporizador.destruir(mismo.temporiz_uuid_fuego)
			return False

		if mismo.pausado:
			return False

		if not forzado:
			balas_activas = 0
			for bala in balas:
				if bala.owner_class == mismo and bala.estado == bala.ESTADO_ACTIVO:
					balas_activas += 1
			if balas_activas >= mismo.max_balas_activas:
				return False

		bala = Bala(mismo.nivel, mismo.rect.topleft, mismo.direccion)

		if mismo.lado == mismo.LADO_JUGADOR:
			bala.owner = mismo.LADO_JUGADOR
		else:
			bala.owner = mismo.LADO_ENEMIGO
			mismo.balaEnCola = False

		bala.owner_class = mismo
		balas.append(bala)
		return True

	def rotate(mismo, direccion, fix_posicion = True):
		""" rotar tanque
		rotar, actualizar la imagen y corregir posicion
		"""
		mismo.direccion = direccion

		if direccion == mismo.DIR_UP:
			mismo.image = mismo.imagen_arrib
		elif direccion == mismo.DIR_RIGHT:
			mismo.image = mismo.imagen_derecha
		elif direccion == mismo.DIR_DOWN:
			mismo.image = mismo.imagen_abajo
		elif direccion == mismo.DIR_LEFT:
			mismo.image = mismo.imagen_izquierda

		if fix_posicion:
			new_x = mismo.masCercano(mismo.rect.left, 8) + 3
			new_y = mismo.masCercano(mismo.rect.top, 8) + 3

			if (abs(mismo.rect.left - new_x) < 5):
				mismo.rect.left = new_x

			if (abs(mismo.rect.top - new_y) < 5):
				mismo.rect.top = new_y

	def giroAtras(mismo):
		""" Gira el tanque en dirección opuesta"""
		if mismo.direccion in (mismo.DIR_UP, mismo.DIR_RIGHT):
			mismo.rotate(mismo.direccion + 2, False)
		else:
			mismo.rotate(mismo.direccion - 2, False)

	def actualizar(mismo, time_passed):
		""" Actualizar temporizador y explosión (si corresponde) """
		if mismo.estado == mismo.ESTADO_EXPLOTANDO:
			if not mismo.explosion.active:
				mismo.estado = mismo.ESTADO_MUERTO
				del mismo.explosion

	def masCercano(mismo, num, base):
		""" Número redondo a mas cercano divisible"""
		return int(round(num / (base * 1.0)) * base)


	def impacto_bala(mismo, fuego_amigo = False, danio = 100, tanque = None):
		""" impacto de bala
		Devuelve True si la bala debe destruirse con el impacto.
		Solo el fuego amigo del enemigo no desencadena la explosión de bala.
		"""

		if mismo.blindado:
			return True

		if not fuego_amigo:
			mismo.vida -= danio
			if mismo.vida < 1:
				if mismo.lado == mismo.LADO_ENEMIGO:
					tanque.trophies["enemigo"+str(mismo.type)] += 1
					points = (mismo.type+1) * 100
					tanque.puntaje += points
					if reproducir_sonidos:
						sonidos["explosion"].play()

				mismo.explotar()
			return True

		if mismo.lado == mismo.LADO_ENEMIGO:
			return False
		elif mismo.lado == mismo.LADO_JUGADOR:
			if not mismo.paralizado:
				mismo.colocar_paraliz(True)
				mismo.temporizador_uuid_paralise = gtemporizador.add(10000, lambda :mismo.colocar_paraliz(False), 1)
			return True

	def colocar_paraliz(mismo, paralizado = True):
		""" establecer tanque en estado paralizado
		@param boolean paralizado
		@return None
		"""
		if mismo.estado != mismo.ESTADO_VIDO:
			gtemporizador.destruir(mismo.temporizador_uuid_paralise)
			return
		mismo.paralizado = paralizado