# Analysing and evaluating interactions
This subproject shows how interactions can be analysed and evaluated. Interactions need to be captured in EMISSOR format as different scenarios.

## Requirements

Before opening the  notebooks, make sure Jupyter is running in a virtual environment with the packages installed from the ```requirements.txt``` file.

Using venv:
   ```
    python -m venv --python=3.11 evaluate
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=evaluate
   ```


Using Conda:
```
    conda create -n evaluate python=3.11
    conda activate evaluate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=evaluate
```

With the environment active, launch Jupyter lab from the CLI.
