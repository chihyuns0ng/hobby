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
        df = df.rename(columns={'분석판수': '픽 횟수'})
        
        # 승률 str->float
        df['승률_float'] = df['전체승률'].str.replace('%', '').astype(float)
        # 픽률 (ipynb 코드에서 가져온 매치 수 값 이용)
        total_matches = 134925 
        df['픽률'] = (df['픽 횟수'] / total_matches) * 100 * 10

        df['픽률_per'] = df['픽률'].map(lambda x: f"{x:.1f}%")
        
        return df
    except FileNotFoundError:
        st.error("CSV 파일이 없습니다. 분석 코드를 먼저 실행해주세요.")
        return None

df = load_data()

if df is not None:
    # 검색 필터
    search_query = st.sidebar.text_input("챔피언 이름 검색", "")
    min_games = st.sidebar.slider("최소 픽 수", 0, int(df['픽 횟수'].max()), 5)
    
    filtered_df = df[(df['챔피언'].str.contains(search_query)) & (df['픽 횟수'] >= min_games)]

    # 메인 지표 (KPI)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 분석 챔피언 수", len(df))
    col2.metric("최고 승률", df.iloc[0]['챔피언'], df.iloc[0]['전체승률'])
    col3.metric("최다 선택", df.loc[df['픽 횟수'].idxmax(), '챔피언'], f"{df['픽 횟수'].max()} games")
    top_pick = df.loc[df['픽률'].idxmax()]
    col4.metric("최고 픽률", top_pick['챔피언'], f"{top_pick['픽률']:.1f}%")

    st.divider()

    # 데이터 테이블 출력
    st.subheader("🏆 전체 통계 및 조합 데이터")

    exclude_cols = ['승률_float', '픽률_per']
    available_cols = [c for c in df.columns if c not in exclude_cols]
    # 컬럼 선택 기능
    selected_cols = st.multiselect(
        "표시할 컬럼 선택", 
        available_cols, 
        default=['챔피언', '전체승률', '픽률', '픽 횟수', '승률1위_조합', '판수1위_조합']
    )
    
    st.dataframe(
        filtered_df[selected_cols], 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "픽률": st.column_config.NumberColumn("픽률", format="%.1f%%")
        }
    )

    # 시각화 섹션
    st.divider()
    c1, c2 = st.columns(2)

    import altair as alt

    with c1:
        st.subheader("📈 승률 Top 10")
        top_10_wr = df.nlargest(10, '승률_float').sort_values('승률_float', ascending=False)
        
        chart1 = alt.Chart(top_10_wr).mark_bar(color="#ff4b4b").encode(
            x=alt.X('챔피언:N', sort=None, title='챔피언'),
            y=alt.Y('승률_float:Q', title='승률 (%)'),
            tooltip=['챔피언', '전체승률']
        ).properties(height=400)
        st.altair_chart(chart1, use_container_width=True)

    with c2:
        st.subheader("🔥 픽률 Top 10")
        top_10_pick = df.nlargest(10, '픽률').sort_values('픽률', ascending=False)
        
        chart2 = alt.Chart(top_10_pick).mark_bar(color="#29b5e8").encode(
            x=alt.X('챔피언:N', sort=None, title='챔피언'),
            y=alt.Y('픽률:Q', title='픽률 (%)'),
            tooltip=['챔피언', '픽률_per']
        ).properties(height=400)
        st.altair_chart(chart2, use_container_width=True)


    # 상세 조합 조회기
    st.divider()
    st.subheader("🔍 특정 챔피언 상세 조합 분석")
    target_champ = st.selectbox("챔피언을 선택하세요", df['챔피언'].unique())
    
    champ_data = df[df['챔피언'] == target_champ].iloc[0]

    st.write(f"💡 **{target_champ}**의 현재 칼바람 픽률은 약 **{champ_data['픽률']:.1f}%** 입니다.")
    
    inner_c1, inner_c2 = st.columns(2)
    with inner_c1:
        st.info(f"✨ **{target_champ}** 승률 기반 추천")
        for i in range(1, 4):
            st.write(f"{i}위: {champ_data[f'승률{i}위_조합']} ({champ_data[f'승률{i}위_WR']})")
    
    with inner_c2:
        st.success(f"🔥 **{target_champ}** 인기 조합 (판수)")
        for i in range(1, 4):
            st.write(f"{i}위: {champ_data[f'판수{i}위_조합']} ({champ_data[f'판수{i}위_판수']}판)")


















