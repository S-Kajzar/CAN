#!/usr/bin/env python3
"""Génère ../index.html à partir du gabarit et du contenu du sujet.

Le bloc <style>, le moteur Grading et le moteur applicatif sont repris du
gabarit (source/gabarit-exercice-interactif.html). Seules les zones prévues
pour un nouveau sujet sont remplacées : CONSEIL_MIN, DECOR, DR_NAMES et le
nombre de pages annoncé dans la fenêtre « Imprimer les DR ».

Usage : python3 source/build.py
"""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GABARIT = os.path.join(HERE, "gabarit-exercice-interactif.html")
OUT = os.path.join(ROOT, "index.html")


def data_uri(name):
    with open(os.path.join(HERE, "images", name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


IMG_DOC = data_uri("doc-numerisation-4bits.png")      # 1300 x 1300
IMG_DR = data_uri("dr-courbe-analogique.png")          # 1300 x 1160

TITLE = "Numériser un signal : le convertisseur analogique/numérique"

# ---------------------------------------------------------------------------
# Parties : la durée conseillée fixe la pondération
# ---------------------------------------------------------------------------
PARTS = [
    {"num": "1", "title": "Analyser un convertisseur sur 4 bits", "minutes": 20, "duration": "20 min"},
    {"num": "2", "title": "Améliorer la résolution : passage sur 5 bits", "minutes": 20, "duration": "20 min"},
    {"num": "3", "title": "Doubler la fréquence d'échantillonnage", "minutes": 20, "duration": "20 min"},
]
TOTAL_MIN = sum(p["minutes"] for p in PARTS)

# ---------------------------------------------------------------------------
# Unités
# ---------------------------------------------------------------------------
U_BITS = {"label": "bits", "accept": ["bit", "bits"]}
U_MBIT = {"label": "Mbit", "accept": ["mbit", "mbits", "megabit", "megabits", "millionbits", "millionsbits"]}
# « 4,8.10^6 bits » : le moteur lit 4,8 puis « e6bits »
U_E6BITS = {"label": "bits", "accept": ["e6bit", "e6bits"]}
U_OCT = {"label": "octets", "accept": ["o", "octet", "octets", "byte", "bytes"]}
U_E6OCT = {"label": "octets", "accept": ["e6o", "e6octet", "e6octets"]}
U_KO = {"label": "ko", "accept": ["ko", "kio", "kilooctet", "kilooctets", "kilo-octet", "kilo-octets",
                                  "kibioctet", "kibioctets"]}
U_V = {"label": "V", "accept": ["v", "volt", "volts"]}
U_MV = {"label": "mV", "accept": ["mv", "millivolt", "millivolts"]}
U_MS = {"label": "ms", "accept": ["ms", "milliseconde", "millisecondes"]}
U_US = {"label": "µs", "accept": ["µs", "μs", "us", "microseconde", "microsecondes"]}
U_S = {"label": "s", "accept": ["s", "seconde", "secondes"]}
U_KHZ = {"label": "kHz", "accept": ["khz", "kilohertz"]}
U_HZ = {"label": "Hz", "accept": ["hz", "hertz"]}


def bits(value, mega=None):
    g = {"type": "num", "value": value, "absTol": 0, "unit": U_BITS}
    if mega is not None:
        g["variants"] = [
            {"value": mega, "absTol": 0.0005, "unit": U_MBIT, "strictUnit": True},
            {"value": mega, "absTol": 0.0005, "unit": U_E6BITS, "strictUnit": True},
        ]
    return g


def octets(value, mega=None):
    g = {"type": "num", "value": value, "absTol": 0, "unit": U_OCT}
    if mega is not None:
        g["variants"] = [{"value": mega, "absTol": 0.0005, "unit": U_E6OCT, "strictUnit": True}]
    return g


def ko(value):
    return {"type": "num", "value": value, "absTol": 0.005, "unit": U_KO}


def count(value):
    return {"type": "num", "value": value, "absTol": 0}


H_UNIT = "Saisis la valeur <strong>avec son unité</strong> : l'unité vaut la moitié des points de la question."
H_UNIT_C = "Arrondir au centième. " + H_UNIT
H_UNIT_M = "Arrondir au millième. " + H_UNIT
H_INT = "Réponds par un nombre entier."
H_KO = "Arrondir au centième. Saisis la valeur <strong>avec son unité</strong> (ici le ko, imposé par l'énoncé) : l'unité vaut la moitié des points de la question."

# ---------------------------------------------------------------------------
# Questions : (id, label, partie, énoncé, consigne, grader, réponse attendue, démarche)
# ---------------------------------------------------------------------------
Q = {}
ORDER = []


def question(qid, part, stem, hint, grader, expected, why, pts=1):
    label = "Q" + qid[1:].replace("_", ".")
    Q[qid] = {"label": label, "part": part, "pts": pts, "grader": grader,
              "stem": stem, "hint": hint, "expected": expected, "why": why}
    ORDER.append(qid)
    return qid


# ----- Partie 1 -----
question("q1_1", "1", "Sur combien de bits travaille ce convertisseur ?", H_UNIT,
         {"type": "num", "value": 4, "absTol": 0, "unit": U_BITS},
         "n = 4 bits",
         "<p>L'axe des valeurs binaires de DP1 va de <b>0000</b> à <b>1111</b> : chaque code compte "
         "<b>4 chiffres binaires</b>. Le convertisseur travaille donc sur <b>n = 4 bits</b>.</p>")
question("q1_2", "1", "Combien de valeurs binaires différentes ce convertisseur peut-il produire ?", H_INT,
         count(16), "16 valeurs",
         "<p>Avec n bits, on peut former 2<sup>n</sup> codes différents : 2<sup>4</sup> = <b>16 valeurs</b>, "
         "de 0000 à 1111. On les compte d'ailleurs directement sur DP1 : 16 bandes horizontales.</p>")
question("q1_3", "1", "Déterminer la période d'échantillonnage T<sub>e</sub> utilisée par ce convertisseur.", H_UNIT_C,
         {"type": "num", "value": 0.25, "absTol": 0.005, "unit": U_MS,
          "variants": [{"value": 250, "absTol": 0.5, "unit": U_US, "strictUnit": True},
                       {"value": 0.00025, "absTol": 0.000005, "unit": U_S, "strictUnit": True}]},
         "T<sub>e</sub> = 0,25 ms (soit 250 µs)",
         "<p>Sur DP1, la fenêtre de <b>4 ms</b> est découpée en <b>16 colonnes</b> de largeur T<sub>e</sub> : "
         "le 1<sup>er</sup> échantillon est pris à t = 0, le dernier à 3,75 ms, et il est tenu jusqu'à 4 ms.</p>"
         "<p>T<sub>e</sub> = 4 ms ÷ 16 = <b>0,25 ms</b> = 250 µs = 2,5×10<sup>−4</sup> s.</p>")
question("q1_4", "1", "Calculer la fréquence d'échantillonnage f<sub>e</sub>.", H_UNIT_C,
         {"type": "num", "value": 4, "absTol": 0.005, "unit": U_KHZ,
          "variants": [{"value": 4000, "absTol": 0.5, "unit": U_HZ, "strictUnit": True}]},
         "f<sub>e</sub> = 4 kHz (soit 4 000 Hz)",
         "<p>La fréquence d'échantillonnage est le nombre d'échantillons pris par seconde : "
         "f<sub>e</sub> = 1 ÷ T<sub>e</sub>.</p>"
         "<p>f<sub>e</sub> = 1 ÷ (0,25×10<sup>−3</sup> s) = <b>4 000 Hz = 4 kHz</b>. Il faut convertir T<sub>e</sub> "
         "en secondes pour obtenir des hertz.</p>")
question("q1_5", "1", "La plage de conversion s'étend de −2 V à +2 V. Calculer le pas (quantum) de ce convertisseur.",
         H_UNIT_C,
         {"type": "num", "value": 0.25, "absTol": 0.005, "unit": U_V,
          "variants": [{"value": 250, "absTol": 0.5, "unit": U_MV, "strictUnit": True}]},
         "p = 0,25 V (soit 250 mV)",
         "<p>La plage de conversion vaut 2 − (−2) = <b>4 V</b>. Elle est partagée en 2<sup>4</sup> = 16 bandes "
         "égales, visibles sur DP1.</p><p>p = 4 V ÷ 16 = <b>0,25 V</b> (250 mV).</p>"
         "<p class=\"small\">Certains manuels définissent le pas par plage ÷ (2<sup>n</sup> − 1) = 4 ÷ 15 ≈ 0,27 V. "
         "Ici, DP1 montre 16 bandes égales entre −2 V et +2 V : on retient 0,25 V.</p>")
question("q1_6", "1", "Pour mémoriser le signal numérique correspondant à ces 4 ms, combien de bits de données faut-il ?",
         H_UNIT, bits(64), "64 bits",
         "<p>Nombre d'échantillons sur 4 ms : 4 ÷ 0,25 = <b>16</b>. Chaque échantillon est codé sur 4 bits.</p>"
         "<p>16 × 4 = <b>64 bits</b>.</p>")
question("q1_7", "1", "Le signal dure maintenant 5 minutes. Combien de bits de données faut-il pour le mémoriser ?",
         H_UNIT, bits(4800000, 4.8), "4 800 000 bits (4,8×10<sup>6</sup> bits)",
         "<p>5 min = 5 × 60 = <b>300 s</b>.</p>"
         "<p>Nombre d'échantillons : 300 s ÷ 0,25×10<sup>−3</sup> s = <b>1 200 000</b> "
         "(ou 300 s × 4 000 Hz).</p><p>1 200 000 × 4 bits = <b>4 800 000 bits</b>.</p>")
question("q1_8", "1", "Exprimer ce dernier résultat en ko, avec 1 ko = 1 024 octets.", H_KO,
         ko(585.9375), "585,94 ko",
         "<p>1 octet = 8 bits : 4 800 000 ÷ 8 = <b>600 000 octets</b>.</p>"
         "<p>600 000 ÷ 1 024 = 585,9375, soit <b>585,94 ko</b> au centième.</p>")

# ----- Partie 2 -----
question("q2_1", "2", "Le convertisseur passe sur 5 bits. Combien de valeurs binaires différentes peut-il produire ?",
         H_INT, count(32), "32 valeurs",
         "<p>2<sup>5</sup> = <b>32 valeurs</b>, de 00000 à 11111 : deux fois plus qu'avec 4 bits. "
         "Chaque bit supplémentaire double le nombre de niveaux.</p>")
question("q2_2", "2", "La plage de conversion reste −2 V à +2 V. Calculer le pas de ce convertisseur.", H_UNIT_M,
         {"type": "num", "value": 0.125, "absTol": 0.0005, "unit": U_V,
          "variants": [{"value": 125, "absTol": 0.5, "unit": U_MV, "strictUnit": True}]},
         "p = 0,125 V (soit 125 mV)",
         "<p>p = 4 V ÷ 2<sup>5</sup> = 4 ÷ 32 = <b>0,125 V</b> (125 mV).</p>"
         "<p>Le pas est deux fois plus fin qu'avec 4 bits : chaque bande de DP1 est coupée en deux.</p>")
# Q2.3 : tracé (voir SKETCHES)
question("q2_4", "2", "Pour mémoriser le signal numérique correspondant à ces 4 ms, combien de bits de données faut-il ?",
         H_UNIT, bits(80), "80 bits",
         "<p>T<sub>e</sub> n'a pas changé (0,25 ms) : il y a toujours <b>16 échantillons</b> sur 4 ms, "
         "mais chacun est maintenant codé sur 5 bits.</p><p>16 × 5 = <b>80 bits</b>.</p>")
question("q2_5", "2", "Pour un signal de 5 minutes, combien de bits de données faut-il ?",
         H_UNIT, bits(6000000, 6), "6 000 000 bits (6×10<sup>6</sup> bits)",
         "<p>300 s ÷ 0,25×10<sup>−3</sup> s = 1 200 000 échantillons.</p>"
         "<p>1 200 000 × 5 bits = <b>6 000 000 bits</b>.</p>")
question("q2_6", "2", "Exprimer ce résultat en octets.", H_UNIT, octets(750000, 0.75), "750 000 octets",
         "<p>1 octet = 8 bits : 6 000 000 ÷ 8 = <b>750 000 octets</b>.</p>")
question("q2_7", "2", "Exprimer ce résultat en ko, avec 1 ko = 1 024 octets.", H_KO,
         ko(732.421875), "732,42 ko",
         "<p>750 000 ÷ 1 024 = 732,421875, soit <b>732,42 ko</b> au centième.</p>")

# ----- Partie 3 -----
question("q3_1", "3", "On double la fréquence d'échantillonnage. Calculer la nouvelle période d'échantillonnage T<sub>e</sub>'.",
         H_UNIT_M,
         {"type": "num", "value": 0.125, "absTol": 0.0005, "unit": U_MS,
          "variants": [{"value": 125, "absTol": 0.5, "unit": U_US, "strictUnit": True},
                       {"value": 0.000125, "absTol": 0.0000005, "unit": U_S, "strictUnit": True}]},
         "T<sub>e</sub>' = 0,125 ms (soit 125 µs)",
         "<p>f<sub>e</sub>' = 2 × 4 kHz = <b>8 kHz</b>. La période est l'inverse de la fréquence : si f<sub>e</sub> "
         "double, T<sub>e</sub> est divisée par deux.</p>"
         "<p>T<sub>e</sub>' = 1 ÷ 8 000 Hz = 0,125×10<sup>−3</sup> s = <b>0,125 ms</b> (125 µs).</p>")
# Q3.2 : tracé (voir SKETCHES)
question("q3_3", "3", "Pour mémoriser le signal numérique correspondant à ces 4 ms, combien de bits de données faut-il ?",
         H_UNIT, bits(160), "160 bits",
         "<p>Nombre d'échantillons sur 4 ms : 4 ÷ 0,125 = <b>32</b>, chacun codé sur 5 bits.</p>"
         "<p>32 × 5 = <b>160 bits</b>.</p>")
question("q3_4", "3", "Pour un signal de 5 minutes, combien de bits de données faut-il ?",
         H_UNIT, bits(12000000, 12), "12 000 000 bits (1,2×10<sup>7</sup> bits)",
         "<p>300 s ÷ 0,125×10<sup>−3</sup> s = <b>2 400 000</b> échantillons.</p>"
         "<p>2 400 000 × 5 bits = <b>12 000 000 bits</b>.</p>")
question("q3_5", "3", "Exprimer ce résultat en octets.", H_UNIT, octets(1500000, 1.5), "1 500 000 octets",
         "<p>12 000 000 ÷ 8 = <b>1 500 000 octets</b>.</p>")
question("q3_6", "3", "Exprimer ce résultat en ko, avec 1 ko = 1 024 octets.", H_KO,
         ko(1464.84375), "1 464,84 ko",
         "<p>1 500 000 ÷ 1 024 = 1 464,84375, soit <b>1 464,84 ko</b> au centième.</p>")
question("q3_7", "3", "Par combien la taille du fichier de 5 minutes a-t-elle été multipliée entre la partie 1 "
         "(4 bits, f<sub>e</sub>) et la partie 3 (5 bits, 2 f<sub>e</sub>) ?",
         "Réponds par un nombre, au dixième.",
         {"type": "num", "value": 2.5, "absTol": 0.05},
         "× 2,5",
         "<p>12 000 000 ÷ 4 800 000 = <b>2,5</b>.</p>"
         "<p>On retrouve ce facteur sans calcul de taille : la résolution passe de 4 à 5 bits (× 5/4 = × 1,25) "
         "et le nombre d'échantillons double (× 2) ; 1,25 × 2 = 2,5. Une numérisation plus fidèle se paie "
         "en place mémoire.</p>")

# ---------------------------------------------------------------------------
# Tracés
# ---------------------------------------------------------------------------
# Lecture de la courbe sur le DR (pixels du fond) : instants d'échantillonnage
# (traits gris aux rangs pairs, milieux aux rangs impairs) et ordonnée de la courbe.
CAN_TS = [111, 139, 167, 194, 221, 250, 278, 306, 334, 362, 391, 420, 448, 476, 504, 532,
          560, 588, 617, 645, 673, 702, 730, 758, 786, 814, 842, 869, 896, 927, 958, 988]
CAN_YS = [617, 629, 532, 426, 323, 229, 179, 207, 272, 354, 446, 534, 599, 638, 621, 575,
          516, 452, 392, 356, 370, 430, 462, 444, 403, 399, 455, 552, 665, 770, 810, 790]
TOP, BOT = 91, 1082  # +2 V et −2 V sur le DR


def volts(y):
    return 2 - (y - TOP) / (BOT - TOP) * 4


def level(y):
    k = round((y - TOP) / ((BOT - TOP) / 32))
    return 2 - k * 0.125


def frn(x, d=2):
    s = ("%." + str(d) + "f") % x
    s = s.replace("-", "−").replace(".", ",")
    return "0,00" if s in ("−0,00",) else s


def samples_table(step):
    rows = []
    for n, i in enumerate(range(0, 32, step)):
        t = i * 0.125
        rows.append("<tr><td>%d</td><td>%s</td><td>%s</td><td><b>%s</b></td></tr>" % (
            n + 1, frn(t, 3 if step == 1 else 2), frn(volts(CAN_YS[i]), 2), frn(level(CAN_YS[i]), 3)))
    return ('<div class="recap-wrap" style="padding:6px 0 0"><table class="t" style="min-width:0">'
            "<thead><tr><th>Échantillon</th><th>t (ms)</th><th>Tension lue (V)</th><th>Niveau retenu (V)</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table></div>")


SKETCHES = [
    {
        "id": "sk_q2_3", "part": "2", "after": "q2_2", "label": "Q2.3", "bg": "CAN5", "deps": ["q2_1", "q2_2"],
        "stem": "Sur DR1, tracer la grille d'amplitude du convertisseur 5 bits, puis la courbe numérisée.",
        "side": "<p>1. Au crayon (noir, trait fin) : la grille d'amplitude, faite de traits horizontaux régulièrement "
                "espacés entre −2 V et +2 V (les deux bords sont déjà tracés).</p>"
                "<p>2. En couleur : la courbe numérisée, en gardant la période d'échantillonnage de la partie 1 "
                "(traits verticaux gris). Chaque échantillon est tenu jusqu'au suivant, comme sur DP1.</p>"
                "<p class=\"small\">Outil Ligne pour les traits droits ; le zoom aide à placer les paliers.</p>",
        "criteria": [
            "Ma grille compte 32 bandes horizontales entre −2 V et +2 V (31 traits ajoutés entre les deux bords).",
            "Mes traits de grille sont horizontaux et régulièrement espacés (bandes de même hauteur).",
            "Ma courbe numérisée compte 16 paliers, chacun commençant sur un trait vertical gris.",
            "Chaque palier est horizontal et tenu jusqu'au trait gris suivant (aucune pente entre deux échantillons).",
            "Chaque palier est sur le trait horizontal le plus proche de la courbe à l'instant de l'échantillon "
            "(ou sur le trait voisin quand la courbe passe à mi-chemin).",
        ],
        "expl": "<p><b>Grille.</b> 2<sup>5</sup> = 32 bandes de 0,125 V entre −2 V et +2 V : chaque bande de DP1 "
                "est coupée en deux.</p>"
                "<p><b>Courbe numérisée.</b> T<sub>e</sub> ne change pas : 16 échantillons, un par trait gris. "
                "À chaque instant d'échantillonnage, on lit la tension de la courbe et on retient le niveau "
                "de la grille le plus proche (même convention que DP1) ; ce niveau est tenu pendant T<sub>e</sub>. "
                "Les points rouges de la correction marquent les valeurs échantillonnées.</p>"
                "<p>L'écart entre la courbe et l'escalier ne dépasse plus un demi-pas, soit 0,0625 V, contre 0,125 V "
                "sur 4 bits : l'escalier épouse mieux la courbe en amplitude, mais rate toujours les détails plus "
                "brefs que T<sub>e</sub> (le creux vers 0,5 ms par exemple).</p>"
                + samples_table(2) +
                "<p class=\"small\">Tensions lues sur le document, à ± 0,05 V près : un palier décalé d'un niveau "
                "là où la courbe passe à mi-chemin entre deux traits n'est pas une erreur.</p>",
    },
    {
        "id": "sk_q3_2", "part": "3", "after": "q3_1", "label": "Q3.2", "bg": "CAN5X2", "deps": ["q3_1"],
        "stem": "Sur DR2, tracer la grille d'amplitude et la grille d'échantillonnage, puis la courbe numérisée.",
        "side": "<p>1. Au crayon (noir, trait fin) : la grille d'amplitude du convertisseur 5 bits, puis les "
                "traits verticaux qui correspondent à la nouvelle période d'échantillonnage.</p>"
                "<p>2. En couleur : la courbe numérisée, un palier par instant d'échantillonnage.</p>"
                "<p class=\"small\">Outil Ligne pour les traits droits ; le zoom aide à placer les paliers.</p>",
        "criteria": [
            "J'ai ajouté un trait vertical au milieu de chaque intervalle gris (32 colonnes de même largeur).",
            "Ma grille d'amplitude compte 32 bandes horizontales régulières entre −2 V et +2 V.",
            "Ma courbe numérisée compte 32 paliers, un par trait vertical (gris ou ajouté).",
            "Chaque palier est horizontal et tenu jusqu'au trait vertical suivant.",
            "Chaque palier est sur le trait horizontal le plus proche de la courbe à l'instant de l'échantillon "
            "(ou sur le trait voisin quand la courbe passe à mi-chemin).",
        ],
        "expl": "<p><b>Grille d'échantillonnage.</b> f<sub>e</sub> double, donc T<sub>e</sub>' = 0,125 ms : "
                "un nouvel instant d'échantillonnage au milieu de chaque intervalle gris, soit 32 colonnes "
                "sur 4 ms (traits pointillés de la correction).</p>"
                "<p><b>Grille d'amplitude.</b> Inchangée par rapport à DR1 : 32 bandes de 0,125 V.</p>"
                "<p><b>Courbe numérisée.</b> Même méthode qu'en Q2.3, avec deux fois plus d'échantillons : "
                "les marches sont deux fois plus courtes et l'escalier suit maintenant le creux vers 0,5 ms "
                "et les deux bosses entre 2 et 3 ms, qu'il lissait auparavant.</p>"
                + samples_table(1) +
                "<p class=\"small\">Tensions lues sur le document, à ± 0,05 V près.</p>",
    },
]
for s in SKETCHES:
    s["pts"] = len(s["criteria"])

# ---------------------------------------------------------------------------
# Points par partie
# ---------------------------------------------------------------------------
for p in PARTS:
    p["points"] = sum(q["pts"] for q in Q.values() if q["part"] == p["num"]) + \
        sum(s["pts"] for s in SKETCHES if s["part"] == p["num"])


def pct(p):
    return ("%.1f" % (p["minutes"] / TOTAL_MIN * 100)).replace(".", ",")


# ---------------------------------------------------------------------------
# Rendu HTML
# ---------------------------------------------------------------------------
def chip(doc):
    return '<button type="button" class="doc-chip" data-doc="%s" aria-pressed="false">%s</button>' % (doc, doc)


def qbar(label, docs, ans="ci-dessous"):
    return ('<div class="qbar" role="group" aria-label="%s"><div class="qb-num">%s</div>'
            '<div class="qb-docs">Documents à consulter : %s</div><div class="qb-ans">Répondre : %s</div></div>'
            % (re.sub("<[^>]+>", "", label), label, " ".join(chip(d) for d in docs), ans))


def q_html(qid):
    q = Q[qid]
    lab = q["label"]
    return f"""
        <div class="q" id="{qid}" data-q="{qid}">
          <p class="q-stem"><span class="q-num">{lab}</span> <strong>{q['stem']}</strong></p>
          <p class="q-hint" id="h-{qid}">{q['hint']}</p>
          <div class="q-row">
            <input type="text" class="q-input" id="in-{qid}" aria-label="Réponse {lab}" aria-describedby="h-{qid}" autocomplete="off" autocapitalize="off" spellcheck="false">
            <button type="button" class="btn btn-validate">Valider</button>
            <span class="q-status" aria-live="polite"></span>
            <span class="print-only pstat">Non validée : comptée fausse</span>
          </div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="q-unit-msg" hidden></p>
            <p class="q-expected"><span>Réponse attendue :</span> {q['expected']}</p>
            <div class="q-why">{q['why']}</div>
          </div>
        </div>"""


def sketch_html(s):
    lab = s["label"]
    part = next(p for p in PARTS if p["num"] == s["part"])
    deps = " et ".join(Q[d]["label"] for d in s["deps"])
    crits = "".join('<label class="se-item"><input type="checkbox" data-crit="%d"><span>%s</span></label>' % (i, c)
                    for i, c in enumerate(s["criteria"]))
    return f"""
        <div class="sketch" data-sketch="{s['id']}" id="{s['id']}">
          <p class="q-stem"><span class="q-num">{lab}</span> <strong>{s['stem']}</strong></p>
          <div class="sk-layout">
            <div class="sk-main">
              <div class="sk-toolbar" role="toolbar" aria-label="Outils de tracé {lab}">
                <button type="button" data-tool="pen" aria-pressed="true">Crayon</button>
                <button type="button" data-tool="line" aria-pressed="false">Ligne</button>
                <button type="button" data-tool="arrow" aria-pressed="false">Flèche</button>
                <button type="button" data-tool="text" aria-pressed="false">Texte</button>
                <button type="button" data-tool="erase" aria-pressed="false">Gomme</button>
                <span class="sep"></span>
                <button type="button" class="sw" data-color="#1F5FA8" aria-label="Couleur bleue" aria-pressed="true" style="background:#1F5FA8"></button>
                <button type="button" class="sw" data-color="#1B7A43" aria-label="Couleur verte" aria-pressed="false" style="background:#1B7A43"></button>
                <button type="button" class="sw" data-color="#1C2530" aria-label="Couleur noire" aria-pressed="false" style="background:#1C2530"></button>
                <span class="sep"></span>
                <span class="tb-group"><span class="tb-lab">Trait</span>
                  <button type="button" data-width="fin" aria-pressed="false">Fin</button>
                  <button type="button" data-width="moyen" aria-pressed="true">Moyen</button>
                  <button type="button" data-width="epais" aria-pressed="false">Épais</button></span>
                <span class="sep"></span>
                <span class="tb-group"><span class="tb-lab">Zoom</span>
                  <button type="button" data-zoom="out" aria-label="Réduire le zoom">−</button>
                  <span class="zoom-val">100 %</span>
                  <button type="button" data-zoom="in" aria-label="Agrandir le zoom">+</button>
                  <button type="button" data-zoom="reset">Ajuster</button></span>
                <span class="sep"></span>
                <button type="button" data-act="undo">Annuler</button>
                <button type="button" data-act="clear">Tout effacer</button>
                <span class="spacer"></span>
                <button type="button" class="btn-drprint" data-act="drprint">Imprimer les DR</button>
                <button type="button" data-act="full" aria-pressed="false">Plein écran</button>
              </div>
              <div class="sk-stage"><img class="sk-bg" src="{IMG_DR}" width="1300" height="1160" alt="" hidden>
                <canvas role="img" aria-label="Zone de tracé sur le document réponse {lab}"></canvas></div>
              <div class="sk-foot">
                <button type="button" class="btn btn-sketch">Valider mon tracé</button>
                <label class="sk-corr-toggle"><input type="checkbox"> Superposer la correction</label>
                <span class="sk-meas" aria-live="polite"></span><span class="q-status" aria-live="polite"></span>
              </div>
              <div class="sk-print-wrap print-only"><p>Tracé de l'élève</p><img class="sk-print sk-print-student" alt="Tracé de l'élève">
                <p>Correction superposée au document réponse</p><img class="sk-print sk-print-corr" alt="Correction du tracé"></div>
              <div class="selfeval" hidden>
                <p class="se-title">Auto-évaluation — {s['pts']} points sur les {part['points']} de la partie {part['num']}</p>
                <p class="se-lead">Compare ton tracé à la correction ci-dessous, puis coche uniquement ce que ton tracé comporte réellement. Sois honnête : c'est toi qui repères ce qu'il te reste à travailler.</p>
                {crits}
                <div class="se-foot"><button type="button" class="btn btn-self">Valider mon auto-évaluation</button>
                  <span class="se-score" aria-live="polite"></span></div>
                <p class="print-only se-print"></p>
              </div>
            </div>
            <div class="sk-side">{s['side']}</div>
          </div>
          <p class="sk-note sk-note-wrap">La correction se superposera à ton tracé une fois {"la question" if len(s['deps']) == 1 else "les questions"} {deps} {"validée" if len(s['deps']) == 1 else "validées"}. <span class="sk-wait" aria-live="polite"></span></p>
          <div class="q-expl" hidden><p class="q-expected"><span>Correction du tracé</span></p>
            {s['expl']}</div>
        </div>"""


def part_head(p):
    return f"""
  <section class="part" id="partie-{p['num']}" aria-labelledby="t-partie-{p['num']}">
    <header class="part-head"><div class="part-num" aria-hidden="true">{p['num']}</div>
      <div><h2 id="t-partie-{p['num']}"><span class="sr-only">Partie {p['num']} : </span>{p['title']}</h2>
        <div class="duree">Durée conseillée : {p['duration']} · Barème : {p['points']} points, soit {pct(p)} % de la note</div></div></header>
    <div class="part-body">"""


PART_END = """
    </div>
  </section>
"""

FIG_DP1 = (f'<figure class="fig"><img src="{IMG_DOC}" width="1300" height="1300" '
           'alt="Courbe analogique (en noir) et sa numérisation sur 4 bits (en vert) : axe des tensions de −2 V à +2 V, '
           'codes binaires de 0000 à 1111, 16 échantillons sur 4 ms">'
           '<figcaption>DP1 — Courbe analogique (en noir) et résultat de sa conversion numérique sur 4 bits (en vert).'
           '</figcaption></figure>')

body_parts = []

# Partie 1
p1 = PARTS[0]
body_parts.append(part_head(p1))
body_parts.append("""
      <p>Un convertisseur analogique/numérique (CAN) mesure la tension d'un signal à intervalles réguliers
        (échantillonnage), puis remplace chaque mesure par le code binaire du niveau le plus proche (quantification).
        Le document DP1 montre une tension analogique (en noir) et le résultat de sa conversion (en vert).</p>
""" + "      " + FIG_DP1 + "\n")
body_parts.append("      " + qbar("Q1.1 à Q1.5", ["DP1"]))
for qid in ["q1_1", "q1_2", "q1_3", "q1_4", "q1_5"]:
    body_parts.append(q_html(qid))
body_parts.append("\n      " + qbar("Q1.6 à Q1.8", ["DP1", "DT1"]))
body_parts.append('\n      <div class="data"><p class="data-title">Données</p><ul><li>1 octet = 8 bits.</li>'
                  '<li>Dans tout le sujet, 1 ko = 1 024 octets.</li></ul></div>')
for qid in ["q1_6", "q1_7", "q1_8"]:
    body_parts.append(q_html(qid))
body_parts.append(PART_END)

# Partie 2
p2 = PARTS[1]
body_parts.append(part_head(p2))
body_parts.append("""
      <p>On cherche à améliorer ce convertisseur. Première piste : affiner la quantification en codant chaque
        échantillon sur <b>5 bits</b> au lieu de 4. La période d'échantillonnage T<sub>e</sub> ne change pas.</p>
""")
body_parts.append("      " + qbar("Q2.1 et Q2.2", ["DP1", "DT1"]))
for qid in ["q2_1", "q2_2"]:
    body_parts.append(q_html(qid))
body_parts.append("\n      " + qbar("Q2.3", ["DP1"], "sur DR1 ci-dessous"))
body_parts.append(sketch_html(SKETCHES[0]))
body_parts.append("\n      " + qbar("Q2.4 à Q2.7", ["DT1"]))
for qid in ["q2_4", "q2_5", "q2_6", "q2_7"]:
    body_parts.append(q_html(qid))
body_parts.append(PART_END)

# Partie 3
p3 = PARTS[2]
body_parts.append(part_head(p3))
body_parts.append("""
      <p>Deuxième piste : on garde le codage sur <b>5 bits</b> et on <b>double la fréquence d'échantillonnage</b>.</p>
""")
body_parts.append("      " + qbar("Q3.1", ["DP1"]))
body_parts.append(q_html("q3_1"))
body_parts.append("\n      " + qbar("Q3.2", ["DP1"], "sur DR2 ci-dessous"))
body_parts.append(sketch_html(SKETCHES[1]))
body_parts.append("\n      " + qbar("Q3.3 à Q3.7", ["DT1"]))
for qid in ["q3_3", "q3_4", "q3_5", "q3_6", "q3_7"]:
    body_parts.append(q_html(qid))
body_parts.append(PART_END)

N_Q = len(Q)
N_SK = len(SKETCHES)
TOTAL_LABEL = "%d h %02d" % divmod(TOTAL_MIN, 60)

# Accueil compact : illustration à côté du titre, boutons de mode visibles sans défiler.
# Feuille complémentaire, placée après le <style> du gabarit qui reste inchangé.
HOME_FIT_CSS = """<style>
#home{min-height:0; padding:18px 20px 20px}
.home-inner{max-width:1180px}
.home-sub{font-size:.95rem; line-height:1.45}
.home-facts span{display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.mc-lead{margin:0 0 4px}
.mode-card li{font-size:.93rem; line-height:1.4}
.home-top{display:grid; grid-template-columns:minmax(0,1fr) auto; gap:14px; align-items:stretch}
.home-top .home-head{display:flex; flex-direction:column; justify-content:center}
.home-top .home-hero{margin:0; padding:6px; display:flex; align-items:center; justify-content:center}
.home-top .home-hero img{width:auto; height:clamp(140px,26vh,240px); max-width:100%}
.home-facts{margin:12px 0 14px}
.home-facts div{padding:7px 12px}
.home-choose{margin:0 0 8px; font-size:1.25rem}
.mode-card{padding:12px 18px 14px}
.mode-card ul{margin:0 0 10px}
.mode-card li{margin:.12rem 0}
.mode-card .btn{padding:9px 16px}
.home-note{margin:10px 0 0}
@media (min-width:601px) and (max-height:700px){
  #home{padding-top:12px}
  .home-head{padding:12px 18px}
  #home h1{font-size:1.9rem}
  .home-top .home-hero img{height:clamp(120px,24vh,170px)}
  .home-facts{margin:8px 0 10px}
  .home-facts div{padding:5px 12px}
  .home-choose{display:none}
}
@media (max-width:820px){
  .home-top{grid-template-columns:1fr}
  .home-top .home-hero img{height:clamp(100px,18vh,170px)}
  .modes{grid-template-columns:1fr 1fr; gap:10px}
  .mode-card li{font-size:.92rem}
}
@media (max-width:600px){
  #home{padding:12px 12px 14px}
  #home h1{font-size:1.45rem}
  .home-head{padding:12px 14px}
  .home-sub{font-size:.88rem; line-height:1.4}
  .home-facts{gap:6px; margin:10px 0}
  .home-facts div{padding:5px 9px}
  .home-facts b{font-size:1.05rem}
  .home-facts span{display:none}
  .modes{gap:10px}
  .mode-card ul{display:none}
  .mode-card{padding:10px 12px 12px}
  .mode-card h3{font-size:1.1rem}
  .mc-lead{font-size:.88rem}
  .mode-card .btn{padding:8px 10px; font-size:.92rem; align-self:stretch}
  .mc-lead{margin:2px 0 8px}
  .home-note{display:none}
  .home-top .home-hero img{height:clamp(80px,15vh,150px)}
}
@media (max-width:600px) and (max-height:720px){
  .home-sub{display:none}
  .home-top{gap:8px}
}
</style>"""

HEAD_COMMENT = """<!-- Exercice généré par source/build.py à partir de source/gabarit-exercice-interactif.html.
     Ne pas modifier ce fichier à la main : modifier source/build.py puis relancer
     « python3 source/build.py ». -->"""

DOCS_HTML = f"""
<nav class="rail" aria-label="Dossiers de présentation et dossier technique">
  <button type="button" class="tab" data-doc="DP1" aria-selected="false" title="Courbe et numérisation sur 4 bits">DP1</button>
  <div class="grp" aria-hidden="true"></div>
  <button type="button" class="tab dt" data-doc="DT1" aria-selected="false" title="Caractéristiques et conventions">DT1</button>
</nav>

<aside id="docpanel" aria-label="Documents du sujet" aria-hidden="true">
  <div class="dp-head">
    <h3 id="dp-title">Documents</h3>
    <button type="button" id="dp-out" aria-label="Réduire">−</button><span id="dp-zoom" class="small">100 %</span>
    <button type="button" id="dp-in" aria-label="Agrandir">+</button>
    <button type="button" id="dp-fit">Ajuster</button>
    <button type="button" id="dp-close">Fermer</button>
  </div>
  <div class="dp-tabs" role="tablist" aria-label="Choisir un document">
    <button type="button" data-doc="DP1" aria-selected="false">DP1</button>
    <button type="button" data-doc="DT1" aria-selected="false">DT1</button>
  </div>
  <div class="dp-body">
    <section class="doc" id="doc-DP1" data-title="DP1 : courbe analogique et numérisation sur 4 bits" data-kind="Dossier présentation">
      <img class="doc-img" src="{IMG_DOC}" alt="Courbe analogique (en noir) et sa numérisation sur 4 bits (en vert), 16 échantillons sur 4 ms, tensions de −2 V à +2 V, codes 0000 à 1111" width="1300" height="1300">
      <p class="doc-cap">En noir, la tension analogique ; en vert, le signal numérisé. Axe vertical : de −2 V à +2 V, codes binaires de 0000 à 1111. Axe horizontal : fenêtre de 4 ms, du 1<sup>er</sup> au dernier échantillon.</p>
    </section>
    <section class="doc" id="doc-DT1" data-title="DT1 : caractéristiques et conventions" data-kind="Dossier technique">
      <div class="doc-text">
        <h3>Caractéristiques du convertisseur étudié</h3>
        <table class="t">
          <tbody>
            <tr><th>Plage de conversion</th><td>de −2 V à +2 V</td></tr>
            <tr><th>Fenêtre observée sur DP1, DR1 et DR2</th><td>4 ms</td></tr>
            <tr><th>Durée du signal complet</th><td>5 minutes</td></tr>
            <tr><th>Maintien de l'échantillon</th><td>chaque valeur numérisée est tenue jusqu'à l'échantillon suivant</td></tr>
            <tr><th>Niveau retenu</th><td>le niveau de quantification le plus proche de la tension échantillonnée</td></tr>
          </tbody>
        </table>
        <h3>Unités de quantité d'information</h3>
        <table class="t">
          <tbody>
            <tr><th>bit</th><td>chiffre binaire : 0 ou 1</td></tr>
            <tr><th>octet (o)</th><td>1 octet = 8 bits</td></tr>
            <tr><th>kilo-octet (ko)</th><td>dans ce sujet, 1 ko = 1 024 octets</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</aside>
"""

HOME_HTML = f"""
<section id="home" aria-labelledby="home-title">
  <div class="home-inner">
    <div class="home-top">
    <header class="home-head">
      <h1 id="home-title">{TITLE}</h1>
      <p class="home-sub">Un convertisseur analogique/numérique transforme une tension qui varie en continu en une suite de codes binaires. On analyse d'abord un convertisseur 4 bits, puis on l'améliore en augmentant sa résolution et sa fréquence d'échantillonnage, en mesurant à chaque fois le prix à payer en place mémoire.</p>
    </header>
    <figure class="home-hero">
      <img src="{IMG_DOC}" alt="Courbe analogique et sa numérisation en escalier sur 4 bits" width="1300" height="1300">
    </figure>
    </div>
    <div class="home-facts">
      <div><b>{len(PARTS)} parties</b><span>du 4 bits à la version améliorée</span></div>
      <div><b>{TOTAL_LABEL}</b><span>conseillée, fixe la pondération</span></div>
      <div><b>2 documents</b><span>DP1 et DT1 consultables</span></div>
      <div><b>{N_SK} tracés</b><span>sur DR, auto-évalués</span></div>
    </div>
    <h2 class="home-choose">Choisis ton mode de travail</h2>
    <div class="modes">
      <article class="mode-card">
        <div class="mc-head"><span class="mc-tag">Mode 1</span><h3>Mode entraînement</h3></div>
        <p class="mc-lead">Pour apprendre en avançant, question par question.</p>
        <ul><li>Chaque question se valide isolément ; la démarche corrigée s'affiche aussitôt.</li>
          <li>La note pondérée s'actualise en continu dans le bandeau.</li>
          <li>Les documents et le chronomètre restent disponibles, sans contrainte de temps.</li></ul>
        <button type="button" class="btn btn-mode" data-mode="training">Commencer l'entraînement</button>
      </article>
      <article class="mode-card exam">
        <div class="mc-head"><span class="mc-tag">Mode 2</span><h3>Mode examen</h3></div>
        <p class="mc-lead">Pour se placer en conditions d'évaluation.</p>
        <ul><li>Aucune correction et aucune note pendant la composition ; les réponses restent modifiables.</li>
          <li>Le chronomètre tourne, à comparer à la durée conseillée.</li>
          <li>En fin de sujet, le bouton « J'ai fini, je fais corriger ma copie » dévoile d'un coup les corrections, les notes par partie et la note globale.</li></ul>
        <button type="button" class="btn btn-mode" data-mode="exam">Composer en mode examen</button>
      </article>
    </div>
    <p class="home-note small">Le mode se choisit une seule fois : pour en changer, recharge la page. Rien n'est enregistré sur l'ordinateur.</p>
  </div>
</section>
"""

MAIN_HEAD = f"""
<main class="page">
  <section class="print-only print-summary">
    <p>Élève : <span class="print-nom"></span> | Copie imprimée le <span class="print-date"></span></p>
    <p>Mode : <span class="print-mode"></span> | Temps de rédaction : <strong class="print-time"></strong> (durée conseillée : {TOTAL_LABEL})</p>
    <p class="print-note-line">Note finale pondérée : <strong class="final-note"></strong></p>
    <p class="print-nograde">Copie non corrigée : les corrections et la note n'apparaissent qu'après la remise de la copie en mode examen.</p>
  </section>

  <header class="cartouche">
    <div class="title">
      <h1>{TITLE}</h1>
      <p>{N_Q} questions notées (unités comprises) et {N_SK} tracés auto-évalués, répartis en {len(PARTS)} parties pondérées par leur durée.</p></div>
    <div class="nom"><label for="nom-eleve">Nom et prénom</label><input id="nom-eleve" type="text" autocomplete="name"></div>
  </header>

  <div class="consignes">
    <p class="only-training"><strong>Mode entraînement.</strong> Réponds dans chaque champ puis clique sur « Valider » : une réponse validée est définitive et sa correction s'affiche aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Compose tout le sujet sans correction ni note : tes réponses restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections, les notes par partie et la note globale.</p>
    <p><strong>Les unités sont notées.</strong> Pour toute question numérique, la valeur vaut la moitié des points et l'unité l'autre moitié : une valeur juste écrite sans unité, ou avec une unité fausse, ne rapporte qu'un demi-point.</p>
    <p>Le dossier de présentation (DP1) et le dossier technique (DT1) s'ouvrent avec les onglets sur le bord droit, ou avec les boutons des en-têtes de question.</p>
    <p><strong>Les tracés comptent aussi.</strong> Quand la correction du tracé s'affiche, tu t'attribues toi-même les points à l'aide d'une grille de critères.</p>
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque partie est notée sur 20, puis pèse au prorata de son temps. Le récapitulatif de fin de sujet donne le détail partie par partie.</p>
  </div>
"""

RECAP_AND_BANNER = """
  <section class="recap" id="recap" aria-labelledby="t-recap">
    <header class="recap-head"><h2 id="t-recap">Récapitulatif et note finale</h2>
      <p class="small">Les questions non validées comptent comme fausses. Chaque partie est ramenée sur 20, puis pondérée par sa durée conseillée.</p></header>
    <div id="exam-submit-wrap">
      <p class="es-lead">Ta copie n'est pas encore corrigée : aucune réponse n'est verrouillée, tu peux encore revenir sur les questions et les tracés.</p>
      <button type="button" class="btn btn-exam" id="exam-submit">J'ai fini, je fais corriger ma copie</button>
      <p class="es-warn" id="exam-warn" role="alert"></p>
    </div>
    <div id="recap-graded">
      <div class="recap-wrap">
        <table class="t recap-table">
          <thead><tr><th>Partie</th><th>Durée</th><th>Poids</th><th>Points</th><th>Note /20</th><th>Contribution</th></tr></thead>
          <tbody id="recap-body"></tbody>
          <tfoot><tr><th colspan="4">Note globale pondérée</th><th class="final-note"></th><th></th></tr></tfoot>
        </table>
      </div>
      <p class="final-detail small"></p>
    </div>
    <div class="recap-foot" id="recap-foot"><button type="button" class="btn btn-print">Imprimer ma copie</button>
      <span class="small no-print">L'impression reprend tes réponses, les corrections, tes tracés et ce récapitulatif.</span></div>
  </section>
</main>

<footer class="banner" aria-label="Suivi de la composition">
  <div class="score-block"><div class="lab">Note provisoire</div><div class="score" id="score-val">–<small>/20</small></div></div>
  <div class="exam-block"><div class="lab">Mode examen</div><div class="exam-state">Note masquée</div></div>
  <div class="timer-block"><div class="lab">Temps</div><div class="timer" id="timer-val">0:00:00</div></div>
  <div class="count" id="score-count" aria-live="polite"></div>
  <div class="spacer"></div>
  <button type="button" class="btn-docs" id="btn-docs">Documents</button>
</footer>
"""

# ---------------------------------------------------------------------------
# Configuration JS
# ---------------------------------------------------------------------------
parts_cfg = [{k: p[k] for k in ("num", "title", "minutes", "duration", "points")} for p in PARTS]
qcfg = {qid: {"label": Q[qid]["label"], "part": Q[qid]["part"], "pts": Q[qid]["pts"], "grader": Q[qid]["grader"]}
        for qid in ORDER}
skcfg = {s["id"]: {"bg": s["bg"], "deps": s["deps"], "label": s["label"], "part": s["part"], "pts": s["pts"],
                   "criteria": s["criteria"]} for s in SKETCHES}


def js(o):
    return json.dumps(o, ensure_ascii=False)


CONFIG_SCRIPT = ("<script>window.__PARTS__ = " + js(parts_cfg) + ";\nwindow.__QCFG__ = " + js(qcfg) +
                 ";\nwindow.__SKCFG__ = " + js(skcfg) + ";</script>")

DECOR_JS = """  /* Repères lus sur le fond du DR (pixels de l'image) :
       CAN.top / CAN.bot : traits +2 V et −2 V ; CAN.x0 / CAN.x1 : début et fin de la fenêtre de 4 ms
       CAN.ts : instants d'échantillonnage à 0,125 ms (rangs pairs = traits gris, à 0,25 ms)
       CAN.ys : ordonnée de la courbe analogique à ces instants */
  var CAN = { top: %(top)d, bot: %(bot)d, x0: 103, x1: 1017,
    ts: %(ts)s,
    ys: %(ys)s };
  function canBand() { return (CAN.bot - CAN.top) / 32; }
  function canFrame(c) {
    line(c, CAN.x0, CAN.top, CAN.x1, CAN.top, "#1C2530", 1.6);
    line(c, CAN.x0, CAN.bot, CAN.x1, CAN.bot, "#1C2530", 1.6);
    text(c, "+2 V", 94, CAN.top, "#1C2530", 22, "right", "700");
    text(c, "−2 V", 94, CAN.bot, "#1C2530", 22, "right", "700");
  }
  function canGrid(c) {
    var b = canBand(), k, j;
    for (k = 1; k < 32; k++) line(c, CAN.x0, CAN.top + k * b, CAN.x1, CAN.top + k * b, "rgba(198,40,40,.5)", 1);
    for (j = 0; j < 32; j++) {
      var code = (31 - j).toString(2); while (code.length < 5) code = "0" + code;
      text(c, code, 1026, CAN.top + (j + 0.5) * b, CORR, 14, "left", "700");
    }
  }
  function canStairs(c, step) {
    var b = canBand(), prev = null, i;
    for (i = 0; i < CAN.ts.length; i += step) {
      var xa = CAN.ts[i], xb = i + step < CAN.ts.length ? CAN.ts[i + step] : CAN.x1;
      var y = CAN.top + Math.round((CAN.ys[i] - CAN.top) / b) * b;
      if (prev !== null) line(c, xa, prev, xa, y, CORR, 3.4);
      line(c, xa, y, xb, y, CORR, 3.4);
      dot(c, xa, CAN.ys[i], 5, CORR);
      prev = y;
    }
  }
  var DECOR = {
    CAN5: {
      pad: { t: 12, r: 12, b: 12, l: 12 }, rs: 2,
      decorate: canFrame,
      correction: function (c) { canGrid(c); canStairs(c, 2); }
    },
    CAN5X2: {
      pad: { t: 12, r: 12, b: 12, l: 12 }, rs: 2,
      decorate: canFrame,
      correction: function (c) {
        for (var i = 1; i < CAN.ts.length; i += 2) line(c, CAN.ts[i], CAN.top, CAN.ts[i], CAN.bot, CORR, 1.4, [8, 6]);
        canGrid(c); canStairs(c, 1);
      }
    }
  };
""" % {"top": TOP, "bot": BOT, "ts": js(CAN_TS), "ys": js(CAN_YS)}

DR_NAMES_JS = """  var DR_NAMES = {
    CAN5: { doc: "DR1", q: "Q2.3", t: "Numérisation sur 5 bits", scale: false },
    CAN5X2: { doc: "DR2", q: "Q3.2", t: "Numérisation sur 5 bits, fréquence d'échantillonnage doublée", scale: false }
  };
"""


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------
def must_sub(pattern, repl, s, flags=re.S):
    out, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    assert n == 1, "motif introuvable dans le gabarit : " + pattern
    return out


def build():
    g = open(GABARIT, encoding="utf-8").read()
    style = re.search(r"<style>:root.*?</style>", g, re.S).group(0)
    scripts = re.findall(r"<script>.*?</script>", g, re.S)
    grading = next(s for s in scripts if "/*GRADING-START*/" in s)
    app = next(s for s in scripts if "var QCFG = window.__QCFG__" in s)

    # Zones propres au sujet dans le moteur applicatif
    app = must_sub(r"var CONSEIL_MIN = \d+;", "var CONSEIL_MIN = %d;" % TOTAL_MIN, app)
    app = must_sub(r"  var DECOR = \{.*?\n  \};\n", DECOR_JS, app)
    app = must_sub(r"  var DR_NAMES = \{.*?\n  \};\n", DR_NAMES_JS, app)
    app = must_sub(r"<p>Quatre pages, une par document,",
                   "<p>' + order.length + ' page' + (order.length > 1 ? 's' : '') + ', une par document,", app)

    html = "\n".join([
        "<!DOCTYPE html>",
        '<html lang="fr">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        HEAD_COMMENT,
        "<title>%s — exercice interactif</title>" % TITLE,
        '<meta name="description" content="Échantillonnage, quantification, résolution d\'un convertisseur '
        'analogique/numérique et taille mémoire d\'un signal numérisé.">',
        style,
        HOME_FIT_CSS,
        "</head>",
        '<body class="no-mode">',
        DOCS_HTML,
        HOME_HTML,
        MAIN_HEAD,
        "".join(body_parts),
        RECAP_AND_BANNER,
        CONFIG_SCRIPT,
        grading,
        app,
        "</body>",
        "</html>",
        "",
    ])
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("écrit :", OUT, "(%d octets)" % len(html.encode("utf-8")))
    print("points par partie :", [(p["num"], p["points"], p["minutes"]) for p in PARTS])


if __name__ == "__main__":
    build()
