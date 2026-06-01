CREATE TABLE IF NOT EXISTS fact_yearly_partisi (
    release_year int,
    primary_genre text,
    total_films int,
    total_revenue bigint,
    total_budget bigint,
    total_profit bigint,
    avg_rating numeric,
    mega_blockbuster_count int,
    blockbuster_count int,
    loss_count int
) PARTITION BY RANGE (release_year);

CREATE TABLE IF NOT EXISTS fact_yearly_1900s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1900) TO (1920);
CREATE TABLE IF NOT EXISTS fact_yearly_1920s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1920) TO (1930);
CREATE TABLE IF NOT EXISTS fact_yearly_1930s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1930) TO (1940);
CREATE TABLE IF NOT EXISTS fact_yearly_1940s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1940) TO (1950);
CREATE TABLE IF NOT EXISTS fact_yearly_1950s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1950) TO (1960);
CREATE TABLE IF NOT EXISTS fact_yearly_1960s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1960) TO (1970);
CREATE TABLE IF NOT EXISTS fact_yearly_1970s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1970) TO (1980);
CREATE TABLE IF NOT EXISTS fact_yearly_1980s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1980) TO (1990);
CREATE TABLE IF NOT EXISTS fact_yearly_1990s PARTITION OF fact_yearly_partisi FOR VALUES FROM (1990) TO (2000);
CREATE TABLE IF NOT EXISTS fact_yearly_2000s PARTITION OF fact_yearly_partisi FOR VALUES FROM (2000) TO (2010);
CREATE TABLE IF NOT EXISTS fact_yearly_2010s PARTITION OF fact_yearly_partisi FOR VALUES FROM (2010) TO (2030);

INSERT INTO fact_yearly_partisi
SELECT * FROM silver_mart_silver_mart.fact_yearly;