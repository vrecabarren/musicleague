install:
	pip install -r requirements_dev.txt
	pip install -r requirements.txt

lint:
	flake8 feedback app.py --ignore=F821,E123,W292,W391,E731 --exclude=feedback/api.py

run:
	python app.py

unit:
	nosetests --logging-level=ERROR
