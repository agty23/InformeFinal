import math
import random
import sys
import pygame

class Particula:
    # Definir el radio de búsqueda como una constante
    RADIO_BUSQUEDA = 100  # Radio de búsqueda en píxeles

    def __init__(self, id, x, y, pasos_restantes, frecuencia_movimiento=1000, radio_busqueda=RADIO_BUSQUEDA):
        self.id = id  # ID único para cada partícula
        self.x = x
        self.y = y
        self.color = (0, 0, 255)  # Azul
        self.pasos_restantes = pasos_restantes
        self.ha_comido = False
        self.comidas_realizadas = 0  # Conteo de veces que ha comido
        self.tam_paso = 20  # Tamaño fijo del paso
        self.ultimo_movimiento = pygame.time.get_ticks()  # Tiempo acumulado desde el último movimiento
        self.frecuencia_movimiento = frecuencia_movimiento  # Milisegundos entre movimientos, ajustable
        self.historial = [(x, y)]
        self.max_historial = 10
        self.se_ha_movido = False  # Bandera para saber si se ha movido
        self.radio_busqueda = radio_busqueda  # Radio de búsqueda de comida (usa la constante por defecto)

    def mover(self, caja_verde, comidas, particulas):
        if self.pasos_restantes <= 0:
            return

        # Filtrar comidas dentro del radio de búsqueda
        comidas_en_rango = [
            comida for comida in comidas
            if math.dist((self.x, self.y), (comida.x, comida.y)) <= self.radio_busqueda
        ]

        if comidas_en_rango:  # Si hay comida en el radio de búsqueda
            # Encontrar la comida más cercana
            comida_mas_cercana = min(comidas_en_rango,
                                     key=lambda comida: math.dist((self.x, self.y), (comida.x, comida.y)))
            distancia = math.dist((self.x, self.y), (comida_mas_cercana.x, comida_mas_cercana.y))

            # Si está muy cerca, directamente la "come"
            if distancia < 1:
                self.x, self.y = comida_mas_cercana.x, comida_mas_cercana.y
                self.ha_comido = True
                self.comidas_realizadas += 1
                if self.comidas_realizadas == 2:
                    self.frecuencia_movimiento = max(200, self.frecuencia_movimiento // 2)
                return

            # Calcular la dirección hacia la comida más cercana (solo en X o Y)
            dx = comida_mas_cercana.x - self.x
            dy = comida_mas_cercana.y - self.y

            # Determinar el tamaño del paso ajustado
            paso_ajustado = min(self.tam_paso, distancia)  # No mover más allá de la comida

            # Mover en la dirección que más reduzca la distancia
            if abs(dx) > abs(dy):  # Mover en el eje X
                direccion_x = paso_ajustado if dx > 0 else -paso_ajustado
                direccion_y = 0
            else:  # Mover en el eje Y
                direccion_x = 0
                direccion_y = paso_ajustado if dy > 0 else -paso_ajustado

            # Calcular la nueva posición
            nueva_x = self.x + direccion_x
            nueva_y = self.y + direccion_y

        else:  # Si no hay comida en el radio de búsqueda, moverse aleatoriamente
            # Definir posibles direcciones aleatorias (solo arriba, abajo, izquierda, derecha)
            posibles_direcciones = [
                (self.tam_paso, 0),  # Derecha
                (-self.tam_paso, 0),  # Izquierda
                (0, self.tam_paso),  # Abajo
                (0, -self.tam_paso)  # Arriba
            ]
            direccion_x, direccion_y = random.choice(posibles_direcciones)

            # Calcular la nueva posición
            nueva_x = self.x + direccion_x
            nueva_y = self.y + direccion_y

        # Verificar colisión con los límites
        if (caja_verde["x_min"] <= nueva_x <= caja_verde["x_max"] and
                caja_verde["y_min"] <= nueva_y <= caja_verde["y_max"]):
            # Verificar colisión con otras partículas
            colision = any(
                otra.id != self.id and math.dist((nueva_x, nueva_y), (otra.x, otra.y)) < 10
                for otra in particulas
            )
            if not colision:
                # Si no hay colisión, mover la partícula
                self.x = nueva_x
                self.y = nueva_y

        # Actualizar el historial de posiciones
        self.historial.append((self.x, self.y))
        if len(self.historial) > self.max_historial:
            self.historial.pop(0)

        if (caja_verde["x_min"] <= nueva_x <= caja_verde["x_max"] and
                caja_verde["y_min"] <= nueva_y <= caja_verde["y_max"]):
            self.x = nueva_x
            self.y = nueva_y
            self.historial.append((self.x, self.y))
            if len(self.historial) > self.max_historial:
                self.historial.pop(0)
            self.pasos_restantes -= 1  # Reducir pasos restantes

    def esta_cerca(self, comida):
        distancia = math.sqrt((self.x - comida.x) ** 2 + (self.y - comida.y) ** 2)
        return distancia < 10


class Comida:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (255, 0, 0)  # Rojo


def obtener_entrada_usuario(mensaje, tipo=int, minimo=None, maximo=None):
    while True:
        try:
            entrada = tipo(input(mensaje))
            if minimo is not None and entrada < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and entrada > maximo:
                print(f"El valor debe ser menor o igual a {maximo}.")
                continue
            return entrada
        except ValueError:
            print(f"Por favor, ingresa un valor válido de tipo numérico positivo.")


class SimulacionCaminarAleatorio:
    def __init__(self, ancho=550, alto=550):

        self.color_fondo = (255, 255, 255)
        self.caja_verde = {
            "x_min": 50,
            "x_max": ancho - 50,
            "y_min": 50,
            "y_max": alto - 50,
        }

        max_particulas = 30
        max_comida = 30
        max_ciclos = 20
        self.pasos_generales = obtener_entrada_usuario(
            f"Ingrese el número de pasos generales para las partículas (1-20): ", int, 1, 20
        )
        self.num_particulas = obtener_entrada_usuario(
            f"Ingresa el número de partículas (1 - {max_particulas}): ", int, 1, max_particulas
        )
        self.num_comida = obtener_entrada_usuario(
            f"Ingresa el número de comida (1 - {max_comida}): ", int, 1, max_comida
        )
        self.max_ciclos = obtener_entrada_usuario(
            f"Ingresa el número máximo de ciclos (1 - {max_ciclos}): ", int, 1, max_ciclos
        )
        pygame.init()
        # Cargar imágenes
        self.img_entorno = pygame.image.load('img/entorno.jpeg')
        self.img_leon = pygame.image.load('img/leon.png')
        self.img_cebra = pygame.image.load('img/cebra.png')


        self.ancho = ancho
        self.alto = alto
        self.pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption("Caminata Aleatoria con Comida")

        self.ciclo_actual = 1

        self.ejecutando = True
        self.pausado = False
        self.mostrar_rastros = True
        self.simulacion_iniciada = False

        self.particulas = self.inicializar_particulas()
        self.comidas = self.inicializar_comida()

        self.fuente = pygame.font.Font(None, 36)
        self.fuente_pequena = pygame.font.Font(None, 24)
        self.fuente_pequena_titulo = pygame.font.Font(None, 30)

        # Agregar botón "Iniciar"
        self.boton_iniciar = pygame.Rect(self.ancho // 2 - 75, self.alto // 2, 150, 50)
        self.mostrar_boton = True  # Nueva bandera

    def posicion_en_limite(self):
        borde = random.choice(["superior", "inferior", "izquierdo", "derecho"])
        if borde == "superior":
            return (
                random.uniform(self.caja_verde["x_min"], self.caja_verde["x_max"]),
                self.caja_verde["y_min"]
            )
        elif borde == "inferior":
            return (
                random.uniform(self.caja_verde["x_min"], self.caja_verde["x_max"]),
                self.caja_verde["y_max"]
            )
        elif borde == "izquierdo":
            return (
                self.caja_verde["x_min"],
                random.uniform(self.caja_verde["y_min"], self.caja_verde["y_max"])
            )
        else:
            return (
                self.caja_verde["x_max"],
                random.uniform(self.caja_verde["y_min"], self.caja_verde["y_max"])
            )

    def inicializar_particulas(self):
        particulas = []
        posiciones_ocupadas = []  # Lista para almacenar posiciones ocupadas
        distancia_minima = 20  # Ajusta esto según el tamaño de las partículas

        for i in range(self.num_particulas):
            intentos = 0
            max_intentos = 100  # Evitar bucle infinito si no hay espacio suficiente
            while intentos < max_intentos:
                x, y = self.posicion_en_limite()
                if all(math.sqrt((x - px) ** 2 + (y - py) ** 2) >= distancia_minima for px, py in posiciones_ocupadas):
                    posiciones_ocupadas.append((x, y))  # Agregar la nueva posición válida
                    break
                intentos += 1

            # Si se superó el límite de intentos, forzar una posición aleatoria
            if intentos == max_intentos:
                print(
                    f"Advertencia: No se encontró una posición válida para la partícula {i + 1}. Ubicándola sin restricciones.")
                x, y = random.uniform(self.caja_verde["x_min"], self.caja_verde["x_max"]), random.uniform(
                    self.caja_verde["y_min"], self.caja_verde["y_max"])
                posiciones_ocupadas.append((x, y))

            particulas.append(Particula(i + 1, x, y, self.pasos_generales))

        return particulas

    def inicializar_comida(self):
        comidas = []
        for _ in range(self.num_comida):
            x = random.uniform(self.caja_verde["x_min"], self.caja_verde["x_max"])
            y = random.uniform(self.caja_verde["y_min"], self.caja_verde["y_max"])
            comidas.append(Comida(x, y))
        return comidas

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.pausado = not self.pausado
                elif evento.key == pygame.K_r:
                    self.reiniciar_simulacion()
                elif evento.key == pygame.K_t:
                    self.mostrar_rastros = not self.mostrar_rastros
                elif evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if self.boton_iniciar.collidepoint(evento.pos):
                    self.simulacion_iniciada = True
                    self.mostrar_boton = False  # Ocultar el botón después del clic

    def reiniciar_simulacion(self):
        self.particulas = self.inicializar_particulas()
        self.ciclo_actual = 1
        self.simulacion_iniciada = False

    def actualizar(self, tiempo_actual):
        if self.pausado or not self.simulacion_iniciada:
            return

        particulas_sobrevivientes = []
        for particula in self.particulas:
            if particula.pasos_restantes > 0 or particula.comidas_realizadas > 0:  # Si ha comido al menos una vez
                if tiempo_actual - particula.ultimo_movimiento >= particula.frecuencia_movimiento:
                    particula.mover(self.caja_verde, self.comidas, self.particulas)  # Pasar la lista de comidas
                    particula.ultimo_movimiento = tiempo_actual  # Actualizar el último movimiento

                    # Comprobar si la partícula está cerca de la comida
                    for comida in self.comidas[:]:
                        if particula.esta_cerca(comida):
                            self.comidas.remove(comida)
                            particula.ha_comido = True
                            particula.comidas_realizadas += 1
                            print(f"Partícula {particula.id} ha comido {particula.comidas_realizadas} veces.")

                            # Reducir la frecuencia de movimiento si ha comido 2 veces
                            if particula.comidas_realizadas == 2:
                                particula.frecuencia_movimiento = max(200, particula.frecuencia_movimiento // 2)
                                print(f"Partícula {particula.id} ha reducido su frecuencia de movimiento.")

                # Incluir las partículas que han comido al menos una vez o que aún tienen pasos restantes
                if particula.comidas_realizadas > 0 or particula.pasos_restantes > 0:
                    particulas_sobrevivientes.append(particula)

        # Verificar si el ciclo ha terminado
        if not any(p.pasos_restantes > 0 for p in self.particulas):
            if particulas_sobrevivientes and self.ciclo_actual < self.max_ciclos:
                self.ciclo_actual += 1

                # Nueva lógica para evitar posiciones demasiado cercanas en cada ciclo
                nuevas_particulas = []
                posiciones_ocupadas = set()
                distancia_minima = 10  # Ajusta según necesidad

                for p in particulas_sobrevivientes:
                    while True:
                        x, y = self.posicion_en_limite()
                        if all(math.sqrt((x - px) ** 2 + (y - py) ** 2) > distancia_minima for px, py in
                               posiciones_ocupadas):
                            posiciones_ocupadas.add((x, y))
                            break

                    nuevas_particulas.append(
                        Particula(p.id, x, y, self.pasos_generales, frecuencia_movimiento=p.frecuencia_movimiento))

                self.particulas = nuevas_particulas
            else:
                self.mostrar_mensaje_fin_juego()
                self.simulacion_iniciada = False

    def mostrar_mensaje_fin_juego(self):
        self.pantalla.fill(self.color_fondo)
        texto = f"No hay más partículas, quedaron {self.max_ciclos - self.ciclo_actual} ciclos restantes."
        superficie_texto = self.fuente_pequena_titulo.render(texto, True, (0, 0, 0))
        rect_texto = superficie_texto.get_rect(center=(self.ancho // 2, self.alto // 2))
        self.pantalla.blit(superficie_texto, rect_texto)
        pygame.display.flip()
        pygame.time.delay(8000)
        self.ejecutando = False


    def dibujar(self):
        self.pantalla.fill(self.color_fondo)

        # Dibujar fondo
        if self.img_entorno:
            self.pantalla.blit(self.img_entorno, (0, 0))

        # Dibujar caja verde (zona de movimiento)
        pygame.draw.rect(
            self.pantalla, (0, 255, 0),
            (self.caja_verde["x_min"], self.caja_verde["y_min"],
            self.caja_verde["x_max"] - self.caja_verde["x_min"],
            self.caja_verde["y_max"] - self.caja_verde["y_min"]),
            3
        )

        # Dibujar comida
        for comida in self.comidas:
            imagen_cebra = pygame.transform.scale(self.img_cebra, (20, 20))
            self.pantalla.blit(imagen_cebra, (int(comida.x) - 10, int(comida.y) - 10))

        # Dibujar partículas con su radio de búsqueda
        for particula in self.particulas:
            # Dibujar el radio de búsqueda (círculo azul con transparencia)
            superficie_transparente = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            pygame.draw.circle(
                superficie_transparente,
                (255, 255, 255, 50),  # Azul con 50 de transparencia
                (int(particula.x), int(particula.y)),
                particula.radio_busqueda, 3
            )
            self.pantalla.blit(superficie_transparente, (0, 0))

            # Dibujar la partícula
            imagen = pygame.transform.scale(self.img_leon, (20, 20))
            self.pantalla.blit(imagen, (int(particula.x) - 10, int(particula.y) - 10))

            # Mostrar el ID de la partícula
            texto_id = self.fuente_pequena.render(str(particula.id), True, (0, 0, 0))
            self.pantalla.blit(texto_id, (int(particula.x) + 5, int(particula.y) + 5))

        # Dibujar información del ciclo
        texto_info = f"Ciclo: {self.ciclo_actual}/{self.max_ciclos}"
        superficie_texto = self.fuente.render(texto_info, True, (255, 255, 255))
        self.pantalla.blit(superficie_texto, (10, 10))
        # Dibujar botón Iniciar
        if self.mostrar_boton:
            pygame.draw.rect(self.pantalla, (0, 0, 255), self.boton_iniciar)
            texto_boton = self.fuente.render("Iniciar", True, (255, 255, 255))
            self.pantalla.blit(texto_boton, (self.ancho // 2 - 40, self.alto // 2 + 10))
        pygame.display.flip()



    def correr(self):
        reloj = pygame.time.Clock()

        while self.ejecutando:
            tiempo_actual = pygame.time.get_ticks()  # Tiempo actual en milisegundos
            self.manejar_eventos()
            self.actualizar(tiempo_actual)  # Pasa el tiempo actual a la actualización
            self.dibujar()
            reloj.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    simulacion = SimulacionCaminarAleatorio()
    simulacion.correr()