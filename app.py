import streamlit as st
import pandas as pd
import pickle
import requests

# --- Load Data ---
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- Fetch Poster Function with error handling ---
def fetch_poster(movie_id):
    """
    Fetch poster from TMDb. Returns placeholder if API fails or movie_id is invalid.
    """
    if not movie_id:
        return "https://via.placeholder.com/200x300?text=No+Poster"

    api_key = "91f183bebcf36e8c918aa00a329f0cd1"  # Replace with your TMDb API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    except requests.exceptions.RequestException:
        pass

    # Fallback placeholder
    return "https://via.placeholder.com/200x300?text=No+Poster"

# --- Recommendation Function ---
def recommend(movie):
    """
    Returns top 5 recommended movie titles and their posters.
    """
    if movie not in movies['title'].values:
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    # Get top 5 similar movies (skip the first one which is the selected movie)
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].title)
        # Use movie_id if exists, else fallback
        movie_id = movies.iloc[i[0]].get('movie_id', None)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# --- Streamlit UI ---
st.set_page_config(page_title="Movie Recommendation System", layout="wide")
st.title("🎬 Advanced Movie Recommendation System")

selected_movie = st.selectbox("Choose a movie:", movies['title'].values)

if st.button("Get Recommendations"):
    names, posters = recommend(selected_movie)
    
    if names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(names[i])
                st.image(posters[i], use_column_width=True)
    else:
        st.warning("No recommendations available for this movie.")
