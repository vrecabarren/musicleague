lint:
	flake8 feedback --ignore=F821,E123,W292,W391,E731

unit:
	nosetests --logging-level=ERROR
