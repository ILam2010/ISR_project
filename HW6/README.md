README_HW6 = 
HW6 - Learning to Rank (Information Retrieval + Machine Learning)

Overview:
This project builds a learning-to-rank system that converts documents into feature vectors and uses machine learning to rank them.

Pipeline:
1. Build term frequency dictionary (totalTF.p)
2. Generate feature matrix (BM25, TF-IDF, Laplace, JM)
3. Create labeled dataset using cranqrel relevance judgments
4. Train machine learning model (Linear Regression)
5. Generate ranked output for evaluation

Features Used:
- BM25
- TF-IDF
- Laplace Smoothing
- Jelinek-Mercer

Machine Learning:
- Linear Regression model
- K-Fold Cross Validation

How to Run:
1. Build term frequencies:
   python build_totalTF.py

2. Create feature matrix:
   python Feature_Matrix.py

3. Train model and generate ranking:
   python ML_Learning_Algorithms.py

Evaluation:
Use trec_eval.pl to evaluate results:
perl trec_eval.pl cranqrel trainingperformance.txt

Output Files:
- staticFeatureMatrix.csv
- trainingperformance.txt
- totalTF.p

Key Idea:
Instead of manually ranking documents, the system learns ranking patterns from data using machine learning.

