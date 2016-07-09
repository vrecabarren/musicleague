ci: install lint unit

install:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt

lint:
	flake8 feedback app.py

logs:
	heroku logs -n 1500

run:
	heroku local

unit:
	nosetests --with-coverage --logging-level=ERROR
