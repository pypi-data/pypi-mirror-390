#Building a natural language processing (NLP) model for sentiment analysis.
from sklearn.datasets import fetch_20newsgroups 
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.naive_bayes import BernoulliNB, MultinomialNB 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import accuracy_score 
newsgroups = fetch_20newsgroups(subset='all') 
X_text = newsgroups.data 
Y = newsgroups.target 
 
vectorizer_binary = CountVectorizer(binary=True) 
vectorizer_counts = CountVectorizer(binary=False) 
 
X1 = vectorizer_binary.fit_transform(X_text) 
X2 = vectorizer_counts.fit_transform(X_text) 
 
Xtrain1, Xtest1, Ytrain1, Ytest1 = train_test_split(X1, Y, test_size=0.2, random_state=42) 
Xtrain2, Xtest2, Ytrain2, Ytest2 = train_test_split(X2, Y, test_size=0.2, random_state=42) 
 
bnb = BernoulliNB() 
mnb = MultinomialNB() 
 
bnb.fit(Xtrain1, Ytrain1) 
mnb.fit(Xtrain2, Ytrain2) 
 
ypred1 = bnb.predict(Xtest1) 
ypred2 = mnb.predict(Xtest2) 
 
acc_bnb = accuracy_score(Ytest1, ypred1)
accuracy_score(Ytest2,ypred2)
