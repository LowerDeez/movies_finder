start:
	# Clean orphan images
	docker system prune
	# Run container
	docker-compose up --build

createsuperuser:
	docker-compose run --user 1000:1000 --rm backend python manage.py createsuperuser

makemigrations:
	docker-compose run --rm backend bash -c "python manage.py makemigrations $(app)"

migrate:
	docker-compose run --user 1000:1000 --rm backend bash -c "python manage.py migrate $(app)"

startapp:
	docker-compose run --user 1000:1000 --rm backend bash -c "python manage.py startapp $(app) apps/$(app)"

start_subapp:
	docker-compose run --user 1000:1000 --rm backend bash -c "python manage.py startapp $(subapp) apps/$(app)/$(subapp)"

create_templates:
	docker-compose run --user 1000:1000 --rm backend bash -c "python manage.py create_templates"

update_project:
	docker-compose run --user 1000:1000 --rm backend bash -c "cd app/deploy && fab update_project"

update_transes:
	docker-compose run --user 1000:1000 --rm backend bash -c "python manage.py update_translation_fields"

shell:
	docker-compose run backend python manage.py shell

frontend_run:
	docker-compose run --user 1000:1000 --rm frontend bash -c "$(cmd)"

backend_manage:
	docker-compose run --user 1000:1000 --rm backend bash -c "python manage.py $(cmd)"

backend_run:
	docker-compose run --rm backend bash -c "$(cmd)"

clean_all_dockers:
	docker system prune
	docker system prune -a
