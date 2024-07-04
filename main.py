# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from openai import OpenAI
import subprocess
import json


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def seleccion_juego():
    subprocess.run(["clear"], shell=True)
    print("Games available:")
    script_result = subprocess.run(
        ["ls glulxe-games"],
        shell=True,
        capture_output=True,
        text=True
    ).stdout
    jogos = script_result.split("\n")
    jogos.pop(-1)

    for indice, game in enumerate(jogos):
        print(indice + 1, end="")
        print(" ", end="")
        print(game.split(".")[0])
    print("Type the number of which game do you want to play.")
    print(">", end="")

    seleccion = input()
    centinela = True
    while centinela:
        if seleccion.isdecimal():
            if 1 <= int(seleccion) <= len(jogos):
                centinela = False
            else:
                print("The number is out of boundaries.")
                print("Type a suitable number: ", end="")
                seleccion = input()
        else:
            print("...")
            print("That is not a number...")
            print("Type a NUMBER please: ", end="")
            seleccion = input()

    subprocess.run(["clear"], shell=True)
    return jogos[int(seleccion)-1]


def never_trust_the_user(entrada, guardados):

    if entrada[-5:] != ".save":
        return 1
    if len(entrada) > 32:
        return 2
    if not entrada[:-5].isalpha():
        return 3
    if not entrada[:-5].isascii():
        return 4
    if entrada in guardados:
        return 5
    return 0


def interaccion_directa(memoria):
    entrada_usuario = input()
    memoria.append(entrada_usuario)
    return entrada_usuario


def impresion(jasonDecodificado, memoria):
    centinela = True
    resultado = ""
    lineas_imprimir = []
    if jasonDecodificado["type"] == "update":
        if not "specialinput" in jasonDecodificado:
            if "lines" in jasonDecodificado["content"][0]:
                for elemento in jasonDecodificado["content"][0]["lines"]:
                    for parte in elemento["content"]:
                        lineas_imprimir.append(parte["text"]+"\n")
                if len(jasonDecodificado["content"]) > 1:
                    for elemento in jasonDecodificado["content"][1]["text"]:
                        if len(elemento) == 0:
                            lineas_imprimir.append("\n")
                        elif "append" not in elemento:
                            if "content" in elemento:
                                if elemento["content"][0]["text"] != ">":
                                    lineas_imprimir.append(elemento["content"][0]["text"]+"\n")
                                    resultado += (elemento["content"][0]["text"]+" ")
                                else:
                                    lineas_imprimir.append(elemento["content"][0]["text"])
            else:
                for elemento in jasonDecodificado["content"][0]["text"]:
                    if len(elemento) == 0:
                        lineas_imprimir.append("\n")
                    elif "append" not in elemento:
                        lineas_imprimir.append(elemento["content"][0]["text"]+"\n")
                if jasonDecodificado["input"] == []:
                    centinela = False
        else:
            lineas_imprimir.append("Type the file name. The file name must end with .save and it should only contain english alphabet symbols.\n")
            lineas_imprimir.append(">")
    else:
        #print(jasonDecodificado)
        lineas_imprimir.append(jasonDecodificado+"\n")
        centinela = False

    memoria.append(resultado[:-1])  # En principio hay un espacio al final y hay que quitarlo pero no es seguro que esté siempre.
    return centinela, lineas_imprimir


def mensajear(client, prompt, reservadas, memoria):
    entrada_usuario = input()

    memoria.append(entrada_usuario)
    if entrada_usuario not in reservadas:
        if entrada_usuario[0] != "#":
            completion = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": entrada_usuario}
                ]
            )
            return completion.choices[0].message.content
        else:
            return entrada_usuario[1:]
    else:
        return entrada_usuario


def repeticion(client, prompt, historico_chat, historico_glulxe, historico_usuario, iteracion):
    conversacion = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": historico_usuario[len(historico_usuario) - 1]}
    ]
    for i in range(1, iteracion+1, 1):
        conversacion.append({"role": "assistant", "content": historico_chat[len(historico_chat)-i]})
        conversacion.append({"role": "user", "content": "The answer of the game to your response was: "+historico_glulxe[len(historico_glulxe)-i]})

    conversacion[len(conversacion)-1]["content"] += " Please, reformulate your response."

    completion = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="gpt-4o",
        messages=conversacion
    )

    return completion.choices[0].message.content


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # INICIO DEL PROGRAMA PRINCIPAL

    juego = seleccion_juego()
    jasonDecodificado = {}
    historico_chat = []  # Respuestas proporcionadas por ChatGPT
    historico_usuario = []  # Input del usuario
    historico_glulxe = []  # Respuestas de la máquina Glulxe
    salida_en_crudo = []  # Respuestas de la máquina en formato JSON.
    centinela = True
    palabras_reservadas = []  # Palabras que no deben ser procesadas por ChatGPT
    verbos = []  # Lista con ejemplos de verbos para construir el prompt de ChatGPT
    no_entendidas = []  # Lista con las respuestas de la máquina que implican una repetición de la consulta a ChatGPT
    llave_api = ""

    # Lista con los nombres de los de archivos de guardado disponibles.
    script_result = subprocess.run(
        ["ls *.save"],
        shell=True,
        capture_output=True,
        text=True
    ).stdout
    saved_files = script_result.split("\n")
    saved_files.pop(-1)

    # Carga de la lista de comandos y palabras reservadas e inicialización del prompt.
    prompt = ("Hey! I am playing an interactive fiction game. Please, translate my words to game commands."
              " These commands must be written in lowercase and with no punctuation signs."
              " These are some of the verbs that can be used, although these are not all of them:")

    with open("config/palabras_reservadas", 'r') as comandos_especiales:
        for line in comandos_especiales:
            palabras_reservadas.append(line[:-1])

    with open("config/comandos", 'r') as comandos:
        for line in comandos:
            verbos.append(line[:-1])
            prompt += " " + line[:-1] + ","
    prompt = prompt[:-1] + "."

    with open("config/no_entendido", 'r') as frases:
        for line in frases:
            no_entendidas.append(line[:-1])

    # Creación del cliente de OpenAI
    with open("config/api_key", 'r') as llave:
        for line in llave:
            llave_api += line

    llave_api = llave_api[:-1]  # Se elimina el salto de línea que hay al final
    client = OpenAI(
        api_key=llave_api
    )

    # Invocación de la máquina como proceso en segundo plano.
    glulxe = subprocess.Popen(
        ["glulxe/glulxe", "-fm", "glulxe-games/"+juego],
        bufsize=0,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    num_repeticiones = 1
    # Bucle principal
    while centinela:
        line = glulxe.stdout.readline()
        fullOutput = ""
        fullOutput += line.decode()
        while line != "\n".encode():
            line = glulxe.stdout.readline()
            fullOutput += line.decode()
        jasonDecodificado = json.loads(fullOutput)
        salida_en_crudo.append(fullOutput)

        centinela, lista_imprimir = impresion(jasonDecodificado, historico_glulxe)

        if historico_glulxe[len(historico_glulxe)-1] in no_entendidas and num_repeticiones < 3:

            respuestaChat = repeticion(client, prompt, historico_chat, historico_glulxe, historico_usuario, num_repeticiones)
            mensaje = {
                "type": jasonDecodificado["input"][0]["type"],
                "gen": jasonDecodificado["input"][0]["gen"],
                "window": jasonDecodificado["input"][0]["id"],
                "value": respuestaChat
            }
            glulxe.stdin.write((json.dumps(mensaje)).encode())
            glulxe.stdin.write("\n".encode())
            historico_chat.append(respuestaChat)
            num_repeticiones += 1
        else:
            num_repeticiones = 1
            for line in lista_imprimir:
                print(line, end="")

            if centinela:
                # si input es vacío significa que se ha salido con éxito y hay que terminar la ejecución de la función
                if "input" in jasonDecodificado and jasonDecodificado["input"] != []:
                    respuestaChat = mensajear(client, prompt, palabras_reservadas, historico_usuario)
                    #respuestaChat = interaccion_directa(historico_usuario)
                    mensaje = {
                        "type": jasonDecodificado["input"][0]["type"],
                        "gen": jasonDecodificado["input"][0]["gen"],
                        "window": jasonDecodificado["input"][0]["id"],
                        "value": respuestaChat
                    }
                    glulxe.stdin.write((json.dumps(mensaje)).encode())
                    glulxe.stdin.write("\n".encode())
                    historico_chat.append(respuestaChat)

                elif ("specialinput" in jasonDecodificado) and (jasonDecodificado["specialinput"]["filemode"] == "write"):  # Caso guardar partida

                    respuestaChat = interaccion_directa(historico_usuario)

                    # Comprobación de que la entrada del usuario sea correcta.
                    sobreescrito = False
                    comprobacion = never_trust_the_user(respuestaChat, saved_files)
                    while comprobacion != 0:
                        if comprobacion == 5:   # Caso en que se vaya a sobreescribir un archivo de guardado.
                            print("Do you want to overwrite the file "+respuestaChat+"?")
                            print(">", end="")
                            confirmacion = interaccion_directa(historico_usuario)
                            if confirmacion != "yes":
                                print("Type a different filename: ", end="")
                                respuestaChat = interaccion_directa(historico_usuario)
                                comprobacion = never_trust_the_user(respuestaChat, saved_files)
                            else:
                                comprobacion = 0
                                sobreescrito = True
                        else:
                            if comprobacion == 1:  # Si no acaba con la extension '.save'.
                                print("Incorrect type of file. The filename must end with the '.save' extension.")
                            elif comprobacion == 2:  # La entrada del usuario es demasiado larga.
                                print("Too many characters. The length of the filename must not exceed 32 characters, including the extension.")
                            elif comprobacion == 3 or comprobacion == 4:  # La entrada contiene carácteres alfanuméricos.
                                print("The filename should be plain text, with no spaces or alphanumeric characters.")
                            print("Type a different filename: ", end="")
                            respuestaChat = interaccion_directa(historico_usuario)
                            comprobacion = never_trust_the_user(respuestaChat, saved_files)

                    mensaje = {
                        "type": "specialresponse",
                        "gen": jasonDecodificado["gen"],
                        "response": "fileref_prompt",
                        "value": respuestaChat
                    }
                    glulxe.stdin.write((json.dumps(mensaje)).encode())
                    glulxe.stdin.write("\n".encode())
                    historico_chat.append(respuestaChat)
                    if not sobreescrito:
                        saved_files.append(respuestaChat)
                    print("GAME SAVED!")

                elif ("specialinput" in jasonDecodificado) and (jasonDecodificado["specialinput"]["filemode"] == "read"):  # Caso cargar partida

                    subprocess.run(["clear"], shell=True)

                    print("Saved files:")
                    for indice, game in enumerate(saved_files):
                        print(indice + 1, end="")
                        print(" ", end="")
                        print(game.split(".")[0])
                    print("Type the file you want to load.")
                    print(">", end="")

                    seleccion = input()
                    flag = True
                    while flag:
                        if seleccion.isdecimal():
                            if 1 <= int(seleccion) <= len(saved_files):
                                flag = False
                            else:
                                print("The number is out of boundaries.")
                                print("Type a suitable number: ", end="")
                                seleccion = input()
                        else:
                            print("...")
                            print("That is not a number...")
                            print("Type a NUMBER please: ", end="")
                            seleccion = input()

                    respuestaChat = saved_files[int(seleccion)-1]

                    mensaje = {
                        "type": "specialresponse",
                        "gen": jasonDecodificado["gen"],
                        "response": "fileref_prompt",
                        "value": respuestaChat
                    }
                    glulxe.stdin.write((json.dumps(mensaje)).encode())
                    glulxe.stdin.write("\n".encode())
                    historico_chat.append(respuestaChat)
                    subprocess.run(["clear"], shell=True)
                else:
                    centinela = False

    with open("logs/log_glulxe", 'w') as log:
        for line in historico_glulxe:
            log.write(line)
            log.write("\n")

    with open("logs/log_usuario", 'w') as log:
        for line in historico_usuario:
            log.write(line)
            log.write("\n")

    with open("logs/log_chatgpt", 'w') as log:
        for line in historico_chat:
            log.write(line)
            log.write("\n")

    with open("logs/guardado_glulxe.json", 'w') as guardado:
        for line in salida_en_crudo:
            guardado.write(str(line))

    print_hi('this is the End...')
