import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import math
import os

from modele import Graphe, INF
from algorithme import FloydWarshallAlgo


class FloydWarshallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projet SM601 - Floyd-Warshall Visualizer (Ultra)")
        self.root.geometry("1250x850")
        self.root.configure(bg="#ecf0f1")

        # État de l'application
        self.graphe = None
        self.algo = None  # Instance de notre logique Floyd-Warshall
        self.sommets_pos = {}

        # Styles de couleurs
        self.colors = {
            'bg': "#ecf0f1",
            'sidebar': "#2c3e50",
            'node': "#3498db",
            'node_active': "#e74c3c",
            'edge': "#95a5a6",
            'edge_in': "#27ae60",
            'edge_out': "#e67e22",
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

        style_btn = {"relief": tk.FLAT, "pady": 6, "font": ("Helvetica", 10, "bold"), "cursor": "hand2"}

        tk.Button(self.sidebar, text="📂 Charger Graphe (.txt)", command=self.charger_fichier,
                  bg="#34495e", fg="white", **style_btn).pack(fill=tk.X, pady=5)

        self.btn_next = tk.Button(self.sidebar, text="▶ Étape Suivante (k)", command=self.prochaine_etape,
                                  bg="#27ae60", fg="white", state=tk.DISABLED, **style_btn)
        self.btn_next.pack(fill=tk.X, pady=5)

        self.btn_run_all = tk.Button(self.sidebar, text="▶▶ Exécuter tout (Rapide)", command=self.executer_tout,
                                     bg="#16a085", fg="white", state=tk.DISABLED, **style_btn)
        self.btn_run_all.pack(fill=tk.X, pady=5)

        self.btn_restart = tk.Button(self.sidebar, text="🔄 Recommencer (Début)", command=self.restart_simulation,
                                     bg="#f39c12", fg="white", state=tk.DISABLED, **style_btn)
        self.btn_restart.pack(fill=tk.X, pady=5)

        tk.Button(self.sidebar, text="🗑 Tout Effacer", command=self.reset_all,
                  bg="#c0392b", fg="white", **style_btn).pack(fill=tk.X, pady=5)

        tk.Button(self.sidebar, text="💾 Exporter les Traces (.txt)", command=self.exporter_traces,
                  bg="#2980b9", fg="white", **style_btn).pack(fill=tk.X, pady=(5, 20))

        # --- Zone Recherche de Chemin ---
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

        # Légende & Logs
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

        tk.Label(self.sidebar, text="JOURNAL", fg="#bdc3c7", bg=self.colors['sidebar'],
                 font=("Helvetica", 10, "bold")).pack(pady=(10, 5))
        self.log_text = tk.Text(self.sidebar, height=10, bg="#34495e", fg="#ecf0f1", font=("Consolas", 9), bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # --- Zone Principale ---
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=15, pady=15)

        self.canvas_frame = tk.LabelFrame(self.main_container, text="Visualisation Graphique", bg="white",
                                          font=("Helvetica", 10, "bold"), fg=self.colors['text'])
        self.canvas_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, pady=(0, 15))

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.notebook = ttk.Notebook(self.main_container, height=250)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.X)

        self.tab_Init = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_Init, text="  Matrice Initiale (M0)  ")

        self.tab_L = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_L, text="  Matrice des Distances (L)  ")

        self.tab_P = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_P, text="  Matrice des Prédécesseurs (P)  ")

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
        # Initialisation via la nouvelle classe Algorithmique
        self.algo = FloydWarshallAlgo(self.graphe)

        self.btn_next.config(state=tk.NORMAL)
        self.btn_run_all.config(state=tk.NORMAL)
        self.btn_restart.config(state=tk.NORMAL)

        self.dessiner_graphe()
        self.afficher_matrices()
        self.log("Prêt. Cliquez sur 'Étape Suivante' ou 'Exécuter tout'.")

    def reset_all(self):
        self.graphe = None
        self.algo = None
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
        self.btn_run_all.config(state=tk.DISABLED)
        self.btn_restart.config(state=tk.DISABLED)

    def prochaine_etape(self):
        if not self.algo: return
        if self.algo.termine:
            messagebox.showinfo("Fin", "L'algorithme est terminé.")
            return

        k_pivot = self.algo.k + 1
        self.log(f"--- k = {k_pivot} (Pivot) ---")

        # Appel à la logique mathématique pure
        modifications = self.algo.etape_suivante()

        # Affichage des logs
        for (i, j, old_dist, new_dist) in modifications:
            self.log(f"Mise à jour {i}->{j}: {old_dist} -> {new_dist}")

        if self.algo.nouveau_circuit_detecte:
            messagebox.showwarning("Alerte", f"Circuit absorbant détecté via sommet {self.algo.k} !")
            self.log("ALERTE : Circuit Absorbant !")

        self.afficher_matrices()
        self.dessiner_graphe()

        if self.algo.termine:
            self.btn_next.config(state=tk.DISABLED)
            self.btn_run_all.config(state=tk.DISABLED)

    def executer_tout(self):
        if not self.algo: return
        if self.algo.termine:
            messagebox.showinfo("Fin", "L'algorithme est déjà terminé.")
            return

        self.log(f"Exécution rapide depuis k={self.algo.k + 1} jusqu'à {self.graphe.n - 1}...")

        # Appel à la logique mathématique pure
        self.algo.executer_tout()

        if self.algo.circuit_absorbant:
            messagebox.showwarning("Alerte", "Circuit absorbant détecté !")
            self.log("ALERTE : Circuit Absorbant détecté après exécution ! (Diagonale L < 0)")
        else:
            self.log("L'algorithme est arrivé à terme avec succès.")

        self.afficher_matrices()
        self.dessiner_graphe()

        self.btn_next.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        messagebox.showinfo("Fin", "Exécution terminée.")

    def calculer_chemin(self):
        if not self.algo:
            messagebox.showwarning("Attention", "Veuillez charger et initialiser un graphe d'abord.")
            return

        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())

            # Appel à la logique algorithmique
            resultat, message_ou_cout = self.algo.reconstruire_chemin(start, end)

            if resultat is None:  # Erreur ou impossible (ex: Circuit absorbant)
                self.lbl_result_path.config(text=message_ou_cout)
            else:
                path_str = " -> ".join(map(str, resultat))
                self.lbl_result_path.config(text=f"Chemin: {path_str}\nCoût Total: {message_ou_cout}")

        except ValueError:
            self.lbl_result_path.config(text="Entrez des nombres entiers.")

    def dessiner_graphe(self):
        self.canvas.delete("all")
        if not self.graphe: return
        n = self.graphe.n

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w, h = 800, 500
        cx, cy = w / 2, h / 2
        r = min(w, h) / 3

        for i in range(n):
            angle = (i * 2 * math.pi) / n - math.pi / 2
            self.sommets_pos[i] = (cx + r * math.cos(angle), cy + r * math.sin(angle))

        k_actuel = self.algo.k if self.algo else -1

        for i in range(n):
            for j in range(n):
                if self.graphe.adj[i][j] == INF: continue

                x1, y1 = self.sommets_pos[i]
                x2, y2 = self.sommets_pos[j]

                color = self.colors['edge']
                width = 1
                if j == k_actuel:
                    color, width = self.colors['edge_in'], 2
                elif i == k_actuel:
                    color, width = self.colors['edge_out'], 2
                if i == k_actuel and j == k_actuel: color = self.colors['node_active']

                poids = str(self.graphe.adj[i][j])

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

                if (self.graphe.adj[j][i] != INF):
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

        for i, (x, y) in self.sommets_pos.items():
            color = self.colors['node_active'] if i == k_actuel else self.colors['node']
            self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill=color, outline="white", width=2)
            self.canvas.create_text(x, y, text=str(i), fill="white", font=("Arial", 11, "bold"))

    def create_text_bg(self, x, y, text, color):
        self.canvas.create_rectangle(x - 10, y - 8, x + 10, y + 8, fill="white", outline=color, width=1)
        self.canvas.create_text(x, y, text=text, fill=color, font=("Arial", 9, "bold"))

    def afficher_matrices(self):
        self.tree_Init.delete(*self.tree_Init.get_children())
        self.tree_L.delete(*self.tree_L.get_children())
        self.tree_P.delete(*self.tree_P.get_children())

        if not self.graphe or not self.algo: return
        n = self.graphe.n
        cols = ["src\\dest"] + [str(i) for i in range(n)]

        for tree in [self.tree_Init, self.tree_L, self.tree_P]:
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=50, anchor="center")

        k_actuel = self.algo.k

        for i in range(n):
            row_Init = [i]
            row_L = [i]
            row_P = [i]
            for j in range(n):
                val_init = self.graphe.adj[i][j]
                row_Init.append("∞" if val_init == INF else val_init)

                val = self.algo.L[i][j]
                row_L.append("∞" if val == INF else val)

                p_val = self.algo.P[i][j]
                row_P.append("-" if p_val is None else p_val)

            tags = ('pivot',) if i == k_actuel else ()
            self.tree_Init.insert("", tk.END, values=row_Init, tags=tags)
            self.tree_L.insert("", tk.END, values=row_L, tags=tags)
            self.tree_P.insert("", tk.END, values=row_P, tags=tags)

        self.tree_Init.tag_configure('pivot', background="#d5f5e3")
        self.tree_L.tag_configure('pivot', background="#d5f5e3")
        self.tree_P.tag_configure('pivot', background="#d5f5e3")

    def exporter_traces(self):
        if not self.algo:
            messagebox.showwarning("Attention", "Veuillez charger un graphe d'abord.")
            return

        if not self.algo.termine:
            messagebox.showwarning("Attention", "Veuillez terminer l'algorithme avant d'exporter les traces.")
            return

        chemin_sauvegarde = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Enregistrer les traces d'exécution"
        )
        if not chemin_sauvegarde: return

        n = self.graphe.n
        with open(chemin_sauvegarde, 'w', encoding='utf-8') as f:
            f.write("=== TRACES D'EXÉCUTION DE L'ALGORITHME DE FLOYD-WARSHALL ===\n\n")

            f.write("--- Matrice Initiale (M0) ---\n")
            f.write("src\\dest\t" + "\t".join(str(i) for i in range(n)) + "\n")
            for i in range(n):
                ligne = [str(self.graphe.adj[i][j]) if self.graphe.adj[i][j] != INF else "INF" for j in range(n)]
                f.write(f"{i}\t\t" + "\t".join(ligne) + "\n")
            f.write("\n")

            f.write("--- Matrice des Distances Finale (L) ---\n")
            f.write("src\\dest\t" + "\t".join(str(i) for i in range(n)) + "\n")
            for i in range(n):
                ligne = [str(self.algo.L[i][j]) if self.algo.L[i][j] != INF else "INF" for j in range(n)]
                f.write(f"{i}\t\t" + "\t".join(ligne) + "\n")
            f.write("\n")

            f.write("--- Matrice des Prédécesseurs Finale (P) ---\n")
            f.write("src\\dest\t" + "\t".join(str(i) for i in range(n)) + "\n")
            for i in range(n):
                ligne = [str(self.algo.P[i][j]) if self.algo.P[i][j] is not None else "-" for j in range(n)]
                f.write(f"{i}\t\t" + "\t".join(ligne) + "\n")
            f.write("\n")

            circuits = self.algo.get_circuits_absorbants()
            if circuits:
                f.write("!!! ALERTE : CIRCUIT ABSORBANT DÉTECTÉ !!!\n")
                f.write("Le circuit absorbant a été détecté via une valeur négative sur la diagonale de L.\n")
                f.write(f"Sommets absorbants impliqués : {circuits}\n")
                f.write("Conséquence : Le calcul des plus courts chemins n'a pas de sens pour ce graphe.\n")
            else:
                f.write("--- Liste de tous les Chemins Minimaux ---\n")
                for start in range(n):
                    for end in range(n):
                        if start != end:
                            res, cout = self.algo.reconstruire_chemin(start, end)
                            if res is None:
                                f.write(f"De {start} vers {end} : {cout}\n")
                            else:
                                path_str = " -> ".join(map(str, res))
                                f.write(f"De {start} vers {end} : {path_str} (Coût Total : {cout})\n")

        messagebox.showinfo("Succès", f"Traces exportées avec succès dans :\n{os.path.basename(chemin_sauvegarde)}")
        self.log("Traces exportées avec succès.")
