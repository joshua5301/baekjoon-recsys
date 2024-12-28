import streamlit as st
import requests
import bojrecsys
import os

st.set_page_config(
    page_title = 'Baekjoon Recsys',
    page_icon = ':sparkles:',
    layout = 'wide'
) 

st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

loader = bojrecsys.Loader()
problem_df = loader.load_preproc_df('problem_info')
problem_df = problem_df.set_index('problemId')

_, right = st.columns([10, 3])
recommend_tab, similar_tab = st.tabs(['유저 별 추천 문제', '유사한 문제'])

with recommend_tab:
    st.header('백준 문제 추천해드립니다! :sunglasses:')
    handle = st.text_input(label='solved.ac 핸들', placeholder='solved.ac 핸들을 입력해주세요. ex) 37aster', label_visibility='hidden')
with similar_tab:
    st.header('유사한 문제 보여드립니다! :star-struck:')
    problem_id = st.text_input(label='백준 문제 번호', placeholder='백준 문제 번호를 입력해주세요. ex) 1644', label_visibility='hidden')
    if problem_id:
        try:
            problem_id = int(problem_id)
            if problem_id < 1000:
                raise ValueError
        except ValueError:
            st.subheader('\n')
            with st.columns([1, 5, 1])[1].container(border=True):
                st.subheader('잘못된 입력입니다. 문제 \'번호\'를 입력해주세요!')
                problem_id = None

with right.popover('난이도 제한 :chart_with_upwards_trend:', use_container_width=True):
    tiers = ['B', 'S', 'G', 'P', 'D', 'R']
    levels = [f'{tier}{num}' for tier in tiers for num in range(5, 0, -1)]
    min_level, max_level = st.select_slider('티어 제한', options=levels, value=('B5', 'R1'))

@st.cache_data
def get_ids(input: str | int):
    if type(input) == str:
        model: bojrecsys.CollaborativeRecSys = loader.load_model('collaborative_recsys')
        ids = model.get_recommendations(input, 20000)
    else:
        model: bojrecsys.ContentRecSys = loader.load_model('content_recsys')
        ids = model.get_similar_problems(input, 20000)
    return ids

@st.cache_data
def get_matched_ids(input: str | int, min_level: int, max_level: int) -> list[int]:
    global levels
    matched_ids = []
    ids = get_ids(input)
    for id in ids:
        try:
            level = problem_df.loc[id]['level']
        except KeyError:
            continue
        if levels.index(min_level) + 1 <= level <= levels.index(max_level) + 1:
            matched_ids.append(id)
    return matched_ids[:10]

def show_ids(ids: list[int]):
    row1 = st.columns(5)
    row2 = st.columns(5)
    for id, col in zip(ids, row1 + row2):
        title = problem_df.loc[id]['titleKo']
        level = problem_df.loc[id]['level']
        tile = col.container(border=True)
        with tile:
            _, mid, _ = st.columns(3)
            with mid:
                image_dir = os.path.join(os.path.dirname(__file__), 'assets', 'level', f'{level}.png')
                st.image(image_dir, use_column_width=True)
                disable_fullscreen = r'<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
                st.markdown(disable_fullscreen, unsafe_allow_html=True)
            st.link_button(f"{id} - {title}",f"https://www.acmicpc.net/problem/{id}", use_container_width=True)

with recommend_tab:
    if handle:
        try:
            recommend_ids = get_matched_ids(handle, min_level, max_level)
            show_ids(recommend_ids)
        except KeyError:
            st.subheader('\n')
            with st.columns([1, 5, 1])[1].container(border=True):
                st.subheader('존재하지 않는 핸들입니다. :pensive:')
                st.subheader('solved.ac에 가입된 아이디인가요?')
        except requests.exceptions.ConnectionError:
            with st.columns([1, 5, 1])[1].container(border=True):
                st.subheader('solved.ac 서버가 바쁜가봐요. :pensive:')
                st.subheader('잠시 후 시도해주세요.')

with similar_tab:
    if problem_id:
        try:
            similar_ids = get_matched_ids(int(problem_id), min_level, max_level)
            show_ids(similar_ids)
        except KeyError:
            st.subheader('\n')
            with st.columns([1, 5, 1])[1].container(border=True):
                st.subheader('존재하지 않는 문제 번호입니다. :sob:')
                st.subheader('최신 문제들(32000번대 이후)는 아직 추가되지 않았습니다.')
                st.subheader('또한 컨텐츠 기반 추천의 경우 한국어 문제들만 지원됩니다.')

