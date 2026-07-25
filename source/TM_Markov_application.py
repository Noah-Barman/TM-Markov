from tkinter import *
from tkinter import ttk, messagebox, font
from collections import Counter

from random import randint

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ======================================================
# VARIABLES GLOBALES
# ======================================================

dernieres_evolutions = []
resultats_finaux = []
moyenne = []

dernier_canvas = None
dernier_ax = None
derniere_figure = None
couleur_graphique = "steelblue"

mode_affichage = "evolution"


# ======================================================
# PARAMETRES
# ======================================================

def recuperer_parametres():

    try:
        return (
            int(entry_depart.get()),
            int(entry_min.get()),
            int(entry_max.get()),
            int(entry_mise_parite.get()),
            int(entry_mise_couleur.get()),
            int(entry_lance.get()),
            int(entry_iterations.get())
        )

    except ValueError:

        messagebox.showerror(
            "Erreur",
            "Veuillez entrer uniquement des nombres entiers."
        )

        return None



# ======================================================
# CREATION DES MISES
# ======================================================

def creer_mises(mise_parite, mise_couleur):

    pairs = set(range(2, 37, 2))
    impairs = set(range(1, 37, 2))


    # -------- Parité --------

    if mise_parite > 0:

        choix = combo_parite.get()

        if choix == "pair":
            parite = pairs

        elif choix == "impair":
            parite = impairs

        else:
            parite = {0}

    else:
        parite = set()



    # -------- Couleur --------

    rouge = {
        1,3,5,7,9,12,14,16,18,
        19,21,23,25,27,30,32,34,36
    }

    noir = {
        2,4,6,8,10,11,13,15,17,
        20,22,24,26,28,29,31,33,35
    }


    if mise_couleur > 0:

        choix = combo_couleur.get()

        if choix == "rouge":
            couleur = rouge

        elif choix == "noir":
            couleur = noir

        else:
            couleur = {0}

    else:
        couleur = set()


    return parite, couleur




# ======================================================
# SIMULATION
# ======================================================

def simulation_evolutions():

    global dernieres_evolutions
    global resultats_finaux
    global moyenne


    param = recuperer_parametres()

    if param is None:
        return


    (
        argent_depart,
        minimum,
        maximum,
        mise_parite,
        mise_couleur,
        lance,
        iterations
    ) = param



    parite, couleur = creer_mises(
        mise_parite,
        mise_couleur
    )


    total_mise = mise_parite + mise_couleur


    dernieres_evolutions = []
    resultats_finaux = []



    # ==============================
    # Simulation des parties
    # ==============================

    for _ in range(iterations):

        argent = argent_depart

        evolution = [argent]


        for _ in range(lance):

            if not (minimum < argent < maximum):
                break


            if argent < total_mise:
                break



            argent -= total_mise


            nombre = randint(0, 36)


            if nombre in couleur:
                argent += 2 * mise_couleur


            if nombre in parite:
                argent += 2 * mise_parite



            evolution.append(argent)



        # Complétion pour avoir des longueurs identiques

        evolution.extend(
            [argent] * (lance + 1 - len(evolution))
        )


        dernieres_evolutions.append(evolution)
        resultats_finaux.append(argent)




    # ==============================
    # Calcul moyenne
    # ==============================

    moyenne = [
        sum(valeurs) / len(dernieres_evolutions)
        for valeurs in zip(*dernieres_evolutions)
    ]



    # ==============================
    # Conservation du mode affichage
    # ==============================

    if mode_affichage == "statistique":

        simulation_statistique()

    elif mode_affichage == "moyenne":

        afficher_moyenne()

    else:

        afficher_evolutions(
            dernieres_evolutions
        )

# ======================================================
# AFFICHAGE DES EVOLUTIONS
# ======================================================

def afficher_evolutions(evolutions):

    global mode_affichage

    mode_affichage = "evolution"


    if not evolutions:

        messagebox.showwarning(
            "Attention",
            "Effectuez d'abord une simulation."
        )

        return



    fig, ax = plt.subplots()


    for evolution in evolutions:

        ax.plot(
            evolution,
            color="gray",
            alpha=0.3
        )


    afficher_canvas(fig, ax)





# ======================================================
# AFFICHAGE MOYENNE
# ======================================================

def afficher_moyenne():

    global mode_affichage

    mode_affichage = "moyenne"


    if not dernieres_evolutions:

        messagebox.showwarning(
            "Attention",
            "Effectuez d'abord une simulation."
        )

        return



    fig, ax = plt.subplots()


    # Evolutions individuelles légèrement transparentes

    for evolution in dernieres_evolutions:

        ax.plot(
            evolution,
            color="gray",
            alpha=0.15
        )


    ax.plot(
        moyenne,
        color="red",
        linewidth=3,
        label="Moyenne"
    )


    ax.legend()


    afficher_canvas(fig, ax)





# ======================================================
# ANALYSE STATISTIQUE
# ======================================================

def simulation_statistique():

    global mode_affichage

    mode_affichage = "statistique"


    if not resultats_finaux:

        messagebox.showwarning(
            "Attention",
            "Effectuez d'abord une simulation."
        )

        return



    minimum = int(entry_min.get())
    maximum = int(entry_max.get())


    valeurs = list(
        range(
            minimum,
            maximum + 1
        )
    )


    compteur = Counter(resultats_finaux)

    proportions = [
        100 * compteur[v]
        / len(resultats_finaux)

        for v in valeurs
    ]



    fig, ax = plt.subplots()


    ax.bar(
        valeurs,
        proportions,
        color=couleur_graphique
    )


    afficher_canvas(fig, ax)


# ======================================================
# AFFICHAGE CANVAS
# ======================================================

def afficher_canvas(fig=None, ax=None):

    global dernier_ax


    dernier_ax.clear()


    dernier_ax.grid()


    if ax is not None:

        # copie des éléments du nouveau graphique
        for ligne in ax.lines:
            dernier_ax.plot(
                ligne.get_xdata(),
                ligne.get_ydata(),
                color=ligne.get_color(),
                alpha=ligne.get_alpha(),
                linewidth=ligne.get_linewidth(),
                label=ligne.get_label()
            )


        for barre in ax.patches:
            dernier_ax.bar(
                barre.get_x(),
                barre.get_height(),
                width=barre.get_width(),
                color=barre.get_facecolor()
            )


        dernier_ax.set_title(
            ax.get_title()
        )

        dernier_ax.set_xlabel(
            ax.get_xlabel()
        )

        dernier_ax.set_ylabel(
            ax.get_ylabel()
        )

    dernier_ax.relim()
    dernier_ax.autoscale_view()

    dernier_canvas.draw()

# ======================================================
# INTERFACE
# ======================================================

fenetre = Tk()

fenetre.title(
    "Simulation roulette - Chaîne de Markov"
)

fenetre.geometry(
    "1800x1150"
)

fenetre.minsize(
    1050,
    850
)

police_titre = font.Font(
    family="Arial",
    size=16,
    weight="bold"
)

# ======================================================
# INITIALISATION GRAPHIQUE
# ======================================================

def initialiser_graphique():

    global dernier_canvas
    global dernier_ax
    global derniere_figure


    derniere_figure, dernier_ax = plt.subplots(
        figsize=(8,5),
        dpi=100
    )


    derniere_figure.subplots_adjust(
        left=0.09,
        right=0.97,
        bottom=0.12,
        top=0.92
    )


    dernier_canvas = FigureCanvasTkAgg(
        derniere_figure,
        zone_graphique
    )


    dernier_canvas.get_tk_widget().pack(
        expand=True,
        fill=BOTH,
        padx=10,
        pady=10
    )


    dernier_canvas.draw()


# ======================================================
# ADAPTATION INTERFACE
# ======================================================

def mettre_a_jour_polices(taille):

    police = ("Arial", taille)


    # Labels + champs
    for widget in frame_param.winfo_children():

        if isinstance(widget, (Label, Entry)):

            widget.configure(
                font=police
            )


    # Boutons
    for widget in frame_boutons.winfo_children():

        if isinstance(widget, Button):

            widget.configure(
                font=police
            )


    # Texte instructions
    police_generale.configure(
        size=taille
    )


def adapter_interface(event=None):

    largeur = fenetre.winfo_width()
    hauteur = fenetre.winfo_height()


    # Calcul plus adapté
    taille = int(
        largeur / 80
    )


    taille = max(
        12,
        min(
            20,
            taille
        )
    )


    mettre_a_jour_polices(
        taille
    )


    texte_explication.configure(
        wraplength=int(
            largeur * 0.55
        )
    )

# ======================================================
# ZONE PARAMETRES
# ======================================================

frame_param = LabelFrame(
    fenetre,
    text="Paramètres",
    padx=25,
    pady=25,
    font=police_titre
)

frame_param.pack(
    side=LEFT,
    padx=20,
    pady=20,
    fill=Y
)



def champ(nom, valeur=""):

    Label(
        frame_param,
        text=nom,
        font=("Arial", 12)
    ).pack(
        pady=3
    )

    entree = Entry(
    frame_param,
    font=("Arial", 12),
    width=15
    )

    entree.insert(
        0,
        valeur
    )

    entree.pack(
        pady=(0,5)
    )

    return entree




entry_depart = champ(
    "Argent initial",
    "5"
)


entry_min = champ(
    "Minimum",
    "0"
)


entry_max = champ(
    "Maximum",
    "10"
)


entry_mise_parite = champ(
    "Mise parité",
    "0"
)



Label(
    frame_param,
    text="Parité"
).pack()



combo_parite = ttk.Combobox(
    frame_param,
    values=[
        "pair",
        "impair",
        "0"
    ],
    state="readonly",
    font=("Arial", 12),
    width=13
)


combo_parite.current(0)

combo_parite.pack(
    pady=(0,5)
)




entry_mise_couleur = champ(
    "Mise couleur",
    "1"
)



Label(
    frame_param,
    text="Couleur"
).pack()



combo_couleur = ttk.Combobox(
    frame_param,
    values=[
        "rouge",
        "noir",
        "vert"
    ],
    state="readonly",
    font=("Arial", 12),
    width=13
)


combo_couleur.current(0)

combo_couleur.pack(
    pady=(0,5)
)



entry_lance = champ(
    "Nombre de lancés",
    "10"
)


entry_iterations = champ(
    "Nombre d'itérations",
    "1000"
)




# ======================================================
# BOUTONS
# ======================================================

frame_boutons = Frame(
    frame_param
)

frame_boutons.pack(
    pady=10
)


Button(
    frame_boutons,
    text="Nouvelle simulation",
    command=simulation_evolutions,
    width=25,
    font=("Arial", 12)
).pack(
    pady=3
)


Button(
    frame_boutons,
    text="Afficher les itérations",
    command=lambda: afficher_evolutions(dernieres_evolutions),
    width=25,
    font=("Arial", 12)
).pack(
    pady=3
)


Button(
    frame_boutons,
    text="Afficher la moyenne",
    command=afficher_moyenne,
    width=25,
    font=("Arial", 12)
).pack(
    pady=3
)


Button(
    frame_boutons,
    text="Analyse statistique",
    command=simulation_statistique,
    width=25,
    font=("Arial", 12)
).pack(
    pady=3
)


# ======================================================
# ZONE GRAPHIQUE
# ======================================================

frame_graph = LabelFrame(
    fenetre,
    text="Résultats",
    padx=20,
    pady=20,
    font=police_titre
)

frame_graph.pack(
    side=RIGHT,
    expand=True,
    fill=BOTH,
    padx=(0,20),
    pady=20
)




zone_graphique = Frame(
    frame_graph
)

zone_graphique.pack(
    expand=True,
    fill=BOTH,
    pady=5
)

zone_graphique.pack_propagate(False)

# IMPORTANT :
# Aucun bind Configure ici
# Matplotlib garde une taille stable





# ======================================================
# TEXTE EXPLICATION
# ======================================================

zone_texte = LabelFrame(
    frame_graph,
    text="Instructions",
    padx=10,
    pady=10,
    font=police_titre
)

zone_texte.pack(
    side=BOTTOM,
    fill=X,
    padx=10,
    pady=(5,10)
)


police_generale = font.Font(
    family="Arial",
    size=14
)




texte_explication = Label(
    zone_texte,
    text=(
        "Utilisation de l'application :\n\n"

        "1) Entrez les paramètres de la simulation : argent initial, "
        "bornes d'arrêt (min/max), mises et nombre de lancés.\n"

        "2) Cliquez sur 'Nouvelle simulation' pour générer les trajectoires "
        "possibles de la chaîne de Markov.\n"

        "3) Cliquez sur 'Afficher les itérations' pour observer "
        "l'évolution de l'argent au cours des différentes simulations.\n"

        "4) Cliquez sur 'Afficher la moyenne' pour afficher "
        "l'évolution moyenne de l'argent.\n"

        "5) Cliquez sur 'Analyse statistique' pour observer la répartition "
        "finale des états atteints.\n\n"

        "Les bornes minimale et maximale représentent les états absorbants "
        "de la chaîne de Markov : lorsqu'une simulation atteint l'une de ces "
        "valeurs, elle s'arrête car le joueur a soit perdu, soit atteint "
        "son objectif."
    ),

    font=police_generale,
    justify=CENTER,
    anchor="center",
    wraplength=850
)


texte_explication.pack(
    fill=X,
    padx=10,
    pady=5
)




# ======================================================
# LANCEMENT
# ======================================================

initialiser_graphique()

fenetre.bind(
    "<Configure>",
    adapter_interface
)

fenetre.after(
    200,
    adapter_interface
)

fenetre.mainloop()