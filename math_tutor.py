import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import load_prompt
from langchain_core.output_parsers import StrOutputParser
import base64

load_dotenv()

st.title("📸 사고력 강화형 AI 수학 튜터")
st.write("문제 이미지를 업로드하거나, 궁금한 내용을 입력해보세요! 단계별 힌트를 제공합니다.")

# --------------------------------------------------------
# 세션 초기화
# --------------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "hint_step" not in st.session_state:
    st.session_state.hint_step = 0

# --------------------------------------------------------
# 모델 & YAML 프롬프트
# --------------------------------------------------------
model = ChatOpenAI(
    model="gpt-4o-mini",
    max_tokens=1024
)

prompt = load_prompt("./templates/math_tutor.yaml", encoding="utf-8")

parser = StrOutputParser()

# --------------------------------------------------------
# 이미지 업로드 + 미리보기
# --------------------------------------------------------
uploaded_file = st.file_uploader("📷 문제 사진을 업로드하세요", type=["png", "jpg", "jpeg"])

base64_img = None
if uploaded_file:
    st.image(uploaded_file, caption="📘 업로드한 문제 이미지", use_column_width=True)
    base64_img = base64.b64encode(uploaded_file.read()).decode("utf-8")

# --------------------------------------------------------
# 힌트 버튼
# --------------------------------------------------------
st.write("### 🔍 원하는 도움을 선택하세요!")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👶 어떻게 접근해야 할지 모르겠어요 (1단계 힌트)"):
        st.session_state.hint_step = 1

with col2:
    if st.button("🧠 핵심 개념이 알고 싶어요 (2단계 힌트)"):
        st.session_state.hint_step = 2

with col3:
    if st.button("🚀 거의 다 풀었어요! 마지막 도움! (3단계 힌트)"):
        st.session_state.hint_step = 3

# --------------------------------------------------------
# 대화 기록 출력
# --------------------------------------------------------
for role, content in st.session_state.chat:
    st.chat_message(role).write(content)

# --------------------------------------------------------
# 사용자 입력
# --------------------------------------------------------
user_text = st.chat_input("✏️ 질문 또는 풀이를 입력하세요!")

if user_text or uploaded_file:

    # 사용자 메시지 저장
    st.session_state.chat.append(("user", user_text if user_text else "[이미지 업로드됨]"))

    # 이미지 + 텍스트를 하나의 메시지로 구성
    user_content = [
        {
            "type": "text",
            "text": f"힌트 단계: {st.session_state.hint_step}\n학생 입력: {user_text}"
        }
    ]

    if base64_img:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
        })

    # 모델 호출
    response = model.invoke([
    {"role": "system", "content": prompt.template},   # 수정된 부분
    {"role": "user", "content": user_content}
])

    answer = response.content

    # 기록 저장
    st.session_state.chat.append(("assistant", answer))

    # 출력
    st.chat_message("assistant").write(answer)
