import streamlit as st
import json
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def load_rubric(uploaded_file):
    content = uploaded_file.getvalue().decode("utf-8")
    return json.loads(content)

def evaluate_work(rubric, student_work):
    prompt = f"""
    다음은 학생 작품 평가를 위한 루브릭입니다:
    {json.dumps(rubric, ensure_ascii=False, indent=2)}

    다음은 평가할 학생의 작품입니다:
    {student_work}

    이 루브릭을 사용하여 학생의 작품을 평가해주세요. 각 평가 기준에 대해 다음을 제공해주세요:
    1. 점수 (최상: 20점, 상: 16점, 중: 12점, 하: 8점, 최하: 4점)
    2. 간단한 평가 설명
    3. 개선을 위한 건설적인 피드백

    마지막에는 총점과 전체적인 피드백을 제공해주세요.

    응답은 다음 형식으로 작성해주세요:
    평가 기준 1: [점수]점
    설명: [평가 설명]
    피드백: [건설적인 피드백]

    평가 기준 2: [점수]점
    설명: [평가 설명]
    피드백: [건설적인 피드백]

    ...

    총점: [총점]점

    전체 피드백: [전체적인 건설적 피드백]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 교육 전문가로서 학생의 작품을 평가하고 건설적인 피드백을 제공합니다."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"평가 중 오류가 발생했습니다: {str(e)}")
        return None

def main():
    st.title("학생 작품 평가 앱")

    uploaded_file = st.file_uploader("루브릭 JSON 파일을 업로드하세요", type="json")
    
    if uploaded_file is not None:
        try:
            rubric = load_rubric(uploaded_file)
            st.success("루브릭이 성공적으로 로드되었습니다.")

            # 루브릭 내용 표시
            st.subheader("로드된 루브릭:")
            st.json(rubric)

            student_work = st.text_area("학생의 작품을 입력하세요", height=300)

            if st.button("평가하기"):
                if student_work:
                    with st.spinner('작품을 평가 중입니다...'):
                        evaluation = evaluate_work(rubric, student_work)
                    if evaluation:
                        st.markdown("## 평가 결과")
                        st.markdown(evaluation)
                else:
                    st.warning("학생의 작품을 입력해주세요.")
        except json.JSONDecodeError:
            st.error("올바른 JSON 형식의 루브릭 파일을 업로드해주세요.")
        except Exception as e:
            st.error(f"루브릭 처리 중 오류가 발생했습니다: {str(e)}")
    else:
        st.info("시작하려면 루브릭 JSON 파일을 업로드하세요.")

if __name__ == "__main__":
    main()
