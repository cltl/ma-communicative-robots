# ekg-tutorial

Sample code to use knowledge graphs to represent dialogue

## Description

This repository contains Jupyter notebooks that showcase how to turn dialogue into an RDF graph representation.

## Getting started

### Prerequisites

1. This repository uses Python >= 3.8 . Be sure to run in a virtual python environment (e.g. conda, venv, mkvirtualenv,
   etc.). For example:

   ```bash
   conda create --name ekg-tutorial python=3.8
   conda activate ekg-tutorial
   ```

2. You need to download and run [GraphDB Free](http://graphdb.ontotext.com/). Please create a repository
   called `sandbox`.

### Installation

1. In the root directory of this repo run

    ```bash
    pip install -r requirements.txt
    python -m ipykernel install --name=ekg-tutorial
    ```

### Usage

You may run any of the notebooks by launching the Jupyter Notebook interface:

   ```bash
   jupyter notebook 
   ```

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License.
See [`LICENSE`](https://github.com/selBaez/ekg-tutorial/blob/main/LICENCE) for more information.

## Authors

* [Selene Báez Santamaría](https://selbaez.github.io/)