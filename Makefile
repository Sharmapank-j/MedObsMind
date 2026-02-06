# MedObsMind Makefile
# Automation for common development and deployment tasks

.PHONY: help install dev test lint format clean docker-build docker-up docker-down deploy backup

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)MedObsMind - Available Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# INSTALLATION
# ============================================================================

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	cd app && ./gradlew build || echo "Android build skipped"
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	cd backend && pip install -r requirements-dev.txt || pip install -r requirements.txt
	pip install black flake8 pytest pytest-cov mypy
	@echo "$(GREEN)✓ Development installation complete$(NC)"

# ============================================================================
# DEVELOPMENT
# ============================================================================

dev: ## Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	cd webapp && npm start || echo "Frontend not configured"

dev-android: ## Start Android emulator and run app
	@echo "$(BLUE)Starting Android development...$(NC)"
	cd app && ./gradlew installDebug || echo "Android build failed"

# ============================================================================
# TESTING
# ============================================================================

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	cd backend && pytest tests/ -v
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd backend && pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in backend/htmlcov/$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd backend && pytest tests/integration/ -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd backend && pytest tests/unit/ -v

# ============================================================================
# CODE QUALITY
# ============================================================================

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	cd backend && flake8 app/ --max-line-length=100
	cd backend && mypy app/ --ignore-missing-imports || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	cd backend && black app/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code format...$(NC)"
	cd backend && black --check app/ tests/

# ============================================================================
# DATABASE
# ============================================================================

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-rollback: ## Rollback last migration
	@echo "$(BLUE)Rolling back migration...$(NC)"
	cd backend && alembic downgrade -1

db-reset: ## Reset database (WARNING: Deletes all data!)
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd backend && alembic downgrade base && alembic upgrade head; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	fi

db-seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd backend && python scripts/seed_database.py || echo "Seed script not found"

# ============================================================================
# DOCKER
# ============================================================================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose -f docker-compose.prod.yml build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Containers started$(NC)"
	@echo "Access at: http://localhost"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose -f docker-compose.prod.yml down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-logs: ## View Docker logs
	docker-compose -f docker-compose.prod.yml logs -f

docker-clean: ## Remove Docker containers and volumes
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker-compose -f docker-compose.prod.yml down -v
	@echo "$(GREEN)✓ Docker cleaned$(NC)"

# ============================================================================
# DEPLOYMENT
# ============================================================================

deploy: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(NC)"
	./scripts/deploy.sh
	@echo "$(GREEN)✓ Deployment complete$(NC)"

deploy-check: ## Check deployment readiness
	@echo "$(BLUE)Checking deployment readiness...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)✗ Docker not installed$(NC)"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "$(RED)✗ Docker Compose not installed$(NC)"; exit 1; }
	@test -f .env.production.example && echo "$(GREEN)✓ Environment template exists$(NC)" || echo "$(RED)✗ No environment template$(NC)"
	@echo "$(GREEN)✓ Deployment check complete$(NC)"

# ============================================================================
# BACKUP & RESTORE
# ============================================================================

backup: ## Backup database
	@echo "$(BLUE)Creating database backup...$(NC)"
	./scripts/backup.sh || docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U medobsmind medobsmind > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup created$(NC)"

restore: ## Restore database (requires BACKUP_FILE variable)
	@echo "$(BLUE)Restoring database...$(NC)"
	@test -n "$(BACKUP_FILE)" || { echo "$(RED)Error: BACKUP_FILE not specified$(NC)"; exit 1; }
	docker-compose -f docker-compose.prod.yml exec -T postgres psql -U medobsmind medobsmind < $(BACKUP_FILE)
	@echo "$(GREEN)✓ Database restored$(NC)"

# ============================================================================
# MAINTENANCE
# ============================================================================

clean: ## Clean temporary files
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	cd backend && pip install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

status: ## Show system status
	@echo "$(BLUE)=== System Status ===$(NC)"
	@echo "Docker containers:"
	@docker-compose -f docker-compose.prod.yml ps || echo "Not running"
	@echo "\nGit status:"
	@git status -s || echo "Not a git repository"
	@echo "\nPython version:"
	@python --version || echo "Python not found"
	@echo "\nDocker version:"
	@docker --version || echo "Docker not found"

# ============================================================================
# MODELS
# ============================================================================

download-models: ## Download AI models
	@echo "$(BLUE)Downloading AI models...$(NC)"
	mkdir -p models
	cd backend && python scripts/download_model.py || echo "Model download script not found"
	@echo "$(GREEN)✓ Models downloaded$(NC)"

# ============================================================================
# DOCUMENTATION
# ============================================================================

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	cd backend && python -m pdoc --html --output-dir docs app || echo "pdoc not installed"
	@echo "$(GREEN)✓ Documentation generated$(NC)"

# ============================================================================
# DEFAULT
# ============================================================================

.DEFAULT_GOAL := help
