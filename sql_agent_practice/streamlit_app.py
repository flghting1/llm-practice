import html
import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("SQL_API_URL", "http://127.0.0.1:8003")

QUICK_QUESTIONS = [
    ("商品销售额", "各商品的销售额是多少？"),
    ("城市客户", "每个城市有多少客户？"),
    ("订单状态", "不同状态的订单数量是多少？"),
    ("最高消费", "谁的消费最高？"),
]


st.set_page_config(
    page_title="QUERYROOM | SQL 数据分析",
    page_icon="Q",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700;900&display=swap');
    .stApp { background:#08110f; color:#e6f0ea; font-family:'Manrope','Noto Sans SC',sans-serif; }
    [data-testid="stHeader"] { background:rgba(8,17,15,.9); }
    [data-testid="stSidebar"] { background:#0c1815; border-right:1px solid #22362f; }
    [data-testid="stSidebar"] > div:first-child { padding:2rem 1.2rem; }
    .block-container { max-width:1240px; padding:2.25rem 3.4rem 5rem; }
    .brand { display:flex; align-items:center; gap:.7rem; margin-bottom:2.3rem; }
    .brand-mark { width:32px; height:32px; display:grid; place-items:center; border:1px solid #65a99a; color:#9be6d2; font:700 1rem 'DM Mono',monospace; }
    .brand-name { color:#f0f8f4; font-size:.84rem; font-weight:800; letter-spacing:.12em; }
    .brand-sub, .eyebrow, .metric-label, .answer-kicker, .answer-meta, .side-item strong { font-family:'DM Mono',monospace; }
    .brand-sub { color:#789389; font-size:.62rem; letter-spacing:.08em; margin-top:.1rem; }
    .eyebrow { color:#a3e3ba; font-size:.7rem; letter-spacing:.15em; margin-bottom:.65rem; }
    h1 { color:#eff8f2 !important; font-size:clamp(2rem,4vw,3.6rem) !important; line-height:1.07 !important; letter-spacing:-.04em; margin:0 !important; }
    .hero-copy { color:#9eb1a8; font-size:1rem; line-height:1.7; max-width:640px; margin:.9rem 0 1.9rem; }
    .metric-row { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:1.5rem; }
    .metric { background:#0f201b; border:1px solid #29463b; padding:14px 16px; }
    .metric-label { color:#86a096; font-size:.65rem; letter-spacing:.08em; }
    .metric-value { color:#edf7f0; font-size:1.35rem; font-weight:700; margin-top:5px; }
    .metric-value span { color:#a3e3ba; font:.68rem 'DM Mono',monospace; margin-left:5px; }
    .section-label { color:#c8d9d0; font-size:.8rem; font-weight:700; letter-spacing:.05em; margin:1.65rem 0 .65rem; }
    .stTextInput input { background:#0c1a17 !important; color:#edf7f0 !important; border:1px solid #3e5d51 !important; border-radius:2px !important; min-height:46px; }
    .stTextInput input:focus { border-color:#9be6d2 !important; box-shadow:0 0 0 1px #9be6d2 !important; }
    .stTextInput label { color:#91a99f !important; font:.7rem 'DM Mono',monospace !important; }
    .stButton button, .stFormSubmitButton button { border-radius:2px !important; border:1px solid #9be6d2 !important; background:#9be6d2 !important; color:#071310 !important; min-height:42px; font-weight:800 !important; }
    .stButton button:hover, .stFormSubmitButton button:hover { background:#c1f4e5 !important; border-color:#c1f4e5 !important; }
    .quick-label { color:#789389; font:.65rem 'DM Mono',monospace; letter-spacing:.08em; margin:1.1rem 0 .45rem; }
    [data-testid="stVerticalBlockBorderWrapper"] { background:#0d1b17; border-color:#28443a; border-radius:2px; }
    .answer-kicker { color:#a3e3ba; font-size:.66rem; letter-spacing:.12em; margin-bottom:.45rem; }
    .answer-title { color:#eef8f2; font-size:1.2rem; font-weight:700; }
    .answer-meta { color:#8da59a; font-size:.68rem; border-top:1px solid #28443a; padding-top:.8rem; margin-top:1rem; }
    .side-title { color:#d4e2db; font-size:.72rem; font-weight:700; letter-spacing:.08em; margin:1.5rem 0 .75rem; }
    .side-item { display:flex; justify-content:space-between; color:#93a99f; font-size:.76rem; padding:.55rem 0; border-bottom:1px solid #20382f; }
    .side-item strong { color:#dff0e7; font-size:.68rem; font-weight:500; }
    .status-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#a3e3ba; margin-right:7px; box-shadow:0 0 9px #a3e3ba; }
    .footer-note { color:#698278; font:.62rem 'DM Mono',monospace; line-height:1.7; margin-top:2rem; }
    [data-testid="stDataFrame"] { border:1px solid #28443a; }
    @media (max-width:760px) { .block-container { padding:1.5rem 1rem 3rem; } .metric-row { grid-template-columns:1fr; } h1 { font-size:2.4rem !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

if "question" not in st.session_state:
    st.session_state.question = QUICK_QUESTIONS[0][1]

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">Q</div><div><div class="brand-name">QUERYROOM</div><div class="brand-sub">CONTROLLED SQL WORKSPACE</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-title">执行边界</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span><i class="status-dot"></i>查询通道</span><strong>READY</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>语句策略</span><strong>SELECT ONLY</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>执行上限</span><strong>100 ROWS</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>失败修复</span><strong>MAX 1</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-title">固定回归集</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>正常业务问题</span><strong>4 CASES</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>危险 SQL</span><strong>4 CASES</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item"><span>无效问题</span><strong>2 CASES</strong></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-note">只读分析 | 数据库 Authorizer<br>规则型自然语言转 SQL 原型</div>', unsafe_allow_html=True)

st.markdown('<div class="eyebrow">CONTROLLED DATA ANALYSIS / 02</div>', unsafe_allow_html=True)
st.markdown('<h1>让业务问题，落到<br><span style="color:#a3e3ba">可控的查询。</span></h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">面向销售、客户与订单分析的受控 SQL 查询原型。自然语言只负责表达问题，权限与执行边界由数据库执行层兜底。</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="metric-row"><div class="metric"><div class="metric-label">Query policy</div><div class="metric-value">READ <span>ONLY</span></div></div><div class="metric"><div class="metric-label">Evaluation set</div><div class="metric-value">4 + 4 <span>FIXED CASES</span></div></div><div class="metric"><div class="metric-label">Execution guard</div><div class="metric-value">2 <span>MAX ATTEMPTS</span></div></div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="quick-label">常用业务查询</div>', unsafe_allow_html=True)
quick_columns = st.columns(len(QUICK_QUESTIONS))
for column, (label, value) in zip(quick_columns, QUICK_QUESTIONS):
    if column.button(label, use_container_width=True):
        st.session_state.question = value

st.markdown('<div class="section-label">分析问题</div>', unsafe_allow_html=True)
with st.form("sql_query_form"):
    question = st.text_input(
        "QUERY",
        key="question",
        max_chars=200,
        placeholder="输入一个销售、客户或订单分析问题",
    )
    submitted = st.form_submit_button("生成受控查询  ->", use_container_width=True)

if submitted:
    cleaned_question = question.strip()
    if not cleaned_question:
        st.warning("问题不能为空。")
        st.stop()

    try:
        with st.spinner("正在生成并执行只读查询"):
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": cleaned_question},
                timeout=30,
            )

        if response.status_code != 200:
            detail = response.json().get("detail", "查询失败")
            st.error(detail)
            st.stop()

        result = response.json()
    except requests.ConnectionError:
        st.error("无法连接 SQL 查询服务。")
        st.stop()
    except requests.RequestException as error:
        st.error(f"请求失败：{error}")
        st.stop()

    rows = result["rows"]
    dataframe = pd.DataFrame(rows)
    status_text = "REPAIRED ONCE" if result.get("repaired") else "EXECUTED"

    st.markdown('<div class="section-label">查询结果</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="answer-kicker">' + status_text + '</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="answer-title">'
            + html.escape(result["description"])
            + '</div>',
            unsafe_allow_html=True,
        )
        metric_columns = st.columns(3)
        metric_columns[0].metric("返回记录", len(rows))
        metric_columns[1].metric("执行次数", result.get("attempts", 1))
        metric_columns[2].metric("修复状态", "已修复" if result.get("repaired") else "未触发")
        st.markdown(
            '<div class="answer-meta">READ-ONLY EXECUTION | QUERY: '
            + html.escape(cleaned_question)
            + '</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">生成的 SQL</div>', unsafe_allow_html=True)
    st.code(result["sql"], language="sql")

    st.markdown('<div class="section-label">数据结果</div>', unsafe_allow_html=True)
    if dataframe.empty:
        st.info("查询结果为空。")
    else:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)

        numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
        label_columns = [
            column for column in dataframe.columns if column not in numeric_columns
        ]
        if numeric_columns and label_columns:
            st.markdown('<div class="section-label">结果分布</div>', unsafe_allow_html=True)
            chart_data = dataframe.set_index(label_columns[0])[[numeric_columns[-1]]]
            st.bar_chart(chart_data, use_container_width=True, color="#9be6d2")
