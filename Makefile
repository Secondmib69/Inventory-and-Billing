up:
	docker compose up -d --build

down:
	docker compose down

migrate:
	docker compose exec django_web python backend/manage.py migrate

shell:
	docker compose exec django_web python backend/manage.py shell