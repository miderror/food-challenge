ifneq (,$(wildcard ./.env))
	include .env
	export
endif

COMPOSE_PROJECT_NAME_DEV=food_challenge_dev
COMPOSE_PROJECT_NAME_PROD=food_challenge_prod

COMPOSE_FILE_DEV = docker/docker-compose.dev.yaml
COMPOSE_FILE_PROD = docker/docker-compose.prod.yaml
ENV_FILE = .env

DC_DEV=docker compose -f $(COMPOSE_FILE_DEV) -p $(COMPOSE_PROJECT_NAME_DEV) --env-file $(ENV_FILE)
DC_PROD=docker compose -f $(COMPOSE_FILE_PROD) -p $(COMPOSE_PROJECT_NAME_PROD) --env-file $(ENV_FILE)

.PHONY: help \
dev-build dev-up dev-down dev-stop dev-restart dev-logs dev-shell dev-link-images \
dev-startapp dev-makemigrations dev-migrate dev-superuser dev-static dev-seed-products dev-update-facts \
prod-build prod-up prod-down prod-stop prod-restart prod-logs prod-shell \
prod-migrate prod-superuser prod-static prod-seed-products prod-link-images prod-update-facts

# ====================================================================================

dev-build:
	$(DC_DEV) build

dev-up:
	$(DC_DEV) up -d

dev-down:
	$(DC_DEV) down $(args)

dev-stop:
	$(DC_DEV) stop

dev-restart:
	$(DC_DEV) restart $(s)

dev-logs:
	$(DC_DEV) logs -f $(s)

dev-shell:
	$(DC_DEV) exec $(s) sh

dev-startapp:
	$(DC_DEV) exec backend python backend/manage.py startapp $(args)

dev-makemigrations:
	$(DC_DEV) exec backend python backend/manage.py makemigrations $(args)

dev-migrate:
	$(DC_DEV) exec backend python backend/manage.py migrate

dev-superuser:
	$(DC_DEV) exec backend python backend/manage.py createsuperuser

dev-static:
	$(DC_DEV) exec backend python backend/manage.py collectstatic --noinput

dev-seed-products:
	$(DC_DEV) exec backend python backend/manage.py seed_products

dev-link-images:
	$(DC_DEV) exec backend python backend/manage.py link_product_images

dev-update-facts:
	$(DC_DEV) exec backend python backend/manage.py update_product_facts

# ====================================================================================

prod-build:
	$(DC_PROD) build

prod-up:
	$(DC_PROD) up -d

prod-down:
	$(DC_PROD) down $(args)

prod-stop:
	$(DC_PROD) stop

prod-restart:
	$(DC_PROD) restart $(s)

prod-logs:
	$(DC_PROD) logs -f $(s)

prod-shell:
	$(DC_PROD) exec $(s) sh

prod-makemigrations:
	$(DC_DEV) exec backend python backend/manage.py makemigrations $(args)

prod-migrate:
	$(DC_PROD) exec backend python backend/manage.py migrate

prod-superuser:
	$(DC_PROD) exec backend python backend/manage.py createsuperuser

prod-static:
	$(DC_PROD) exec backend python backend/manage.py collectstatic --noinput

prod-seed-products:
	$(DC_PROD) exec backend python backend/manage.py seed_products

prod-link-images:
	$(DC_PROD) exec backend python backend/manage.py link_product_images

prod-update-facts:
	$(DC_PROD) exec backend python backend/manage.py update_product_facts


# ====================================================================================
# === DATABASE & MEDIA MIGRATION ===
# ====================================================================================

DUMP_TABLES = \
	products_productcategory \
	products_product \
	products_product_categories \
	content_aboutproject \
	content_aboutprojectmedia \
	content_bottexts \
	content_faq \
	content_sitesettings

DUMP_FLAGS = $(foreach table,$(DUMP_TABLES),-t $(table))

prod-dump-data:
	@echo "Creating dump for tables: $(DUMP_TABLES)..."
	$(DC_PROD) exec -T -e PGPASSWORD=$(POSTGRES_PASSWORD) db pg_dump -h $(POSTGRES_HOST) -U $(POSTGRES_USER) -d $(POSTGRES_DB) --clean --if-exists $(DUMP_FLAGS) > prod_data_dump.sql
	@echo "Dump saved to prod_data_dump.sql"

prod-restore-data:
	@echo "Restoring data from prod_data_dump.sql..."
	cat prod_data_dump.sql | $(DC_PROD) exec -T -e PGPASSWORD=$(POSTGRES_PASSWORD) db psql -h $(POSTGRES_HOST) -U $(POSTGRES_USER) -d $(POSTGRES_DB)
	@echo "Data restored successfully."

prod-backup-media:
	@echo "Backing up media volume..."
	$(DC_PROD) run --rm --entrypoint tar -v $(shell pwd):/backup backend czvf /backup/prod_media_backup.tar.gz -C /app/backend/media .
	@echo "Media backup saved to prod_media_backup.tar.gz"

prod-restore-media:
	@echo "Restoring media volume..."
	$(DC_PROD) run --rm --entrypoint tar -v $(shell pwd):/backup backend xzvf /backup/prod_media_backup.tar.gz -C /app/backend/media
	@echo "Media restored successfully."
