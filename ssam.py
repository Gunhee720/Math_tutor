import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import base64
import traceback

load_dotenv()

st.title("📸 사고력 강화형 AI 튜터 (디버깅 버전)")

# ----------------------------------------------------------
# Checkpoint 1
# ----------------------------------------------------------
print("🟦 Checkpoint 1: Streamlit UI 로드됨")

# 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    print("🟩 chat_history initialized")

if "hint_step" not in st.session_state:
    st.session_state.hint_step = 0
    print("🟩 hint_step initialized")

# ----------------------------------------------------------
# Checkpoint 2
# ----------------------------------------------------------
print("🟦 Checkpoint 2: 모델 로드 시작")

try:
    model = ChatOpenAI(
        model="gpt-4o-mini",
        max_tokens=1024
    )
    print("🟩 모델 로드 성공")
except Exception as e:
    print("❌ 모델 로딩 실패:")
    st.code(str(e))
    st.stop()

# ----------------------------------------------------------
# 파일 업로드
# ----------------------------------------------------------
print("🟦 Checkpoint 3: 파일 업로드 확인")
uploaded_file = st.file_uploader("풀고싶은 문제를 올려주세요!", type=["png", "jpg", "jpeg"])
print("📄 uploaded_file =", uploaded_file)

def encode_image(file):
    try:
        data = file.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        print("❌ 이미지 인코딩 실패:")
        st.code(str(e))
        return None

# ----------------------------------------------------------
# 지난 대화 출력
# ----------------------------------------------------------
print("🟦 Checkpoint 4: 이전 대화 렌더링 시작")
for role, content in st.session_state.chat_history:
    st.chat_message(role).write(content)
print("🟩 이전 대화 렌더링 완료")

# ----------------------------------------------------------
# 힌트 버튼
# ----------------------------------------------------------
print("🟦 Checkpoint 5: 힌트 버튼 렌더링")

c1, c2, c3 = st.columns(3)
if c1.button("1단계 힌트"):
    st.session_state.hint_step = 1
if c2.button("2단계 힌트"):
    st.session_state.hint_step = 2
if c3.button("3단계 힌트"):
    st.session_state.hint_step = 3

print("🎚 현재 hint_step =", st.session_state.hint_step)

# ----------------------------------------------------------
# 사용자 입력
# ----------------------------------------------------------
print("🟦 Checkpoint 6: 텍스트 입력 대기")
user_text = st.chat_input("질문 또는 풀이 입력")
print("📄 user_text =", user_text)

# ----------------------------------------------------------
# 모델 호출 준비
# ----------------------------------------------------------
if user_text or uploaded_file:

    print("🟦 Checkpoint 7: 모델 호출 준비")

    st.session_state.chat_history.append(("user", user_text if user_text else "[이미지 업로드됨]"))

    # content 구성
    content = [
        {
            "type": "text",
            "text": f"""
너는 사고력 강화형 AI 수학 튜터다.
정답은 절대 알려주지 않는다.
힌트 단계: {st.session_state.hint_step}
학생 입력: {user_text}
"""
        }
    ]

    if uploaded_file:
        print("🟦 Checkpoint 7-1: 이미지 base64 변환 시도")
        base64_img = encode_image(uploaded_file)
        st.write("📄 base64 문자 길이:", len(base64_img) if base64_img else "None")

        if base64_img:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_img}"}
            })
            print("🟩 이미지 content 구성 완료")

    # ----------------------------------------------------------
    # 모델 실제 호출 및 예외 처리
    # ----------------------------------------------------------
    st.write("🟦 Checkpoint 8: 모델 호출 시작")

    try:
        response = model.invoke([
            {"role": "user", "content": content}
        ])
        print("🟩 모델 응답 성공")
    except Exception as e:
        print("❌ 모델 호출 중 에러 발생")
        st.code(traceback.format_exc())  # 전체 오류 표시
        st.stop()

    # 응답 처리
    answer = response.content
    st.session_state.chat_history.append(("assistant", answer))
    st.chat_message("assistant").write(answer)

    print("🟩 전체 프로세스 완료")

