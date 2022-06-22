import uuid

class Temporizador(object):
	def __init__(mismo):
		mismo.temporizadores = []

	def add(mismo, interval, f, repeat = -1):
		options = {
			"interval"	: interval,
			"callback"	: f,
			"repeat"		: repeat,
			"times"			: 0,
			"time"			: 0,
			"uuid"			: uuid.uuid4()
		}
		mismo.temporizadores.append(options)

		return options["uuid"]

	def destruir(mismo, uuid_nr):
		for temporizador in mismo.temporizadores:
			if temporizador["uuid"] == uuid_nr:
				mismo.temporizadores.remove(temporizador)
				return

	def actualizar(mismo, time_passed):
		for temporizador in mismo.temporizadores:
			temporizador["time"] += time_passed
			if temporizador["time"] > temporizador["interval"]:
				temporizador["time"] -= temporizador["interval"]
				temporizador["times"] += 1
				if temporizador["repeat"] > -1 and temporizador["times"] == temporizador["repeat"]:
					mismo.temporizadores.remove(temporizador)
				try:
					temporizador["callback"]()
				except:
					try:
						mismo.temporizadores.remove(temporizador)
					except:
            pass