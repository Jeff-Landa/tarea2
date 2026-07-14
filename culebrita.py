# CONSIDERACIÓN: En Windows debes instalar la librería primero con: pip install windows-curses
import curses
import random
import time

def inicializar_tablero(ancho, alto, obstaculos):
    tablero = []
    for f in range(alto):
        fila = []
        for c in range(ancho):
            if f == 0 or f == alto - 1 or c == 0 or c == ancho - 1:
                fila.append('#') #Límites del tablero
            elif (f, c) in obstaculos:
                fila.append('X') #Obstáculos internos
            else:
                fila.append(' ')
        tablero.append(fila)
    return tablero

def generar_comida(serpiente, ancho, alto, obstaculos):
    while True:
        comida_f = random.randint(1, alto - 2)
        comida_c = random.randint(1, ancho - 2)
        #La comida no puede aparecer dentro de la serpiente ni en un obstáculo
        if (comida_f, comida_c) not in serpiente and (comida_f, comida_c) not in obstaculos:
            return (comida_f, comida_c)

def jugar_nivel(stdscr, nivel, ancho, alto, velocidad, meta, obstaculos):
    stdscr.nodelay(True)
    stdscr.timeout(velocidad)
    
    #La serpiente empieza siempre en el centro del mapa actual
    centro_f, centro_c = alto // 2, ancho // 2
    serpiente = [(centro_f, centro_c), (centro_f, centro_c - 1), (centro_f, centro_c - 2)]
    direccion = 'D'
    puntuacion = 0
    comida = generar_comida(serpiente, ancho, alto, obstaculos)
    
    #Variables para comida especial
    comida_especial = None
    tiempo_aparicion = 0
    duracion_especial = 5 #Segundos antes de que desaparezca
    
    #Mensaje de inicio de nivel
    stdscr.erase()
    stdscr.addstr(alto // 2, (ancho // 2) - 5, f"NIVEL {nivel}")
    stdscr.addstr((alto // 2) + 1, (ancho // 2) - 10, f"Objetivo: {meta} puntos")
    stdscr.refresh()
    curses.napms(2000) #Pausa de 2 segundos antes de empezar

    while True:
        stdscr.erase()
        tablero = inicializar_tablero(ancho, alto, obstaculos)
        
        #Dibujar comida normal
        cf, cc = comida
        tablero[cf][cc] = '*'
        
        #Lógica de la comida especial
        if comida_especial:
            #Revisar si ya pasaron los 5 segundos
            if time.time() - tiempo_aparicion > duracion_especial:
                comida_especial = None #Desaparece por tiempo
            else:
                cfe, cce = comida_especial
                tablero[cfe][cce] = '@' #Dibujar manzana dorada

        #Dibujar serpiente
        for f, c in serpiente:
            tablero[f][c] = 'O'
            
        #Dibujar tablero en pantalla
        for idx, fila in enumerate(tablero):
            stdscr.addstr(idx, 0, "".join(fila))
            
        stdscr.addstr(alto, 0, f"Nivel: {nivel} | Puntuación: {puntuacion}/{meta}")
        stdscr.refresh()

        #Controles
        try:
            tecla = stdscr.getch()
            if tecla != -1:
                char = chr(tecla).lower()
                if char == 'w' and direccion != 'S': direccion = 'W'
                elif char == 's' and direccion != 'W': direccion = 'S'
                elif char == 'a' and direccion != 'D': direccion = 'A'
                elif char == 'd' and direccion != 'A': direccion = 'D'
        except:
            pass

        #Calcular nueva cabeza
        cabeza_f, cabeza_c = serpiente[0]
        if direccion == 'W': cabeza_f -= 1
        elif direccion == 'S': cabeza_f += 1
        elif direccion == 'A': cabeza_c -= 1
        elif direccion == 'D': cabeza_c += 1
        nueva_cabeza = (cabeza_f, cabeza_c)

        #Colisiones con paredes
        if nueva_cabeza[0] == 0 or nueva_cabeza[0] == alto - 1 or nueva_cabeza[1] == 0 or nueva_cabeza[1] == ancho - 1:
            return False #Perdió
        #Colisiones con sí misma o con obstáculos ('X')
        if nueva_cabeza in serpiente or nueva_cabeza in obstaculos:
            return False #Perdió

        #Mover la serpiente
        serpiente.insert(0, nueva_cabeza)

        #Detección de comida normal y especial
        if nueva_cabeza == comida:
            puntuacion += 1
            if puntuacion >= meta: 
                return True #Ganó el nivel
            
            comida = generar_comida(serpiente, ancho, alto, obstaculos)
            
            #20% de probabilidad de que aparezca una manzana dorada
            if not comida_especial and random.random() < 0.20:
                obstaculos_temp = obstaculos + [comida]
                comida_especial = generar_comida(serpiente, ancho, alto, obstaculos_temp)
                tiempo_aparicion = time.time()
                
        elif comida_especial and nueva_cabeza == comida_especial:
            puntuacion += 3 #Da 3 puntos
            if puntuacion >= meta: 
                return True #Ganó el nivel
            comida_especial = None #La comimos
        else:
            serpiente.pop() #Si no come nada, pierde la cola para mantener el tamaño

def main(stdscr):
    curses.curs_set(0)
    
    #Definición de niveles: (Nivel, Ancho, Alto, Velocidad, Puntos para avanzar, Obstáculos)
    niveles = [
        #Nivel 1: Clásico
        {"nivel": 1, "ancho": 50, "alto": 20, "vel": 120, "meta": 5, "obs": []},
        
        #Nivel 2: Más rápido, muro vertical en el medio
        {"nivel": 2, "ancho": 50, "alto": 20, "vel": 100, "meta": 10, 
         "obs": [(f, 25) for f in range(5, 15)]}, 
        
        #Nivel 3: Mapa más pequeño, muy rápido, esquinas bloqueadas
        {"nivel": 3, "ancho": 35, "alto": 15, "vel": 80, "meta": 15, 
         "obs": [(3,3), (3,4), (4,3), (3,31), (3,30), (4,31), (11,3), (11,4), (10,3), (11,31), (11,30), (10,31)]}
    ]

    #Iterar a través de los niveles
    for config in niveles:
        victoria = jugar_nivel(stdscr, config["nivel"], config["ancho"], config["alto"], config["vel"], config["meta"], config["obs"])
        
        if not victoria:
            #Pantalla de Game Over
            stdscr.erase()
            stdscr.addstr(5, 10, "GAME OVER")
            stdscr.addstr(7, 10, "Presiona cualquier tecla para salir...")
            stdscr.nodelay(False)
            stdscr.getch()
            return #Termina el programa si pierdes

    # Si termina el bucle for sin morir, ganó todo el juego
    stdscr.erase()
    stdscr.addstr(5, 10, "¡FELICIDADES! HAS COMPLETADO TODOS LOS NIVELES.")
    stdscr.addstr(7, 10, "Presiona cualquier tecla para salir...")
    stdscr.nodelay(False)
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
