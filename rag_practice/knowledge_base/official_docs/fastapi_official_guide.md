# FastAPI 官方文档要点

资料来源：https://fastapi.tiangolo.com/

FastAPI 是一个用于构建 Python Web API 的框架，基于 Python 类型提示提供数据校验、接口文档和编辑器支持。

## 路由

可以使用装饰器声明请求方法和路径，例如 `@app.get()` 和 `@app.post()`。路由函数接收请求参数并返回可以被序列化为 JSON 的数据。

## 请求模型

FastAPI 通常使用 Pydantic 模型描述请求体。字段类型、长度和默认值可以形成自动校验规则。输入不符合模型规则时，框架会返回结构化错误响应。

## 响应模型

响应模型可以限制接口返回字段并生成 OpenAPI Schema，避免意外暴露内部数据。

## 自动接口文档

FastAPI 根据路由、请求模型和响应模型自动生成 OpenAPI 文档。默认 Swagger UI 地址是 `/docs`，ReDoc 地址是 `/redoc`。

## 异常处理

可使用 `HTTPException` 返回明确的 HTTP 状态码和错误信息。生产环境不应该向用户暴露完整 Python 堆栈或敏感配置。

## 部署

开发阶段可以使用 Uvicorn 启动服务。容器部署时需要监听 `0.0.0.0`，并通过端口映射将容器端口暴露给宿主机。