full_context = """
Python 是一种编程语言。
Git 用来记录代码变化。
HTTP 用来进行网络通信。
RAG 会先检索相关资料，再交给模型回答。
Docker 用来封装应用及其运行环境。
"""

relevant_context = """
RAG 会先检索相关资料，再交给模型回答。
"""

question = "RAG 的基本流程是什么？"

print("完整上下文字符数：", len(full_context))
print("相关上下文字符数：", len(relevant_context))
print("问题字符数：", len(question))
print("节省字符数：", len(full_context) - len(relevant_context))