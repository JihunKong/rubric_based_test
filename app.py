import streamlit as st
import json
import pandas as pd
import openai

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# JSON 파일 업로드 및 파싱
def load_rubric(uploaded_file):
    if uploaded_file is not None:
        rubric = json.load(uploaded_file)
        return rubric
    return None

# 배점 조정 함수
def adjust_points(rubric):
    total_original_points = sum(criterion['points'] for criterion in rubric.values())
    adjustment_factor = 100 / total_original_points
    
    adjusted_rubric = {}
    for criterion, details in rubric.items():
        adjusted_points = round(details['points'] * adjustment_factor, 2)
        adjusted_rubric[criterion] = {**details, 'points': adjusted_points, 'original_points': details['points']}
    
    return adjusted_rubric

# 학생 작품 평가
def evaluate_work(rubric, student_work):
    scores = {}
    feedback = {}
    total_score = 0
    
    for criterion, details in rubric.items():
        prompt = f"""
        평가 기준: {criterion}
        설명: {details['description']}
        최고점 기준: {details['exemplary']}
        원래 배점: {details['original_points']}점
        조정된 배점: {details['points']}점
        학생 작품:
        {student_work}
        
        위 정보를 바탕으로 다음을 수행하세요:
        1. 0부터 {details['points']}까지의 점수를 부여하세요.
        2. 점수에 대한 간단한 설명과 개선을 위한 구체적인 피드백을 제공하세요.
        
        응답 형식:
        점수: [0-{details['points']} 사이의 숫자]
        설명: [점수에 대한 간단한 설명]
        피드백: [개선을 위한 구체적인 제안]
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}]
        )
        
        result = response.choices[0].message.content.split('\n')
        score = float(result[0].split(':')[1].strip())
        explanation = result[1].split(':')[1].strip()
        feedback_text = result[2].split(':')[1].strip()
        
        scores[criterion] = score
        feedback[criterion] = f"{explanation}\n\n개선 제안: {feedback_text}"
        total_score += score
    
    return scores, feedback, total_score

# Streamlit 앱
def main():
    st.title("학생 작품 평가 시스템")
    
    # JSON 파일 업로드
    uploaded_file = st.file_uploader("루브릭 JSON 파일을 업로드하세요", type="json")
    original_rubric = load_rubric(uploaded_file)
    
    if original_rubric:
        adjusted_rubric = adjust_points(original_rubric)
        st.success("루브릭이 성공적으로 로드되고 배점이 조정되었습니다.")
        
        # 조정된 루브릭 표시
        st.subheader("조정된 루브릭")
        for criterion, details in adjusted_rubric.items():
            st.write(f"{criterion}: {details['points']}점 (원래 {details['original_points']}점)")
        
        # 학생 작품 입력
        work_type = st.radio("학생 작품 입력 방식을 선택하세요:", ("텍스트 입력", "파일 업로드"))
        
        if work_type == "텍스트 입력":
            student_work = st.text_area("학생 작품을 여기에 입력하세요:")
        else:
            work_file = st.file_uploader("학생 작품 파일을 업로드하세요", type=["txt", "pdf"])
            if work_file:
                student_work = work_file.getvalue().decode("utf-8")
            else:
                student_work = ""
        
        if st.button("평가하기") and student_work:
            scores, feedback, total_score = evaluate_work(adjusted_rubric, student_work)
            
            st.subheader("평가 결과")
            st.write(f"총점: {total_score:.2f}/100")
            
            for criterion, score in scores.items():
                st.write(f"\n{criterion}: {score:.2f}/{adjusted_rubric[criterion]['points']} (원래 배점: {adjusted_rubric[criterion]['original_points']})")
                st.write(feedback[criterion])
    else:
        st.warning("루브릭 JSON 파일을 먼저 업로드해주세요.")

if __name__ == "__main__":
    main()
