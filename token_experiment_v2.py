article = """
Python 是一种适合初学者的编程语言。
它可以用于脚本、后端服务、数据分析和人工智能应用。
学习 Python 时，需要掌握变量、字符串、列表、字典、条件判断、循环和函数。
Git 可以记录代码变化，帮助开发者保存不同版本。
HTTP 和 API 用于让不同程序之间进行通信。
RAG 的基本流程是先把资料切分，再检索和问题相关的片段，最后把相关片段交给模型回答。
Docker 可以把应用和依赖封装在一起，方便部署。
"""

# 模拟一篇较长文章
long_article = article * 40

# 切成 5 段
part_length = len(long_article) // 5
parts = [
    long_article[i:i + part_length]
    for i in range(0, len(long_article), part_length)
][:5]

question = "RAG 的基本流程是什么？"

# 模拟检索：找到包含 RAG 的片段
relevant_parts = [
    part for part in parts
    if "RAG" in part
]

full_context = "\n".join(parts)
relevant_context = "\n".join(relevant_parts)

# 粗略估算：中文字符数约等于 token 数量级
def estimate_tokens(text):
    return len(text)

print("文章字符数：", len(long_article))
print("文章估算 token 数：", estimate_tokens(long_article))
print("分段数量：", len(parts))
print("全文上下文字符数：", len(full_context))
print("相关片段数量：", len(relevant_parts))
print("相关上下文字符数：", len(relevant_context))
print("节省字符数：", len(full_context) - len(relevant_context))
print("问题：", question)