from dagor import JuegoCaballosBailadores, JugadorCaballosBailadoresAleatorio
from v1 import JugadorCaballosBailadoresEquipoV1
from equipo8 import JugadorCaballosBailadoresEquipo8

if __name__ == '__main__':
    juego = JuegoCaballosBailadores(
        JugadorCaballosBailadoresAleatorio('Equipo8'),
        JugadorCaballosBailadoresEquipo8('V2'),
        5, 8)
    juego.inicia(veces=100, delta_max=2)