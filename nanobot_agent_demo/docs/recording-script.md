# 演示录制脚本

1. 运行 `docker compose up --build`，浏览器打开 `http://localhost:5173`。
2. 选择“库存预警”，保留默认问题，点击“运行工作流”。
3. 展示 Router 到 Finalizer 的执行轨迹、库存结果、来源和“本地模拟数据”边界。
4. 切换到“确定性”模式再次运行，说明没有 API Key 也可复现测试和演示。
5. 结束画面显示 `python -m unittest discover -s tests -v` 与项目 README。

不要在录屏中显示 `.env` 文件、API Key、真实店铺信息或未验证的外部模型结果。
