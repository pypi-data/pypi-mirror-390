.PHONY: all

all: tests

######## Setup ########

VERSION = 1.0.1
DIST=dist/basil_core-${VERSION}.tar.gz
version: clean
	sed --in-place "s/version = .*/version = \"${VERSION}\"/g" pyproject.toml
	sed --in-place "s/ version: .*/ version: '${VERSION}',/g" meson.build
	echo "__version__ = '${VERSION}'" > __version__.py
	echo "__version__ = '${VERSION}'" > src/basil_core/__version__.py
EXAMPLE_LOCATION = ./

######## Installation ########
$(DIST): clean version
	- git add src meson.build __version__.py
	- git commit
	python3 -m build

install: $(DIST)
	python3 -m pip install $(DIST)

testpypi: tests
	python3 -m twine upload --repository testpypi $(DIST)

pypi: testpypi
	python3 -m twine upload $(DIST)

######## Tests ########
test_coordinates: install
	python3 $(EXAMPLE_LOCATION)/tests/test_coordinates.py

test_distance: install
	python3 $(EXAMPLE_LOCATION)/tests/test_distance.py

test_orbit: install
	python3 $(EXAMPLE_LOCATION)/tests/test_orbit.py

test_hypercube: install
	python3 $(EXAMPLE_LOCATION)/tests/test_hypercube.py

test_random: install
	python3 $(EXAMPLE_LOCATION)/tests/test_random.py

test_callister: install
	python3 $(EXAMPLE_LOCATION)/tests/test_callister_priors.py

# This is not one of the required unit tests because it depends on
# the gaussian process code
test_histogram_overhang: install
	python3 $(EXAMPLE_LOCATION)/tests/test_histogram_overhang.py

test_corner: install
	python3 $(EXAMPLE_LOCATION)/tests/test_corner.py

test_indexer: install
	python3 $(EXAMPLE_LOCATION)/tests/test_indexer.py

test_schechter: install
	python3 ${EXAMPLE_LOCATION}/tests/test_schechter.py

test_relations: install
	mkdir -p ${EXAMPLE_LOCATION}/data
	python3 ${EXAMPLE_LOCATION}/tests/test_relations.py

tests: test_coordinates test_distance test_orbit test_random test_callister test_indexer test_schechter
#tests: test_coordinates test_distance test_orbit test_random test_callister test_corner test_indexer test_schechter

######## Clean ########
clean:
	rm -rf $(EXAMPLE_LOCATION)/src/*.egg-info
	rm -rf $(EXAMPLE_LOCATION)/dist
	rm -rf $(EXAMPLE_LOCATION)/build
	rm -rf ${EXAMPLE_LOCATION}/data/*
