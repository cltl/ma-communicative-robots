# AI2Thor interaction and image interpretation

This subproject shows how to interact in the AI2Thor world and process images

## Requirements

Before opening the  notebooks, make sure Jupyter is running in a virtual environment with the packages installed from the ```requirements.txt``` file.

Using venv:
   ```
    python -m venv --python=3.11 aithor
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=aithor
   ```


Using Conda:
```
    conda create -n aithor python=3.11
    conda activate aithor
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=aithor
```

With the environment active, launch Jupyter lab from the CLI.
