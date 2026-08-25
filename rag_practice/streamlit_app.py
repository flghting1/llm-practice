import os

import requests
import streamlit as st


API_URL = os.getenv(
    "RAG_API_URL",
    "http://127.0.0.1:8001/ask",
)

st.set_page_config(
    page_title="NEXUS | 求职知识库",
    page_icon="*",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700;900&display=swap');
    .stApp { background:#070c15; color:#e8edf7; font-family:'Manrope','Noto Sans SC',sans-serif; }
    [data-testid="stHeader"] { background:rgba(7,12,21,.86); }
    [data-testid="stSidebar"] { background:#0b1220; border-right:1px solid #1b2638; }
    [data-testid="stSidebar"] > div:first-child { padding:2rem 1.25rem; }
    .block-container { max-width:1240px; padding:2.25rem 3.5rem 5rem; }
    .brand { display:flex; align-items:center; gap:.7rem; margin-bottom:2.5rem; }
    .brand-mark { width:32px; height:32px; display:grid; place-items:center; border:1px solid #416c6a; color:#74e0c1; font-size:1.1rem; }
    .brand-name { color:#f5f7fb; font-size:.84rem; font-weight:800; letter-spacing:.12em; }
    .brand-sub, .eyebrow, .answer-kicker, .answer-meta, .source-meta { font-family:'DM Mono',monospace; }
    .brand-sub { color:#6f7c90; font-size:.62rem; letter-spacing:.08em; margin-top:.1rem; }
    .eyebrow { color:#74e0c1; font-size:.7rem; letter-spacing:.16em; margin-bottom:.65rem; }
    h1 { color:#f6f8fc !important; font-size:clamp(2rem,4vw,3.8rem) !important; letter-spacing:-.055em; line-height:1.05 !important; margin:0 !important; }
    .hero-copy { color:#9aa7bb; font-size:1rem; line-height:1.7; max-width:600px; margin:.9rem 0 2rem; }
    .metric-row { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:0 0 2.4rem; }
    .metric { background:#0d1625; border:1px solid #233148; padding:15px 17px; }
    .metric-label { color:#7f8ca2; font:.65rem 'DM Mono',monospace; letter-spacing:.08em; }
    .metric-value { color:#e9eef8; font-size:1.4rem; font-weight:700; margin-top:5px; }
    .metric-value span { color:#74e0c1; font-size:.7rem; font-family:'DM Mono',monospace; margin-left:5px; }
    .section-label { color:#c5cede; font-size:.78rem; font-weight:700; letter-spacing:.05em; margin:1.4rem 0 .65rem; }
    .stTextArea textarea { background:#0d1727 !important; color:#edf3fc !important; border:1px solid #32425c !important; border-radius:2px !important; font-size:1rem !important; min-height:132px; }
    .stTextArea textarea:focus { border-color:#74e0c1 !important; box-shadow:0 0 0 1px #74e0c1 !important; }
    .stTextArea label { color:#8996aa !important; font-size:.72rem !important; font-family:'DM Mono',monospace; }
    .stButton button, .stFormSubmitButton button { border-radius:2px !important; border:1px solid #4fbd9f !important; background:#74e0c1 !important; color:#07131a !important; font-weight:800 !important; min-height:44px; }
    .stButton button:hover, .stFormSubmitButton button:hover { background:#a0f0da !important; border-color:#a0f0da !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { background:#0d1625; border-color:#25344b; border-radius:2px; }
    .answer-kicker { color:#74e0c1; font-size:.65rem; letter-spacing:.12em; margin-bottom:.5rem; }
    .answer-meta { color:#7d8ba1; font-size:.68rem; border-top:1px solid #233148; padding-top:.8rem; margin-top:1rem; }
    .source-card { border-left:2px solid #5d83d8; background:#101a2a; padding:12px 14px; margin:8px 0; }
    .source-title { color:#e7edf8; font-size:.88rem; font-weight:700; }
    .source-meta { color:#8090a8; font-size:.67rem; margin-top:5px; }
    .side-title { color:#dce5f3; font-size:.72rem; font-weight:700; letter-spacing:.08em; margin:1.5rem 0 .8rem; }
    .side-item { display:flex; justify-content:space-between; color:#8c9ab0; font-size:.76rem; padding:.55rem 0; border-bottom:1px solid #1a2638; }
    .side-item strong { color:#dce6f5; font-family:'DM Mono',monospace; font-weight:500; }
    .status-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#74e0c1; margin-right:7px; box-shadow:0 0 10px #74e0c1; }
    .footer-note { color:#5f6d81; font:.62rem 'DM Mono',monospace; line-height:1.7; margin-top:2rem; }
    @media (max-width:760px) { .block-container { padding:1.5rem 1rem 3rem; } .metric-row { grid-template-columns:1fr; } h1 { font-size:2.4rem !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">*</div><div><div class="brand-name">NEXUS RAG</div><div class="brand-sub">PERSONAL KNOWLEDGE SYSTEM</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-title">系统状态</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span><i class="status-dot"></i>检索服务</span><strong>READY</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>知识文档</span><strong>18 MD</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>索引分片</span><strong>35</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-title">检索策略</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>Embedding</span><strong>bge-small-zh</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>回答模式</span><strong>evidence-first</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-note">证据优先 | 可追溯引用<br>面向求职准备的个人知识工作台</div>', unsafe_allow_html=True)

st.markdown('<div class="eyebrow">PERSONAL KNOWLEDGE WORKSPACE / 01</div>', unsafe_allow_html=True)
st.markdown('<h1>把知识，变成<br><span style="color:#74e0c1">更好的回答。</span></h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">面向 AI 岗位准备的检索增强问答。连接岗位描述、技术文档与面试笔记，让每一次回答都有依据。</div>', unsafe_allow_html=True)
st.markdown('<div class="metric-row"><div class="metric"><div class="metric-label">Knowledge base</div><div class="metric-value">18 <span>DOCUMENTS</span></div></div><div class="metric"><div class="metric-label">Indexed chunks</div><div class="metric-value">35 <span>RETRIEVAL UNITS</span></div></div><div class="metric"><div class="metric-label">Answer policy</div><div class="metric-value">CITED <span>GROUNDED</span></div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">向知识库提问</div>', unsafe_allow_html=True)

with st.form("question_form"):
    question = st.text_area(
        "QUERY",
        height=132,
        max_chars=500,
        placeholder="输入你正在准备的问题，例如：如何把项目上线？",
    )
    submitted = st.form_submit_button(
        "检索并生成回答  ->",
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
            st.markdown('<div class="section-label">回答结果</div>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<div class="answer-kicker">GROUNDED RESPONSE</div>', unsafe_allow_html=True)
                st.markdown(result["answer"])

                answer_mode = result.get("answer_mode")
                if answer_mode == "llm":
                    mode_text = "LLM | 基于检索证据生成"
                elif answer_mode == "no_answer":
                    mode_text = "REFUSED | 当前资料不足"
                else:
                    mode_text = "FALLBACK | 离线证据回答"
                st.markdown('<div class="answer-meta">' + mode_text + " | QUERY: " + question + "</div>", unsafe_allow_html=True)

            st.markdown('<div class="section-label">引用来源</div>', unsafe_allow_html=True)
            sources = result["sources"]

            if not sources:
                st.info("未找到可引用的资料。")

            for source in sources:
                st.markdown(
                    '<div class="source-card"><div class="source-title">'
                    + str(source["title"])
                    + '</div><div class="source-meta">'
                    + str(source["source"])
                    + " | 相似度 "
                    + format(source["score"], ".4f")
                    + "</div></div>",
                    unsafe_allow_html=True,
                )
