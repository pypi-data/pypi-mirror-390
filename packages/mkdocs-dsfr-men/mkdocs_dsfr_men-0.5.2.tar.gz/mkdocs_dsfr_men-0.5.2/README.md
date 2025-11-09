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

**Prérequis** :

1. **Python ≥ 3.9** - Vérifiez avec `python3 --version`
    ```sh
    # Ubuntu/Debian
    sudo apt install python3 python3-venv

    # macOS
    brew install python3

    # Windows : téléchargez depuis python.org
    ```

2. **uv** (gestionnaire de paquets moderne) - Vérifiez avec `uv --version`
    ```sh
    # Installation rapide (Linux/macOS)
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Ou via pip
    pip install uv
    ```

**Actions** :

1. Initialiser un nouveau projet avec uv
    ```sh
    uv init --no-workspace mon-projet
    cd mon-projet
    ```

2. Ajouter les dépendances MkDocs et le thème DSFR
    ```sh
    uv add mkdocs mkdocs-dsfr-men
    ```

3. Créer la structure de documentation
    ```sh
    mkdir -p docs
    ```

4. Page d'accueil
    ````sh
    cat > docs/index.md << 'INDEXEOF'
    # Bienvenue

    Bienvenue dans la documentation de mon projet.

    ```dsfr-plugin-alert
    type: warning
    title: "⚠️ Utilisation interdite en dehors des sites Internet de l'État"
    description: Il est formellement interdit à tout autre acteur d’utiliser le Système de Design de l’État (les administrations territoriales ou tout autre acteur privé) pour des sites web ou des applications.
    ```

    ## Navigation rapide

    - [Exemples](exemples.md)
    INDEXEOF
    ````

5. Page d'exemples
    ```sh
    cat > docs/exemples.md << 'EXEOF'
    # Exemples
    EXEOF
    ```

6. Configurer le thème dans mkdocs.yml
    ```sh
    cat > mkdocs.yml << EOF
    ---
    # Project information
    site_name: Mon Projet
    site_url: https://example.com/
    site_description: Description de mon projet
    site_dir: public
    docs_dir: docs

    # Repository
    repo_name: Mon Repo Name
    repo_url: https://gitlab.mim-libre.fr/mon_groupe/mon_projet

    # Theme
    theme:
      name: dsfr
      logo_title: Intitulé<br>Officiel
      header:
        service_title: Mon Service
        service_tagline: Description de mon service

    # Plugins
    plugins:
      - search
      - dsfr-plugin

    # Markdown extensions
    markdown_extensions:
      - attr_list
      - pymdownx.emoji:
          emoji_generator: !!python/name:pymdownx.emoji.to_svg
    EOF
    ```

7. Lancer le serveur de développement
    ```sh
    uv run mkdocs serve --livereload
    ```

Votre site est maintenant accessible sur `http://localhost:8000`

> **💡 Pourquoi uv ?**
> - **Ultra-rapide** : 10-100x plus rapide que pip
> - **Lock file automatique** : `uv.lock` garantit les mêmes versions partout (comme `package-lock.json`)
> - **Environnement virtuel automatique** : `.venv` créé et géré automatiquement
> - **Standard moderne** : utilise `pyproject.toml` (PEP 621)
> - **Commandes simples** : `uv add`, `uv remove`, `uv sync` (comme npm)

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
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (gestionnaire de paquets moderne)

**Installation de uv** :
```sh
# Via curl (recommandé)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

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
uv pip install -e .
# Alternative : pip install -e .
```

Le flag `-e` (mode éditable) permet de modifier le code source du thème et de voir les changements immédiatement sans réinstallation.

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

## 📦 Gestion des dépendances

### Avec uv (recommandé - moderne)

`uv` gère automatiquement `pyproject.toml` et `uv.lock` :

```sh
# Ajouter une dépendance
uv add mkdocs-material  # Ajoute et installe immédiatement

# Ajouter une dépendance de développement
uv add --dev pytest

# Supprimer une dépendance
uv remove mkdocs-material

# Installer toutes les dépendances (comme npm install)
uv sync

# Mettre à jour une dépendance
uv add --upgrade mkdocs mkdocs-dsfr-men
```

**Fichier `pyproject.toml` généré automatiquement** :
```toml
[project]
name = "mon-projet"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "mkdocs>=1.6.1",
    "mkdocs-dsfr-men>=0.4.1",
]
```

### Migration depuis requirements.txt

Si vous avez déjà un `requirements.txt` :

```sh
# Créer le pyproject.toml
uv init --no-workspace

# Importer les dépendances
uv add $(cat requirements.txt | grep -v '^#' | grep -v '^$')
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
