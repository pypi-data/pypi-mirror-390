# Máquina de Pachinko, hecho por Sergio De la Rubia Fernández y Daniel Vega
import random
import time

def juegoPrincipal():
    tirosrestantes = 0
    restantesgiro = 20
    totalbolas = 0

    # ---- JUEGO PRINCIPAL ----
    while tirosrestantes < 8:
        try:
            nbolas = int(input("¿Cuántas bolas quiere meter? (1-10): "))
            if nbolas > 10 or nbolas <= 0:
                raise ValueError
            else:
                print("Bolas introducidas.")
        except ValueError:
            print("Por favor, introduzca un número válido.")
        else:
            aciertosbolas = random.randint(0, nbolas)
            restantesgiro -= aciertosbolas
            totalbolas += nbolas
            if restantesgiro < 0:
                restantesgiro = 0
            
            tirosrestantes += 1
            print(f"Han entrado {aciertosbolas} bolas. Quedan {restantesgiro} para que comience el giro. (Tiro {tirosrestantes}/8)")
            if restantesgiro == 0:
                tirosrestantes = 8

    # ---- FIN DE TIRADAS ----
    if tirosrestantes == 8 and restantesgiro > 0:
        print("Has hecho 8 tiros pero no has introducido suficientes bolas para girar el tambor. El juego ha terminado.")
        suficientes = False
    else:
        if restantesgiro == 0:
            print("\nComienza a girar el tambor...")
            time.sleep(3)
            ran1 = random.randint(1, 10)
            ran2 = random.randint(1, 10)
            listaran1 = [ran1, 0, 0]
            listaran2 = [ran1, 0, ran2]

            print(listaran1)
            time.sleep(2)
            print(listaran2)

            if ran1 == ran2:
                print("\033[93mHas alcanzado el modo fiebre!!\033[0m")
                print("Tienes 5 intentos de meter hasta 20 bolas por intento.")
                suficientes = True
            else:
                print("No se ha alcanzado el modo fiebre.")
                suficientes = False
    if suficientes:
        modoFiebre(ran1, ran2, totalbolas)
    return suficientes

def modoFiebre(ran1: int, ran2: int, totalbolas: int):
    ran3 = random.randint(0, 9)
    fiebre = 5
    acumulacionfiebre = 0
    totalfiebre = 0
    resultado = False

    while fiebre > 0:
        try:
            bolasfiebre = int(input("¿Cuántas bolas en este intento? (1-20): "))
            if bolasfiebre > 20 or bolasfiebre <= 0:
                raise ValueError
            else:
                print("Bolas introducidas.")
        except ValueError:
            print("Por favor, introduzca un número válido.")
        else:
            aciertosfiebre = random.randint(0, bolasfiebre)
            fiebre -= 1
            totalfiebre += bolasfiebre
            acumulacionfiebre += aciertosfiebre
            print(f"Han entrado {aciertosfiebre} bolas. Total acumulado: {acumulacionfiebre}\n")

    if acumulacionfiebre >= 50:
        ran3 = ran1
        print("Has acumulado 50 o más bolas. Jackpot garantizado!")
        time.sleep(2)
        listaran3 = [ran1, ran3, ran2]
        print(listaran3)
        resultado = True
            
    #  CINEMÁTICAS VISUALES 

    elif acumulacionfiebre >= 25:
        print("\nHas acumulado más de 25 bolas, se activa una cinemática visual...")
        time.sleep(3)
        cinematica = random.randint(1, 3)
        print("\n")

            #  CINEMÁTICA 1: BOLERA 
        if cinematica == 1:
            print("🎳 CINEMÁTICA: EL LANZAMIENTO PERFECTO 🎳")
            time.sleep(2)
            print("Preparando tiro...")
            for i in range(1, 11):
                print(" " * i + "🏐", end="\r")
                time.sleep(0.1)
            print("\nLa bola impacta contra los bolos...")
            time.sleep(1.5)
            tirados = random.randint(0, 10)
            print(f"¡Ha tirado {tirados} bolos!")
            time.sleep(1.5)
            if random.randint(1, 10) <= tirados:
                print("¡STRIKE! Probabilidad aumentada al 100%")
                ran3 = ran1
                resultado = True
            else:
                print("Casi... pero no fue strike.")
                if(ran3 == ran1):
                    resultado = True
                else:
                    resultado = False

        # CINEMÁTICA 2: DESPEGUE ESPACIAL 
        elif cinematica == 2:
            print("🚀 CINEMÁTICA: LANZAMIENTO ESPACIAL 🚀")
            print("Cuenta atrás para el despegue...")
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            print("¡Despegue!")
            for i in range(10):
                print(" " * i + "🚀", end="\r")
                time.sleep(0.15)
            print("\nEl cohete ha alcanzado el espacio.")
            if random.randint(1, 10) <= 7:
                print("¡Éxito total! +70% probabilidad de JACKPOT.")
                if(ran1>5):
                    ran3 = random.randint(ran1-2, ran1+1)
                else:
                    ran3 = random.randint(ran1, ran1+2)
                if(ran3 == ran1):
                    resultado = True
                else:
                    resultado = False
            else:
                print("Algo falló en el motor... No hay bonificación.")
                if(ran3 == ran1):
                    resultado = True
                else:
                    resultado = False

        # CINEMÁTICA 3: TSUNAMI DE BOLAS 
        elif cinematica == 3:
            print("🌊 CINEMÁTICA: TSUNAMI DE BOLAS 🌊")
            print("Una ola de bolas invade la máquina...")
            for i in range(5):
                print("🌊" * (i + 1))
                time.sleep(0.4)
            print("¡Impacto total!")
            if random.randint(1, 10) <= 5:
                print("¡La ola arrasa todo! +50% probabilidad de JACKPOT.")
                if(ran1>=5):
                    ran3 = random.randint(ran1-5, ran1+1)
                else:
                    ran3 = random.randint(ran1, ran1+5)
                if(ran3 == ran1):
                    resultado = True
                else:
                    resultado = False
            else:
                print("La ola fue pequeña... No hubo efecto.")
                if(ran3 == ran1):
                    resultado = True
                else:
                    resultado = False

        time.sleep(3)
        print("\nY el número es...")
        time.sleep(2)
        listaran3 = [ran1, ran3, ran2]
        print(listaran3)

    else:
        # Si no llega ni a 25 bolas
        print("No has acumulado suficientes bolas. No hay potenciador.\n")
        print("Y el número es...")
        time.sleep(3)
        listaran3 = [ran1, ran3, ran2]
        print(listaran3)
        if(ran3 == ran1):
            resultado = True
        else:
            resultado = False
    totalfinal = totalfiebre + totalbolas
    mostrar_resultado(resultado)
    print(f"Has utilizado un total de {totalfinal} bolas.\n")
        

def reiniciar_juego():
    global tirosrestantes, restantesgiro, totalbolas
    tirosrestantes = 0
    restantesgiro = 20
    totalbolas = 0

def mostrar_resultado(resultado):
    if resultado:
        print("\033[92m¡JACKPOT, felicidades, has ganado!\033[0m")  # Verde
    else:
        print("\033[91mUna pena... reinicia el programa para volver a jugar.\033[0m")  # Rojo

# Bienvenida
print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
print("                                                                          PACHINKO                                                                                       ")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
print("Reglas del juego: Es una máquina de pachinko! Para quien no sepa cómo funciona, pachinko es una versión japonesa de las máquinas tragaperras, pero con bolas.")
print("El objetivo es meter 20 bolas en agujeros que suman puntos. Puedes meter hasta 10 bolas por tiro, y tienes 8 tiros.")
print("Cuando llegues a 20 bolas acertadas, girará el tambor tipo tragaperras. Si el 1º y 3º número coinciden, entrarás en modo fiebre.")
print("En modo fiebre puedes meter hasta 20 bolas por intento durante 5 rondas, y dependiendo de tus aciertos verás cinemáticas visuales con bonificaciones.")
print("Buena suerte!\n")

while True:
    suficientes = juegoPrincipal()
    # ---- REINICIO ----
    reiniciar = input("Presiona 'a' para reiniciar el juego o cualquier otra tecla para salir: ")
    if reiniciar.lower() != 'a':
        print("Gracias por jugar al Pachinko.")
        break
