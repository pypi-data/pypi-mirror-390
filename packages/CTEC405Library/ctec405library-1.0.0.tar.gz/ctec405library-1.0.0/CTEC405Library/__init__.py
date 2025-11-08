import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import nltk
try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    nltk.download('popular')
from .Functions import enableLogging, disableLogging, printTable, printVariable, readExcelSpreadsheet, encodeLabels, readImages, getPrompt, getRootWords
from .Architectures import feedForwardNN
