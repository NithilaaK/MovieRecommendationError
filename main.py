from flask import Flask, jsonify, request
import csv
from flask_cors import CORS

all_movies = []

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("movies.csv", low_memory=False)
df.dropna()

count = CountVectorizer(stop_words="english")
count_matrix = count.fit_transform(df["title_cl"].values.astype('U'))

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
indices = pd.Series(df.index, index=df['title'])

def get_recommendation(title, cosine_sim):
    idx=indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x:x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    #print(df['title'].iloc[movie_indices])
    return (df['title'].iloc[movie_indices])

output = df[["url", "title", "text", "lang", "total_events"]].head(20).values.tolist()

with open("movies.csv") as f:
    reader = csv.reader(f)
    data = list(reader)
    all_movies = data[1:]

liked_movies = []
not_liked_movies = []
did_not_watch = []

app = Flask(__name__)
cors = CORS(app)

@app.route("/get-movie")
def get_movie():
    global all_movies
    return jsonify({
        "data":all_movies[0],
        "status":"Success"
    })

@app.route("/liked-movie", methods=["POST"])
def liked_movie():
    global all_movies
    movie = all_movies[0]
    all_movies = all_movies[1:]
    liked_movies.append(movie)
    return jsonify({
        "status": "Success"
    }), 201
    
@app.route("/unliked-movie", methods=["POST"])
def unliked_movie():
    global all_movies
    movie = all_movies[0]
    all_movies = all_movies[1:]
    not_liked_movies.append(movie)
    return jsonify({
        "status":"Success"
    }), 201

@app.route("/did-not-watch", methods=["POST"])
def didnotwatch():
    global all_movies
    movie = all_movies[0]
    all_movies = all_movies[1:]
    did_not_watch.append(movie)
    return jsonify({
        "status":"Success"
    }), 201

@app.route("/popular-movies")
def popular_movies():
    movie_data = []
    for movie in output:
        dat = {
            "url": movie[0],
            "title": movie[1],
            "text": movie[2],
            "lang": movie[3],
            "total_events": movie[4]
        }
        movie_data.append(dat)
    return jsonify({
        "data": movie_data,
        "status": "success"
    }), 200

@app.route("/recommended-movies")
def recommended_movies():
    all_recommended = []
    for liked_movie in liked_movies:    
        output = get_recommendation(liked_movie[4])
        for data in output:
            all_recommended.append(data)
    all_recommended.sort()
    import itertools as it
    all_recommended = list(all_recommended for all_recommended,_ in it.groupby(all_recommended))
    movie_data = []
    for recommended in all_recommended:
        dat = {
            "url": recommended[0],
            "title": recommended[1],
            "text": recommended[2],
            "lang": recommended[3],
            "total_events": recommended[4]
        }
        movie_data.append(dat)
    return jsonify({
        "data": movie_data,
        "status": "success"
    }), 200

if __name__ == "__main__":
    app.run()