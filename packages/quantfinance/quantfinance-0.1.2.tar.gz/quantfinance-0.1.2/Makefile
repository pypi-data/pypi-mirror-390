.PHONY: help install install-dev test test-cov lint format clean build docs serve-docs

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
PYLINT := $(PYTHON) -m pylint

# Couleurs pour l'affichage
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Affiche l'aide
	@echo "$(BLUE)Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Installe le package
	@echo "$(BLUE)Installation du package...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)✓ Installation terminée$(NC)"

install-dev: ## Installe le package avec les dépendances de développement
	@echo "$(BLUE)Installation en mode développement...$(NC)"
	$(PIP) install -e ".[dev,docs,data,viz]"
	$(PIP) install pre-commit
	pre-commit install
	@echo "$(GREEN)✓ Installation dev terminée$(NC)"

test: ## Lance les tests
	@echo "$(BLUE)Lancement des tests...$(NC)"
	$(PYTEST) tests/ -v
	@echo "$(GREEN)✓ Tests terminés$(NC)"

test-cov: ## Lance les tests avec couverture
	@echo "$(BLUE)Lancement des tests avec couverture...$(NC)"
	$(PYTEST) tests/ -v --cov=quantfinance --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/$(NC)"

test-fast: ## Lance les tests rapides (sans les tests lents)
	@echo "$(BLUE)Lancement des tests rapides...$(NC)"
	$(PYTEST) tests/ -v -m "not slow"
	@echo "$(GREEN)✓ Tests rapides terminés$(NC)"

test-watch: ## Lance les tests en mode watch
	@echo "$(BLUE)Mode watch activé...$(NC)"
	$(PYTEST) tests/ -v --watch

lint: ## Vérifie le code avec flake8
	@echo "$(BLUE)Vérification du code avec flake8...$(NC)"
	$(FLAKE8) quantfinance tests
	@echo "$(GREEN)✓ Linting terminé$(NC)"

type-check: ## Vérifie les types avec mypy
	@echo "$(BLUE)Vérification des types...$(NC)"
	$(MYPY) quantfinance
	@echo "$(GREEN)✓ Type checking terminé$(NC)"

pylint: ## Vérifie le code avec pylint
	@echo "$(BLUE)Vérification avec pylint...$(NC)"
	$(PYLINT) quantfinance
	@echo "$(GREEN)✓ Pylint terminé$(NC)"

format: ## Formate le code avec black et isort
	@echo "$(BLUE)Formatage du code...$(NC)"
	$(BLACK) quantfinance tests examples
	$(ISORT) quantfinance tests examples
	@echo "$(GREEN)✓ Formatage terminé$(NC)"

format-check: ## Vérifie le formatage sans modifier
	@echo "$(BLUE)Vérification du formatage...$(NC)"
	$(BLACK) --check quantfinance tests examples
	$(ISORT) --check-only quantfinance tests examples
	@echo "$(GREEN)✓ Vérification terminée$(NC)"

check-all: format-check lint type-check ## Lance toutes les vérifications
	@echo "$(GREEN)✓ Toutes les vérifications sont passées$(NC)"

clean: ## Nettoie les fichiers temporaires
	@echo "$(BLUE)Nettoyage...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf build dist htmlcov .coverage coverage.xml
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

build: clean ## Construit le package
	@echo "$(BLUE)Construction du package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Package construit dans dist/$(NC)"

docs: ## Génère la documentation
	@echo "$(BLUE)Génération de la documentation...$(NC)"
	cd docs && make html
	@echo "$(GREEN)✓ Documentation générée dans docs/_build/html/$(NC)"

serve-docs: docs ## Sert la documentation localement
	@echo "$(BLUE)Serveur de documentation démarré sur http://localhost:8000$(NC)"
	cd docs/_build/html && $(PYTHON) -m http.server 8000

publish-test: build ## Publie sur TestPyPI
	@echo "$(BLUE)Publication sur TestPyPI...$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Publié sur TestPyPI$(NC)"

publish: build ## Publie sur PyPI
	@echo "$(YELLOW)⚠️  Publication sur PyPI (production)$(NC)"
	@read -p "Êtes-vous sûr? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -m twine upload dist/*; \
		echo "$(GREEN)✓ Publié sur PyPI$(NC)"; \
	else \
		echo "$(RED)Publication annulée$(NC)"; \
	fi

run-examples: ## Lance tous les exemples
	@echo "$(BLUE)Exécution des exemples...$(NC)"
	@for file in examples/*.py; do \
		echo "$(YELLOW)Exécution de $$file...$(NC)"; \
		$(PYTHON) $$file; \
	done
	@echo "$(GREEN)✓ Tous les exemples ont été exécutés$(NC)"

benchmark: ## Lance les benchmarks de performance
	@echo "$(BLUE)Lancement des benchmarks...$(NC)"
	$(PYTHON) -m pytest tests/ -v --benchmark-only
	@echo "$(GREEN)✓ Benchmarks terminés$(NC)"

security: ## Vérifie les vulnérabilités de sécurité
	@echo "$(BLUE)Vérification de sécurité...$(NC)"
	$(PYTHON) -m bandit -r quantfinance
	$(PYTHON) -m safety check
	@echo "$(GREEN)✓ Vérification terminée$(NC)"

init-project: ## Initialise un nouveau projet
	@echo "$(BLUE)Initialisation du projet...$(NC)"
	git init
	$(MAKE) install-dev
	pre-commit install
	@echo "$(GREEN)✓ Projet initialisé$(NC)"

docker-build: ## Construit l'image Docker
	@echo "$(BLUE)Construction de l'image Docker...$(NC)"
	docker build -t quantfinance:latest -f docker/Dockerfile .
	@echo "$(GREEN)✓ Image Docker construite$(NC)"

docker-run: ## Lance le container Docker
	@echo "$(BLUE)Lancement du container Docker...$(NC)"
	docker run -it --rm -v $(PWD):/app quantfinance:latest
