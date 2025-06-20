import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="GoodReads Dataset Visualization",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Goodreads 100K Books Dashboard")

# Upload dataset dari UI
uploaded_file = st.file_uploader("Upload file CSV Goodreads 100K", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Drop missing data penting
    df = df.dropna(subset=['title', 'author', 'rating', 'genre'])

    # Sidebar filters
    st.sidebar.header("Filter Buku")
    
    all_genres = sorted(set(g for genre in df['genre'].dropna() for g in genre.split(',')))
    selected_genres = st.sidebar.multiselect("Pilih Genre:", all_genres)
    
    rating_range = st.sidebar.slider("Rentang Rating:", 0.0, 5.0, (3.0, 5.0), 0.1)
    pages_range = st.sidebar.slider("Jumlah Halaman:", int(df.pages.min()), int(df.pages.max()), (50, 500))
    
    # Filter data
    filtered_df = df[df['rating'].between(*rating_range)]
    filtered_df = filtered_df[filtered_df['pages'].between(*pages_range)]
    
    if selected_genres:
        filtered_df = filtered_df[filtered_df['genre'].apply(lambda x: any(g in x for g in selected_genres))]
    
    st.markdown("""
    Gunakan filter di sebelah kiri untuk mengeksplorasi buku berdasarkan genre, rating, dan jumlah halaman.
    """)
    
    # Dropdown untuk memilih jenis visualisasi
    viz_option = st.selectbox("Pilih Visualisasi:", ["Rating vs Jumlah Halaman", "Top Genre Berdasarkan Rating"])
    
    if viz_option == "Rating vs Jumlah Halaman":
        fig = px.scatter(filtered_df,
                         x="pages", y="rating",
                         hover_data=["title", "author", "genre"],
                         title="Rating vs Jumlah Halaman",
                         labels={"pages": "Jumlah Halaman", "rating": "Rating"})
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_option == "Top Genre Berdasarkan Rating":
        genre_ratings = []
        for genre in all_genres:
            genre_df = df[df['genre'].str.contains(genre, na=False)]
            avg_rating = genre_df['rating'].mean()
            genre_ratings.append((genre, avg_rating))
        genre_ratings.sort(key=lambda x: x[1], reverse=True)
        top_genres = pd.DataFrame(genre_ratings[:10], columns=["Genre", "Rata-rata Rating"])
        fig = px.bar(top_genres, x="Genre", y="Rata-rata Rating", title="Top 10 Genre Berdasarkan Rata-rata Rating")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tampilkan detail buku
    st.subheader("📖 Daftar Buku")
    show_cols = ["title", "author", "rating", "reviews", "pages", "genre"]
    st.dataframe(filtered_df[show_cols].sort_values(by="rating", ascending=False).reset_index(drop=True))
