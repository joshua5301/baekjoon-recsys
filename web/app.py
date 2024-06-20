import streamlit as st
import bojrecsys
import os

st.set_page_config(
    page_title = '백준 문제 추천',
    layout = 'wide'
) 

loader = bojrecsys.Loader()
problem_df = loader.load_preproc_df('problem_info')
problem_df.set_index('problemId', drop=True)
problem_df = problem_df.set_index('problemId')

_, right1, right2 = st.columns([10, 3, 3])
recommend_tab, similar_tab = st.tabs(['유저 별 추천 문제', '유사한 문제'])

with recommend_tab:
    st.header('백준 문제 추천해드립니다! :sunglasses:')
    handle = st.text_input(label='solved.ac 핸들', placeholder='solved.ac 핸들을 입력해주세요.', label_visibility='hidden')
with similar_tab:
    st.header('유사한 문제 보여드립니다! :star-struck:')
    problem_id = st.text_input(label='백준 문제 번호', placeholder='백준 문제 번호를 입력해주세요.', label_visibility='hidden')
with right1.popover('난이도 제한 :chart_with_upwards_trend:', use_container_width=True):
    tiers = ['B', 'S', 'G', 'P', 'D', 'R']
    levels = [f'{tier}{num}' for tier in tiers for num in range(5, 0, -1)]
    min_level, max_level = st.select_slider('티어 제한', options=levels, value=('B5', 'R1'))
with right2.popover('추천 방식 :gear:', use_container_width=True):
    how = ['잠재 요인 기반', '다른 유저가 푼 기록 기반', '문제 본문 기반']
    model_names = ['latent_factor_model', 'item_model', 'content_model']
    selected_how = st.selectbox(label='추천 방식', options=how, label_visibility='collapsed')
    selected_model_name = model_names[how.index(selected_how)]

@st.cache_data
def get_matched_ids(model_name: str, input: str | int) -> list[int]:
    model: bojrecsys.RecSys = loader.load_model(model_name)
    if type(input) == str:
        get_ids = model.get_recommendations
    else:
        get_ids = model.get_similar_problems
    matched_ids = []
    id_num = 10
    while len(matched_ids) < 10:
        ids = get_ids(input, id_num)
        is_in_range = lambda id: levels.index(min_level) + 1 <= problem_df.loc[id]['level'] <= levels.index(max_level) + 1
        matched_ids = [id for id in ids if is_in_range(id)]
        id_num *= 2
    return matched_ids

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
                image_dir = os.path.join(os.path.dirname(__file__), 'assets', f'{level}.png')
                st.image(image_dir, width=70)
                disable_fullscreen = r'<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
                st.markdown(disable_fullscreen, unsafe_allow_html=True)
            st.link_button(f"{id} - {title}",f"https://www.acmicpc.net/problem/{id}", use_container_width=True)


if handle:
    recommend_ids = get_matched_ids(selected_model_name, handle)
    with recommend_tab:
        show_ids(recommend_ids)
if problem_id:
    similar_ids = get_matched_ids(selected_model_name, int(problem_id))
    with similar_tab:
        show_ids(similar_ids)