# 📘 MkDocs DSFR

![gitlab-pipeline-status](https://img.shields.io/gitlab/pipeline-status/mkdocs%2Fmkdocs-dsfr-men?gitlab_url=https%3A%2F%2Fgitlab.mim-libre.fr)
[![pypi](https://img.shields.io/pypi/v/mkdocs-dsfr-men.svg)](https://pypi.org/project/mkdocs-dsfr-men/)
[![pyversions](https://img.shields.io/pypi/pyversions/mkdocs-dsfr-men.svg)](https://pypi.python.org/pypi/mkdocs-dsfr-men)
[![downloads](https://img.shields.io/pypi/dm/mkdocs-dsfr-men.svg)](https://pypi.org/project/mkdocs-dsfr-men/)
[![license](https://img.shields.io/pypi/l/mkdocs-dsfr-men.svg)](https://pypi.python.org/pypi/mkdocs-dsfr-men)

**MkDocs DSFR** est un portage du
[Système de Design Français](https://www.systeme-de-design.gouv.fr/version-courante/fr) (ou DSFR) sous forme de thème [MkDocs](https://www.mkdocs.org/).

## ⚠️ Utilisation interdite en dehors des sites Internet de l'État

> Il est formellement interdit à tout autre acteur d’utiliser le Système de Design de l’État (les administrations territoriales ou tout autre acteur privé) pour des sites web ou des applications.
>
> Le Système de Design de l’État représente l’identité numérique de l’État. En cas d’usage à des fins trompeuses ou frauduleuses, l'État se réserve le droit d’entreprendre les actions nécessaires pour y mettre un terme.

👉 Voir README du DSFR [ici](https://github.com/GouvernementFR/dsfr/blob/main/README.md#licence-et-droit-dutilisation).

## ⚡ Démarrage rapide

```sh
# 1. Créer un nouveau projet MkDocs sans installation globale
uvx --from mkdocs mkdocs new mon-projet
cd mon-projet

# 2. Ajouter le thème MkDocs DSFR (recommandé : uv)
uv pip install mkdocs-dsfr-men
# Alternative : pip install mkdocs-dsfr-men

# 3. Configurer le thème dans mkdocs.yml
cat > mkdocs.yml << EOF
site_name: Mon Projet

theme:
  name: dsfr
  header:
    service_title: Mon Service
    service_tagline: Description de mon service
EOF

# 4. Lancer le serveur de développement avec le thème
uvx --from mkdocs-dsfr-men mkdocs serve
```

Votre site est maintenant accessible sur `http://localhost:8000`

## 📁 Structure du projet

```text
mkdocs-dsfr/
├── src/             # Code source du thème MkDocs DSFR
├── docs/            # Documentation du thème
├── tests/           # Tests unitaires Python (Pytest) et end-to-end (CodeceptJS)
├── pyproject.toml   # Configuration du package
└── README.md        # Ce fichier
```

## 🚀 Installation

### Prérequis

- Python >= 3.9
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommandé)
- pip (optionnel si vous préférez rester sur pip)

### Installation avec uv (recommandée)

```sh
uv pip install mkdocs-dsfr-men
```

Pour installer une version spécifique depuis le dépôt Git :

```sh
# Branche principale
uv pip install git+https://gitlab.mim-libre.fr/digital-commons/world/european-union/france/administration/education-nationale/projet/produit/mkdocs-dsfr.git

# Branche ou tag spécifique
uv pip install "git+https://gitlab.mim-libre.fr/digital-commons/world/european-union/france/administration/education-nationale/projet/produit/mkdocs-dsfr.git@nom-de-branche"
```

> **Astuce** : `uvx --from mkdocs-dsfr-men mkdocs serve` permet de lancer MkDocs avec le thème sans installation globale supplémentaire.

### Installation via pip (alternative)

```sh
pip install mkdocs-dsfr-men

# Branche principale
pip install git+https://gitlab.mim-libre.fr/digital-commons/world/european-union/france/administration/education-nationale/projet/produit/mkdocs-dsfr.git

# Branche ou tag spécifique
pip install "git+https://gitlab.mim-libre.fr/digital-commons/world/european-union/france/administration/education-nationale/projet/produit/mkdocs-dsfr.git@nom-de-branche"
```

### Installation en mode développement

Pour contribuer au projet ou tester des modifications locales :

```sh
# Cloner le dépôt
git clone https://gitlab.mim-libre.fr/digital-commons/world/european-union/france/administration/education-nationale/projet/produit/mkdocs-dsfr.git
cd mkdocs-dsfr

# Installer en mode éditable (recommandé : uv)
uv pip install
# Alternative : pip install
```

Le mode éditable (`-e`) permet de modifier le code source et de voir les changements immédiatement sans réinstallation.

## ⚙️ Configuration

### Configuration minimale

Dans le fichier de configuration `mkdocs.yml` :

```yaml
site_name: Mon Site

theme:
  name: dsfr
  header:
    service_title: Titre de mon service
    service_tagline: Baseline de mon service
```

### Configuration complète

Pour un exemple de configuration complète, consultez le fichier [`mkdocs.yml`](mkdocs.yml) de ce dépôt.

### Plugins disponibles

Le thème fournit également un plugin MkDocs pour des fonctionnalités avancées :

```yaml
plugins:
  - search
  - dsfr-plugin  # Plugin DSFR pour fonctionnalités supplémentaires
```

## 📚 Documentation

- **Documentation du thème** : Consultez [`docs/`](docs/) pour la documentation complète du thème
- **Tests** : Voir [`tests/codeceptjs/README.md`](tests/codeceptjs/README.md) pour la documentation des tests E2E

## 🧪 Tests

Toutes les commandes doivent être exécutées depuis la racine du dépôt et passent par le Taskfile.

### Préparer l’environnement

```sh
task dev:up
```

### Lancer la suite complète (build + déploiement + Pytest + CodeceptJS)

```sh
task devsecops
```

ou

```sh
task test:tdd
```

### Lancer uniquement les tests unitaires

```sh
task test:pytest
```

### Lancer uniquement les tests end-to-end

```sh
task test:codeceptjs
```

Pour plus de détails sur les tests E2E, consultez la [documentation dédiée](tests/codeceptjs/README.md).

## 🤝 Contribuer

Consultez le guide [CONTRIBUTING.md](CONTRIBUTING.md) pour savoir comment contribuer au projet.
