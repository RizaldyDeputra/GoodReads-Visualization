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
    viz_option = st.selectbox("Pilih Visualisasi:", [
        "Rating vs Jumlah Halaman",
        "Top Genre Berdasarkan Rating",
        "Distribusi Rating Buku",
        "Distribusi Jumlah Halaman",
        "Jumlah Buku per Format",
        "Rating vs Jumlah Review",
        "Top 10 Penulis Paling Produktif",
        "Genre Terpopuler Berdasarkan Jumlah Buku",
        "Rata-rata Rating per Penulis (Top 10)"
    ])

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

    elif viz_option == "Distribusi Rating Buku":
        fig = px.histogram(filtered_df, x="rating", nbins=30, title="Distribusi Rating Buku")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Distribusi Jumlah Halaman":
        fig = px.histogram(filtered_df, x="pages", nbins=30, title="Distribusi Jumlah Halaman Buku")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Jumlah Buku per Format":
        format_count = df['bookformat'].value_counts().reset_index()
        format_count.columns = ['Format', 'Jumlah']
        fig = px.bar(format_count, x='Format', y='Jumlah', title="Jumlah Buku per Format")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Rating vs Jumlah Review":
        fig = px.scatter(filtered_df,
                         x="reviews", y="rating",
                         hover_data=["title", "author"],
                         title="Rating vs Jumlah Review",
                         labels={"reviews": "Jumlah Review", "rating": "Rating"})
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Top 10 Penulis Paling Produktif":
        author_counts = df['author'].value_counts().head(10).reset_index()
        author_counts.columns = ['Author', 'Jumlah Buku']
        fig = px.bar(author_counts, x='Author', y='Jumlah Buku', title="Top 10 Penulis Paling Produktif")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Genre Terpopuler Berdasarkan Jumlah Buku":
        from collections import Counter
        genre_list = [g.strip() for genre in df['genre'].dropna() for g in genre.split(',')]
        genre_counter = Counter(genre_list)
        genre_df = pd.DataFrame(genre_counter.items(), columns=['Genre', 'Jumlah Buku']).sort_values(by='Jumlah Buku', ascending=False).head(10)
        fig = px.bar(genre_df, x='Genre', y='Jumlah Buku', title="Top 10 Genre Terpopuler Berdasarkan Jumlah Buku")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Rata-rata Rating per Penulis (Top 10)":
        top_authors = df.groupby('author')['rating'].mean().sort_values(ascending=False).head(10).reset_index()
        top_authors.columns = ['Author', 'Rata-rata Rating']
        fig = px.bar(top_authors, x='Author', y='Rata-rata Rating', title="Top 10 Penulis dengan Rata-rata Rating Tertinggi")
        st.plotly_chart(fig, use_container_width=True)

    # Tampilkan detail buku
    st.subheader("📖 Daftar Buku")
    show_cols = ["title", "author", "rating", "reviews", "pages", "genre"]
    st.dataframe(filtered_df[show_cols].sort_values(by="rating", ascending=False).reset_index(drop=True))
