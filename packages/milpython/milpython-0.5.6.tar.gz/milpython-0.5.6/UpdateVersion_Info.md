# MilPython

Uploading a new Version:
1. Change version number in setup.py
2. cmd in diesem Verzeichnis: 
- Version erstellen: python setup.py sdist
- Version testen: pip install ./dist/MilPython-0.0.2.tar.gz
- Version hochladen: py -m twine upload dist/*
3. (Version auf Pc updaten: pip install MilPython -U)