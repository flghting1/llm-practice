import pandas as pd
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8005"

st.set_page_config(
    page_title="简历与 JD 匹配助手",
    page_icon="",
    layout="wide",
)

st.title("简历与 JD 匹配助手")
st.caption("支持单个岗位匹配和多个岗位对比")

default_resume = """
熟悉 Python、Git、FastAPI、RAG、Embedding、Docker、
Streamlit、Prompt、Pydantic 和自动化测试。
"""

default_jd = """
岗位要求：Python、FastAPI、RAG、Embedding、Docker、
SQL、Streamlit 和测试经验。
"""

mode = st.radio(
    "匹配模式",
    ["单个 JD 匹配", "多个 JD 对比"],
    horizontal=True,
)

resume_text = st.text_area(
    "简历内容",
    value=default_resume,
    height=220,
)

if mode == "单个 JD 匹配":
    jd_text = st.text_area(
        "岗位 JD",
        value=default_jd,
        height=220,
    )

    if st.button(
        "开始匹配",
        type="primary",
        use_container_width=True,
    ):
        if not resume_text.strip():
            st.warning("请输入简历内容")
            st.stop()

        if not jd_text.strip():
            st.warning("请输入岗位 JD")
            st.stop()

        try:
            response = requests.post(
                f"{API_URL}/match",
                json={
                    "resume_text": resume_text,
                    "jd_text": jd_text,
                },
                timeout=30,
            )

            if response.status_code != 200:
                st.error(
                    response.json().get(
                        "detail",
                        "匹配失败",
                    )
                )
                st.stop()

            report = response.json()

        except requests.ConnectionError:
            st.error(
                "无法连接匹配 API，请确认 API 已启动"
            )
            st.stop()

        st.subheader("匹配概览")

        columns = st.columns(3)
        columns[0].metric(
            "匹配分数",
            f"{report['match_score']} 分",
        )
        columns[1].metric(
            "风险等级",
            report["risk_level"],
        )
        columns[2].metric(
            "缺少技能",
            len(report["missing_skills"]),
        )

        st.info(report["explanation"])

        st.subheader("技能对比")

        skill_rows = [
            {
                "技能状态": "已掌握",
                "技能": skill,
            }
            for skill in report["matched_skills"]
        ] + [
            {
                "技能状态": "缺少",
                "技能": skill,
            }
            for skill in report["missing_skills"]
        ]

        skills_df = pd.DataFrame(skill_rows)

        if not skills_df.empty:
            st.dataframe(
                skills_df,
                use_container_width=True,
                hide_index=True,
            )

        chart_df = pd.DataFrame(
            {
                "技能数量": [
                    len(report["matched_skills"]),
                    len(report["missing_skills"]),
                ]
            },
            index=["已掌握技能", "缺少技能"],
        )

        st.bar_chart(chart_df)

        st.subheader("建议补充的项目")

        if report["projects_to_build"]:
            for project in report["projects_to_build"]:
                st.write(f"- {project}")
        else:
            st.success("当前没有必须补充的项目")

        st.subheader("面试风险点")

        if report["interview_risks"]:
            for risk in report["interview_risks"]:
                st.write(f"- {risk}")
        else:
            st.success("暂未发现明显面试风险")

        with st.expander("查看完整 JSON 报告"):
            st.json(report)

else:
    st.markdown(
        "每行填写一个岗位，格式为：岗位名称｜JD 内容"
    )

    default_multi_jd = """RAG 应用开发岗位｜要求 Python、FastAPI、RAG、Embedding、Docker、SQL 和测试经验。
后端 API 开发岗位｜要求 Python、FastAPI、Git、REST API 和 Docker。
数据分析开发岗位｜要求 Python、SQL、Streamlit 和测试经验。"""

    multi_jd_text = st.text_area(
        "多个岗位 JD",
        value=default_multi_jd,
        height=180,
    )

    if st.button(
        "开始对比",
        type="primary",
        use_container_width=True,
    ):
        if not resume_text.strip():
            st.warning("请输入简历内容")
            st.stop()

        jd_items = []

        for line_number, line in enumerate(
            multi_jd_text.splitlines(),
            start=1,
        ):
            if not line.strip():
                continue

            if "｜" not in line:
                st.error(
                    f"第 {line_number} 行缺少分隔符｜"
                )
                st.stop()

            name, jd = line.split("｜", maxsplit=1)

            if not name.strip() or not jd.strip():
                st.error(
                    f"第 {line_number} 行岗位名称或 JD 为空"
                )
                st.stop()

            jd_items.append(
                {
                    "name": name.strip(),
                    "jd": jd.strip(),
                }
            )

        if not jd_items:
            st.warning("请至少填写一份 JD")
            st.stop()

        try:
            response = requests.post(
                f"{API_URL}/compare",
                json={
                    "resume_text": resume_text,
                    "jd_items": jd_items,
                },
                timeout=30,
            )

            if response.status_code != 200:
                st.error(
                    response.json().get(
                        "detail",
                        "对比失败",
                    )
                )
                st.stop()

            result = response.json()

        except requests.ConnectionError:
            st.error(
                "无法连接匹配 API，请确认 API 已启动"
            )
            st.stop()

        st.success(
            f"建议优先关注：{result['best_match']}"
        )

        st.info(result["recommendation"])

        if result["common_missing_skills"]:
            st.warning(
                "共同技能缺口："
                + "、".join(
                    result["common_missing_skills"]
                )
            )

        rows = []

        for item in result["comparisons"]:
            report = item["report"]

            rows.append(
                {
                    "岗位": item["jd_name"],
                    "匹配分数": report["match_score"],
                    "风险等级": report["risk_level"],
                    "已掌握技能数": len(
                        report["matched_skills"]
                    ),
                    "缺少技能数": len(
                        report["missing_skills"]
                    ),
                    "缺少技能": "、".join(
                        report["missing_skills"]
                    ),
                }
            )

        comparison_df = pd.DataFrame(rows)

        st.subheader("岗位对比结果")

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
        )

        chart_df = comparison_df.set_index("岗位")[
            ["匹配分数"]
        ]

        st.subheader("岗位匹配分数")

        st.bar_chart(
            chart_df,
            use_container_width=True,
        )

        with st.expander("查看完整 JSON 报告"):
            st.json(result)