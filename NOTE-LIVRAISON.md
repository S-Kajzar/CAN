# Note de livraison : convertisseur analogique/numérique

`index.html` est désormais généré à partir du gabarit `source/gabarit-exercice-interactif.html` par `source/build.py`. Le bloc `<style>`, le moteur Grading et le moteur applicatif sont repris du gabarit. Il ne faut pas modifier `index.html` à la main : on modifie `source/build.py`, puis on relance :

```
python3 source/build.py
node source/tests/grading.test.js      # 117 vérifications du moteur de correction
node source/tests/e2e.js               # parcours navigateur (Playwright)
```

## Structure retenue

| Partie | Contenu | Durée | Points | Poids |
|---|---|---|---|---|
| 1 | Analyser le convertisseur 4 bits (Q1.1 à Q1.8) | 20 min | 8 | 33,3 % |
| 2 | Passage sur 5 bits (Q2.1, Q2.2, tracé Q2.3, Q2.4 à Q2.7) | 20 min | 6 + 5 | 33,3 % |
| 3 | Fréquence d'échantillonnage doublée (Q3.1, tracé Q3.2, Q3.3 à Q3.7) | 20 min | 6 + 5 | 33,3 % |

- Il y a 20 questions notées et 2 tracés auto-évalués (5 critères chacun), pour une durée conseillée de 1 h 00.
- Il y a deux documents : DP1 (la courbe et sa numérisation sur 4 bits) et DT1 (caractéristiques et conventions). DR1 et DR2 sont les fonds de tracé.
- Le sujet d'origine n'indiquait aucune durée. Le découpage en 3 × 20 min est un choix, donc une pondération égale entre les parties.

## Erreurs ou imprécisions corrigées dans le source

- **« Les valeurs max et min du signal analogique sont 2 V et −2 V »** : c'est faux, le signal culmine vers +1,65 V. Les ±2 V sont les bornes de la **plage de conversion**. La phrase devient « La plage de conversion s'étend de −2 V à +2 V ».
- **Document réponse sans graduation** : le DR d'origine ne porte ni +2 V ni −2 V. Ces repères et les deux bords de la grille sont redessinés en code (`decorate`), sinon l'élève ne peut pas construire la grille.
- **Axe du temps décalé sur DP1 et sur le DR** : il est tracé environ 0,09 V sous le milieu de la plage ±2 V. On le voit sur DP1, où le « 0 » ne tombe pas sur la frontière 0111/1000. Ce point est signalé sans être corrigé dans l'image. La grille de correction s'appuie sur les bornes ±2 V.

## Décisions d'interprétation

- **Pas (quantum)** : q = plage ÷ 2ⁿ = 4 ÷ 16 = 0,25 V, comme le montrent les 16 bandes égales de DP1. La variante plage ÷ (2ⁿ − 1) ≈ 0,27 V est comptée fausse et commentée dans la démarche.
- **1 ko = 1 024 octets** : c'est la convention imposée par l'énoncé. Il s'agit en toute rigueur du kibioctet (Kio), donc « kio » est accepté. La convention est rappelée dans DT1.
- **Convention de quantification pour la correction des tracés** : on retient le niveau le plus proche de la tension échantillonnée, et ce palier est tenu jusqu'à l'échantillon suivant. C'est la convention de DP1 : la courbe verte la respecte sur 15 des 16 échantillons, et le 16e se trouve sur le passage à 0 V, à l'endroit où l'axe est décalé.
- **Correction des tracés** : les tensions ont été lues automatiquement sur l'image du DR, à ± 0,05 V près. Quelques échantillons tombent presque à mi-chemin entre deux niveaux. Le 5e critère de chaque grille tolère donc un palier décalé d'un niveau dans ce cas.
- **Pas de tolérance sur les nombres entiers** (comptes de bits ou d'octets). Pour les ko, la tolérance est de ± 0,005 : l'arrondi au centième est juste, la troncature (585,93) est fausse.
- **Unités** : les questions de taille mémoire (bits, octets, ko), de période, de fréquence et de pas sont notées à demi-point pour l'unité. Les comptes de valeurs (Q1.2 et Q2.1) et le facteur Q3.7 sont sans unité. Les écritures acceptées pour les unités sont les suivantes :
  - période : ms, µs ou s ;
  - fréquence : kHz ou Hz ;
  - pas : V ou mV ;
  - taille mémoire : bits, Mbit, « millions de bits », octets, ko, kio.
- **Une valeur sans unité n'est acceptée que dans l'unité principale** : « 250 » sans unité ne vaut pas « 250 µs ».

## Mise en page de l'accueil

L'illustration est placée à côté du titre, avec une hauteur limitée, et l'accueil est resserré pour que les boutons de mode soient visibles sans défiler. Ces règles sont dans une feuille de style complémentaire (`HOME_FIT_CSS` dans `build.py`), ajoutée après le `<style>` du gabarit, qui reste inchangé. Sur les petits écrans, les listes des cartes de mode et le sous-titre peuvent être masqués.

## Questions reformulées, découpées ou fusionnées

- **Renumérotation** : le source numérotait de nouveau à partir de Q1 dans chaque étape de la partie 2. Ses étapes deviennent les parties 2 et 3, numérotées Q2.x et Q3.x.
- **Fusion des tracés** : « tracer la grille » et « tracer la courbe numérisée » portaient sur le même dessin. Elles sont fusionnées en un seul tracé par document réponse (Q2.3 sur DR1, Q3.2 sur DR2). Avant, ces questions n'étaient pas notées et se faisaient sur papier. Elles sont maintenant tracées à l'écran et auto-évaluées.

## Questions ajoutées

- **Q3.1** : calcul de la nouvelle période T<sub>e</sub>' = 0,125 ms. Ce résultat est nécessaire au tracé Q3.2, dont la correction ne s'affiche qu'après la validation de Q3.1.
- **Q3.7** : synthèse « par combien la taille du fichier a-t-elle été multipliée ? ». La réponse est × 2,5, soit × 5/4 pour la résolution et × 2 pour la fréquence.

## Points signalés sans modification

- **Vérification des résultats** : tous les résultats numériques du source ont été recalculés et sont justes (64 bits, 4 800 000 bits, 585,94 ko, 80 bits, 6 000 000 bits, 750 000 octets, 732,42 ko, 160 bits, 12 000 000 bits, 1 500 000 octets, 1 464,84 ko).
- **Écart au gabarit dans le moteur** : seules les zones prévues pour chaque sujet ont été adaptées, à savoir `DECOR`, `DR_NAMES` et `CONSEIL_MIN`. `CONSEIL_MIN` passe de 300 à 60 min pour que le chronomètre vire au jaune au bon moment. Une seule autre modification a été faite : le texte « Quatre pages » de la fenêtre « Imprimer les DR » était codé en dur et indique maintenant le nombre réel de DR (2).
- **Saisie `4,8.10^6 bits`** : elle est acceptée, mais `4,8.10^6` sans unité est compté faux. Le moteur lit « 4,8 » suivi de « .e6 » et ne peut pas reconnaître une unité manquante. L'écriture `4,8×10^6` fonctionne dans tous les cas.

## Vérifications faites

- **Tests du moteur de correction** : 117 vérifications. Chaque question a au moins un cas juste et un cas faux, ainsi que des cas limites : virgule, casse, espaces de milliers, notation scientifique, unités absentes ou voisines.
- **Tests Playwright, sans aucune erreur JavaScript** :
  - accueil seul affiché au chargement ;
  - sujet parfait noté 20,0/20 ;
  - demi-point avec le message « Unité manquante » ;
  - verrouillage des réponses validées ;
  - correction d'un tracé retenue tant que ses questions dépendantes ne sont pas validées ;
  - copie imprimée dans les deux états, avec la mention « Copie non corrigée » et aucun corrigé tant que la copie d'examen n'est pas remise ;
  - confirmation en deux temps avant la remise, avec le nombre de réponses vides ;
  - arrêt du chronomètre à la remise ;
  - fenêtre « Imprimer les DR » avec 2 feuilles ;
  - affichage mobile en 390 px sans défilement horizontal ;
  - accueil sans défilement : les deux boutons de mode sont visibles d'emblée, de 360×640 à 1920×950 (hauteurs utiles réelles de navigateur).
- **Poids des images** : environ 0,45 Mo une fois intégrées, pour une limite de 1,5 Mo.
