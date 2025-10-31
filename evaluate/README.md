# Capturing interactions in EMISSOR
This subproject shows how interactions can be captured in EMISSOR.

## Requirements

Before opening the  notebooks, make sure Jupyter is running in a virtual environment with the packages installed from the ```requirements.txt``` file.

Using venv:
   ```
    python -m venv --python=3.11 emissor
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=emissor
   ```


Using Conda:
```
    conda create -n emissor python=3.11
    conda activate emissor
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=emissor
```

With the environment active, launch Jupyter lab from the CLI.
