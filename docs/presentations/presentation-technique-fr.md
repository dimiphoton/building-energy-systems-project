---
marp: true
theme: portfolio
paginate: true
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.40](../../pictures/presentations/photos/building-corridors.png)

# Quelle puissance,
# et quelle classe,
# à Danderyd ?

BI · Bâtiment · Python / pandas / matplotlib

3 étages · 1 350 m² · horaire · 2017

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/building-corridors.png)

# Le symptôme est
# une consigne
# qui lâche.

En dessous de 20 °C par grand froid, le système émetteur est sous-dimensionné ou l'enveloppe fuit trop.

**On cherche la puissance de dimensionnement, puis l'étiquette.**

---

<!-- _class: split -->

![bg right:44%](../../pictures/presentations/photos/building-corridors.png)

# Le résultat sert
# au syndic et
# au bureau d'études.

La copropriété arbitre les travaux. Le calcul suit le sujet ETA013 : DVUT, Um, déficit, EP.

**La date du 29 août 1986 fixe la ville, l'année et la PAC.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/building-corridors.png)

# Les coursives sont
# des dalles qui
# traversent l'isolant.

Ψ = 0,6 W/(m·K) sur 180 m. Le mur lui-même, méthode λ, sort à U = 0,40. Les vitrages sont à 2,9.

---

<!-- _class: split -->

![bg left:42%](../../pictures/presentations/photos/building-corridors.png)

# Une heure,
# une température,
# un bilan.

Sveby 2017 pour Danderyd, 8 760 heures. Année type 1991–2020 pour la correction.

**Saison imposée : 15 septembre – 15 mai. Solaire : la figure du sujet, pas le fichier météo.**

---

<!-- _class: split -->

# On isole le jour
# de dimensionnement
# des apports gratuits.

Puissance de calcul : pas de soleil, pas d'occupants. Tb ne garde que les appareils, 4 W/m².

**Le déficit de saison, lui, compte les trois apports.**

---

<!-- _class: dark -->

# Périmètre tenu.

Puissance à la DVUT. Um. Déficit de saison. EP après correction d'année normale.

Pas de simulation dynamique. Pas de facteur d'utilisation des apports.

---

<!-- _class: chart -->

# La DVUT est plus froide que presque toutes les heures de 2017.

![w:900](../../pictures/presentations/duration-temperature.png)

---

<!-- _class: full -->

![bg brightness:0.42](../../pictures/presentations/photos/building-corridors.png)

# 46,5 kW
# à −10,7 °C.

Um = 0,589 W/(m²·K), au-dessus du 0,40 du neuf. Tb = 18,2 °C. Classe **E**, 108 kWh/m²·an.

---

<!-- _class: chart -->

# H_tr vaut 1 016 W/K. La ventilation en ajoute 407.

![w:900](../../pictures/presentations/design-power-shares.png)

---

<!-- _class: split -->

# 2017 était un peu
# plus doux que
# la normale.

Facteur de correction 1,019 sur les degrés-heures de base Tb. 80,2 MWh deviennent 81,7 MWh.

**Le recalcul direct sur l'année type donne 83,1 MWh. Même ordre.**

---

<!-- _class: chart -->

# L'étiquette E se joue autour de 108. La limite du neuf est 75.

![w:980](../../pictures/presentations/energy-class.png)

---

<!-- _class: split -->

![bg right:40%](../../pictures/presentations/photos/building-corridors.png)

# La PAC ne couvre
# que le chauffage.

COP 3, électricité pondérée 1,8, F_geo = 1,0 à Danderyd.

**Dans l'EP : chauffage 36, eau chaude 45, électricité des communs 27.**

---

<!-- _class: dark -->

# Trois limites,
# dites telles quelles.

La liste des villes n'était pas dans le PDF : n° 29 = Danderyd. Le solaire est lu sur la figure, à ± 5 W/m². Le COP 3 tient encore à la DVUT, ce qui est optimiste.

---

<!-- _class: full -->

![bg brightness:0.40](../../pictures/presentations/photos/building-corridors.png)

# Récupérer l'air extrait
# économise plus
# que les coursives.

Les trois gestes ensemble : −60 MWh, classe D. L'eau chaude électrique empêche d'atteindre C.

---

<!-- _class: actions -->

# Les leviers, dans l'ordre du mégawattheure.

**Air extrait, récupération 80 %** — environ 29 MWh.

**Vitrage U = 1,0** — environ 26 MWh.

**Ψ des coursives à 0,20** — environ 8 MWh.

---

<!-- _class: cta -->

![bg brightness:0.32](../../pictures/presentations/photos/building-corridors.png)

# Reprendre le calcul.

```bash
pip install -e ".[dev]"
python -m building_energy.cli
pytest
```

[Code](https://github.com/dimiphoton/building-energy-systems-project)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2-150458?logo=pandas&logoColor=white)
![matplotlib](https://img.shields.io/badge/matplotlib-3-11557c?logo=matplotlib&logoColor=white)
