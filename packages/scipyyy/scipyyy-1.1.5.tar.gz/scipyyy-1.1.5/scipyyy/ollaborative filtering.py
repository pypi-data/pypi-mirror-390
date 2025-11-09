#Developing a recommendation system using collaborative filtering approaches. 
import pandas as pd 
import numpy as np 
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.metrics.pairwise import cosine_similarity 
 
df=pd.read_csv("movies1.csv") 
df.head(3) 
 
feature=['keywords','cast','genres','director'] 
 
for i in feature: 
    df[i]=df[i].fillna('') 
 
def combine_features(row): 
    return row['keywords']+" "+row['cast']+" "+row['genres']+" "+row['director'] 
 
df['combined_features']=df.apply(combine_features,axis=1) 
print(df['combined_features'].head()) 
 
df['combined_features'].iloc[1] 
 
cv=CountVectorizer() 
count_matrix=cv.fit_transform(df['combined_features']) 
count_matrix.toarray() 
 
count_matrix.shape 
cosine_sim=cosine_similarity(count_matrix) 
 
cosine_sim 
df[df.title=="Pirates of the Caribbean: At World's End"] 
movies_user_likes="Pirates of the Caribbean: At World's End" 
 
def get_index_from_title(title): 
    return df[df.title==title].index.values[0] 
 
movies_index=get_index_from_title(movies_user_likes) 
movies_index 
 
np.int64(1) 
 
similar_movies=list(enumerate(cosine_sim[movies_index])) 
sorted_similar_movies=sorted(similar_movies,key=lambda x:x[1],reverse=True) 
sorted_similar_movies 
 
def get_title(index): 
  return df[df.index==index]["title"].values[0] 
 
i=0 
for movie in sorted_similar_movies: 
  print(get_title(movie[0])) 
  i=i+1 
  if i>10: 
    break 
