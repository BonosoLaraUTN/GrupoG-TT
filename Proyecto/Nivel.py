import os

from Utilidades import *

class myRect(pygame.Rect):
	""" Añadir tipo de propiedad """
	def __init__(mismo, left, top, width, height, type):
		pygame.Rect.__init__(mismo, left, top, width, height)
		mismo.type = type

class Nivel():

	# tipos de materiales
	(BALDOSA_VACIA, MATERIAL_LADRILLO, MATERIAL_ACERO, MATERIAL_AGUA, MATERIAL_HIERBA, MATERIAL_CONGELADO) = range(6)

	# ancho/alto del material en px
	MATERIAL_TAMANIO = 16

	def __init__(mismo, estatua, nr_nivel = None):
		""" Hay un total de 35 niveles diferentes. Si nr_nivel es mayor que 35, 
		pase al siguiente nivel correspondiente, por ejemplo, si nr_nivel es 37, entonces cargue el nivel 2 """

		# numero máximo de enemigos simultáneamente en el mapa
		mismo.max_active_enemigos = 4

		imagen_baldosas = [
			pygame.Surface((8*2, 8*2)),
			sprites.subsurface(48*2, 64*2, 8*2, 8*2),
			sprites.subsurface(48*2, 72*2, 8*2, 8*2),
			sprites.subsurface(56*2, 72*2, 8*2, 8*2),
			sprites.subsurface(64*2, 64*2, 8*2, 8*2),
			sprites.subsurface(64*2, 64*2, 8*2, 8*2),
			sprites.subsurface(72*2, 64*2, 8*2, 8*2),
			sprites.subsurface(64*2, 72*2, 8*2, 8*2)
		]
		mismo.baldosa_vacia = imagen_baldosas[0]
		mismo.material_ladrillo = imagen_baldosas[1]
		mismo.material_acero = imagen_baldosas[2]
		mismo.material_hierba = imagen_baldosas[3]
		mismo.material_agua = imagen_baldosas[4]
		mismo.material_agua1 = imagen_baldosas[5]
		mismo.material_agua2 = imagen_baldosas[6]
		mismo.material_congelado = imagen_baldosas[7]

		mismo.reacc_obstaculos = []

		nr_nivel = 0 if nr_nivel == None else nr_nivel%35 
		if nr_nivel == 0:
			nr_nivel = 35

		mismo.cargarNivel(nr_nivel)

		# las baldosas reaccionan en el mapa, los tanques no pueden moverse
		mismo.reacc_obstaculos = []

		# actualizar estas baldosas
		mismo.actualizarReaccionObst(estatua)

		gtemporizador.add(400, lambda :mismo.alternar_olas())

	def golpear_baldosa(mismo, estatua, pos, poder = 1, sound = False):
		#Golpea la baldosa

		for baldosa in mismo.mapr:
			if baldosa.topleft == pos:
				if baldosa.type == mismo.MATERIAL_LADRILLO:
					if reproducir_sonidos and sound:
						sonidos["ladrillo"].play()
					mismo.mapr.remove(baldosa)
					mismo.actualizarReaccionObst(estatua)
					return True
				elif baldosa.type == mismo.MATERIAL_ACERO:
					if reproducir_sonidos and sound:
						sonidos["acero"].play()
					if poder == 2:
						mismo.mapr.remove(baldosa)
						mismo.actualizarReaccionObst(estatua)
					return True
				else:
					return False

	def alternar_olas(mismo):
		"""Alternar imagen de agua"""
		if mismo.material_agua == mismo.material_agua1:
			mismo.material_agua = mismo.material_agua2
		else:
			mismo.material_agua = mismo.material_agua1


	def cargarNivel(mismo, nr_nivel = 0):
		""" Cargar nivel especificado
		
		"""
		filename = "niveles/"+str(nr_nivel)
		if (not os.path.isfile(filename)):
			return False
		nivel = []
		f = open(filename, "r")
		data = f.read().split("\n")
		mismo.mapr = []
		x, y = 0, 0
		for row in data:
			for ch in row:
				if ch == "#":
					mismo.mapr.append(myRect(x, y, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_LADRILLO))
				elif ch == "@":
					mismo.mapr.append(myRect(x, y, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_ACERO))
				elif ch == "~":
					mismo.mapr.append(myRect(x, y, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_AGUA))
				elif ch == "%":
					mismo.mapr.append(myRect(x, y, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_HIERBA))
				elif ch == "-":
					mismo.mapr.append(myRect(x, y, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_TAMANIO, mismo.MATERIAL_CONGELADO))
				x += mismo.MATERIAL_TAMANIO
			x = 0
			y += mismo.MATERIAL_TAMANIO
		return True


	def dibujar(mismo, pantalla, baldosas = None):
		""" Dibuja un mapa específico sobre la superficie existente """

		if baldosas == None:
			baldosas = [MATERIAL_LADRILLO, MATERIAL_ACERO, MATERIAL_AGUA, MATERIAL_HIERBA, MATERIAL_CONGELADO]

		for baldosa in mismo.mapr:
			if baldosa.type in baldosas:
				if baldosa.type == mismo.MATERIAL_LADRILLO:
					pantalla.blit(mismo.material_ladrillo, baldosa.topleft)
				elif baldosa.type == mismo.MATERIAL_ACERO:
					pantalla.blit(mismo.material_acero, baldosa.topleft)
				elif baldosa.type == mismo.MATERIAL_AGUA:
					pantalla.blit(mismo.material_agua, baldosa.topleft)
				elif baldosa.type == mismo.MATERIAL_CONGELADO:
					pantalla.blit(mismo.material_congelado, baldosa.topleft)
				elif baldosa.type == mismo.MATERIAL_HIERBA:
					pantalla.blit(mismo.material_hierba, baldosa.topleft)

	def actualizarReaccionObst(mismo, estatua):
		""" Establecer la reaccion a todas las baldosas 
		que los jugadores pueden destruir con balas """

		mismo.reacc_obstaculos = [estatua.rect]

		for baldosa in mismo.mapr:
			if baldosa.type in (mismo.MATERIAL_LADRILLO, mismo.MATERIAL_ACERO, mismo.MATERIAL_AGUA):
				mismo.reacc_obstaculos.append(baldosa)

	def constr_fortaleza(mismo, estatua, baldosa):
		""" Construir muros alrededor del estatua hechos de baldosa"""

		posicions = [
			(11*mismo.MATERIAL_TAMANIO, 23*mismo.MATERIAL_TAMANIO),
			(11*mismo.MATERIAL_TAMANIO, 24*mismo.MATERIAL_TAMANIO),
			(11*mismo.MATERIAL_TAMANIO, 25*mismo.MATERIAL_TAMANIO),
			(14*mismo.MATERIAL_TAMANIO, 23*mismo.MATERIAL_TAMANIO),
			(14*mismo.MATERIAL_TAMANIO, 24*mismo.MATERIAL_TAMANIO),
			(14*mismo.MATERIAL_TAMANIO, 25*mismo.MATERIAL_TAMANIO),
			(12*mismo.MATERIAL_TAMANIO, 23*mismo.MATERIAL_TAMANIO),
			(13*mismo.MATERIAL_TAMANIO, 23*mismo.MATERIAL_TAMANIO)
		]

		obsolete = []

		for i, rect in enumerate(mismo.mapr):
			if rect.topleft in posicions:
				obsolete.append(rect)
		for rect in obsolete:
			mismo.mapr.remove(rect)

		for pos in posicions:
			mismo.mapr.append(myRect(pos[0], pos[1], mismo.MATERIAL_TAMANIO, mismo.MATERIAL_TAMANIO, baldosa))

		mismo.actualizarReaccionObst(estatua)
