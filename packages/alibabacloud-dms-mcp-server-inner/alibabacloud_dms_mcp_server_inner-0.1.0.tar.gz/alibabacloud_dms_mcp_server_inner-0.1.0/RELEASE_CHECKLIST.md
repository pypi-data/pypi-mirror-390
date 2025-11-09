# 发布前检查清单

在发布新版本之前，请确保完成以下检查：

## ✅ 代码检查

- [ ] 所有代码已通过测试
- [ ] 没有语法错误或 lint 错误
- [ ] 代码已提交到 Git 仓库

## ✅ 版本和元数据

- [ ] 在 `pyproject.toml` 中更新了版本号
- [ ] 版本号遵循语义化版本规范（如 0.1.0 → 0.1.1）
- [ ] 更新了 `README.md`（如有必要）
- [ ] 更新了 `CHANGELOG.md`（如有）

## ✅ 依赖检查

- [ ] 所有依赖项已在 `pyproject.toml` 中正确声明
- [ ] 依赖版本号合理（避免过于严格的版本限制）
- [ ] 测试了依赖项的安装

## ✅ 功能测试

- [ ] 本地测试通过：`uv run server.py` 或 `python -m alibabacloud_dms_mcp_server_inner.server`
- [ ] 环境变量 `ACCESS_KEY_ID` 和 `ACCESS_KEY_SECRET` 正常工作
- [ ] `CONNECTION_STRING` 配置正常工作（如适用）

## ✅ 构建测试

- [ ] 成功构建包：`uv build`
- [ ] 构建产物在 `dist/` 目录中
- [ ] 使用 `twine check dist/*` 验证包格式

## ✅ 安装测试

- [ ] 从本地构建的包安装测试：
  ```bash
  uv pip install dist/alibabacloud_dms_mcp_server_inner-*.whl
  ```
- [ ] 安装后可以正常运行：`dms-mcp-server` 或 `alibabacloud-dms-mcp-server-inner`

## ✅ PyPI 准备

- [ ] 已注册 PyPI 账号
- [ ] 已配置 PyPI API token（用于 twine）
- [ ] 已测试 TestPyPI 发布（推荐）

## ✅ Git 标签

- [ ] 创建了 Git 标签：`git tag v0.1.0`
- [ ] 推送了标签到远程：`git push origin v0.1.0`

## ✅ 文档

- [ ] README.md 中的使用说明是最新的
- [ ] 示例配置正确
- [ ] 环境变量说明清晰

## 发布步骤

完成所有检查后，按以下步骤发布：

1. **更新版本号**
   ```bash
   # 编辑 pyproject.toml，更新 version
   ```

2. **构建包**
   ```bash
   uv build
   ```

3. **验证包**
   ```bash
   twine check dist/*
   ```

4. **测试发布（推荐）**
   ```bash
   twine upload --repository testpypi dist/*
   ```

5. **正式发布**
   ```bash
   twine upload dist/*
   ```

6. **创建 Git 标签**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

7. **验证发布**
   - 访问 https://pypi.org/project/alibabacloud-dms-mcp-server-inner/
   - 测试安装：`uvx alibabacloud-dms-mcp-server-inner@0.1.0`

## 发布后

- [ ] 更新项目文档（如有必要）
- [ ] 通知团队成员新版本发布
- [ ] 记录发布日志


