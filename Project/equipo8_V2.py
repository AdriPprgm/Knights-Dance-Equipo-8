#type: ignore

from dagor import JugadorCaballosBailadores

from collections import deque

class JugadorCaballosBailadoresEquipo8_V2(JugadorCaballosBailadores):

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
                
                if (0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols 
                    and new_pos not in visited and new_pos):

                    if new_pos == goal:
                        return dist + 1
                    
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
        distancia_defensa = self.BFS(mi_caballo, mi_rey, rens, cols)

        if distancia_rey == 0:
            return 500000

        if distancia_caballo == 0:
            return 400000
        
        opp_a_mi_rey = self.BFS(caballo_opp, mi_rey, rens, cols)
        opp_a_mi_caballo = self.BFS(caballo_opp, mi_caballo, rens, cols)
        opp_simbolo = 'N' if self.simbolo == 'B' else 'B'
        
        puntos = 0
        puntos -= distancia_rey 

        if distancia_rey > opp_a_mi_rey:
            if distancia_defensa < opp_a_mi_rey:
                puntos += 50000
            else:
                puntos -= 10000
        
        if distancia_rey == opp_a_mi_rey:
            if turno == opp_simbolo:
                puntos -= 10000

        opp_posibles = self.posiciones_siguientes((opp_simbolo, rens, cols, rB, rN, cB, cN))
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
                puntos += 30000

        if distancia_rey == 1 and turno == self.simbolo:
            if opp_a_mi_caballo > 1:
                puntos += 50000
            elif opp_a_mi_caballo == 1:
                puntos += 45000 
            else:
                puntos += 50000

        if opp_a_mi_caballo == 1 and turno == opp_simbolo:
            puntos -= 50000
        
        if distancia_caballo == 1 and turno == self.simbolo:
            puntos += 50000
        
        if distancia_rey == 1 and opp_a_mi_caballo >= 2:
            puntos += 40000
        
        if opp_a_mi_rey == 1 and turno == opp_simbolo:
            puntos -= 50000

        return puntos

    def minimax(self, posicion, maximizing: bool, depth: int, alpha: float = float("-inf"), beta: float = float("inf")) -> float:
        ganador = self.triunfo(posicion)
        if ganador is not None:
            if ganador == self.simbolo:
                return 1e9
            else:
                return -1e9
        
        if depth == 0:
            return self.heuristica(posicion)
            
        posibles = self.posiciones_siguientes(posicion)

        if not posibles:
            return self.heuristica(posicion)

        if maximizing:
            for move in posibles:
                result = self.minimax(move, False, depth - 1, alpha, beta)  
                alpha = max(result, alpha)
                if beta <= alpha:
                    break
            return alpha
        else:
            for move in posibles:
                result = self.minimax(move, True, depth - 1, alpha, beta)
                beta = min(result, beta)
                if beta <= alpha:
                    break
            return beta

    def tira(self, posicion):
        posibles = self.posiciones_siguientes(posicion)

        best_move = None
        best_score = float("-inf")
        for move in posibles:
            if self.triunfo(move) == self.simbolo:
                return move
            result: float = self.minimax(move, False, depth=5)
            if result > best_score:
                best_score = result
                best_move = move
        return best_move