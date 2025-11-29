from dagor import JuegoCaballosBailadores, JugadorCaballosBailadoresAleatorio
from equipo8 import JugadorCaballosBailadoresEquipo8
from equipo8_V2 import JugadorCaballosBailadoresEquipo8_V2

if __name__ == '__main__':
    juego = JuegoCaballosBailadores(
        JugadorCaballosBailadoresEquipo8('Equipo8'),
        JugadorCaballosBailadoresEquipo8_V2('V2'),
        5, 8)
    juego.inicia(veces=100, delta_max=2)