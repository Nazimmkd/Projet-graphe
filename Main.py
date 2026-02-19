import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import math
import os

# --- LOGIQUE ALGORITHMIQUE ---

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


# --- INTERFACE GRAPHIQUE ---

class FloydWarshallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projet SM601 - Floyd-Warshall Visualizer (Ultra)")
        self.root.geometry("1250x850")  # Un peu plus grand pour accommoder les ajouts
        self.root.configure(bg="#ecf0f1")

        # État de l'application
        self.graphe = None
        self.L = []  # Matrice des distances
        self.P = []  # Matrice des prédécesseurs
        self.k = -1
        self.sommets_pos = {}

        # Styles de couleurs
        self.colors = {
            'bg': "#ecf0f1",
            'sidebar': "#2c3e50",
            'node': "#3498db",  # Bleu
            'node_active': "#e74c3c",  # Rouge (Pivot)
            'edge': "#95a5a6",  # Gris (Inactif)
            'edge_in': "#27ae60",  # Vert (Entrant vers k)
            'edge_out': "#e67e22",  # Orange (Sortant de k)
            'text': "#2c3e50"
        }

        self.setup_ui()

    def setup_ui(self):
        # --- Panneau Latéral ---
        self.sidebar = tk.Frame(self.root, width=300, bg=self.colors['sidebar'], padx=15, pady=15)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="CONTRÔLES", fg="white", bg=self.colors['sidebar'],
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 20))

        # Boutons
        style_btn = {"relief": tk.FLAT, "pady": 6, "font": ("Helvetica", 10, "bold"), "cursor": "hand2"}

        tk.Button(self.sidebar, text="📂 Charger Graphe (.txt)", command=self.charger_fichier,
                  bg="#34495e", fg="white", **style_btn).pack(fill=tk.X, pady=5)

        self.btn_next = tk.Button(self.sidebar, text="▶ Étape Suivante (k)", command=self.prochaine_etape,
                                  bg="#27ae60", fg="white", state=tk.DISABLED, **style_btn)
        self.btn_next.pack(fill=tk.X, pady=5)

        self.btn_restart = tk.Button(self.sidebar, text="🔄 Recommencer (Début)", command=self.restart_simulation,
                                     bg="#f39c12", fg="white", state=tk.DISABLED, **style_btn)
        self.btn_restart.pack(fill=tk.X, pady=5)

        tk.Button(self.sidebar, text="🗑 Tout Effacer", command=self.reset_all,
                  bg="#c0392b", fg="white", **style_btn).pack(fill=tk.X, pady=20)

        # --- NOUVEAU : Zone Recherche de Chemin ---
        tk.Label(self.sidebar, text="TROUVER UN CHEMIN", fg="white", bg=self.colors['sidebar'],
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 10))

        path_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        path_frame.pack(fill=tk.X)

        tk.Label(path_frame, text="De:", fg="#bdc3c7", bg=self.colors['sidebar']).grid(row=0, column=0, padx=5)
        self.entry_start = tk.Entry(path_frame, width=5)
        self.entry_start.grid(row=0, column=1, padx=5)

        tk.Label(path_frame, text="Vers:", fg="#bdc3c7", bg=self.colors['sidebar']).grid(row=0, column=2, padx=5)
        self.entry_end = tk.Entry(path_frame, width=5)
        self.entry_end.grid(row=0, column=3, padx=5)

        tk.Button(self.sidebar, text="🔍 Calculer le Chemin", command=self.calculer_chemin,
                  bg="#8e44ad", fg="white", **style_btn).pack(fill=tk.X, pady=10)

        self.lbl_result_path = tk.Label(self.sidebar, text="", fg="#f1c40f", bg=self.colors['sidebar'], wraplength=270,
                                        justify=tk.LEFT)
        self.lbl_result_path.pack(fill=tk.X)

        # Légende
        legend_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        legend_frame.pack(fill=tk.X, pady=20)
        tk.Label(legend_frame, text="LÉGENDE :", fg="white", bg=self.colors['sidebar'],
                 font=("Helvetica", 10, "bold")).pack(anchor="w")
        tk.Label(legend_frame, text="■ Sommet Pivot (k)", fg=self.colors['node_active'],
                 bg=self.colors['sidebar']).pack(anchor="w")
        tk.Label(legend_frame, text="■ Arc Entrant (vers k)", fg=self.colors['edge_in'],
                 bg=self.colors['sidebar']).pack(anchor="w")
        tk.Label(legend_frame, text="■ Arc Sortant (de k)", fg=self.colors['edge_out'], bg=self.colors['sidebar']).pack(
            anchor="w")

        # Logs
        tk.Label(self.sidebar, text="JOURNAL", fg="#bdc3c7", bg=self.colors['sidebar'],
                 font=("Helvetica", 10, "bold")).pack(pady=(10, 5))
        self.log_text = tk.Text(self.sidebar, height=10, bg="#34495e", fg="#ecf0f1", font=("Consolas", 9), bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # --- Zone Principale ---
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=15, pady=15)

        # 1. Canvas
        self.canvas_frame = tk.LabelFrame(self.main_container, text="Visualisation Graphique",
                                          bg="white", font=("Helvetica", 10, "bold"), fg=self.colors['text'])
        self.canvas_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, pady=(0, 15))

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 2. Matrices (Onglets L et P)
        # Utilisation d'un Notebook pour afficher L et P
        self.notebook = ttk.Notebook(self.main_container, height=250)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.X)

        # Onglet Init (Nouvel onglet)
        self.tab_Init = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_Init, text="  Matrice Initiale (M0)  ")

        # Onglet L
        self.tab_L = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_L, text="  Matrice des Distances (L)  ")

        # Onglet P
        self.tab_P = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_P, text="  Matrice des Prédécesseurs (P)  ")

        # Configuration Treeviews
        self.tree_Init = self.create_treeview(self.tab_Init)
        self.tree_L = self.create_treeview(self.tab_L)
        self.tree_P = self.create_treeview(self.tab_P)

    def create_treeview(self, parent):
        style = ttk.Style()
        style.configure("Treeview", font=("Consolas", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        tree = ttk.Treeview(parent, show="headings", selectmode="none")
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def log(self, message):
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)

    def charger_fichier(self):
        chemin = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not chemin: return

        try:
            with open(chemin, 'r') as f:
                lignes = [l.strip() for l in f.readlines() if l.strip()]
                if len(lignes) < 2: raise ValueError("Fichier vide ou invalide")

                nb_sommets = int(lignes[0])
                nb_arcs = int(lignes[1])

                self.graphe = Graphe(nb_sommets)
                for i in range(2, 2 + nb_arcs):
                    parts = lignes[i].split()
                    if len(parts) >= 3:
                        u, v, p = map(int, parts[:3])
                        self.graphe.ajouter_arc(u, v, p)

            self.log_text.delete(1.0, tk.END)
            self.lbl_result_path.config(text="")
            self.log(f"Fichier chargé : {os.path.basename(chemin)}")

            self.restart_simulation()

        except Exception as e:
            messagebox.showerror("Erreur", f"Lecture impossible : {e}")

    def restart_simulation(self):
        if not self.graphe: return
        self.initialiser_algorithme()
        self.btn_next.config(state=tk.NORMAL)
        self.btn_restart.config(state=tk.NORMAL)
        self.dessiner_graphe()
        self.afficher_matrices()
        self.log("Prêt. Cliquez sur 'Étape Suivante'.")

    def reset_all(self):
        self.graphe = None
        self.L = []
        self.P = []
        self.k = -1
        self.sommets_pos = {}

        self.canvas.delete("all")
        self.tree_Init.delete(*self.tree_Init.get_children())
        self.tree_L.delete(*self.tree_L.get_children())
        self.tree_P.delete(*self.tree_P.get_children())
        self.log_text.delete(1.0, tk.END)
        self.lbl_result_path.config(text="")
        self.entry_start.delete(0, tk.END)
        self.entry_end.delete(0, tk.END)

        self.btn_next.config(state=tk.DISABLED)
        self.btn_restart.config(state=tk.DISABLED)

    def initialiser_algorithme(self):
        n = self.graphe.n
        # Init L
        self.L = [row[:] for row in self.graphe.adj]
        # Init P (Prédécesseurs)
        # P[i][j] = i si un arc existe, sinon None. (Par convention, P[i][i] = i ou None, ici on met None pour i==j)
        self.P = [[None] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j and self.graphe.adj[i][j] != INF:
                    self.P[i][j] = i
        self.k = -1

    def prochaine_etape(self):
        if not self.graphe or self.k >= self.graphe.n - 1:
            messagebox.showinfo("Fin", "L'algorithme est terminé.")
            return

        self.k += 1
        n = self.graphe.n
        modif_count = 0

        self.log(f"--- k = {self.k} (Pivot) ---")

        for i in range(n):
            for j in range(n):
                if self.L[i][self.k] != INF and self.L[self.k][j] != INF:
                    new_dist = self.L[i][self.k] + self.L[self.k][j]
                    if new_dist < self.L[i][j]:
                        self.log(f"Mise à jour {i}->{j}: {self.L[i][j]} -> {new_dist}")
                        self.L[i][j] = new_dist
                        # Mise à jour du prédécesseur : pour aller de i à j, on passe par ce qui permettait d'aller de k à j
                        self.P[i][j] = self.P[self.k][j]
                        modif_count += 1

        if any(self.L[i][i] < 0 for i in range(n)):
            messagebox.showwarning("Alerte", f"Circuit absorbant détecté via sommet {self.k} !")
            self.log("ALERTE : Circuit Absorbant !")

        self.afficher_matrices()
        self.dessiner_graphe()

    def calculer_chemin(self):
        """Reconstruit le chemin à partir de la matrice P."""
        if not self.P:
            messagebox.showwarning("Attention", "Veuillez charger un graphe d'abord.")
            return

        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
            n = self.graphe.n

            if not (0 <= start < n and 0 <= end < n):
                self.lbl_result_path.config(text="Sommets invalides.")
                return

            # Vérification circuit absorbant
            if any(self.L[i][i] < 0 for i in range(n)):
                self.lbl_result_path.config(text="Calcul impossible : Circuit Absorbant.")
                return

            if self.L[start][end] == INF:
                self.lbl_result_path.config(text=f"Pas de chemin entre {start} et {end}.")
                return

            # Reconstruction
            chemin = [end]
            curr = end
            while curr != start:
                curr = self.P[start][curr]
                if curr is None:  # Ne devrait pas arriver si L != INF
                    self.lbl_result_path.config(text="Erreur chemin.")
                    return
                chemin.append(curr)

            chemin.reverse()
            path_str = " -> ".join(map(str, chemin))
            cout = self.L[start][end]
            self.lbl_result_path.config(text=f"Chemin: {path_str}\nCoût Total: {cout}")

        except ValueError:
            self.lbl_result_path.config(text="Entrez des nombres entiers.")

    def dessiner_graphe(self):
        self.canvas.delete("all")
        n = self.graphe.n

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w, h = 800, 500
        cx, cy = w / 2, h / 2
        r = min(w, h) / 3

        # Positions
        for i in range(n):
            angle = (i * 2 * math.pi) / n - math.pi / 2
            self.sommets_pos[i] = (cx + r * math.cos(angle), cy + r * math.sin(angle))

        # Arcs
        for i in range(n):
            for j in range(n):
                if self.graphe.adj[i][j] == INF: continue

                x1, y1 = self.sommets_pos[i]
                x2, y2 = self.sommets_pos[j]

                color = self.colors['edge']
                width = 1
                if j == self.k:
                    color, width = self.colors['edge_in'], 2
                elif i == self.k:
                    color, width = self.colors['edge_out'], 2
                if i == self.k and j == self.k: color = self.colors['node_active']

                poids = str(self.graphe.adj[i][j])

                # Boucle
                if i == j:
                    if self.graphe.adj[i][j] == 0: continue
                    angle = math.atan2(y1 - cy, x1 - cx)
                    loop_r = 25
                    lx = x1 + loop_r * 2.5 * math.cos(angle)
                    ly = y1 + loop_r * 2.5 * math.sin(angle)
                    self.canvas.create_line(x1, y1, lx, ly, x1, y1, smooth=True, arrow=tk.LAST, fill=color, width=width,
                                            arrowshape=(10, 12, 5))
                    tx, ty = x1 + loop_r * 2.8 * math.cos(angle), y1 + loop_r * 2.8 * math.sin(angle)
                    self.create_text_bg(tx, ty, poids, color)
                    continue

                # Arc normal
                if (self.graphe.adj[j][i] != INF):  # Courbe si bidirectionnel
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    dx, dy = x2 - x1, y2 - y1
                    dist = math.sqrt(dx * dx + dy * dy)
                    offset = 40
                    nx, ny = -dy / dist, dx / dist
                    cx_pt, cy_pt = mid_x + offset * nx, mid_y + offset * ny
                    self.canvas.create_line(x1, y1, cx_pt, cy_pt, x2, y2, smooth=True, arrow=tk.LAST, fill=color,
                                            width=width, arrowshape=(10, 12, 5))
                    self.create_text_bg(cx_pt, cy_pt, poids, color)
                else:
                    dx, dy = x2 - x1, y2 - y1
                    dist = math.sqrt(dx * dx + dy * dy)
                    stop = 20
                    if dist > stop:
                        ex = x2 - (dx / dist) * stop
                        ey = y2 - (dy / dist) * stop
                        self.canvas.create_line(x1, y1, ex, ey, arrow=tk.LAST, fill=color, width=width,
                                                arrowshape=(10, 12, 5))
                        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                        nx, ny = -dy / dist, dx / dist
                        tx, ty = mx + 15 * nx, my + 15 * ny
                        self.create_text_bg(tx, ty, poids, color)

        # Sommets
        for i, (x, y) in self.sommets_pos.items():
            color = self.colors['node_active'] if i == self.k else self.colors['node']
            self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill=color, outline="white", width=2)
            self.canvas.create_text(x, y, text=str(i), fill="white", font=("Arial", 11, "bold"))

    def create_text_bg(self, x, y, text, color):
        self.canvas.create_rectangle(x - 10, y - 8, x + 10, y + 8, fill="white", outline=color, width=1)
        self.canvas.create_text(x, y, text=text, fill=color, font=("Arial", 9, "bold"))

    def afficher_matrices(self):
        # Update L
        self.tree_Init.delete(*self.tree_Init.get_children())
        self.tree_L.delete(*self.tree_L.get_children())
        self.tree_P.delete(*self.tree_P.get_children())
        n = self.graphe.n

        cols = ["src\\dest"] + [str(i) for i in range(n)]

        for tree in [self.tree_Init, self.tree_L, self.tree_P]:
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=50, anchor="center")

        for i in range(n):
            row_Init = [i]
            row_L = [i]
            row_P = [i]
            for j in range(n):
                # Pour Init (M0)
                val_init = self.graphe.adj[i][j]
                row_Init.append("∞" if val_init == INF else val_init)

                # Pour L
                val = self.L[i][j]
                row_L.append("∞" if val == INF else val)

                # Pour P
                p_val = self.P[i][j]
                row_P.append("-" if p_val is None else p_val)

            tags = ('pivot',) if i == self.k else ()
            self.tree_Init.insert("", tk.END, values=row_Init, tags=tags)
            self.tree_L.insert("", tk.END, values=row_L, tags=tags)
            self.tree_P.insert("", tk.END, values=row_P, tags=tags)

        self.tree_Init.tag_configure('pivot', background="#d5f5e3")
        self.tree_L.tag_configure('pivot', background="#d5f5e3")
        self.tree_P.tag_configure('pivot', background="#d5f5e3")


if __name__ == "__main__":
    root = tk.Tk()
    app = FloydWarshallApp(root)
    root.mainloop()