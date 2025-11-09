   ## Documentation

The functions in the package are documented. The documentation in nicely formatted form can be obtained by running `sphinx`. 

First of all, install sphinx and a good theme:
```
pip install sphinx
pip install pydata_sphinx_theme
```

In the `pystran` folder, run
```
sphinx-apidoc -o docs/source pystran/ -e
```
which will create the `.rst` files

Then, go into the `pystran/docs` folder, 
```
cd docs/
```
and run
```
sphinx-build.exe -M html source build
```
Or, in one shot `(cd docs; sphinx-build.exe -M html source build)`.

Now the documentation will be in `pystran/docs/build/html`.
Double click the `index.html` file in that folder.
