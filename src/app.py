import streamlit as st
import pandas as pd 
from als_rec_sys import ALSRecSys
import os
import pickle

# 페이지 기본 설정
st.set_page_config(
    page_title = '백준 알고리즘 문제 추천 시스템',
    layout = 'wide'
)

project_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(project_dir, 'data', 'preprocessed', 'problem_info.csv')
problem_df = pd.read_csv(data_dir, index_col=0)

st.header('백준 문제 추천해드립니다! :sunglasses:')

handle = st.text_input(label='solved.ac 핸들', placeholder='solved.ac 핸들을 입력해주세요.', label_visibility='hidden')
left, mid, right = st.columns([1, 10, 1])
with right.popover('설정 :gear:'):
    tiers = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby']
    levels = [f'{tier} {num}' for tier in tiers for num in range(5, 0, -1)]
    min_level, max_level = st.select_slider('티어 제한', options=levels, value=('Bronze 5', 'Ruby 1'))

with open(os.path.join(project_dir, 'models', 'ALS_model.pkl'), 'br') as file:
    als_model: ALSRecSys = pickle.load(file)
if left.button('추천받기') and handle:
    matched_ids = []
    id_num = 10
    while len(matched_ids) < 10:
        ids = als_model.get_recommendations(handle, id_num)
        is_in_range = lambda id: levels.index(min_level) + 1 <= problem_df.loc[id]['level'] <= levels.index(max_level) + 1
        matched_ids = [id for id in ids if is_in_range(id)]
        id_num *= 2
    row1 = st.columns(5)
    row2 = st.columns(5)
    for id, col in zip(matched_ids, row1 + row2):
        title = problem_df.loc[id]['titleKo']
        level = problem_df.loc[id]['level']
        tile = col.container(border=True)
        with tile:
            left, mid, right = st.columns(3)
            with mid:
                image_dir = os.path.join(project_dir, 'assets', f'{level}.png')
                st.image(image_dir, width=70)
                disable_fullscreen = r'<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
                st.markdown(disable_fullscreen, unsafe_allow_html=True)
            st.link_button(f"{id} - {title}",f"https://www.acmicpc.net/problem/{id}", use_container_width=True)