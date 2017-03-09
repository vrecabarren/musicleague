ci: install lint unit

cleandb:
	mongo test --eval "db.dropDatabase();"

install:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt
	npm install

lint:
	flake8 musicleague app.py --ignore=E731

logs:
	heroku logs -n 1500

react:
	babel musicleague/static/jsx -d musicleague/static/js/react

run:
	heroku local

unit:
	nosetests --with-coverage --logging-level=ERROR
