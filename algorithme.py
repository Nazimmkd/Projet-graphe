from modele import INF


class FloydWarshallAlgo:
    """
    Classe contenant la logique mathématique pure de l'algorithme de Floyd-Warshall.
    Totalement indépendante de l'interface graphique. Idéal pour la présentation du code.
    """

    def __init__(self, graphe):
        self.graphe = graphe
        self.n = graphe.n

        # Initialisation de la matrice des distances (M0)
        self.L = [row[:] for row in self.graphe.adj]

        # Initialisation de la matrice des prédécesseurs (P)
        self.P = [[None] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if i != j and self.graphe.adj[i][j] != INF:
                    self.P[i][j] = i

        self.k = -1
        self.termine = False
        self.circuit_absorbant = False
        self.nouveau_circuit_detecte = False

    def etape_suivante(self):
        """Effectue une seule étape (un pivot k) de l'algorithme."""
        if self.termine or self.k >= self.n - 1:
            return []

        self.k += 1
        modifications = []
        self.nouveau_circuit_detecte = False

        # Cœur de l'algorithme de Floyd-Warshall
        for i in range(self.n):
            for j in range(self.n):
                # Si les chemins i->k et k->j existent
                if self.L[i][self.k] != INF and self.L[self.k][j] != INF:
                    new_dist = self.L[i][self.k] + self.L[self.k][j]

                    # Si le nouveau chemin passant par k est plus court
                    if new_dist < self.L[i][j]:
                        # On stocke les changements pour que l'interface puisse les afficher (Logs)
                        modifications.append((i, j, self.L[i][j], new_dist))

                        self.L[i][j] = new_dist
                        self.P[i][j] = self.P[self.k][j]

        # Vérification de l'apparition de circuits absorbants à cette étape
        if not self.circuit_absorbant:
            if any(self.L[i][i] < 0 for i in range(self.n)):
                self.circuit_absorbant = True
                self.nouveau_circuit_detecte = True

        # Vérifier si on a fini
        if self.k >= self.n - 1:
            self.termine = True

        return modifications

    def executer_tout(self):
        """Exécute toutes les étapes restantes d'un coup."""
        while not self.termine:
            self.etape_suivante()

    def reconstruire_chemin(self, start, end):
        """Reconstruit le chemin le plus court entre 'start' et 'end' en utilisant P."""
        if self.circuit_absorbant:
            return None, "Calcul impossible : Circuit Absorbant."
        if not (0 <= start < self.n and 0 <= end < self.n):
            return None, "Sommets invalides."
        if self.L[start][end] == INF:
            return None, f"Pas de chemin entre {start} et {end}."

        chemin = [end]
        curr = end
        while curr != start:
            curr = self.P[start][curr]
            if curr is None:
                return None, "Erreur lors de la reconstruction du chemin."
            chemin.append(curr)

        chemin.reverse()
        return chemin, self.L[start][end]

    def get_circuits_absorbants(self):
        """Retourne la liste des sommets impliqués dans un circuit absorbant."""
        return [i for i in range(self.n) if self.L[i][i] < 0]
