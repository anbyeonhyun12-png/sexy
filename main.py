import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 든 영화 가운데 해당 기간에 개봉한 영화의 요약 데이터")

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자를 날짜형으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre_first"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 열은 숫자로 변환
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

# ─────────────────────────────────────
# 그래프 1. 장르별 영화 편수
# ─────────────────────────────────────
st.header("그래프 1. 장르별 영화 편수")

genre_counts = (
    df["genre_first"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수",
)

fig.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

fig.update_layout(
    legend_title_text="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "장르별로 전체 영화에서 차지하는 편수와 비율을 한눈에 비교할 수 있습니다."
)

st.divider()

# ─────────────────────────────────────
# 그래프 2. 장르별 영화 트리맵
# ─────────────────────────────────────
st.header("그래프 2. 장르 안에 들어 있는 영화")

treemap_df = df[["genre_first", "movieNm", "total_audi"]].copy()
treemap_df["movieNm"] = treemap_df["movieNm"].fillna("영화명 미상")
treemap_df["total_audi"] = pd.to_numeric(
    treemap_df["total_audi"], errors="coerce"
).fillna(0)

fig2 = px.treemap(
    treemap_df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르별 영화와 총 관객",
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>"
)

fig2.update_layout(
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "각 장르 안에서 영화별 총 관객 규모가 어떻게 다른지 비교할 수 있습니다."
)

st.divider()

# ─────────────────────────────────────
# 그래프 3. 총 관객 분포
# ─────────────────────────────────────
st.header("그래프 3. 총 관객 분포")

hist_df = df[["movieNm", "total_audi"]].copy()
hist_df["total_audi"] = pd.to_numeric(hist_df["total_audi"], errors="coerce")
hist_df = hist_df.dropna(subset=["total_audi"])

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={"total_audi": "총 관객", "count": "영화 편수"},
)

fig3.update_traces(
    hovertemplate="총 관객: %{x:,}명<br>영화 편수: %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 많은 영화가 들어 있는 구간 계산
counts, bin_edges = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True,
).value_counts().sort_index(), None

# 위의 bins와 동일한 구간을 사용하기 위해 다시 계산
hist_bins = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
)
most_common_bin = hist_bins.value_counts().idxmax()

# 총 관객이 가장 많은 영화
max_row = hist_df.loc[hist_df["total_audi"].idxmax()]
max_movie = max_row["movieNm"]
max_audi = int(max_row["total_audi"])

st.markdown(
    f"**이 그래프로 알 수 있는 것:** "
    f"대부분의 영화는 **{most_common_bin.left:,.0f}~{most_common_bin.right:,.0f}명** "
    f"구간에 몰려 있습니다. "
    f"총 관객이 가장 많은 영화는 **{max_movie}**로, "
    f"총 **{max_audi:,}명**을 기록했습니다."
)

st.divider()

# ─────────────────────────────────────
# 그래프 5. 장르별 총 관객 분포
# ─────────────────────────────────────
st.header("그래프 5. 장르별 총 관객 분포")

# 영화가 10편 이상인 장르만 선택
genre_movie_counts = df["genre_first"].value_counts()
valid_genres = genre_movie_counts[genre_movie_counts >= 10].index

box_df = df[
    df["genre_first"].isin(valid_genres)
][["genre_first", "movieNm", "total_audi"]].copy()

box_df["total_audi"] = pd.to_numeric(
    box_df["total_audi"], errors="coerce"
)
box_df = box_df.dropna(subset=["total_audi"])

fig5 = px.box(
    box_df,
    x="genre_first",
    y="total_audi",
    points="outliers",
    hover_data={"movieNm": True, "total_audi": ":,d"},
    title="영화가 10편 이상인 장르별 총 관객 분포",
    labels={
        "genre_first": "장르",
        "total_audi": "총 관객",
        "movieNm": "영화명",
    },
)

fig5.update_traces(
    hovertemplate="<b>%{customdata[0]}</b><br>총 관객: %{y:,}명<extra></extra>"
)

fig5.update_layout(
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "영화가 10편 이상인 장르별로 총 관객의 분포와 중앙값, "
    "그리고 다른 영화보다 관객 수가 크게 벗어난 영화를 비교할 수 있습니다."
)

st.divider()

# ─────────────────────────────────────
# 그래프 8. 10위권 체류 기간과 총 관객의 관계
# ─────────────────────────────────────
st.header("그래프 8")

question = "10위권에 오래 머문 영화는 총 관객도 많은가"
st.subheader(question)

scatter_df = df[["movieNm", "days_in_top10", "total_audi"]].copy()
scatter_df["days_in_top10"] = pd.to_numeric(
    scatter_df["days_in_top10"], errors="coerce"
)
scatter_df["total_audi"] = pd.to_numeric(
    scatter_df["total_audi"], errors="coerce"
)
scatter_df = scatter_df.dropna(
    subset=["movieNm", "days_in_top10", "total_audi"]
)

fig8 = px.scatter(
    scatter_df,
    x="days_in_top10",
    y="total_audi",
    custom_data=["movieNm"],
    title=question,
    labels={
        "days_in_top10": "10위권에 머문 날수",
        "total_audi": "총 관객",
    },
)

fig8.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b>"
        "<br>10위권에 머문 날수: %{x}일"
        "<br>총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig8.update_layout(
    xaxis_title="10위권에 머문 날수",
    yaxis_title="총 관객",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig8, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "10위권에 머문 날수와 총 관객 사이에 어떤 관계가 있는지 살펴볼 수 있습니다."
)

st.divider()
