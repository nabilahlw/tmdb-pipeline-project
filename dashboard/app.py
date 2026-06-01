import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ─── CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="TMDB Movie Pipeline Dashboard",
    page_icon="🎬",
    layout="wide"
)

engine = create_engine('postgresql://admin:adminadmin@localhost:5432/tmdb_db')
schema = 'silver_mart_silver_mart'

# ─── LOAD DATA ────────────────────────────────────────
@st.cache_data
def load_data():
    movies = pd.read_sql(f'SELECT * FROM {schema}.dim_movies', engine)
    revenue = pd.read_sql(f'SELECT * FROM {schema}.dim_revenue', engine)
    genres = pd.read_sql(f'SELECT * FROM {schema}.dim_genres', engine)
    yearly = pd.read_sql(f'SELECT * FROM {schema}.dim_yearlysum', engine)
    return movies, revenue, genres, yearly

movies, revenue, genres, yearly = load_data()

# ─── SIDEBAR FILTERS ──────────────────────────────────
st.sidebar.title("Filter Dashboard")
st.sidebar.markdown("---")

years = sorted(movies['release_year'].dropna().unique().astype(int))
year_range = st.sidebar.slider(
    "Pilih Rentang Tahun",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(1990, 2017)
)

all_genres = sorted(movies['primary_genre'].dropna().unique())
selected_genres = st.sidebar.multiselect(
    "Filter Genre",
    options=all_genres,
    default=[]
)

# ─── FILTER DATA ──────────────────────────────────────
df = movies.copy()
df = df[(df['release_year'] >= year_range[0]) & (df['release_year'] <= year_range[1])]
if selected_genres:
    df = df[df['primary_genre'].isin(selected_genres)]

df_rev = revenue[revenue['movie_id'].isin(df['movie_id'])]

df_yearly = yearly[
    (yearly['release_year'] >= year_range[0]) &
    (yearly['release_year'] <= year_range[1])
].sort_values('release_year')

# ─── TITLE ────────────────────────────────────────────
st.title("🎬 TMDB Movie Analytics Dashboard")
last_updated = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"Last updated: {last_updated}")
st.markdown("---")

# ─── KPI CARDS ────────────────────────────────────────
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_films = len(df)
total_revenue = df['revenue'].sum()
avg_revenue = df['revenue'].mean()
total_profit = (df['revenue'] - df['budget']).sum()
avg_profit = (df['revenue'] - df['budget']).mean()
avg_rating = df['vote_average'].mean()

col1.metric("Total Films", f"{total_films:,}")
col2.metric("Total Revenue", f"${total_revenue/1e9:.1f}B")
col3.metric("Avg Revenue", f"${avg_revenue/1e6:.1f}M")
col4.metric("Total Profit", f"${total_profit/1e9:.1f}B")
col5.metric("Avg Profit", f"${avg_profit/1e6:.1f}M")
col6.metric("Avg Rating", f"{avg_rating:.2f}/10")

st.markdown("---")

# ─── ROW 1: BAR + PIE ─────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Genre by Revenue")
    genre_rev = df.groupby('primary_genre')['revenue'].sum().reset_index()
    genre_rev = genre_rev.sort_values('revenue', ascending=False).head(10)
    fig1 = px.bar(
        genre_rev, x='primary_genre', y='revenue',
        color='revenue', color_continuous_scale='blues',
        labels={'primary_genre': 'Genre', 'revenue': 'Revenue ($)'}
    )
    fig1.update_layout(
        showlegend=False, height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Film Performance Distribution")
    if len(df_rev) > 0:
        perf = df_rev['performance_label'].value_counts().reset_index()
        perf.columns = ['performance_label', 'count']
        fig2 = px.pie(
            perf, values='count', names='performance_label',
            color_discrete_map={
                'Mega Blockbuster': '#4fc3f7',
                'Blockbuster': '#e53935',
                'Profitable': '#f48fb1',
                'Loss': '#1565c0',
                'Break Even': '#43a047'
            }
        )
        fig2.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Tidak ada data revenue untuk filter ini")

st.markdown("---")

# ─── ROW 2: LINE CHART TREND ──────────────────────────
st.subheader(f"Industry Revenue Trend ({year_range[0]}-{year_range[1]})")

if len(df_yearly) > 0:
    fig3 = px.line(
        df_yearly, x='release_year', y='total_revenue',
        markers=True,
        labels={'release_year': 'Year', 'total_revenue': 'Total Revenue ($)'},
        color_discrete_sequence=['#4fc3f7']
    )
    fig3.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    fig3.update_traces(line=dict(width=2))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ─── ROW 3: TOP FILMS TABLE ───────────────────────────
st.subheader("Top 20 Highest Revenue Films")

top_films = df.merge(
    df_rev[['movie_id', 'performance_label', 'roi_pct', 'profit']],
    on='movie_id', how='left'
).sort_values('revenue', ascending=False).head(20)

top_films['revenue_fmt'] = top_films['revenue'].apply(lambda x: f"${x:,.0f}")
top_films['profit_fmt'] = top_films['profit'].apply(
    lambda x: f"${x:,.0f}" if pd.notna(x) else "-"
)
top_films['rating_fmt'] = top_films['vote_average'].apply(lambda x: f"{x:.1f}/1")

display = top_films[[
    'title', 'primary_genre', 'lead_actor', 'director',
    'revenue_fmt', 'profit_fmt', 'performance_label', 'rating_fmt'
]].rename(columns={
    'title': 'Title',
    'primary_genre': 'Genre',
    'lead_actor': 'Lead Actor',
    'director': 'Director',
    'revenue_fmt': 'Revenue',
    'profit_fmt': 'Profit',
    'performance_label': 'Performance',
    'rating_fmt': 'Rating'
}).reset_index(drop=True)

st.dataframe(display, use_container_width=True, height=500)

st.markdown("---")
st.caption("TMDB Movie Pipeline | by Nabila Hulwana Z. | Mini Bootcamp Data Engineering rubythalib.ai")