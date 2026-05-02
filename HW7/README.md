HW7 – Information Retrieval and Machine Learning

This project implements a complete text classification pipeline using the CRANFIELD dataset and machine learning techniques.

## Components
- doc-term.py → document preprocessing
- EmailFilter.py → spam filtering dataset preparation
- FeatureMatrix.py → feature extraction using Elasticsearch
- Indexer.py → indexing documents into Elasticsearch
- MachineLearning.py → classification model training and evaluation
- Tagger.py → labeling utility

## Dataset
- CRANFIELD collection (cran.all.1400)
- Relevance judgments (cranqrel)

## Requirements
pip install scikit-learn numpy pandas elasticsearch bs4 nltk

## Execution Order
1. Indexer.py
2. FeatureMatrix.py
3. MachineLearning.py

## Output
- Feature matrix CSV
- Classification accuracy results
- Ranked retrieval outputs
