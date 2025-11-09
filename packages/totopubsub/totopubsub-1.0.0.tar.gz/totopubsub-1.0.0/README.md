# Toto PubSub for Python

This is the Python implementation of Toto PubSub. 

## Building and Deploying to Pypi
Make sure you have the file `setup.py´ and that the dependencies are setup. <br>
To **build** the package, run: 
```
python setup.py sdist
```

To **upload** the package to PyPi, run:
```
twine upload dist/* 
```

Note that to **publish** packages to PyPi, you need to authenticate via token. <br>
The token needs to be stored in `$HOME/.pypirc` in this format: 
```
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJDMwZDZlMjYzLWExZWUtNGI0ZC......
```
Note that the "username" value is the string `__token__`. The actual token only goes in the password field.

## Additional information
 * [Notes on starting and configuring a Python Virtual Environment](https://snails-shop-mta.craft.me/fo93w8gh34GEUH)
 * [How to build and deploy to Pypi]