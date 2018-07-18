import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from scipy import spatial
import json
import operator

credits=pd.read_csv("C:\\Users\\User\\Downloads\\TMDB\\tmdb_5000_movies.csv")
movies=pd.read_csv("C:\\Users\\User\\Downloads\\TMDB\\tmdb_5000_credits.csv")

x=['genres', 'keywords', 'production_companies', 'production_countries']
for i in x:
    credits[i]=credits[i].apply(json.loads)

def json_to_str(a):
    for index,i in zip(credits.index, credits[a]):
        list1=[]
        for j in i:
            list1.append((j['name']))# the key 'name' contains the name of the coloumn passed
        credits.loc[index, a]=str(list1)
for i in x:
    json_to_str(i)

x=['cast', 'crew']
for i in x:
    movies[i]=movies[i].apply(json.loads)

for index,i in zip(movies.index, movies['cast']):
    list1=[]
    for j in i:
        list1.append(j['name'])
    movies.loc[index,'cast']=str(list1)

for index,i in zip(movies.index, movies['crew']):
    list1=[]
    for j in i:
        if j['job']=='Director':
            list1.append(j['name'])
    movies.loc[index,'crew']=str(list1)

movies.rename(columns={'crew':'director'},inplace=True)
movies_new=credits.merge(movies, left_on='id',right_on='movie_id',how='left')
movies_new=movies_new[['id','original_title','genres','cast','vote_average','director','keywords']]

movies_new['genres']=movies_new['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
movies_new['genres']=movies_new['genres'].str.split(',')

genreList = []
for index, row in movies_new.iterrows():
    genres = row["genres"]

    for i in genres:
        if i not in genreList:
            genreList.append(i)


def binary(genres_of_movie):
    binaryList = []

    for i in genreList:
        if i in genres_of_movie:
            binaryList.append(1)
        else:
            binaryList.append(0)

    return binaryList

movies_new['binarylist']=movies_new['genres'].apply(lambda x: binary(x))

movies_new['keywords']=movies_new['keywords'].str.strip('[]').str.replace(' ','').str.replace("'",'').str.replace('"','')
movies_new['keywords']=movies_new['keywords'].str.split(',')

castList = []
for index, row in movies_new.iterrows():
    cast = row['cast']

    for i in cast:
        if i not in castList:
            castList.append(i)

key_wordList = []
for index, row in movies_new.iterrows():
    keywords = row['keywords']

    for i in keywords:
        if i not in key_wordList:
            key_wordList.append(i)


def binary2(data):
    binaryList = []

    for i in castList:
        if i in data:
            binaryList.append(1)
        else:
            binaryList.append(0)

    return binaryList

movies_new['binary_cast']=movies_new['cast'].apply(lambda x: binary2(x))


def binary3(data):
    binaryList = []

    for i in key_wordList:
        if i in data:
            binaryList.append(1)
        else:
            binaryList.append(0)

    return binaryList

movies_new['binary_keywords']=movies_new['keywords'].apply(lambda x: binary3(x))

movies_new['director']=movies_new['director'].str.strip('[]').str.replace(' ','').str.replace("'",'')
movies_new['director']=movies_new['director'].str.split(',')

DirectorList = []
for index, row in movies_new.iterrows():
    director = row['director']

    for i in director:
        if i not in DirectorList:
            DirectorList.append(i)


def binary4(data):
    binaryList = []

    for i in DirectorList:
        if i in data:
            binaryList.append(1)
        else:
            binaryList.append(0)

    return binaryList

movies_new['binary_director']=movies_new['director'].apply(lambda x: binary4(x))

movies_new=movies_new[['id', 'original_title','genres','binarylist','cast','binary_cast','director','binary_director','keywords', 'binary_keywords', 'vote_average']]
movies_new['id']=list(range(0, len(movies_new)))
movies_new.rename(columns={'binarylist':'binary_gen'},inplace=True)

def Similarity(movieId1, movieId2):
    a = movies_new.iloc[movieId1]
    b = movies_new.iloc[movieId2]

    genresA = a['binary_gen']
    genresB = b['binary_gen']

    genreDistance = spatial.distance.cosine(genresA, genresB)

    scoreA = a['binary_cast']
    scoreB = b['binary_cast']
    castDistance = spatial.distance.cosine(scoreA, scoreB)

    directA = a['binary_director']
    directB = b['binary_director']
    directorDistance = spatial.distance.cosine(directA, directB)

    wordsA = a['binary_keywords']
    wordsB = b['binary_keywords']
    wordsDistance = spatial.distance.cosine(directA, directB)

    return genreDistance + directorDistance + castDistance + wordsDistance

def getname(name=""):
    name=name.title()
    new_movie = pd.DataFrame(movies_new[movies_new['original_title'].str.contains(name)].iloc[0]).T
    selected = new_movie.iloc[:, [0,1 ,2,6]]
    distances = []
    for index, row in movies_new.iterrows():
        if new_movie['id'].values[0] != row['id']:
            dist = Similarity(new_movie['id'].values[0], row['id'])
            distances.append((row['id'], dist))

    distances.sort(key=operator.itemgetter(1))
    top10 = distances[:10]
    recommended=pd.DataFrame(columns=['Title', 'Genre', 'Director'])
    c=0
    for i in top10:
        recommended.loc[c, 'Title']= movies_new.iloc[i[0]][1]
        recommended.loc[c, 'Genre'] = movies_new.iloc[i[0]][2]
        recommended.loc[c, 'Director'] = movies_new.iloc[i[0]][6]
        c=c+1
    return selected, recommended
