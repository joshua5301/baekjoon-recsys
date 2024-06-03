import streamlit as st
import pandas as pd 
import collaborative_model
import os

# 페이지 기본 설정
st.set_page_config(
    page_title = "백준 알고리즘 문제 추천 시스템",
    layout = "wide"
)

project_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(project_dir, 'data', 'preprocessed', 'problem_info.csv')
problem_df = pd.read_csv(data_dir, index_col=0)

st.header("백준 문제 추천해드립니다!")

handle = st.text_input(label='', placeholder='solved.ac 핸들을 입력해주세요.')
if st.button("추천받기") and handle:
    recommendations = collaborative_model.get_recommendations(handle, 10)
    row1 = st.columns(5)
    row2 = st.columns(5)
    for id, col in zip(recommendations, row1 + row2):
        title = problem_df.loc[id]['titleKo']
        level = problem_df.loc[id]['level']
        with col:
            image_dir = os.path.join(project_dir, 'assets', f'{level}.png')
            st.image(image_dir, width=100)
            hide_img_fs = '''
            <style>
            button[title="View fullscreen"]{
                visibility: hidden;}
            </style>
            '''
            st.markdown(hide_img_fs, unsafe_allow_html=True)
            st.link_button(f"{id} - {title}",f"https://www.acmicpc.net/problem/{id}")