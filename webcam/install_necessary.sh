python -m pip install ipywebrtc jupyter
python -m jupyter nbextension install --py --symlink --sys-prefix ipywebrtc
python -m jupyter nbextension enable --py --sys-prefix ipywebrtc
# python -m jupyter labextension link js
# python -m jupyter lab --watch  # for quick rebuilds
