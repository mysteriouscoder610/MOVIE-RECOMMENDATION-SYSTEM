import pandas as pd
import streamlit as st
import pickle
import requests


# Function to fetch the movie poster using TMDB API
def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8646a991b8e16ddbd074ec21f69f942d')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


# Function to fetch movie details using TMDB API
def fetch_movie_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8646a991b8e16ddbd074ec21f69f942d')
    data = response.json()
    return {
        "overview": data.get("overview", "No description available."),
        "release_date": data.get("release_date", "Unknown"),
        "rating": data.get("vote_average", "N/A"),
    }


# Function to fetch movie trailer from TMDB API
def fetch_trailer(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8646a991b8e16ddbd074ec21f69f942d')
    data = response.json()
    for video in data.get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


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
st.markdown(
    """
    <div style="text-align: center;">
        <h1>MOVIE RECOMMENDER SYSTEM</h1>
        <p>Search or select a movie to get recommendations!</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Load movies data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Add a search bar for finding movies
search_query = st.text_input("Search for a movie:", placeholder="Type a movie name...")

selected_movie_name = None  # Initialize variable for selected movie

if search_query:
    # Show matching movies based on search
    matching_movies = movies[movies['title'].str.contains(search_query, case=False)]
    if not matching_movies.empty:
        selected_movie_name = st.selectbox('Did you mean:', matching_movies['title'].values)
    else:
        st.write("No matches found.")
else:
    # If no search query, use the dropdown for movie selection
    selected_movie_name = st.selectbox(
        'WHICH MOVIE YOU WOULD LIKE TO SEE TODAY?',
        movies['title'].values
    )

# Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# When the recommend button is clicked
if selected_movie_name and st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    # Display recommendations in columns
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])

# Display movie details section
st.markdown(
    """
    <div style="text-align: center;">
        <h3>MOVIE DETAILS</h3>
        <p>You can see the details of the selected movie.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if selected_movie_name:
    # Fetch the movie ID for the selected movie
    selected_movie_id = movies[movies['title'] == selected_movie_name].iloc[0].movie_id
    details = fetch_movie_details(selected_movie_id)

    # Display movie poster
    st.image(fetch_poster(selected_movie_id), width=300)

    # Display movie details
    st.subheader(selected_movie_name)
    st.write(f"**Overview:** {details['overview']}")
    st.write(f"**Release Date:** {details['release_date']}")
    st.write(f"**Rating:** {details['rating']}/10")

    # Add "Watch Trailer" feature
    if st.button("Watch Trailer"):
        trailer_url = fetch_trailer(selected_movie_id)
        if trailer_url:
            st.video(trailer_url)
        else:
            st.write("Trailer not available.")
