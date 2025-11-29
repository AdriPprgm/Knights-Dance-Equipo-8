#type: ignore

from dagor import JugadorCaballosBailadores

from collections import deque

class JugadorCaballosBailadoresEquipo8(JugadorCaballosBailadores):

    def BFS(self, start, goal, rows, cols):
        if start == goal:
            return 0
        
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
         
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            pos, dist = queue.popleft()
            
            for dr, dc in knight_moves:
                new_pos = (pos[0] + dr, pos[1] + dc)
                
                if new_pos == goal:
                    return dist + 1
                
                if (0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols 
                    and new_pos not in visited):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        
        return float('inf')

    def heuristica(self, posicion):
        turno, rens, cols, rB, rN, cB, cN = posicion
        mi_rey = rB if self.simbolo == 'B' else rN
        mi_caballo = cB if self.simbolo == 'B' else cN
        rey_opp = rN if self.simbolo == 'B' else rB
        caballo_opp = cN if self.simbolo == 'B' else cB

        distancia_rey = self.BFS(mi_caballo, rey_opp, rens, cols)
        distancia_caballo = self.BFS(mi_caballo, caballo_opp, rens, cols)
        opp_a_mi_rey = self.BFS(caballo_opp, mi_rey, rens, cols)
        opp_a_mi_caballo = self.BFS(caballo_opp, mi_caballo, rens, cols)
        
        puntos = 0
        puntos -= distancia_rey * 15
        puntos -= distancia_caballo * 10

        opp_simbolo = 'N' if self.simbolo == 'B' else 'B'
        opp_posibles = self.posiciones_siguientes((opp_simbolo, rens, cols, rey_opp, caballo_opp, cB, cN))
        opp_mejor_dist = float('inf')
        opp_mejor_pos = None
        for pos in opp_posibles:
            new_caballo_opp = pos[5] if opp_simbolo == 'B' else pos[6]
            dist = self.BFS(new_caballo_opp, mi_rey, rens, cols)
            if dist < opp_mejor_dist:
                opp_mejor_dist = dist
                opp_mejor_pos = new_caballo_opp

        if opp_mejor_pos:
            distancia_intercepcion = self.BFS(mi_caballo, opp_mejor_pos, rens, cols)

            if distancia_intercepcion == 1:
                puntos += 3000
                print(f"¡Intercepción posible! Podemos bloquear desde {mi_caballo} hasta {opp_mejor_pos}")

        if distancia_rey == 0:
            print(f"Puedo capturar rey en {mi_caballo}")
            puntos += 6000

        if distancia_caballo == 0:
            print(f"Puedo capturar caballo en {mi_caballo}")
            puntos += 5000
        
        if distancia_rey == 1:
            print(f"Desde {mi_caballo} podria capturar a su rey")
            puntos += 3000
        
        if distancia_rey == 2:
            print(f"Otro posible camino en {mi_caballo}")
            puntos += 2000
        
        if opp_a_mi_rey == 1:
            puntos -= 4000
        
        if opp_a_mi_caballo == 1:
            print(f"En {mi_caballo} me pueden capturar")
            puntos -= 4000

        return puntos

    def tira(self, posicion):

        posibles = self.posiciones_siguientes(posicion)
        mejor_posicion = posibles[0]
        mejor_score = self.heuristica(mejor_posicion)
        for p in posibles[1:]:
            score = self.heuristica(p)
            if score > mejor_score:
                mejor_score = score
                mejor_posicion = p
        
        return mejor_posicion
            