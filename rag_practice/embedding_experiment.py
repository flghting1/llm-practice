from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "BAAI/bge-small-zh-v1.5"
)

sentences = [
    "怎么保存代码版本？",
    "Git 提交会记录项目在某个时间点的修改。",
    "Python 虚拟环境可以隔离项目依赖。",
]

embeddings = model.encode(
    sentences,
    normalize_embeddings=True,
)

git_score = embeddings[0] @ embeddings[1]
python_score = embeddings[0] @ embeddings[2]

print("向量形状：", embeddings.shape)
print("问题与 Git 提交的相似度：", round(float(git_score), 4))
print("问题与 Python 虚拟环境的相似度：", round(float(python_score), 4))