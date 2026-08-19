import pandas as pd
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8003"

st.set_page_config(
    page_title="SQL 数据分析 Agent",
    page_icon="",
    layout="wide",
)

st.title("SQL 数据分析 Agent")

question = st.text_input(
    "分析问题",
    value="各商品的销售额是多少？",
)

query_button = st.button(
    "查询",
    type="primary",
    use_container_width=True,
)

if query_button:
    if not question.strip():
        st.warning("请输入分析问题")
        st.stop()

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=30,
        )

        if response.status_code != 200:
            error_data = response.json()
            st.error(
                error_data.get(
                    "detail",
                    "查询失败",
                )
            )
            st.stop()

        result = response.json()

    except requests.ConnectionError:
        st.error("无法连接 SQL Agent API")
        st.stop()

    except requests.RequestException as error:
        st.error(f"请求失败：{error}")
        st.stop()

    st.subheader("查询解释")
    st.write(result["description"])

    metric_columns = st.columns(3)

    metric_columns[0].metric(
        "结果数量",
        len(result["rows"]),
    )
    metric_columns[1].metric(
        "SQL 执行次数",
        result.get("attempts", 1),
    )
    metric_columns[2].metric(
        "是否修复",
        "是" if result.get("repaired") else "否",
    )

    st.subheader("生成的 SQL")
    st.code(result["sql"], language="sql")

    st.subheader("查询结果")

    rows = result["rows"]

    if not rows:
        st.info("查询结果为空")
        st.stop()

    dataframe = pd.DataFrame(rows)

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns.tolist()

    label_columns = [
        column
        for column in dataframe.columns
        if column not in numeric_columns
    ]

    if numeric_columns and label_columns:
        st.subheader("数据图表")

        chart_data = dataframe.set_index(
            label_columns[0]
        )[[numeric_columns[-1]]]

        st.bar_chart(
            chart_data,
            use_container_width=True,
        )