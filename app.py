import pandas as pd
import streamlit as st
import pickle
import requests


# Function to fetch the movie poster using TMDB API
def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8646a991b8e16ddbd074ec21f69f942d')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


# Function to recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id  # Fetching the correct movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # Fetch poster from TMDB API
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters


# Streamlit app title
st.title('Movie Recommender System')

# Load movies data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Drop-down to select a movie
selected_movie_name = st.selectbox(
    'WHICH MOVIE YOU WOULD LIKE TO SEE TODAY?',
    movies['title'].values
)

# Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# When the recommend button is clicked
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    # Display recommendations in columns
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
