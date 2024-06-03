import os
import pandas as pd
from langdetect import detect, LangDetectException
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import linear_kernel

# 데이터 파일 경로
project_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(project_dir, 'data', 'preprocessed', 'problem_info.csv')

# 데이터 로드
problem_df = pd.read_csv(data_dir, index_col=0)

# 한국어 콘텐츠 필터링 함수
def is_korean(text):
    try:
        return detect(text) == 'ko'
    except LangDetectException:
        return False

# content 칼럼의 null 값을 빈 문자열로 채움
problem_df['content'] = problem_df['content'].fillna('')

# 언어 감지를 시도하기 전에 텍스트 길이를 확인
problem_df['is_korean'] = problem_df['content'].apply(lambda x: is_korean(x) if len(x) > 0 else False)

# 한국어 콘텐츠로 구성된 데이터프레임
korean_problem_df = problem_df[problem_df['is_korean']]

# TfidfVectorizer
countV = CountVectorizer()
count_matrix = countV.fit_transform(korean_problem_df['content'])
# 코사인 유사도 계산
cosine_sim = linear_kernel(count_matrix, count_matrix)

# 문제 인덱스 매핑 중복 제거
indicies = pd.Series(korean_problem_df.index, index=korean_problem_df['problemId']).drop_duplicates()

def get_recommendations(problemId: int, cosine_sim=cosine_sim):
    if problemId not in indicies:
        return "Problem ID not found in Korean content."
    
    idx = indicies[problemId]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse = True)
    # [(3, 0.8), (2, 0.7), (5, 0.4) ...] 이런 식으로 정리!
    sim_scores =  sim_scores[1:11]  # 자기 자신을 제외한 10개의 추천 문제 슬라이싱
    problem_indices = [i[0] for i in sim_scores]
    return korean_problem_df.iloc[problem_indices]['problemId']

if __name__ == '__main__':
    problems = get_recommendations(1000)
    print(problems)