#type: ignore

from dagor import JugadorCaballosBailadores
from collections import deque

class BotMinimax(JugadorCaballosBailadores):
    """
    Elite Knights Dance bot using enhanced Minimax with Alpha-Beta Pruning.
    Strategy: Deep tactical analysis with adaptive play style.
    """

    def __init__(self, nombre, profundidad=4):
        super().__init__(nombre)
        self.profundidad = profundidad
        self._cache = {}
        self._transposition_table = {}

    def knight_distance(self, start, goal, rows, cols):
        """BFS to calculate actual knight move distance with caching."""
        if start == goal:
            return 0
        
        cache_key = (start, goal, rows, cols)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
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
                    self._cache[cache_key] = dist + 1
                    return dist + 1
                
                if (0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols 
                    and new_pos not in visited):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        
        return float('inf')

    def control_del_tablero(self, mi_caballo, rens, cols):
        """
        Calculate how many squares the knight can reach in 1 move.
        More mobility = better position.
        """
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        alcanzables = 0
        for dr, dc in knight_moves:
            new_pos = (mi_caballo[0] + dr, mi_caballo[1] + dc)
            if 0 <= new_pos[0] < rens and 0 <= new_pos[1] < cols:
                alcanzables += 1
        
        return alcanzables

    def heuristica(self, posicion):
        """
        Elite heuristic evaluation with multiple strategic factors.
        """
        turno, rens, cols, rB, rN, cB, cN = posicion
        
        # Immediate win/loss detection
        ganador = self.triunfo(posicion)
        if ganador == self.simbolo:
            return 1000000
        if ganador == self.contrario.simbolo:
            return -1000000
        
        # Get piece positions
        mi_caballo = cB if self.simbolo == 'B' else cN
        mi_rey = rB if self.simbolo == 'B' else rN
        opp_rey = rN if self.simbolo == 'B' else rB
        opp_caballo = cN if self.simbolo == 'B' else cB
        
        # Calculate all distances
        ataque_rey = self.knight_distance(mi_caballo, opp_rey, rens, cols)
        ataque_caballo = self.knight_distance(mi_caballo, opp_caballo, rens, cols)
        defensa_rey = self.knight_distance(opp_caballo, mi_rey, rens, cols)
        defensa_caballo = self.knight_distance(opp_caballo, mi_caballo, rens, cols)
        
        # Distance between the two knights
        dist_entre_caballos = self.knight_distance(mi_caballo, opp_caballo, rens, cols)
        
        score = 0
        
        # === OFFENSIVE STRATEGY ===
        # Heavily prioritize attacking opponent's king
        score -= ataque_rey * 30
        score -= ataque_caballo * 18
        
        # === DEFENSIVE STRATEGY ===
        # Penalize opponent being close to our pieces
        score += defensa_rey * 15
        score += defensa_caballo * 8
        
        # === TACTICAL BONUSES ===
        # Immediate capture opportunities
        if ataque_rey == 1:
            score += 50000  # Can capture king next move!
        elif ataque_rey == 2:
            score += 8000   # Two moves from king
        elif ataque_rey == 3:
            score += 2000   # Three moves from king
        
        if ataque_caballo == 1:
            score += 30000  # Can capture knight next move!
        elif ataque_caballo == 2:
            score += 4000
        
        # === DEFENSIVE PENALTIES ===
        if defensa_rey == 1:
            score -= 40000  # King in immediate danger!
        elif defensa_rey == 2:
            score -= 10000  # King threatened soon
        
        if defensa_caballo == 1:
            score -= 15000  # Knight in danger
        elif defensa_caballo == 2:
            score -= 5000
        
        # === MOBILITY & BOARD CONTROL ===
        mi_movilidad = self.control_del_tablero(mi_caballo, rens, cols)
        opp_movilidad = self.control_del_tablero(opp_caballo, rens, cols)
        score += (mi_movilidad - opp_movilidad) * 100
        
        # === POSITIONING STRATEGY ===
        # Prefer center control for more options
        centro_r, centro_c = rens // 2, cols // 2
        mi_dist_centro = abs(mi_caballo[0] - centro_r) + abs(mi_caballo[1] - centro_c)
        opp_dist_centro = abs(opp_caballo[0] - centro_r) + abs(opp_caballo[1] - centro_c)
        score += (opp_dist_centro - mi_dist_centro) * 50
        
        # === TACTICAL: CONTROL THE GAP ===
        # If we're closer to opponent's king than they are to ours, bonus
        if ataque_rey < defensa_rey:
            score += 1000
        
        # If knights are close, prefer having better defensive position
        if dist_entre_caballos <= 2:
            score += defensa_rey * 100
        
        # === ENDGAME STRATEGY ===
        # If opponent is very close to our king, prioritize defense over offense
        if defensa_rey <= 2:
            score += defensa_rey * 5000  # Extreme defensive weight
            # Also consider intercepting opponent
            if dist_entre_caballos <= 2:
                score += 3000
        
        return score

    def minimax(self, posicion, profundidad, alpha, beta, es_maximizador):
        """
        Enhanced Minimax with alpha-beta pruning and transposition table.
        """
        # Check transposition table
        pos_key = str(posicion)
        if pos_key in self._transposition_table:
            cached_depth, cached_score = self._transposition_table[pos_key]
            if cached_depth >= profundidad:
                return cached_score
        
        # Base cases
        ganador = self.triunfo(posicion)
        if ganador == self.simbolo:
            return 1000000 + profundidad  # Prefer faster wins
        if ganador == self.contrario.simbolo:
            return -1000000 - profundidad  # Prefer slower losses
        
        if profundidad == 0:
            score = self.heuristica(posicion)
            self._transposition_table[pos_key] = (profundidad, score)
            return score
        
        posibles = self.posiciones_siguientes(posicion)
        
        if not posibles:
            return 0
        
        if es_maximizador:
            max_eval = float('-inf')
            for pos in posibles:
                eval_score = self.minimax(pos, profundidad - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            self._transposition_table[pos_key] = (profundidad, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            for pos in posibles:
                eval_score = self.minimax(pos, profundidad - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            self._transposition_table[pos_key] = (profundidad, min_eval)
            return min_eval

    def tira(self, posicion):
        """
        Choose best move using enhanced minimax.
        """
        # Clear transposition table periodically to prevent memory issues
        if len(self._transposition_table) > 10000:
            self._transposition_table.clear()
        
        posibles = self.posiciones_siguientes(posicion)
        
        # Quick win check
        for p in posibles:
            if self.triunfo(p) == self.simbolo:
                return p
        
        # Quick defensive check - if opponent can win, block if possible
        turno, rens, cols, rB, rN, cB, cN = posicion
        opp_simbolo = self.contrario.simbolo
        opp_posicion = (opp_simbolo, rens, cols, rB, rN, cB, cN)
        opp_posibles = self.posiciones_siguientes(opp_posicion)
        
        for opp_p in opp_posibles:
            if self.triunfo(opp_p) == opp_simbolo:
                # Opponent can win! Try to block or capture their knight
                opp_caballo = cN if opp_simbolo == 'B' else cB
                for p in posibles:
                    mi_caballo_nuevo = p[5] if self.simbolo == 'B' else p[6]
                    if mi_caballo_nuevo == opp_caballo:
                        return p  # Capture their knight!
        
        # Use minimax to find best move
        mejor_posicion = posibles[0]
        mejor_score = float('-inf')
        
        # Sort moves by heuristic first (move ordering for better pruning)
        posibles_ordenados = sorted(posibles, 
                                    key=lambda p: self.heuristica(p), 
                                    reverse=True)
        
        for p in posibles_ordenados:
            score = self.minimax(p, self.profundidad - 1, float('-inf'), float('inf'), False)
            if score > mejor_score:
                mejor_score = score
                mejor_posicion = p
        
        return mejor_posicion


# Test the bot
if __name__ == '__main__':
    from dagor import JuegoCaballosBailadores
    from Project.Equipo8 import JugadorCaballosBailadoresEquipo00
    
    print("="*70)
    print("BATTLE: Equipo00 vs Enhanced BotMinimax")
    print("="*70)
    
    juego = JuegoCaballosBailadores(
        JugadorCaballosBailadoresEquipo00('Equipo00'),
        BotMinimax('BotMinimax', profundidad=4),
        5, 8
    )
    juego.inicia(veces=100, delta_max=2)