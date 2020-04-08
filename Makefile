.PHONY: ALL
ALL: runserver

.PHONY: clean
clean:
	find . -name *.pyc -delete
	rm -rf venv

venv:
	python3 -m virtualenv venv
	venv/bin/python -m pip install -r requirements.txt

.PHONY: runserver
runserver: venv
	venv/bin/python manage.py migrate
	venv/bin/python manage.py runserver

.PHONY : lint
lint: venv
	venv/bin/python -m pip install flake8
	venv/bin/python -m flake8
