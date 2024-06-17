import os

TOP_PATH = os.path.dirname(os.path.dirname(__file__))
RAW_PATH =  os.path.join(TOP_PATH, 'data', 'raw')
PREPROC_PATH = os.path.join(TOP_PATH, 'data', 'preprocessed')
MODEL_PATH = os.path.join(TOP_PATH, 'models')