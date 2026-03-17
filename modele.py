# --- LOGIQUE ALGORITHMIQUE ET STRUCTURE DE DONNÉES ---

INF = float('inf')

class Graphe:
    def __init__(self, num_sommets):
        self.n = num_sommets
        # Matrice d'adjacence pour les poids
        self.adj = [[INF] * self.n for _ in range(self.n)]
        for i in range(self.n):
            self.adj[i][i] = 0

    def ajouter_arc(self, u, v, poids):
        if 0 <= u < self.n and 0 <= v < self.n:
            self.adj[u][v] = poids