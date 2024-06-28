# TFG

Este TFG tiene como objetivo proporcionar la posibilidad de jugar a aventuras conversacionales basadas en texto mediante el uso del lenguaje natural. Como traductor de lenguaje natural a órdenes comprensibles por la aventura conversacional se utilizará GPT-4.

## Dependencias

Para usar este TFG se necesita:
- **Python 3.8.10** o superior y los siguientes módulos:
	- **json**
	- **subprocess**
	- **openai**
- [Glulxe][glulx]
- [RemGlk][glk] library.
- Juegos compatibles con **Glulx**.
- Se necesita un sistema **GNU/Linux**.

[glulx]: http://eblong.com/zarf/glulx/index.html
[glk]: http://eblong.com/zarf/glk/index.html

## Guía de Instalación

### Glulxe

Para la instalación de **Glulxe** es necesario de disponer de un compilador de **C** (idealmente **gcc**) y de la utilidad **make**. Una vez instaladas estas herramientas, hay que descargar tanto el código fuente de la máquina **Glulxe** como la librería **RemGlk**. Se nos descargarán sendos comprimidos con el software correspondiente que habrán de descomprimirse.
Una vez hecho esto, dentro del directorio `glulxe-061/glulxe` habrá una gran cantidad de archivos, siendo el `Makefile` el que nos interesa. Este archivo contiene las instrucciones (explicadas en el propio `Makefile` pero en inglés) necesarias para el compilado del código de la máquina **Glulxe**, así como la “vinculación” con la biblioteca **RemGlk**. 

En la primera sección se encuentran las rutas para la biblioteca a utilizar. Lo único que hay que hacer es comentar todas las instrucciones salvo las de la biblioteca **RemGlk**. Hay que asegurarse que las **rutas son adecuadas**, en caso contrario aparecerá un error de compilación. Es recomendable colocar los directorios que contienen el código fuente de **Glulxe** y **RemGlk** al mismo nivel pues será útil posteriormente.

En la segunda sección hay que escoger el **compilador** e indicar es sistema operativo para la compilación. Al estar usando un sistema **GNU/Linux**, también se pide que se indique un **generador de números aleatorios**.

Para la biblioteca **RemGlk** el proceso es muy similar. En este caso solo se pide seleccionar el **compilador** a usar.
Tras esto hay que abrir una **terminal** en el directorio de **RemGlk** y escribir la orden:
						
	make

Y repetir la operación en el directorio de **Glulxe**:

	make

Si todo ha funcionado correctamente la máquina **Glulxe** debería estar instalada. Si se quiere probar que funcione correctamente se pude ejecutar:

	./glulxe filename.ulx

siendo filename.ulx un archivo de juego.

### Instalación de los módulos de Python

Ahora conviene comprobar que los módulos de **Python** necesarios están instalados. En caso de necesitar instalar alguno (dependiendo de qué distribución se utilice habrá variaciones) se puede utilizar la orden:

	sudo apt install Python3-nombre_del_módulo

### Añadir el fichero con la API key

Por último el programa necesita de una **API key** de **OpenAI** para su funcionamiento. Para ello se debe crear un fichero de nombre *api_key* en el directorio *config* donde se depositará dicha API key.

### Organización de los directorios

Para que el programa funcione, el directorio que contenga todos los archivos mencionados debe tener la siguiente estructura:
```
├── config
│   ├── api_key
│   ├── comandos
│   ├── no_entendido
│   └── palabras_reservadas
├── glulxe
│   ├── código de Glulxe
├── glulxe-games
│   ├── archivos de juego
├── logs
│   ├── guardado_glulxe.json
│   ├── log_chatgpt
│   ├── log_glulxe
│   └── log_usuario
├── remglk
│   ├── código de la biblioteca
└── Archivos de guardado
```
Además, debe crearse un directorio adicional, *glulxe-games* donde se almacenarán los juegos compatibles con la máquina **Glulxe**.

## Manual de usuario

Para ejecutar el programa, abrir una terminal en el directorio y escribir:

	python3 main.py

Algunas órdenes útiles:

-   Cargar partida: `restore`
-   Guardar partida: `save`
-   Ayuda del juego: `help`
-   Deshacer movimiento: `undo`
-   Modo *verbose*: `verbose`
-   Salir: `salir`
-   Repetir la orden anterior: `again`
-   Esperar: `wait`
-   Para introducir palabras mágicas y/o palabras clave de una aventura en concreto, debe ser escrita precedida del símbolo `#` sin espacios.

## [Licencia][LICENSE]

[LICENSE]: ./LICENSE

