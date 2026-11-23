# pety bombaman

Un bomber chiquito que camina por el escritorio. Solo va arriba, abajo, izquierda o derecha. Pone bombas de mentira y no borra archivos ni iconos.

Hecho por **LaserBreaker**, con **Grok**.

Este repositorio es el programa. Los dibujos y los sonidos de Super Bomberman 4 no estan aqui: son del juego, y el paquete para la familia se pasa aparte.

## Como abrirlo

Hace falta Python 3.12, Pillow, y junto a `pet.py` las carpetas `art/` y `snd/` mas `hurry.mp3`.

```
pip install pillow
python pet.py
```

Clic derecho sobre el y se va. Si lo arrastras, lo levantas. Un clic le cambia la pose. Dos clics seguidos lo enojan. A las y cincuenta dice hurry up, solo mientras esta abierto.

`Jugar.bat`, `Instalar.bat` y `Quitar.bat` son del paquete portable, el que trae su propio Python.

## Creditos

- **LaserBreaker**: la idea, el nombre, eligio los sprites y los sonidos, y lo preparo para su familia y amigos.
- **Grok (xAI)**: escribio el programa junto con LaserBreaker.
- **Super Bomberman 4**, de Hudson Soft: el bomber blanco, las bombas, los items y los sonidos de pasos, bomba, explosion y voces. Esos dibujos y audios son del juego y no se publican en este repositorio.
- En la hoja de sprites dice **ripped by raccoon**.
- El hurry up no es el audio del juego. Es una voz generada que dice ??????.
- Corre con Python, Tcl/Tk y Pillow.

Para compartir con familia y amigos. No es para vender.
