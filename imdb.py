import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Set up the page
st.set_page_config(page_title="Movie Data Analysis", layout="wide", page_icon="🎬")
st.title("🎬 Movie Data Analysis Dashboard")

# Load the data from the database
@st.cache_data
def load_data():
    # Create a connection to the SQLite database
    engine = create_engine(
    "mysql+pymysql://7xpoQk8hZoeKvv4.root:nFfK6vUMr2eZx09Y@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/imdb",
    connect_args={
        "ssl": {"ca": "C:/Users/91994/Downloads/isrgrootx1 (3).pem"}
    }
    
    )

    # Read the data into a DataFrame
    df = pd.read_sql('SELECT * FROM imdb_2024ml', engine)
    # Convert duration to hours
    df['Duration_Hrs'] = df['Duration'] / 60
    # Clean up any potential missing values
    df = df.dropna()
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Options")

# Genre filter
selected_genres = st.sidebar.multiselect(
    "Select Genre(s)",
    options=df['Genre'].unique(),
    default=df['Genre'].unique()
)

# Rating filter
min_rating = st.sidebar.slider(
    "Minimum Rating",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    step=0.1
)

# Votes filter
min_votes = st.sidebar.number_input(
    "Minimum Votes",
    min_value=0,
    max_value=int(df['Votes'].max()),
    value=0
)

# Duration filter
duration_range = st.sidebar.slider(
    "Select Duration Range (Hours)",
    min_value=0.5,
    max_value=4.0,
    value=(0.5, 4.0),
    step=0.1
)

# Apply filters
filtered_df = df[
    (df['Genre'].isin(selected_genres)) &
    (df['Rating'] >= min_rating) &
    (df['Votes'] >= min_votes) &
    (df['Duration_Hrs'] >= duration_range[0]) &
    (df['Duration_Hrs'] <= duration_range[1])
]

# Main content
st.header("Filtered Data Overview")
st.write(f"Showing {len(filtered_df)} movies out of {len(df)} total movies")

# Display filtered data
st.dataframe(filtered_df[['Title', 'Rating', 'Votes', 'Duration_Hrs', 'Genre']].sort_values(
    by='Rating', ascending=False),
    height=300)

# Visualizations
st.header("Data Visualizations")

# Set up tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Top Movies", 
    "Genre Analysis", 
    "Rating Analysis", 
    "Duration Analysis",
    "Correlations"
])

with tab1:
    st.subheader("Top 10 Movies by Rating")
    top_rated = filtered_df.nlargest(10, 'Rating')[['Title', 'Rating', 'Votes', 'Genre']]
    st.dataframe(top_rated)
    
    st.subheader("Top 10 Movies by Voting Count")
    top_voted = filtered_df.nlargest(10, 'Votes')[['Title', 'Rating', 'Votes', 'Genre']]
    st.dataframe(top_voted)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Genre Distribution")
        genre_counts = filtered_df['Genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=genre_counts, 
            y='Genre', 
            x='Count',
            palette='viridis',
            ax=ax
        )
        ax.set_title("Number of Movies by Genre")
        ax.set_xlabel("Count")
        ax.set_ylabel("Genre")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Most Popular Genres by Voting")
        genre_votes = filtered_df.groupby('Genre')['Votes'].sum().reset_index()
        genre_votes = genre_votes.sort_values('Votes', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(
            genre_votes['Votes'],
            labels=genre_votes['Genre'],
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette('viridis', len(genre_votes))
        )
        ax.set_title("Voting Distribution by Genre")
        st.pyplot(fig)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rating Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(
            filtered_df['Rating'],
            bins=20,
            kde=True,
            color='skyblue',
            ax=ax
        )
        ax.set_title("Distribution of Movie Ratings")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Top Rated Movie by Genre")
        top_by_genre = filtered_df.loc[
            filtered_df.groupby('Genre')['Rating'].idxmax()
        ][['Genre', 'Title', 'Rating']].sort_values('Rating', ascending=False)
        st.dataframe(top_by_genre)

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Duration by Genre")
        avg_duration = filtered_df.groupby('Genre')['Duration_Hrs'].mean().reset_index()
        avg_duration = avg_duration.sort_values('Duration_Hrs', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=avg_duration,
            y='Genre',
            x='Duration_Hrs',
            palette='viridis',
            ax=ax
        )
        ax.set_title("Average Duration by Genre (Hours)")
        ax.set_xlabel("Duration (Hours)")
        ax.set_ylabel("Genre")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Duration Extremes")
        st.write("Shortest Movies:")
        st.dataframe(
            filtered_df.nsmallest(5, 'Duration_Hrs')[['Title', 'Duration_Hrs', 'Genre']]
        )
        
        st.write("Longest Movies:")
        st.dataframe(
            filtered_df.nlargest(5, 'Duration_Hrs')[['Title', 'Duration_Hrs', 'Genre']]
        )

with tab5:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rating vs. Votes")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=filtered_df,
            x='Rating',
            y='Votes',
            hue='Genre',
            palette='viridis',
            alpha=0.7,
            ax=ax
        )
        ax.set_title("Rating vs. Voting Count")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Votes")
        ax.set_yscale('log')  # Log scale for better visualization
        st.pyplot(fig)
    
    with col2:
        st.subheader("Average Rating by Genre")
        genre_rating = filtered_df.groupby('Genre')['Rating'].mean().reset_index()
        genre_rating = genre_rating.sort_values('Rating', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=genre_rating,
            y='Genre',
            x='Rating',
            palette='viridis',
            ax=ax
        )
        ax.set_title("Average Rating by Genre")
        ax.set_xlabel("Average Rating")
        ax.set_ylabel("Genre")
        st.pyplot(fig)

# Additional analysis
st.header("Advanced Analysis")

# Heatmap of average ratings by genre
st.subheader("Heatmap of Ratings by Genre")
heatmap_data = filtered_df.pivot_table(
    index='Genre',
    values='Rating',
    aggfunc='mean'
)
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(
    heatmap_data,
    annot=True,
    cmap='viridis',
    fmt=".1f",
    ax=ax
)
ax.set_title("Average Rating by Genre")
st.pyplot(fig)

# Correlation matrix
st.subheader("Correlation Matrix")
corr = filtered_df[['Rating', 'Votes', 'Duration_Hrs']].corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    corr,
    annot=True,
    cmap='coolwarm',
    vmin=-1,
    vmax=1,
    ax=ax
)
ax.set_title("Correlation Between Variables")
st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("**Movie Data Analysis Dashboard** - Created with Streamlit")