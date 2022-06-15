from Utilidades import *
from Tanque import *
from Bonus import *

class Enemigo(Tanque):

	(TIPO_BASICO, TIPO_RAPIDO, TIPO_PODEROSO, TIPO_ARMADO) = range(4)

	def __init__(mismo, nivel, type, posicion = None, direccion = None, filename = None):

		Tanque.__init__(mismo, nivel, type, posicion = None, direccion = None, filename = None)

		# si es verdad, no dispara
		mismo.balaEnCola = False

		# elegir tipo al azar
		if len(nivel.enemigos_left) > 0:
			mismo.type = nivel.enemigos_left.pop()
		else:
			mismo.estado = mismo.ESTADO_MUERTO
			return

		if mismo.type == mismo.TIPO_BASICO:
			mismo.velocidad = 1
		elif mismo.type == mismo.TIPO_RAPIDO:
			mismo.velocidad = 3
		elif mismo.type == mismo.TIPO_PODEROSO:
			mismo.superPoderes = 1
		elif mismo.type == mismo.TIPO_ARMADO:
			mismo.vida = 400

		# 1 en 5 posibilidades de que este sea un portaaviones adicional, pero solo si no hay otro tanque
		if random.randint(1, 5) == 1:
			mismo.bonus = True
			for enemigo in enemigos:
				if enemigo.bonus:
					mismo.bonus = False
					break

		imagenes = [
			sprites.subsurface(32*2, 0, 13*2, 15*2),
			sprites.subsurface(48*2, 0, 13*2, 15*2),
			sprites.subsurface(64*2, 0, 13*2, 15*2),
			sprites.subsurface(80*2, 0, 13*2, 15*2),
			sprites.subsurface(32*2, 16*2, 13*2, 15*2),
			sprites.subsurface(48*2, 16*2, 13*2, 15*2),
			sprites.subsurface(64*2, 16*2, 13*2, 15*2),
			sprites.subsurface(80*2, 16*2, 13*2, 15*2)
		]

		mismo.image = imagenes[mismo.type+0]

		mismo.imagen_arrib = mismo.image;
		mismo.imagen_izquierda = pygame.transform.rotate(mismo.image, 90)
		mismo.imagen_abajo = pygame.transform.rotate(mismo.image, 180)
		mismo.imagen_derecha = pygame.transform.rotate(mismo.image, 270)

		if mismo.bonus:
			mismo.image1_up = mismo.imagen_arrib;
			mismo.image1_left = mismo.imagen_izquierda
			mismo.image1_down = mismo.imagen_abajo
			mismo.image1_right = mismo.imagen_derecha

			mismo.image2 = imagenes[mismo.type+4]
			mismo.image2_up = mismo.image2;
			mismo.image2_left = pygame.transform.rotate(mismo.image2, 90)
			mismo.image2_down = pygame.transform.rotate(mismo.image2, 180)
			mismo.image2_right = pygame.transform.rotate(mismo.image2, 270)

		mismo.rotate(mismo.direccion, False)

		if posicion == None:
			mismo.rect.topleft = mismo.obtenerPosAparecerGratis()
			if not mismo.rect.topleft:
				mismo.estado = mismo.ESTADO_MUERTO
				return

		# lista de coordenadas del mapa donde debe ir el tanque a continuación
		mismo.path = mismo.generarRuta(mismo.direccion)

		# 1000 es la duración entre tomas
		mismo.temporiz_uuid_fuego = gtemporizador.add(1000, lambda :mismo.fuego())

		# enciende el parpadeo/flash
		if mismo.bonus:
			mismo.temporizador_uuid_flash = gtemporizador.add(200, lambda :mismo.alternarFlash())

	def alternarFlash(mismo):
		""" alternar estado intermitente """
		if mismo.estado not in (mismo.ESTADO_VIDO, mismo.ESTADO_APARECIENDO):
			gtemporizador.destruir(mismo.temporizador_uuid_flash)
			return
		mismo.intermitente = not mismo.intermitente
		if mismo.intermitente:
			mismo.imagen_arrib = mismo.image2_up
			mismo.imagen_derecha = mismo.image2_right
			mismo.imagen_abajo = mismo.image2_down
			mismo.imagen_izquierda = mismo.image2_left
		else:
			mismo.imagen_arrib = mismo.image1_up
			mismo.imagen_derecha = mismo.image1_right
			mismo.imagen_abajo = mismo.image1_down
			mismo.imagen_izquierda = mismo.image1_left
		mismo.rotate(mismo.direccion, False)

	def aparecer_bonus(mismo):
		""" crea una nueva bonificación si es necesario """

		if len(bonuses) > 0:
			return 
		bonus = Bonus(mismo.nivel)
		bonuses.append(bonus)
		gtemporizador.add(500, lambda :bonus.alternarVisibilidad())
		gtemporizador.add(10000, lambda :bonuses.remove(bonus), 1)


	def obtenerPosAparecerGratis(mismo):

		lugaresDisponibles = [
			[(mismo.nivel.MATERIAL_TAMANIO * 2 - mismo.rect.width) / 2, (mismo.nivel.MATERIAL_TAMANIO * 2 - mismo.rect.height) / 2],
			[12 * mismo.nivel.MATERIAL_TAMANIO + (mismo.nivel.MATERIAL_TAMANIO * 2 - mismo.rect.width) / 2, (mismo.nivel.MATERIAL_TAMANIO * 2 - mismo.rect.height) / 2],
			[24 * mismo.nivel.MATERIAL_TAMANIO + (mismo.nivel.MATERIAL_TAMANIO * 2 - mismo.rect.width) / 2,  (mismo.nivel.MATERIAL_TAMANIO * 2 - mismo.rect.height) / 2]
		]

		random.shuffle(lugaresDisponibles)

		for pos in lugaresDisponibles:

			rect_enemigo = pygame.Rect(pos, [26, 26])

			# colisiones con otros enemigos
			collision = False
			for enemigo in enemigos:
				if rect_enemigo.colliderect(enemigo.rect):
					collision = True
					continue

			if collision:
				continue

			# colisiones con jugadores
			collision = False
			for jugador in jugadores:
				if rect_enemigo.colliderect(jugador.rect):
					collision = True
					continue

			if collision:
				continue

			return pos
		return False

	def move(mismo): 
		""" se mueve el enemigo si es posible """

		if mismo.estado != mismo.ESTADO_VIDO or mismo.pausado or mismo.paralizado:
			return

		if mismo.path == []:
			mismo.path = mismo.generarRuta(None, True)

		new_posicion = mismo.path.pop(0)

		# mover enemigo
		if mismo.direccion == mismo.DIR_UP:
			if new_posicion[1] < 0:
				mismo.path = mismo.generarRuta(mismo.direccion, True)
				return
		elif mismo.direccion == mismo.DIR_RIGHT:
			if new_posicion[0] > (416 - 26):
				mismo.path = mismo.generarRuta(mismo.direccion, True)
				return
		elif mismo.direccion == mismo.DIR_DOWN:
			if new_posicion[1] > (416 - 26):
				mismo.path = mismo.generarRuta(mismo.direccion, True)
				return
		elif mismo.direccion == mismo.DIR_LEFT:
			if new_posicion[0] < 0:
				mismo.path = mismo.generarRuta(mismo.direccion, True)
				return

		nueva_rect = pygame.Rect(new_posicion, [26, 26])

		# coliciones con baldosas
		if nueva_rect.collidelist(mismo.nivel.reacc_obstaculos) != -1:
			mismo.path = mismo.generarRuta(mismo.direccion, True)
			return

		# coliciones con otros enemigos
		for enemigo in enemigos:
			if enemigo != mismo and nueva_rect.colliderect(enemigo.rect):
				mismo.giroAtras()
				mismo.path = mismo.generarRuta(mismo.direccion)
				return

		# coliciones con jugadores
		for jugador in jugadores:
			if nueva_rect.colliderect(jugador.rect):
				mismo.giroAtras()
				mismo.path = mismo.generarRuta(mismo.direccion)
				return

		# coliciones con bonuses
		for bonus in bonuses:
			if nueva_rect.colliderect(bonus.rect):
				bonuses.remove(bonus)

		# si no hay colicion, mover enemigo
		mismo.rect.topleft = nueva_rect.topleft


	def actualizar(mismo, time_passed):
		Tanque.actualizar(mismo, time_passed)
		if mismo.estado == mismo.ESTADO_VIDO and not mismo.pausado:
			mismo.move()

	def generarRuta(mismo, direccion = None, fix_direccion = False):
		""" si se especifica la dirección, intente continuar de esa manera, de lo contrario, elija al azar
		"""

		all_direccions = [mismo.DIR_UP, mismo.DIR_RIGHT, mismo.DIR_DOWN, mismo.DIR_LEFT]

		if direccion == None:
			if mismo.direccion in [mismo.DIR_UP, mismo.DIR_RIGHT]:
				opposite_direccion = mismo.direccion + 2
			else:
				opposite_direccion = mismo.direccion - 2
			direccions = all_direccions
			random.shuffle(direccions)
			direccions.remove(opposite_direccion)
			direccions.append(opposite_direccion)
		else:
			if direccion in [mismo.DIR_UP, mismo.DIR_RIGHT]:
				opposite_direccion = direccion + 2
			else:
				opposite_direccion = direccion - 2

			if direccion in [mismo.DIR_UP, mismo.DIR_RIGHT]:
				opposite_direccion = direccion + 2
			else:
				opposite_direccion = direccion - 2
			direccions = all_direccions
			random.shuffle(direccions)
			direccions.remove(opposite_direccion)
			direccions.remove(direccion)
			direccions.insert(0, direccion)
			direccions.append(opposite_direccion)

		# al principio, trabaje con unidades generales (pasos) no px
		x = int(round(mismo.rect.left / 16))
		y = int(round(mismo.rect.top / 16))

		new_direccion = None

		for direccion in direccions:
			if direccion == mismo.DIR_UP and y > 1:
				new_pos_rect = mismo.rect.move(0, -8)
				if new_pos_rect.collidelist(mismo.nivel.reacc_obstaculos) == -1:
					new_direccion = direccion
					break
			elif direccion == mismo.DIR_RIGHT and x < 24:
				new_pos_rect = mismo.rect.move(8, 0)
				if new_pos_rect.collidelist(mismo.nivel.reacc_obstaculos) == -1:
					new_direccion = direccion
					break
			elif direccion == mismo.DIR_DOWN and y < 24:
				new_pos_rect = mismo.rect.move(0, 8)
				if new_pos_rect.collidelist(mismo.nivel.reacc_obstaculos) == -1:
					new_direccion = direccion
					break
			elif direccion == mismo.DIR_LEFT and x > 1:
				new_pos_rect = mismo.rect.move(-8, 0)
				if new_pos_rect.collidelist(mismo.nivel.reacc_obstaculos) == -1:
					new_direccion = direccion
					break

		# si podemos ir a otro lado, dar la vuelta
		if new_direccion == None:
			new_direccion = opposite_direccion
			print ("nav izejas. griezhamies")														

		# fijar la posición de los tanques
		if fix_direccion and new_direccion == mismo.direccion:
			fix_direccion = False

		mismo.rotate(new_direccion, fix_direccion)

		posicions = []

		x = mismo.rect.left
		y = mismo.rect.top

		if new_direccion in (mismo.DIR_RIGHT, mismo.DIR_LEFT):
			axis_fix = mismo.masCercano(y, 16) - y
		else:
			axis_fix = mismo.masCercano(x, 16) - x
		axis_fix = 0

		pixels = mismo.masCercano(random.randint(1, 12) * 32, 32) + axis_fix + 3

		if new_direccion == mismo.DIR_UP:
			for px in range(0, pixels, mismo.velocidad):
				posicions.append([x, y-px])
		elif new_direccion == mismo.DIR_RIGHT:
			for px in range(0, pixels, mismo.velocidad):
				posicions.append([x+px, y])
		elif new_direccion == mismo.DIR_DOWN:
			for px in range(0, pixels, mismo.velocidad):
				posicions.append([x, y+px])
		elif new_direccion == mismo.DIR_LEFT:
			for px in range(0, pixels, mismo.velocidad):
				posicions.append([x-px, y])

		return posicions
