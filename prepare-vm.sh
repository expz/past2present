gsutil -m cp gs://dataproc-initialization-actions/jupyter/jupyter.sh .
chmod a+x jupyter.sh

sudo su root

./jupyter.sh

apt-get install -y --no-install-recommends ffmpeg

/opt/conda/bin/conda install --quiet --yes \
    'conda-forge::blas=*=openblas' \
    'ipywidgets=7.2*' \
    'pandas=0.23*' \
    'numexpr=2.6*' \
    'matplotlib=2.2*' \
    'scipy=1.1*' \
    'seaborn=0.9*' \
    'scikit-learn=0.20*' \
    'scikit-image=0.14*' \
    'sympy=1.1*' \
    'cython=0.28*' \
    'patsy=0.5*' \
    'statsmodels=0.9*' \
    'cloudpickle=0.5*' \
    'dill=0.2*' \
    'numba=0.38*' \
    'bokeh=0.13*' \
    'sqlalchemy=1.2*' \
    'hdf5=1.10*' \
    'h5py=2.7*' \
    'vincent=0.4.*' \
    'beautifulsoup4=4.6.*' \
    'protobuf=3.*' \
    'xlrd' \
    'tensorflow=1.11*' \
    'keras=2.2*' \
    'numpy' \
  && /opt/conda/bin/conda remove --quiet --yes --force qt pyqt \
  && /opt/conda/bin/python -c 'import matplotlib.pyplot'  # Builds font cache.

/opt/conda/bin/conda install -c conda-forge spacy

/opt/conda/bin/python -m spacy download en_core_web_lg

# Workaround for https://github.com/explosion/spaCy/issues/2995
/opt/conda/bin/pip install msgpack==0.5.6

/opt/conda/bin/pip install \
    future \
    backports.csv \
    beautifulsoup4 \
    lxml \
    feedparser \
    pdfminer.six \
    nltk \
    python-docx \
    cherrypy \
  && /opt/conda/bin/pip install --no-deps pattern
 
/opt/conda/bin/pip install benepar \
  && /opt/conda/bin/python -c "import benepar; benepar.download('benepar_en')"

/opt/conda/bin/conda install --yes -c pytorch pytorch-nightly-cpu \
  && /opt/conda/bin/conda install --yes -c fastai fastai

/opt/conda/bin/conda clean -tipsy
