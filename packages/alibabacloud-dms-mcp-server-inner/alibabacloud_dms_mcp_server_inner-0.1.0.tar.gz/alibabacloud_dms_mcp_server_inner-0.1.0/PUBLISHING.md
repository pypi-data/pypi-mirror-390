# 发布指南

本指南说明如何将 `alibabacloud-dms-mcp-server-inner` 发布，以便其他人可以通过 `uvx` 使用。

## 方式一：发布到 PyPI（推荐）

发布到 PyPI 后，任何人都可以通过 `uvx alibabacloud-dms-mcp-server-inner@版本号` 使用。

### 前置准备

1. **注册 PyPI 账号**
   - 访问 https://pypi.org/account/register/ 注册账号
   - 如果已有账号，直接登录

2. **安装构建工具**
   ```bash
   # 使用 uv（推荐）
   uv pip install build twine
   
   # 或使用 pip
   pip install build twine
   ```

3. **配置 PyPI 认证**
   
   创建 `~/.pypirc` 文件（Linux/Mac）或 `%USERPROFILE%\.pypirc`（Windows）：
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi
   
   [pypi]
   username = __token__
   password = pypi-你的API令牌
   
   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-你的测试API令牌
   ```
   
   或者使用环境变量：
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-你的API令牌
   ```

### 发布步骤

1. **更新版本号**
   
   在 `pyproject.toml` 中更新版本号：
   ```toml
   version = "0.1.0"  # 改为新版本，如 "0.1.1"
   ```

2. **构建包**
   ```bash
   # 清理之前的构建文件
   rm -rf dist/ build/ *.egg-info
   
   # 构建分发包
   python -m build
   # 或使用 uv
   uv build
   ```

3. **检查构建结果**
   ```bash
   # 检查构建的文件
   ls -la dist/
   
   # 验证包内容（可选）
   twine check dist/*
   ```

4. **测试发布（可选，推荐）**
   
   先发布到 TestPyPI 测试：
   ```bash
   twine upload --repository testpypi dist/*
   ```
   
   测试安装：
   ```bash
   uvx --index-url https://test.pypi.org/simple/ alibabacloud-dms-mcp-server-inner@0.1.0
   ```

5. **发布到 PyPI**
   ```bash
   twine upload dist/*
   ```

6. **验证发布**
   
   等待几分钟后，访问 https://pypi.org/project/alibabacloud-dms-mcp-server-inner/ 查看
   
   测试安装：
   ```bash
   uvx alibabacloud-dms-mcp-server-inner@0.1.0
   ```

### 使用方式（发布后）

其他人可以通过以下方式使用：

```json
{
  "mcpServers": {
    "dms-mcp-server": {
      "command": "uvx",
      "args": ["alibabacloud-dms-mcp-server-inner@0.1.0"],
      "env": {
        "ACCESS_KEY_ID": "your_access_key_id",
        "ACCESS_KEY_SECRET": "your_access_key_secret",
        "CONNECTION_STRING": "dbName@host:port"
      }
    }
  }
}
```

## 方式二：从 Git 仓库直接使用（无需发布）

如果不想发布到 PyPI，可以直接从 Git 仓库使用。

### 使用方式

其他人可以通过以下配置使用：

```json
{
  "mcpServers": {
    "dms-mcp-server": {
      "command": "uvx",
      "args": [
        "@git+https://gitlab.alibaba-inc.com/idb/alibabacloud-dms-mcp-server-inner.git"
      ],
      "env": {
        "ACCESS_KEY_ID": "your_access_key_id",
        "ACCESS_KEY_SECRET": "your_access_key_secret",
        "CONNECTION_STRING": "dbName@host:port"
      }
    }
  }
}
```

### 指定版本/分支/标签

```json
{
  "mcpServers": {
    "dms-mcp-server": {
      "command": "uvx",
      "args": [
        "@git+https://gitlab.alibaba-inc.com/idb/alibabacloud-dms-mcp-server-inner.git@v0.1.0"
      ],
      "env": {
        "ACCESS_KEY_ID": "your_access_key_id",
        "ACCESS_KEY_SECRET": "your_access_key_secret"
      }
    }
  }
}
```

### 使用特定分支

```json
{
  "mcpServers": {
    "dms-mcp-server": {
      "command": "uvx",
      "args": [
        "@git+https://gitlab.alibaba-inc.com/idb/alibabacloud-dms-mcp-server-inner.git@main"
      ],
      "env": {
        "ACCESS_KEY_ID": "your_access_key_id",
        "ACCESS_KEY_SECRET": "your_access_key_secret"
      }
    }
  }
}
```

## 方式三：发布到私有包索引

如果这是内部项目，可以发布到私有 PyPI 索引。

### 配置私有索引

在 `pyproject.toml` 中添加：

```toml
[[tool.uv.index]]
name = "private"
url = "https://your-private-pypi.com/simple"
```

### 使用方式

```json
{
  "mcpServers": {
    "dms-mcp-server": {
      "command": "uvx",
      "args": [
        "--index-url", "https://your-private-pypi.com/simple",
        "alibabacloud-dms-mcp-server-inner@0.1.0"
      ],
      "env": {
        "ACCESS_KEY_ID": "your_access_key_id",
        "ACCESS_KEY_SECRET": "your_access_key_secret"
      }
    }
  }
}
```

## 版本管理建议

1. **使用语义化版本**（Semantic Versioning）
   - 主版本号.次版本号.修订号（如 1.0.0）
   - 主版本号：不兼容的 API 修改
   - 次版本号：向下兼容的功能性新增
   - 修订号：向下兼容的问题修正

2. **创建 Git 标签**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **更新 CHANGELOG**
   建议创建 `CHANGELOG.md` 记录版本变更。

## 快速发布（使用脚本）

项目提供了发布脚本，可以简化发布流程：

```bash
# 运行发布脚本
./scripts/publish.sh
```

脚本会自动：
1. 检查环境
2. 清理旧文件
3. 构建包
4. 验证包
5. 发布到 PyPI 或 TestPyPI

## 常见问题

### Q: 发布后多久可以在 PyPI 上看到？
A: 通常几分钟内就可以看到，最多可能需要 15-30 分钟。

### Q: 如何更新已发布的版本？
A: 只需更新版本号，重新构建和发布即可。不能覆盖已发布的版本。

### Q: 可以删除已发布的版本吗？
A: PyPI 不允许删除已发布的版本，只能标记为隐藏。

### Q: 如何测试本地构建的包？
A: 可以使用 `pip install dist/alibabacloud_dms_mcp_server_inner-0.1.0-py3-none-any.whl` 安装本地构建的包进行测试。

## 自动化发布（可选）

可以使用 GitHub Actions 或 GitLab CI/CD 自动化发布流程。示例：

```yaml
# .gitlab-ci.yml
stages:
  - build
  - publish

build:
  stage: build
  script:
    - uv build
  artifacts:
    paths:
      - dist/

publish:
  stage: publish
  script:
    - uv pip install twine
    - twine upload dist/*
  only:
    - tags
```

