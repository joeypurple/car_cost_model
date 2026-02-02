# 油电车成本比较模型

这是一个基于 Python 的成本模型，用来比较油车与电车的现金流和 NPV。项目包含 `cost_model.py`（计算逻辑）和 `app.py`（Streamlit 前端）。

快速开始（本地运行）

1. 创建并激活虚拟环境（可选）：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行 Streamlit 应用：

```bash
streamlit run app.py
```

部署到 Streamlit Community Cloud

1. 将仓库推到 GitHub。
2. 在 https://share.streamlit.io/ 登录并选择你的仓库，部署分支即可。Streamlit 会自动使用 `requirements.txt` 安装依赖。

部署到 Hugging Face Spaces（Streamlit）

1. 在 Hugging Face 上创建一个新的 Space，选择 `Streamlit` 模板。
2. 将此仓库代码 push 到该 Space（或直接在 Web UI 上传文件）。
3. HF Spaces 会自动安装 `requirements.txt` 并运行 `streamlit run app.py`。

注意事项

- 如果要通过微信小程序或其他前端调用后端接口，建议将计算逻辑提取为 API（例如使用 FastAPI），并让前端调用 REST 接口获取表格与图像。
- `cost_model.py` 中包含默认参数字典 `inputs`，`app.py` 会更新该字典并调用 `calc_cashflow`。
