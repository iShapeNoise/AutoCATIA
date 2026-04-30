AutoCATIA
=============

!!!NOTICE: This is a customized version of [pycatia-tools](https://github.com/evereux/pycatia-tools/)

Introduction
============
A web based python application built with
[Flask](https://flask.palletsprojects.com/en/latest/), [HTMX](https://htmx.org/)
and [hyperscript](https://hyperscript.org) to interface with CATIA V5 using the
python library [pycatia](https://pycatia.readthedocs.io/en/latest/).

The application contains a collection of tools to speed up common tasks.

Sections:
* Documents >> List of all files opened in CATIA with save options
* Part >> Create and edit Part files
* Product >> Create and edit Product files
* Drawing >> Create and edit Drawings, Pages, Views, and B.O.M.s
* Tools >> Little helper programs like Image-to-Sketch converter s.o.
* Settings >> Company specific settings like logo and template layouts s.o.


AutoCATIA has been built such that adding additional functionality to suit
your purposes is a straight forward process. There is currently no guide
supporting this. However, reading the source code should give enough hints on
how to add functionality.


Requirements
============

* Windows 7 or higher.
* python >= 3.11 (earlier versions upto 3.9 may work but not yet tested)
* CATIA V5 must already be running.


Installation
============

Clone this repository using [git cmd](https://git-scm.com/):

```
git clone https://github.com/iShapeNoise/AutoCATIA.git
```

Change directory to the project folder and create a
[virtual environment](https://docs.python.org/3/library/venv.html) for the
project.

```
python -m venv env
```

Activate the virtual environment

```
env\Scripts\activate.bat
```

Install the requirements.

```
pip install -r requirements.txt
```

Running
-------

To run the application:

```
flask run
```
Open a web browser and access the url https://127.0.0.1:5578
