run:
	python manage.py runserver

shell:
	python manage.py shell

makemigrations:
	python manage.py makemigrations

migrate1:
	python manage.py migrate

migrate: makemigrations \
	migrate1
