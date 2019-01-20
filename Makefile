install:
	python setup.py install

deploy:
	python setup.py sdist bdist_wheel
	twine upload dist/*
