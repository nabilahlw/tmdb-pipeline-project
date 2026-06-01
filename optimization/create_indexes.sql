-- 7 Indexes untuk optimasi query
CREATE INDEX IF NOT EXISTS idx_dim_movies_director ON silver_mart_silver_mart.dim_movies(director);
CREATE INDEX IF NOT EXISTS idx_dim_movies_genre ON silver_mart_silver_mart.dim_movies(primary_genre);
CREATE INDEX IF NOT EXISTS idx_dim_movies_year ON silver_mart_silver_mart.dim_movies(release_year);
CREATE INDEX IF NOT EXISTS idx_dim_movies_genre_rating ON silver_mart_silver_mart.dim_movies(primary_genre, vote_average);
CREATE INDEX IF NOT EXISTS idx_dim_revenue_label ON silver_mart_silver_mart.dim_revenue(performance_label);
CREATE INDEX IF NOT EXISTS idx_dim_revenue_roi ON silver_mart_silver_mart.dim_revenue(roi_pct);
CREATE INDEX IF NOT EXISTS idx_fact_yearly_year ON silver_mart_silver_mart.fact_yearly(release_year);