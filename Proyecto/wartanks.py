import os, pygame, random, sys

from Utilidades import *
from Jugador import *
from Enemigo import *
from Estatua import *
from Nivel import *

class Juego():

	# direcciones constantes
	(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

	MATERIAL_TAMANIO = 16

	def __init__(mismo):

		global pantalla, reproducir_sonidos, sonidos

		# ventana central
		os.environ['SDL_VIDEO_WINDOW_POS'] = 'centro'

		if reproducir_sonidos:
			pygame.mixer.pre_init(44100, -16, 1, 512)

		pygame.init()


		pygame.display.set_caption("War Tanks")

		size = width, height = 480, 416

		if "-f" in sys.argv[1:]:
			pantalla = pygame.display.set_mode(size, pygame.FULLSCREEN)
		else:
			pantalla = pygame.display.set_mode(size)

		mismo.clock = pygame.time.Clock()

		pygame.display.set_icon(sprites.subsurface(0, 0, 13*2, 13*2))

		# load sonidos
		if reproducir_sonidos:
			pygame.mixer.init(44100, -16, 1, 512)
			sonidos["comienzo"] = pygame.mixer.Sound("sonidos/comienzojuego.ogg")
			sonidos["fin"] = pygame.mixer.Sound("sonidos/finjuego.ogg")
			sonidos["puntaje"] = pygame.mixer.Sound("sonidos/puntaje.ogg")
			sonidos["bg"] = pygame.mixer.Sound("sonidos/musicdefondo.ogg")
			sonidos["fuego"] = pygame.mixer.Sound("sonidos/fuego.ogg")
			sonidos["bonus"] = pygame.mixer.Sound("sonidos/bonus.ogg")
			sonidos["explosion"] = pygame.mixer.Sound("sonidos/explosion.ogg")
			sonidos["ladrillo"] = pygame.mixer.Sound("sonidos/ladrillo.ogg")
			sonidos["acero"] = pygame.mixer.Sound("sonidos/acero.ogg")

		mismo.imagen_vida_enemigo = sprites.subsurface(81*2, 57*2, 7*2, 7*2)
		mismo.imagen_vida_jugador = sprites.subsurface(89*2, 56*2, 7*2, 8*2)
		mismo.imagen_bandera = sprites.subsurface(64*2, 49*2, 16*2, 15*2)

		# esto se usa en la pantalla de introduccion
		mismo.jugador_image = pygame.transform.rotate(sprites.subsurface(0, 0, 13*2, 13*2), 270)

		# si es verdad, no se generarán nuevos enemigos durante este tiempo
		mismo.tiempoCongelado = False

		# cargar fuente personalizada
		mismo.font = pygame.font.Font("fonts/prcomienzo.ttf", 16)

		# pre-renderizar juego sobre texto
		mismo.acabaJuego = pygame.Surface((110, 35))
		mismo.acabaJuego.set_colorkey((55,55,55))
		mismo.acabaJuego.blit(mismo.font.render("HAS", False, (250, 20, 10)), [32, 0])
		mismo.acabaJuego.blit(mismo.font.render("PERDIDO", False, (250, 20, 10)), [0, 20])
		mismo.acabaJuego_y = 416+40

		# numero de jugadores. aquí se define el valor del menú preseleccionado
		mismo.nr_de_jugadores = 1

		del jugadores[:]
		del balas[:]
		del enemigos[:]
		del bonuses[:]


	def activacBonus(mismo, bonus, jugador):
		""" ejecutar poderes de bonificación """

		global reproducir_sonidos, sonidos

		if reproducir_sonidos:
			sonidos["bonus"].play()

		jugador.trophies["bonus"] += 1
		jugador.puntaje += 500

		if bonus.bonus == bonus.BONUS_GRANADA:
			for enemigo in enemigos:
				enemigo.explotar()
		elif bonus.bonus == bonus.BONUS_CASCO:
			mismo.escudoJugador(jugador, True, 10000)
		elif bonus.bonus == bonus.BONUS_PALA:
			mismo.nivel.constr_fortaleza(estatua, mismo.nivel.MATERIAL_ACERO)
			gtemporizador.add(10000, lambda :mismo.nivel.constr_fortaleza(estatua, mismo.nivel.MATERIAL_LADRILLO), 1)
		elif bonus.bonus == bonus.BONUS_ESTRELLA:
			jugador.superPoderes += 1
			if jugador.superPoderes == 2:
				jugador.max_balas_activas = 2
		elif bonus.bonus == bonus.BONUS_TANQUES:
			jugador.lives += 1
		elif bonus.bonus == bonus.BONUS_TIEMPO:
			mismo.alterEnemigCongelado(True)
			gtemporizador.add(10000, lambda :mismo.alterEnemigCongelado(False), 1)
		bonuses.remove(bonus)

		etiquetas.append(Etiqueta(bonus.rect.topleft, "500", 500))

	def escudoJugador(mismo, jugador, escudo = True, duration = None):
		""" agregar/quitar escudo
		jugador: jugador (no enemigo)
		escudo: true/false
		duracion: in ms. si no hay, no quite el escudo automaticamente
		"""
		jugador.blindado = escudo
		if escudo:
			jugador.temporiz_uuid_escudo = gtemporizador.add(100, lambda :jugador.alternar_imagen_escudo())
		else:
			gtemporizador.destruir(jugador.temporiz_uuid_escudo)

		if escudo and duration != None:
			gtemporizador.add(duration, lambda :mismo.escudoJugador(jugador, False), 1)


	def aparecerEnemigo(mismo):
		"""aparecer nuevos enemigos si es necesario
		Solo agrega enemigos si:
			- hay al menos uno en la cola
			- la capacidad del mapa no ha excedido su cuota
			- ahora no es tiempo congelado
		"""

		if len(enemigos) >= mismo.nivel.max_active_enemigos:
			return
		if len(mismo.nivel.enemigos_left) < 1 or mismo.tiempoCongelado:
			return
		enemigo = Enemigo(mismo.nivel, 1)

		enemigos.append(enemigo)


	def aparecerJugador(mismo, jugador, limpiar_puntaje = False):
		""" aparecer jugador """
		jugador.reiniciar()

		if limpiar_puntaje:
			jugador.trophies = {
				"bonus" : 0, "enemigo0" : 0, "enemigo1" : 0, "enemigo2" : 0, "enemigo3" : 0
			}

		mismo.escudoJugador(jugador, True, 4000)

	def juegoTerminado(mismo):
		""" termina el juego y vuelve al menú. """

		global reproducir_sonidos, sonidos

		print ("Game Over")
		if reproducir_sonidos:
			for sound in sonidos:
				sonidos[sound].stop()
			sonidos["fin"].play()

		mismo.acabaJuego_y = 416+40

		mismo.game_over = True
		gtemporizador.add(3000, lambda :mismo.mostrarPuntaje(), 1)

	def juegoTerminadopantalla(mismo):
		""" mostrar game over por  pantalla """

		global pantalla

		# detener el bucle principal del juego (si lo hay)
		mismo.corriendo = False

		pantalla.fill([0, 0, 0])

		mismo.dibujarEnLadrillo("game", [125, 140])
		mismo.dibujarEnLadrillo("over", [125, 220])
		pygame.display.flip()

		while 1:
			time_passed = mismo.clock.tick(50)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						mismo.mostrarMenu()
						return

	def mostrarMenu(mismo):
		""" mostrar el menu del juego
		Redibujar pantalla solo cuando se presiona la tecla arriba o abajo. Cuando enter está presionado,
		salir de esta pantalla y comenzar el juego con un número seleccionado de jugadores
		"""

		global pantalla

		# detener el bucle principal del juego (si lo hay)
		mismo.corriendo = False

		# borrar todos los temporizadores
		del gtemporizador.temporizadores[:]

		# establecer el escenario/nivel actual en 0
		mismo.escenario = 0

		mismo.animarIntroPantalla()

		main_loop = True
		while main_loop:
			time_passed = mismo.clock.tick(50)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						quit()
					elif event.key == pygame.K_UP:
						if mismo.nr_de_jugadores == 2:
							mismo.nr_de_jugadores = 1
							mismo.dibujarIntroPantalla()
					elif event.key == pygame.K_DOWN:
						if mismo.nr_de_jugadores == 1:
							mismo.nr_de_jugadores = 2
							mismo.dibujarIntroPantalla()
					elif event.key == pygame.K_RETURN:
						main_loop = False

		del jugadores[:]
		mismo.siguienteNivel()

	def recargarJugadores(mismo):
		""" jugadores iniciales
		Si los jugadores ya existen, simplemente reinícielos
		"""

		if len(jugadores) == 0:
			# primer jugador
			x = 8 * mismo.MATERIAL_TAMANIO + (mismo.MATERIAL_TAMANIO * 2 - 26) / 2
			y = 24 * mismo.MATERIAL_TAMANIO + (mismo.MATERIAL_TAMANIO * 2 - 26) / 2

			jugador = Jugador(
				mismo.nivel, 0, [x, y], mismo.DIR_UP, (0, 0, 13*2, 13*2)
			)
			jugadores.append(jugador)

			# segundo jugador
			if mismo.nr_de_jugadores == 2:
				x = 16 * mismo.MATERIAL_TAMANIO + (mismo.MATERIAL_TAMANIO * 2 - 26) / 2
				y = 24 * mismo.MATERIAL_TAMANIO + (mismo.MATERIAL_TAMANIO * 2 - 26) / 2
				jugador = Jugador(
					mismo.nivel, 0, [x, y], mismo.DIR_UP, (16*2, 0, 13*2, 13*2)
				)
				jugador.controles = [102, 119, 100, 115, 97]
				jugadores.append(jugador)

		for jugador in jugadores:
			jugador.nivel = mismo.nivel
			mismo.aparecerJugador(jugador, True)

	def mostrarPuntaje(mismo):
		""" mostrar puntajes de nivel """

		global pantalla, reproducir_sonidos, sonidos

		# detener el bucle principal del juego (si lo hay)
		mismo.corriendo = False

		# borrar todos los temporizadores
		del gtemporizador.temporizadores[:]

		if reproducir_sonidos:
			for sound in sonidos:
				sonidos[sound].stop()

		puntajeAlto = mismo.cargarPuntajeAlto()

		# actualizar el puntaje alto si es necesario
		if jugadores[0].puntaje > puntajeAlto:
			puntajeAlto = jugadores[0].puntaje
			mismo.guardarPuntajeAlto(puntajeAlto)
		if mismo.nr_de_jugadores == 2 and jugadores[1].puntaje > puntajeAlto:
			puntajeAlto = jugadores[1].puntaje
			mismo.guardarPuntajeAlto(puntajeAlto)

		img_tanques = [
			sprites.subsurface(32*2, 0, 13*2, 15*2),
			sprites.subsurface(48*2, 0, 13*2, 15*2),
			sprites.subsurface(64*2, 0, 13*2, 15*2),
			sprites.subsurface(80*2, 0, 13*2, 15*2)
		]

		img_arrows = [
			sprites.subsurface(81*2, 48*2, 7*2, 7*2),
			sprites.subsurface(88*2, 48*2, 7*2, 7*2)
		]

		pantalla.fill([0, 0, 0])

		# colores																				
		negro = pygame.Color("black")
		blanco = pygame.Color("white")
		celeste = pygame.Color(10, 130, 200)

		pantalla.blit(mismo.font.render("MEJOR PUNTAJE", False, celeste), [100, 35])
		pantalla.blit(mismo.font.render(str(puntajeAlto), False, blanco), [320, 35])

		pantalla.blit(mismo.font.render("NIVEL"+str(mismo.escenario).rjust(3), False, blanco), [170, 65])

		pantalla.blit(mismo.font.render("JUGADOR 1", False, celeste), [25, 95])

		#jugador 1 puntaje global
		pantalla.blit(mismo.font.render(str(jugadores[0].puntaje).rjust(8), False, blanco), [25, 125])

		if mismo.nr_de_jugadores == 2:
			pantalla.blit(mismo.font.render("JUGADOR 2", False, celeste), [310, 95])

			#jugador 2 puntaje global
			pantalla.blit(mismo.font.render(str(jugadores[1].puntaje).rjust(8), False, blanco), [325, 125])

		# tanques y flechas
		for i in range(4):
			pantalla.blit(img_tanques[i], [226, 160+(i*45)])
			pantalla.blit(img_arrows[0], [206, 168+(i*45)])
			if mismo.nr_de_jugadores == 2:
				pantalla.blit(img_arrows[1], [258, 168+(i*45)])

		pantalla.blit(mismo.font.render("TOTAL", False, blanco), [70, 335])

		# subrayado total
		pygame.draw.line(pantalla, blanco, [170, 330], [307, 330], 4)

		pygame.display.flip()

		mismo.clock.tick(2)

		interval = 5

		# puntos y muertes
		for i in range(4):

			# total tanques especificado
			tanques = jugadores[0].trophies["enemigo"+str(i)]

			for n in range(tanques+1):
				if n > 0 and reproducir_sonidos:
					sonidos["puntaje"].play()

				# borrar texto anterior
				pantalla.blit(mismo.font.render(str(n-1).rjust(2), False, negro), [170, 168+(i*45)])
				# imprimir nuevo numero de enemigos
				pantalla.blit(mismo.font.render(str(n).rjust(2), False, blanco), [170, 168+(i*45)])
				# borrar texto anterior
				pantalla.blit(mismo.font.render(str((n-1) * (i+1) * 100).rjust(4)+" PTS", False, negro), [25, 168+(i*45)])
				# imprimir nuevos puntos totales por enemigo
				pantalla.blit(mismo.font.render(str(n * (i+1) * 100).rjust(4)+" PTS", False, blanco), [25, 168+(i*45)])
				pygame.display.flip()
				mismo.clock.tick(interval)

			if mismo.nr_de_jugadores == 2:
				tanques = jugadores[1].trophies["enemigo"+str(i)]

				for n in range(tanques+1):

					if n > 0 and reproducir_sonidos:
						sonidos["puntaje"].play()

					pantalla.blit(mismo.font.render(str(n-1).rjust(2), False, negro), [277, 168+(i*45)])
					pantalla.blit(mismo.font.render(str(n).rjust(2), False, blanco), [277, 168+(i*45)])

					pantalla.blit(mismo.font.render(str((n-1) * (i+1) * 100).rjust(4)+" PTS", False, negro), [325, 168+(i*45)])
					pantalla.blit(mismo.font.render(str(n * (i+1) * 100).rjust(4)+" PTS", False, blanco), [325, 168+(i*45)])

					pygame.display.flip()
					mismo.clock.tick(interval)

			mismo.clock.tick(interval)

		# tanques totales
		tanques = sum([i for i in jugadores[0].trophies.values()]) - jugadores[0].trophies["bonus"]
		pantalla.blit(mismo.font.render(str(tanques).rjust(2), False, blanco), [170, 335])
		if mismo.nr_de_jugadores == 2:
			tanques = sum([i for i in jugadores[1].trophies.values()]) - jugadores[1].trophies["bonus"]
			pantalla.blit(mismo.font.render(str(tanques).rjust(2), False, blanco), [277, 335])

		pygame.display.flip()

		# no hacer nada durante 2 segundos
		mismo.clock.tick(1)
		mismo.clock.tick(1)

		if mismo.game_over:
			mismo.juegoTerminadopantalla()
		else:
			mismo.siguienteNivel()


	def dibujar(mismo):
		global pantalla, estatua

		pantalla.fill([0, 0, 0])

		mismo.nivel.dibujar(pantalla, [mismo.nivel.BALDOSA_VACIA, mismo.nivel.MATERIAL_LADRILLO, mismo.nivel.MATERIAL_ACERO, mismo.nivel.MATERIAL_CONGELADO, mismo.nivel.MATERIAL_AGUA])

		estatua.dibujar(pantalla)

		for enemigo in enemigos:
			enemigo.dibujar(pantalla)

		for etiqueta in etiquetas:
			etiqueta.dibujar(pantalla)

		for jugador in jugadores:
			jugador.dibujar(pantalla)

		for bala in balas:
			bala.dibujar(pantalla)

		for bonus in bonuses:
			bonus.dibujar(pantalla)

		mismo.nivel.dibujar(pantalla, [mismo.nivel.MATERIAL_HIERBA])

		if mismo.game_over:
			if mismo.acabaJuego_y > 188:
				mismo.acabaJuego_y -= 4
			pantalla.blit(mismo.acabaJuego, [152, mismo.acabaJuego_y]) 

		mismo.dibujarBarraLateral()

		pygame.display.flip()

	def dibujarBarraLateral(mismo):

		global pantalla

		x = 416
		y = 0
		pantalla.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))

		xpos = x + 16
		ypos = y + 16

		# dibujar vidas de enemigos
		for n in range(len(mismo.nivel.enemigos_left) + len(enemigos)):
			pantalla.blit(mismo.imagen_vida_enemigo, [xpos, ypos])
			if n % 2 == 1:
				xpos = x + 16
				ypos+= 17
			else:
				xpos += 17

		# la vida de los jugadores
		if pygame.font.get_init():
			text_color = pygame.Color('black')
			for n in range(len(jugadores)):
				if n == 0:
					pantalla.blit(mismo.font.render(str(n+1)+"P", False, text_color), [x+16, y+200])
					pantalla.blit(mismo.font.render(str(jugadores[n].lives), False, text_color), [x+31, y+215])
					pantalla.blit(mismo.imagen_vida_jugador, [x+17, y+215])
				else:
					pantalla.blit(mismo.font.render(str(n+1)+"P", False, text_color), [x+16, y+240])
					pantalla.blit(mismo.font.render(str(jugadores[n].lives), False, text_color), [x+31, y+255])
					pantalla.blit(mismo.imagen_vida_jugador, [x+17, y+255])

			pantalla.blit(mismo.imagen_bandera, [x+17, y+280])
			pantalla.blit(mismo.font.render(str(mismo.escenario), False, text_color), [x+17, y+312])


	def dibujarIntroPantalla(mismo, put_on_surface = True):
		""" Dibujar intro (menu) pantalla
		@param boolean poner en la superficie Si es true, voltear la pantalla después de dibujar
		@return None
		"""

		global pantalla

		pantalla.fill([0, 0, 0])

		if pygame.font.get_init():

			puntajeAlto = mismo.cargarPuntajeAlto()

			pantalla.blit(mismo.font.render("MEJOR PUNTAJE-"+str(puntajeAlto), True, pygame.Color('white')), [80, 35])

			pantalla.blit(mismo.font.render("1 JUGADOR", True, pygame.Color('white')), [165, 250])
			pantalla.blit(mismo.font.render("2 JUGADORES", True, pygame.Color('white')), [165, 275])

			pantalla.blit(mismo.font.render("(C) 2022 UTN.", True, pygame.Color('white')), [135, 350])
			pantalla.blit(mismo.font.render("ALL RIGHTS RESERVED", True, pygame.Color('white')), [85, 380])


		if mismo.nr_de_jugadores == 1:
			pantalla.blit(mismo.jugador_image, [125, 245])
		elif mismo.nr_de_jugadores == 2:
			pantalla.blit(mismo.jugador_image, [125, 270])

		mismo.dibujarEnLadrillo("war", [135, 80])									
		mismo.dibujarEnLadrillo("tanks", [79, 160])

		if put_on_surface:
			pygame.display.flip()

	def animarIntroPantalla(mismo):
		""" voltear la pantalla después de dibujar
		si la tecla Enter está presionada, finaliza la animación inmediatamente
		@return None
		"""

		global pantalla

		mismo.dibujarIntroPantalla(False)
		pantalla_cp = pantalla.copy()

		pantalla.fill([0, 0, 0])

		y = 416
		while (y > 0):
			time_passed = mismo.clock.tick(50)
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						y = 0
						break

			pantalla.blit(pantalla_cp, [0, y])
			pygame.display.flip()
			y -= 5

		pantalla.blit(pantalla_cp, [0, 0])
		pygame.display.flip()


	def chunks(mismo, l, n):
		""" Dividir cadena de texto en fragmentos de tamaño especificado
		@param string l cadena de entrada
		@param int n Size (número de caracteres) de cada fragmento
		@return list
		"""
		return [l[i:i+n] for i in range(0, len(l), n)]

	def dibujarEnLadrillo(mismo, text, pos):
		""" Escriba el texto especificado en "fuente ladrillo"
		Solo están disponibles aquellas letras que forman las palabras "Battle City" y "Game Over"
		Tanto las minúsculas como las mayúsculas son entradas validas, pero la salida siempre es mayúscula
		Cada letra consta de ladrillos de 7x7 que se convierte en una cadena de 49 caracteres de 1 y 0 que,
		a su vez, se convierte en hexadecimal para ahorrar algunos bytes.
		@return None
		"""

		global pantalla

		ladrillos = sprites.subsurface(56*2, 64*2, 8*2, 8*2)
		ladrillo1 = ladrillos.subsurface((0, 0, 8, 8))
		ladrillo2 = ladrillos.subsurface((8, 0, 8, 8))
		ladrillo3 = ladrillos.subsurface((8, 8, 8, 8))
		ladrillo4 = ladrillos.subsurface((0, 8, 8, 8))

		alfabeto = {
			"a" : "0071b63c7ff1e3",
            "b" : "01fb1e3fd8f1fe",
            "c" : "00799e0c18199e",
            "e" : "01fb060f98307e",
            "g" : "007d860cf8d99f",
            "i" : "01f8c183060c7e",
            "k" : "019f77cf1f3767",
            "l" : "0183060c18307e",
            "m" : "018fbffffaf1e3",
            "n" : "018f9fbffbf3e3",
            "o" : "00fb1e3c78f1be",
            "r" : "01fb1e3cff3767",
            "s" : "00fb1e07c0f1be",
            "t" : "01f8c183060c18",
            "v" : "018f1e3eef8e08",
            "w" : "018f1e3d7ffbe3",
            "y" : "019b3667860c18"
		}

		abs_x, abs_y = pos

		for letter in text.lower():

			binstr = ""
			for h in mismo.chunks(alfabeto[letter], 2):
				binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
			binstr = binstr[7:]

			x, y = 0, 0
			letter_w = 0
			surf_letter = pygame.Surface((56, 56))
			for j, row in enumerate(mismo.chunks(binstr, 7)):
				for i, bit in enumerate(row):
					if bit == "1":
						if i%2 == 0 and j%2 == 0:
							surf_letter.blit(ladrillo1, [x, y])
						elif i%2 == 1 and j%2 == 0:
							surf_letter.blit(ladrillo2, [x, y])
						elif i%2 == 1 and j%2 == 1:
							surf_letter.blit(ladrillo3, [x, y])
						elif i%2 == 0 and j%2 == 1:
							surf_letter.blit(ladrillo4, [x, y])
						if x > letter_w:
							letter_w = x
					x += 8
				x = 0
				y += 8
			pantalla.blit(surf_letter, [abs_x, abs_y])
			abs_x += letter_w + 16

	def alterEnemigCongelado(mismo, freeze = True):
		""" congelas/descongelar todos los  enemigos """

		for enemigo in enemigos:
			enemigo.pausado = freeze
		mismo.tiempoCongelado = freeze


	def cargarPuntajeAlto(mismo):
		""" cargar puntaje Alto
		Versión realmente primitiva =] Si por alguna razón no se puede cargar puntaje Alto, devuelve 20000
		@return int
		"""
		filename = ".puntajeAlto"
		if (not os.path.isfile(filename)):
			return 20000

		f = open(filename, "r")
		puntajeAlto = int(f.read())

		if puntajeAlto > 19999 and puntajeAlto < 1000000:
			return puntajeAlto
		else:
			print ("tramposo =[")
			return 20000

	def guardarPuntajeAlto(mismo, puntajeAlto):
		""" guardar puntajeAlto
		@return boolean
		"""
		try:
			f = open(".puntajeAlto", "w")
		except:
			print ("No se puede guardar la puntuación")
			return False
		f.write(str(puntajeAlto))
		f.close()
		return True


	def finishnivel(mismo):
		""" Termina el nivel actual
		Muestra los puntajes ganados y avanza al siguiente escenario
		"""

		global reproducir_sonidos, sonidos

		if reproducir_sonidos:
			sonidos["bg"].stop()

		mismo.active = False
		gtemporizador.add(3000, lambda :mismo.mostrarPuntaje(), 1)

		print ("escenario " + str(mismo.escenario)+" completado")

	def siguienteNivel(mismo):
		""" comienza el siguiente nivel """

		global estatua, reproducir_sonidos, sonidos

		del balas[:]
		del enemigos[:]
		del bonuses[:]
		estatua.rebuild()
		del gtemporizador.temporizadores[:]

		# cargar nivel
		mismo.escenario += 1
		mismo.nivel = Nivel(estatua, mismo.escenario)
		mismo.tiempoCongelado = False

		# establecer el número de enemigos por tipos (básico, rápido, poder, armadura) según el nivel
		niveles_enemigos = (
			(18,2,0,0), (14,4,0,2), (14,4,0,2), (2,5,10,3), (8,5,5,2),
			(9,2,7,2), (7,4,6,3), (7,4,7,2), (6,4,7,3), (12,2,4,2),
			(5,5,4,6), (0,6,8,6), (0,8,8,4), (0,4,10,6), (0,2,10,8),
			(16,2,0,2), (8,2,8,2), (2,8,6,4), (4,4,4,8), (2,8,2,8),
			(6,2,8,4), (6,8,2,4), (0,10,4,6), (10,4,4,2), (0,8,2,10),
			(4,6,4,6), (2,8,2,8), (15,2,2,1), (0,4,10,6), (4,8,4,4),
			(3,8,3,6), (6,4,2,8), (4,4,4,8), (0,10,4,6), (0,6,4,10)
		)

		if mismo.escenario <= 35:
			enemigos_l = niveles_enemigos[mismo.escenario - 1]
		else:
			enemigos_l = niveles_enemigos[34]

		mismo.nivel.enemigos_left = [0]*enemigos_l[0] + [1]*enemigos_l[1] + [2]*enemigos_l[2] + [3]*enemigos_l[3]
		random.shuffle(mismo.nivel.enemigos_left)

		if reproducir_sonidos:
			sonidos["comienzo"].play()
			gtemporizador.add(4330, lambda :sonidos["bg"].play(-1), 1)

		mismo.recargarJugadores()

		gtemporizador.add(3000, lambda :mismo.aparecerEnemigo())

		# si es True, animación comienzo "game over"
		mismo.game_over = False

		# si es False, el juego terminará con/o el asunto "game over"
		mismo.corriendo = True

		# si es False, Los jugadores no podrán hacer nada.
		mismo.active = True

		mismo.dibujar()

		while mismo.corriendo:

			time_passed = mismo.clock.tick(50)

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					pass
				elif event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN and not mismo.game_over and mismo.active:

					if event.key == pygame.K_q:
						quit()
					# alternar sonidos
					elif event.key == pygame.K_m:
						reproducir_sonidos = not reproducir_sonidos
						if not reproducir_sonidos:
							pygame.mixer.stop()
						else:
							sonidos["bg"].play(-1)

					for jugador in jugadores:
						if jugador.estado == jugador.ESTADO_VIDO:
							try:
								index = jugador.controles.index(event.key)
							except:
								pass
							else:
								if index == 0:
									if jugador.fuego() and reproducir_sonidos:
										sonidos["fuego"].play()
								elif index == 1:
									jugador.presionado[0] = True
								elif index == 2:
									jugador.presionado[1] = True
								elif index == 3:
									jugador.presionado[2] = True
								elif index == 4:
									jugador.presionado[3] = True
				elif event.type == pygame.KEYUP and not mismo.game_over and mismo.active:
					for jugador in jugadores:
						if jugador.estado == jugador.ESTADO_VIDO:
							try:
								index = jugador.controles.index(event.key)
							except:
								pass
							else:
								if index == 1:
									jugador.presionado[0] = False
								elif index == 2:
									jugador.presionado[1] = False
								elif index == 3:
									jugador.presionado[2] = False
								elif index == 4:
									jugador.presionado[3] = False

			for jugador in jugadores:
				if jugador.estado == jugador.ESTADO_VIDO and not mismo.game_over and mismo.active:
					if jugador.presionado[0] == True:
						jugador.move(mismo.DIR_UP);
					elif jugador.presionado[1] == True:
						jugador.move(mismo.DIR_RIGHT);
					elif jugador.presionado[2] == True:
						jugador.move(mismo.DIR_DOWN);
					elif jugador.presionado[3] == True:
						jugador.move(mismo.DIR_LEFT);
				jugador.actualizar(time_passed)

			for enemigo in enemigos:
				if enemigo.estado == enemigo.ESTADO_MUERTO and not mismo.game_over and mismo.active:
					enemigos.remove(enemigo)
					if len(mismo.nivel.enemigos_left) == 0 and len(enemigos) == 0:
						mismo.finishnivel()
				else:
					enemigo.actualizar(time_passed)

			if not mismo.game_over and mismo.active:
				for jugador in jugadores:
					if jugador.estado == jugador.ESTADO_VIDO:
						if jugador.bonus != None and jugador.lado == jugador.LADO_JUGADOR:
							mismo.activacBonus(bonus, jugador)
							jugador.bonus = None
					elif jugador.estado == jugador.ESTADO_MUERTO:
						mismo.superPoderes = 0
						jugador.lives -= 1
						if jugador.lives > 0:
							mismo.aparecerJugador(jugador)
						else:
							mismo.juegoTerminado()

			for bala in balas:
				if bala.estado == bala.ESTADO_REMOVIDO:
					balas.remove(bala)
				else:
					bala.actualizar(estatua)

			for bonus in bonuses:
				if bonus.active == False:
					bonuses.remove(bonus)

			for etiqueta in etiquetas:
				if not etiqueta.active:
					etiquetas.remove(etiqueta)

			if not mismo.game_over:
				if not estatua.active:
					mismo.juegoTerminado()

			gtemporizador.actualizar(time_passed)

			mismo.dibujar()

if __name__ == "__main__":

	reproducir_sonidos = True

	game = Juego()
	estatua = Estatua()
	game.mostrarMenu()