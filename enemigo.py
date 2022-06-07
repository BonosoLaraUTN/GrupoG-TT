

class Enemigo(Tanque):

	(TIPO_BASICO, TIPO_RAPIDO, TIPO_PODEROSO, TIPO_ARMADO) = range(4)

	def __init__(mismo, nivel, type, posicion = None, direccion = None, filename = None):

		Tanque.__init__(mismo, nivel, type, posicion = None, direccion = None, filename = None)

		global enemigos, sprites

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