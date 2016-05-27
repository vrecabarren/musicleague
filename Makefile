ci: install lint unit

install:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt

lint:
	flake8 feedback app.py

run:
	python app.py

unit:
	nosetests --logging-level=ERROR
