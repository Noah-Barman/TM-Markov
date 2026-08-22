from tkinter import *
from tkinter import ttk, messagebox, font
from collections import Counter
from random import randint

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


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

# Modes :
# "evolution"  -> simulations + statistiques sélectionnées
# "statistique" -> distribution finale + statistiques
mode_affichage = "evolution"


# ======================================================
# PARAMETRES
# ======================================================

def recuperer_parametres():

    try:

        argent_depart = int(entry_depart.get())
        minimum = int(entry_min.get())
        maximum = int(entry_max.get())
        mise_parite = int(entry_mise_parite.get())
        mise_couleur = int(entry_mise_couleur.get())
        lance = int(entry_lance.get())
        iterations = int(entry_iterations.get())

        if minimum >= maximum:
            raise ValueError(
                "Le minimum doit être inférieur au maximum."
            )

        if not (minimum <= argent_depart <= maximum):
            raise ValueError(
                "L'argent initial doit être compris "
                "entre le minimum et le maximum."
            )

        if mise_parite < 0 or mise_couleur < 0:
            raise ValueError(
                "Les mises doivent être positives ou nulles."
            )

        if lance <= 0:
            raise ValueError(
                "Le nombre de lancers doit être supérieur à 0."
            )

        if iterations <= 0:
            raise ValueError(
                "Le nombre d'itérations doit être supérieur à 0."
            )

        return (
            argent_depart,
            minimum,
            maximum,
            mise_parite,
            mise_couleur,
            lance,
            iterations
        )

    except ValueError as erreur:

        messagebox.showerror(
            "Erreur",
            str(erreur)
        )

        return None


# ======================================================
# CREATION DES MISES
# ======================================================

def creer_mises(mise_parite, mise_couleur):

    pairs = set(range(2, 37, 2))
    impairs = set(range(1, 37, 2))

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


    rouge = {
        1, 3, 5, 7, 9,
        12, 14, 16, 18,
        19, 21, 23, 25, 27,
        30, 32, 34, 36
    }

    noir = {
        2, 4, 6, 8, 10,
        11, 13, 15, 17,
        20, 22, 24, 26, 28, 29,
        31, 33, 35
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

        while len(evolution) < lance + 1:
            evolution.append(argent)

        dernieres_evolutions.append(evolution)
        resultats_finaux.append(argent)

    if dernieres_evolutions:

        tableau = np.array(
            dernieres_evolutions,
            dtype=float
        )

        moyenne = np.mean(
            tableau,
            axis=0
        ).tolist()

    if mode_affichage == "statistique":

        afficher_graphique_statistique()

    else:

        afficher_graphique_evolution()


# ======================================================
# AFFICHAGE DES EVOLUTIONS
# ======================================================

def afficher_evolutions(evolutions=None):

    global mode_affichage, dernieres_evolutions

    mode_affichage = "evolution"

    if evolutions is not None:
        dernieres_evolutions = evolutions

    if not dernieres_evolutions:

        messagebox.showwarning(
            "Attention",
            "Effectuez d'abord une simulation."
        )

        return

    afficher_graphique_evolution()


# ======================================================
# GRAPHIQUE EVOLUTION
# ======================================================

def afficher_graphique_evolution():

    if not dernieres_evolutions:
        return

    preparer_graphique()

    tableau = np.array(
        dernieres_evolutions,
        dtype=float
    )

    # --------------------------------------------------
    # SIMULATIONS INDIVIDUELLES
    # --------------------------------------------------

    for evolution in dernieres_evolutions:

        dernier_ax.plot(
            range(len(evolution)),
            evolution,
            color="gray",
            alpha=0.25,
            linewidth=0.8
        )

    # --------------------------------------------------
    # STATISTIQUES AFFICHEES SUR LE GRAPHIQUE
    # --------------------------------------------------

    x = np.arange(tableau.shape[1])
    lignes_stats = []

    moyenne_trajectoire = np.mean(
        tableau,
        axis=0
    )

    ecart_type_trajectoire = np.std(
        tableau,
        axis=0
    )

    # MOYENNE
    if afficher_moyenne_stat.get():

        dernier_ax.plot(
            x,
            moyenne_trajectoire,
            color="red",
            linewidth=3,
            label="Moyenne",
            zorder=10
        )

        dernier_ax.scatter(
            x,
            moyenne_trajectoire,
            color="red",
            s=12,
            zorder=11
        )

    # ECART TYPE
    if afficher_ecart_type.get():

        borne_inf = (
            moyenne_trajectoire
            - ecart_type_trajectoire
        )

        borne_sup = (
            moyenne_trajectoire
            + ecart_type_trajectoire
        )

        dernier_ax.fill_between(
            x,
            borne_inf,
            borne_sup,
            color="orange",
            alpha=0.30,
            label="± 1 écart type",
            zorder=2
        )

    # ESPERANCE THEORIQUE
    if afficher_esperance.get():

        esperance_trajectoire = (
            calculer_trajectoire_esperance()
        )

        if esperance_trajectoire is not None:

            dernier_ax.plot(
                x,
                esperance_trajectoire,
                color="blue",
                linestyle="--",
                linewidth=2.5,
                label="Espérance théorique",
                zorder=9
            )

    # --------------------------------------------------
    # TITRE ET AXES
    # --------------------------------------------------

    dernier_ax.set_title(
        "Simulations de l'évolution du capital",
        fontsize=15,
        fontweight="bold"
    )

    dernier_ax.set_xlabel(
        "Nombre de lancers"
    )

    dernier_ax.set_ylabel(
        "Capital (CHF)"
    )

    dernier_ax.grid(
        True,
        alpha=0.3
    )

    if (
        afficher_esperance.get()
        or afficher_moyenne_stat.get()
        or afficher_ecart_type.get()
    ):
        dernier_ax.legend(
            loc="best",
            framealpha=0.95
        )

    ajuster_axes()

    dernier_canvas.draw_idle()


# ======================================================
# CALCUL MATRICE DE TRANSITION
# ======================================================


def calculer_matrice_transition(
    minimum,
    maximum,
    mise_parite,
    mise_couleur,
    parite,
    couleur
):

    etats = list(
        range(
            minimum,
            maximum + 1
        )
    )

    taille = len(etats)

    P = np.zeros(
        (taille, taille)
    )

    total_mise = mise_parite + mise_couleur

    index_etat = {
        etat: i
        for i, etat in enumerate(etats)
    }

    for i, argent in enumerate(etats):

        if argent <= minimum or argent >= maximum:

            P[i, i] = 1
            continue

        if argent < total_mise:

            P[i, i] = 1
            continue

        for nombre in range(37):

            nouvel_argent = argent - total_mise

            if nombre in couleur:

                nouvel_argent += (
                    2 * mise_couleur
                )

            if nombre in parite:

                nouvel_argent += (
                    2 * mise_parite
                )

            if nouvel_argent <= minimum:

                nouvel_argent = minimum

            elif nouvel_argent >= maximum:

                nouvel_argent = maximum

            j = index_etat[nouvel_argent]

            P[i, j] += 1 / 37

    return P


# ======================================================
# ESPERANCE THEORIQUE
# ======================================================

def calculer_esperance_theorique():

    param = recuperer_parametres()

    if param is None:
        return None

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

    P = calculer_matrice_transition(
        minimum,
        maximum,
        mise_parite,
        mise_couleur,
        parite,
        couleur
    )

    etats = list(
        range(
            minimum,
            maximum + 1
        )
    )

    distribution = np.zeros(
        len(etats)
    )

    distribution[
        etats.index(argent_depart)
    ] = 1

    distribution_n = (
        distribution
        @ np.linalg.matrix_power(
            P,
            lance
        )
    )

    esperance_theorique = np.dot(
        etats,
        distribution_n
    )

    return esperance_theorique


# ======================================================
# ESPERANCE THEORIQUE A CHAQUE ETAPE
# ======================================================

def calculer_trajectoire_esperance():

    param = recuperer_parametres()

    if param is None:
        return None

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

    P = calculer_matrice_transition(
        minimum,
        maximum,
        mise_parite,
        mise_couleur,
        parite,
        couleur
    )

    etats = np.arange(
        minimum,
        maximum + 1,
        dtype=float
    )

    distribution = np.zeros(len(etats))
    distribution[argent_depart - minimum] = 1

    esperances = []

    for _ in range(lance + 1):
        esperances.append(
            float(np.dot(etats, distribution))
        )
        distribution = distribution @ P

    return esperances


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

    afficher_graphique_statistique()


# ======================================================
# GRAPHIQUE STATISTIQUE
# ======================================================

def afficher_graphique_statistique():

    if not resultats_finaux:
        return

    minimum = int(
        entry_min.get()
    )

    maximum = int(
        entry_max.get()
    )

    valeurs = list(
        range(
            minimum,
            maximum + 1
        )
    )

    compteur = Counter(
        resultats_finaux
    )

    proportions = np.array([
        100 * compteur[v]
        / len(resultats_finaux)

        for v in valeurs
    ])

    moyenne_simulee = np.mean(
        resultats_finaux
    )

    variance_simulee = np.mean(
        (
            np.array(resultats_finaux)
            - moyenne_simulee
        ) ** 2
    )

    ecart_type_simule = np.sqrt(
        variance_simulee
    )

    esperance_theorique = (
        calculer_esperance_theorique()
    )

    if esperance_theorique is None:
        return

    preparer_graphique()

    # ==================================================
    # HISTOGRAMME
    # ==================================================

    dernier_ax.bar(
        valeurs,
        proportions,
        width=0.8,
        color=couleur_graphique,
        alpha=0.75,
        label="Distribution empirique",
        zorder=1
    )

    lignes_stats = []

    # ==================================================
    # ESPERANCE THEORIQUE
    # ==================================================

    if afficher_esperance.get():

        dernier_ax.axvline(
            esperance_theorique,
            color="red",
            linestyle="--",
            linewidth=3.5,
            zorder=10,
            label="Espérance théorique"
        )

        # Marqueur en haut de la ligne
        hauteur_max = max(proportions) if len(proportions) else 1

        lignes_stats.append(
            f"Espérance = "
            f"{esperance_theorique:.3f} CHF"
        )

    # ==================================================
    # MOYENNE EMPIRIQUE
    # ==================================================

    if afficher_moyenne_stat.get():

        dernier_ax.axvline(
            moyenne_simulee,
            color="limegreen",
            linestyle="-",
            linewidth=3.5,
            zorder=11,
            label="Moyenne empirique"
        )

        hauteur_max = max(proportions) if len(proportions) else 1

        lignes_stats.append(
            f"Moyenne = "
            f"{moyenne_simulee:.3f} CHF"
        )

    # ==================================================
    # ECART TYPE
    # ==================================================

    if afficher_ecart_type.get():

        borne_inf = (
            moyenne_simulee
            - ecart_type_simule
        )

        borne_sup = (
            moyenne_simulee
            + ecart_type_simule
        )

        dernier_ax.axvspan(
            borne_inf,
            borne_sup,
            color="orange",
            alpha=0.15,
            label="± 1 écart type"
        )

        lignes_stats.append(
            f"Écart type = "
            f"{ecart_type_simule:.3f} CHF"
        )

    # ==================================================
    # VARIANCE
    # ==================================================

    if afficher_variance.get():

        lignes_stats.append(
            f"Variance = "
            f"{variance_simulee:.3f} CHF²"
        )

    # ==================================================
    # TITRE
    # ==================================================

    dernier_ax.set_title(
        "Distribution du capital après "
        + str(int(entry_lance.get()))
        + " parties",
        fontsize=15,
        fontweight="bold"
    )

    dernier_ax.set_xlabel(
        "Capital final (CHF)"
    )

    dernier_ax.set_ylabel(
        "Proportion (%)"
    )

    dernier_ax.grid(
        True,
        axis="y",
        alpha=0.3
    )

    # ==================================================
    # BOITE STATISTIQUES
    # ==================================================

    if lignes_stats:

        dernier_ax.text(
            0.98,
            0.97,
            "\n".join(lignes_stats),
            transform=dernier_ax.transAxes,
            ha="right",
            va="top",
            fontsize=11,
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor="white",
                edgecolor="gray",
                linewidth=1,
                alpha=0.92
            ),
            zorder=20
        )

    # ==================================================
    # LEGENDE
    # ==================================================

    if (
        afficher_esperance.get()
        or afficher_moyenne_stat.get()
        or afficher_ecart_type.get()
    ):

        dernier_ax.legend(
            loc="upper left",
            framealpha=0.95
        )

    ajuster_axes()

    dernier_canvas.draw_idle()


# ======================================================
# PREPARATION DU GRAPHIQUE
# ======================================================

def preparer_graphique():

    global dernier_ax
    global derniere_figure
    global dernier_canvas

    if derniere_figure is None:

        derniere_figure = plt.Figure(
            dpi=100,
            constrained_layout=True
        )

        dernier_ax = (
            derniere_figure.add_subplot(111)
        )

        dernier_canvas = FigureCanvasTkAgg(
            derniere_figure,
            zone_graphique
        )

        dernier_canvas.get_tk_widget().pack(
            expand=True,
            fill=BOTH
        )

    dernier_ax.clear()


# ======================================================
# AJUSTEMENT DES AXES
# ======================================================

def ajuster_axes():

    if dernier_ax is None:
        return

    dernier_ax.margins(
        x=0.03,
        y=0.06
    )


# ======================================================
# MISE A JOUR AUTOMATIQUE DES STATISTIQUES
# ======================================================

def statistiques_modifiees():

    if not dernieres_evolutions:
        return

    if mode_affichage == "statistique":
        afficher_graphique_statistique()
    else:
        afficher_graphique_evolution()


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
    900,
    650
)


# ======================================================
# POLICES
# ======================================================

police_titre = font.Font(
    family="Arial",
    size=16,
    weight="bold"
)

police_generale = font.Font(
    family="Arial",
    size=12
)


# ======================================================
# STYLE TTk
# ======================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except:
    pass

style.configure(
    "Adaptive.TCombobox",
    font=("Arial", 12)
)

style.configure(
    "Adaptive.TCombobox.Listbox",
    font=("Arial", 12)
)


# ======================================================
# ZONE PARAMETRES
# ======================================================

frame_param = LabelFrame(
    fenetre,
    text="Paramètres",
    padx=12,
    pady=12,
    font=police_titre
)

frame_param.pack(
    side=LEFT,
    padx=(15, 10),
    pady=15,
    fill=Y
)


# ======================================================
# PARAMETRES EN GRILLE
# ======================================================

frame_champs = Frame(
    frame_param
)

frame_champs.pack(
    fill=X
)


def champ_grille(nom, valeur, ligne):

    Label(
        frame_champs,
        text=nom,
        font=("Arial", 12)
    ).grid(
        row=ligne,
        column=0,
        sticky="w",
        padx=(0, 10),
        pady=4
    )

    entree = Entry(
        frame_champs,
        font=("Arial", 12),
        width=10
    )

    entree.insert(
        0,
        valeur
    )

    entree.grid(
        row=ligne,
        column=1,
        sticky="ew",
        pady=4
    )

    return entree


frame_champs.columnconfigure(
    1,
    weight=1
)


entry_depart = champ_grille(
    "Argent initial",
    "5",
    0
)

entry_min = champ_grille(
    "Minimum",
    "0",
    1
)

entry_max = champ_grille(
    "Maximum",
    "10",
    2
)

entry_mise_parite = champ_grille(
    "Mise parité",
    "0",
    3
)


# ======================================================
# COMBO PARITE
# ======================================================

Label(
    frame_champs,
    text="Parité",
    font=("Arial", 12)
).grid(
    row=4,
    column=0,
    sticky="w",
    padx=(0, 10),
    pady=4
)


combo_parite = ttk.Combobox(
    frame_champs,
    values=[
        "pair",
        "impair",
        "0"
    ],
    state="readonly",
    width=10,
    style="Adaptive.TCombobox"
)

combo_parite.current(0)

combo_parite.grid(
    row=4,
    column=1,
    sticky="ew",
    pady=4
)


entry_mise_couleur = champ_grille(
    "Mise couleur",
    "1",
    5
)


# ======================================================
# COMBO COULEUR
# ======================================================

Label(
    frame_champs,
    text="Couleur",
    font=("Arial", 12)
).grid(
    row=6,
    column=0,
    sticky="w",
    padx=(0, 10),
    pady=4
)


combo_couleur = ttk.Combobox(
    frame_champs,
    values=[
        "rouge",
        "noir",
        "vert"
    ],
    state="readonly",
    width=10,
    style="Adaptive.TCombobox"
)

combo_couleur.current(0)

combo_couleur.grid(
    row=6,
    column=1,
    sticky="ew",
    pady=4
)


entry_lance = champ_grille(
    "Nombre de lancers",
    "10",
    7
)

entry_iterations = champ_grille(
    "Nombre de simulations",
    "1000",
    8
)


# ======================================================
# OPTIONS STATISTIQUES
# ======================================================

frame_options = LabelFrame(
    frame_param,
    text="Statistiques",
    padx=8,
    pady=6,
    font=("Arial", 12, "bold")
)

frame_options.pack(
    fill=X,
    pady=(10, 8)
)


afficher_esperance = BooleanVar(
    value=True
)

afficher_moyenne_stat = BooleanVar(
    value=True
)

afficher_variance = BooleanVar(
    value=False
)

afficher_ecart_type = BooleanVar(
    value=False
)


Checkbutton(
    frame_options,
    text="Espérance",
    variable=afficher_esperance,
    command=statistiques_modifiees,
    font=("Arial", 11)
).grid(
    row=0,
    column=0,
    sticky="w"
)


Checkbutton(
    frame_options,
    text="Moyenne",
    variable=afficher_moyenne_stat,
    command=statistiques_modifiees,
    font=("Arial", 11)
).grid(
    row=0,
    column=1,
    sticky="w"
)


Checkbutton(
    frame_options,
    text="Variance",
    variable=afficher_variance,
    command=statistiques_modifiees,
    font=("Arial", 11)
).grid(
    row=1,
    column=0,
    sticky="w"
)


Checkbutton(
    frame_options,
    text="Écart type",
    variable=afficher_ecart_type,
    command=statistiques_modifiees,
    font=("Arial", 11)
).grid(
    row=1,
    column=1,
    sticky="w"
)


# ======================================================
# BOUTONS
# ======================================================

frame_boutons = LabelFrame(
    frame_param,
    text="Affichage",
    padx=8,
    pady=8,
    font=("Arial", 12, "bold")
)

frame_boutons.pack(
    fill=X,
    pady=(5, 0)
)


def creer_bouton(texte, commande):

    bouton = Button(
        frame_boutons,
        text=texte,
        command=commande,
        font=("Arial", 11, "bold"),
        padx=8,
        pady=5
    )

    bouton.pack(
        fill=X,
        pady=3
    )

    return bouton


bouton_simulation = creer_bouton(
    "Nouvelle expérimentation",
    simulation_evolutions
)

bouton_evolution = creer_bouton(
    "Afficher les simulations",
    afficher_evolutions
)

bouton_statistique = creer_bouton(
    "Distribution finale",
    simulation_statistique
)


# ======================================================
# ZONE GRAPHIQUE
# ======================================================

frame_graph = LabelFrame(
    fenetre,
    text="Résultats",
    padx=8,
    pady=8,
    font=police_titre
)

frame_graph.pack(
    side=RIGHT,
    expand=True,
    fill=BOTH,
    padx=(0, 15),
    pady=15
)


zone_graphique = Frame(
    frame_graph
)

zone_graphique.pack(
    expand=True,
    fill=BOTH
)


# ======================================================
# TEXTE EXPLICATION
# ======================================================

zone_texte = LabelFrame(
    frame_graph,
    text="Instructions",
    padx=8,
    pady=6,
    font=police_titre
)

zone_texte.pack(
    side=BOTTOM,
    fill=X,
    padx=5,
    pady=(5, 5)
)


texte_explication = Label(
    zone_texte,
    text=(
        "1) Entrez les paramètres de la simulation.\n"
        "2) Cliquez sur « Nouvelle expérimentation ».\n"
        "3) « Afficher les simulations » montre les différentes trajectoires de la somme d'argent de chaque simulation.\n"
        "4) Les cases « Espérance », « Moyenne » et « Écart type » permettent d'ajouter ces informations directement sur le graphique des simulations et de la distribution finale.\n"
        "5) « Distribution finale » montre la distribution finale.\n\n"
        "Les bornes minimale et maximale représentent les états absorbants."
    ),
    font=police_generale,
    justify=CENTER,
    anchor="center",
    wraplength=850
)

texte_explication.pack(
    fill=X,
    padx=5,
    pady=3
)


# ======================================================
# ADAPTATION INTERFACE
# ======================================================

def mettre_a_jour_polices(taille):

    police = (
        "Arial",
        taille
    )

    # Labels et entrées
    for widget in frame_champs.winfo_children():

        if isinstance(widget, Label):

            widget.configure(
                font=police
            )

        elif isinstance(widget, Entry):

            widget.configure(
                font=police
            )


    # Combobox
    style.configure(
        "Adaptive.TCombobox",
        font=police
    )


    # Options
    for widget in frame_options.winfo_children():

        if isinstance(widget, Checkbutton):

            widget.configure(
                font=police
            )


    # Boutons
    for widget in frame_boutons.winfo_children():

        if isinstance(widget, Button):

            widget.configure(
                font=(
                    "Arial",
                    taille,
                    "bold"
                )
            )


    police_generale.configure(
        size=max(
            10,
            taille - 1
        )
    )


def adapter_interface(event=None):

    largeur = fenetre.winfo_width()
    hauteur = fenetre.winfo_height()

    # --------------------------------------------------
    # Taille de police
    # --------------------------------------------------

    taille = int(
        largeur / 95
    )

    taille = max(
        10,
        min(
            16,
            taille
        )
    )

    mettre_a_jour_polices(
        taille
    )


    # --------------------------------------------------
    # Taille du texte d'explication
    # --------------------------------------------------

    texte_explication.configure(
        wraplength=max(
            350,
            int(largeur * 0.55)
        )
    )


    # --------------------------------------------------
    # Taille minimale des boutons
    # --------------------------------------------------

    hauteur_bouton = max(
        24,
        min(
            40,
            int(hauteur / 25)
        )
    )

    for bouton in frame_boutons.winfo_children():

        bouton.configure(
            pady=max(
                3,
                int(hauteur_bouton / 8)
            )
        )


# ======================================================
# INITIALISATION
# ======================================================

fenetre.bind(
    "<Configure>",
    adapter_interface
)

fenetre.after(
    200,
    adapter_interface
)


fenetre.mainloop()
