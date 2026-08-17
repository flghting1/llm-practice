import os

import requests
import streamlit as st


API_URL = os.getenv(
    "RAG_API_URL",
    "http://127.0.0.1:8001/ask",
)

st.set_page_config(
    page_title="知识库问答",
    layout="centered",
)

st.title("知识库问答")

with st.form("question_form"):
    question = st.text_area(
        "问题",
        height=100,
        max_chars=500,
    )
    submitted = st.form_submit_button(
        "提交问题",
        type="primary",
        use_container_width=True,
    )

if submitted:
    question = question.strip()

    if not question:
        st.warning("问题不能为空。")
    else:
        try:
            with st.spinner("正在检索资料"):
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=30,
                )
                response.raise_for_status()
                result = response.json()

        except requests.Timeout:
            st.error("请求超时，请稍后重试。")

        except requests.RequestException:
            st.error("无法连接知识库服务。")

        else:
            st.subheader("回答")
            st.write(result["answer"])

            st.subheader("来源")
            sources = result["sources"]

            if not sources:
                st.info("未找到可引用的资料。")

            for source in sources:
                st.markdown(
                    f"**{source['title']}**"
                )
                st.caption(
                    f"{source['source']} · "
                    f"相似度 {source['score']:.4f}"
                )