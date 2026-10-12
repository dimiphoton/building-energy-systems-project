# Journal de développement

## 2026-10-12 — Initialisation du projet

- Repo créé à partir du template portfolio.

## 2026-10-12 — Bilan thermique ETA013, variante du 29 août 1986

- Date lue comme 1986, 08, 29 : a = 0, b = 8, c = 2, d = 9. Ville n° 29 =
  Danderyd, année Sveby 2017, consigne 22 °C, PAC air-air COP 3.
- La liste des villes n'était pas dans le PDF. On aligne la numérotation
  sur les lieux SMHI du DVUT Boverket, sans Abisko, parce que le n° 14
  tombe alors sur Bjurholm.
- Résultat : Um = 0,589 W/(m²·K), Tb = 18,2 °C, DVUT 7 jours = −10,7 °C,
  puissance sans apports = 46,5 kW, déficit corrigé = 81,7 MWh, EP = 108
  kWh/m²·an, classe E. L'eau chaude électrique pèse plus que le chauffage
  dans l'EP, parce que la PAC ne couvre que les radiateurs.
- Code en fonctions courtes, tests sur les formules et sur le cas complet.
- Le rapport rendu est aussi un PDF LaTeX
  (`docs/report/assignment-report.pdf`), mêmes chiffres que le Markdown.
