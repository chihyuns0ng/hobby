import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="칼바람 나락 1+2코어 빅데이터", layout="wide")

st.title("📊 칼바람 나락 코어템 시너지 대시보드(260206ver)")
st.sidebar.header("필터 설정")

# 데이터 로드
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('aram_top3_260206.csv')
        # 승률 문자열을 숫자로 변환 (정렬용)
        df['승률_float'] = df['전체승률'].str.replace('%', '').astype(float)
        return df
    except FileNotFoundError:
        st.error("CSV 파일이 없습니다. 분석 코드를 먼저 실행해주세요.")
        return None

df = load_data()

if df is not None:
    # 검색 필터
    search_query = st.sidebar.text_input("챔피언 이름 검색", "")
    min_games = st.sidebar.slider("최소 분석 판수", 0, int(df['분석판수'].max()), 5)
    
    filtered_df = df[(df['챔피언'].str.contains(search_query)) & (df['분석판수'] >= min_games)]

    # 메인 지표 (KPI)
    col1, col2, col3 = st.columns(3)
    col1.metric("총 분석 챔피언 수", len(df))
    col2.metric("최고 승률 챔피언", df.iloc[0]['챔피언'], df.iloc[0]['전체승률'])
    col3.metric("최다 데이터 보유", df.loc[df['분석판수'].idxmax(), '챔피언'], f"{df['분석판수'].max()} games")

    st.divider()

    # 데이터 테이블 출력
    st.subheader("🏆 전체 통계 및 조합 데이터")
    
    # 보고 싶은 컬럼 선택 기능
    selected_cols = st.multiselect(
        "표시할 컬럼 선택", 
        df.columns.tolist(), 
        default=['챔피언', '전체승률', '분석판수', '승률1위_조합', '승률1위_WR', '판수1위_조합']
    )
    
    st.dataframe(filtered_df[selected_cols], use_container_width=True, hide_index=True)

    # 시각화 섹션
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 챔피언별 승률 Top 10")
        top_10_wr = df.nlargest(10, '승률_float')
        st.bar_chart(data=top_10_wr, x='챔피언', y='승률_float', color="#ff4b4b")

    with c2:
        st.subheader("🔥 데이터 집계 순위 (판수)")
        top_10_games = df.nlargest(10, '분석판수')
        st.bar_chart(data=top_10_games, x='챔피언', y='분석판수', color="#0072B2")

    # 상세 조합 조회기
    st.divider()
    st.subheader("🔍 특정 챔피언 상세 조합 분석")
    target_champ = st.selectbox("챔피언을 선택하세요", df['챔피언'].unique())
    
    champ_data = df[df['챔피언'] == target_champ].iloc[0]
    
    inner_c1, inner_c2 = st.columns(2)
    with inner_c1:
        st.info(f"✨ **{target_champ}** 승률 기반 추천")
        for i in range(1, 4):
            st.write(f"{i}위: {champ_data[f'승률{i}위_조합']} ({champ_data[f'승률{i}위_WR']})")
    
    with inner_c2:
        st.success(f"🔥 **{target_champ}** 인기 조합 (판수)")
        for i in range(1, 4):
            st.write(f"{i}위: {champ_data[f'판수{i}위_조합']} ({champ_data[f'판수{i}위_판수']}판)")

