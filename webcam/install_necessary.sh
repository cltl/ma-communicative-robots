sudo apt install ffmpeg
python -m pip install ipywebrtc jupyter av librosa numpy pillow
python -m jupyter nbextension install --py --symlink --sys-prefix ipywebrtc
python -m jupyter nbextension enable --py --sys-prefix ipywebrtc
# python -m jupyter labextension link js
# python -m jupyter lab --watch  # for quick rebuilds
