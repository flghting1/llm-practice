# Python Engineering Pratice

一个最小的资料处理流程:

```text
Markdown → 读取 → 按标题切分 → 保存 JSON → 检索相关段落 → 拼接 Prompt
```

## 文件说明

- `sample_notes.md`: 实例资料
- `read_markdown.py`: 读取 Markdown
- `split_markdown.py`: 按二级标题切分
- `export_sections.py`: 保存为 JSON
- `sections.josn`: 结构化资料
- `model_client.py`: 封装模型调用
- `answer_question.py`: 检索资料并拼接 Prompt
- `test_pipeline.py`: 自动化测试

## 运行资料处理

```powershell
python export_sections.py
```

## 运行问答流程

```powershell
python anser_question.py
```

## 运行测试

```powershell
python -m unittest -v
```

## 当前限制

- 模型调用当前是模拟实现。
- 检索目前只根据标题关键词匹配。
- 暂不支持 PDF、网页和向量检索。