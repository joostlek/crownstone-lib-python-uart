To run the Crownstone Python libraries in a virtual environment, follow these steps:

Install virtualenv:

```
pip3 install virtualenv
```

Create a virtual environment (python3.5+)

```
virtualenv -p python3.7 venv --no-site-packages
```

Enter the virtual environment

```
source venv/bin/activate
```

Install the dependencies (pick the ble one if you want to use ble)
(pip now defaults to the pip that belongs to the python version you selected)

```
pip install -r requirements.txt
```

