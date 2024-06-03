import streamlit as st
import pandas as pd 
from time import sleep
from model import *


#페이지 기본 설정
st.set_page_config(
    page_title = "백준 알고리즘 문제 추천 시스템",
    layout = "wide"
)

#페이지 헤더, 서브 헤더 제목 설정
return_list = list()
st.header("협업 기반 필터링 추천 제공")
if st.button("추천받기"):
    buttons = get_recommendations()
    for button in buttons: 
            st.link_button(f"https://www.acmicpc.net/problem/{button}")


else:
    st.write("(추천 받기)를 클릭하세요")