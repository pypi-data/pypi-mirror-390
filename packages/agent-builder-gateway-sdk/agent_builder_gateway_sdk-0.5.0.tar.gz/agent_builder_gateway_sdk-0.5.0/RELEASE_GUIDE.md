# 发布指南

## 发布到 PyPI

### 前置条件

1. **配置 PyPI API Token**

   在 GitHub 仓库设置中添加 Secret：
   - 进入仓库 Settings -> Secrets and variables -> Actions
   - 点击 "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: 你的 PyPI API Token（从 https://pypi.org/manage/account/token/ 获取）

2. **获取 PyPI API Token**

   - 访问 https://pypi.org/manage/account/token/
   - 点击 "Add API token"
   - Token name: `agent-builder-gateway-sdk-github-actions`
   - Scope: "Entire account" 或仅限此项目
   - 复制生成的 token（格式：`pypi-...`）

### 发布流程

1. **更新版本号**

   编辑 `pyproject.toml`：
   ```toml
   [project]
   version = "0.1.0"  # 修改为新版本号
   ```

2. **提交代码**

   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.0"
   git push
   ```

3. **创建并推送 Tag**

   ```bash
   # 创建 tag
   git tag v0.1.0
   
   # 推送 tag
   git push origin v0.1.0
   ```

4. **自动发布**

   推送 tag 后，GitHub Actions 会自动：
   - 运行测试
   - 构建包
   - 发布到 PyPI
   - 创建 GitHub Release

5. **验证发布**

   - 检查 GitHub Actions 是否成功
   - 访问 https://pypi.org/project/agent-builder-gateway-sdk/
   - 测试安装：
     ```bash
     pip install agent-builder-gateway-sdk
     ```

## 版本号规范

遵循语义化版本（Semantic Versioning）：

- **MAJOR.MINOR.PATCH** (例如：1.2.3)
  - **MAJOR**: 不兼容的 API 变更
  - **MINOR**: 向后兼容的功能新增
  - **PATCH**: 向后兼容的问题修复

示例：
- `0.1.0` - 初始版本
- `0.1.1` - Bug 修复
- `0.2.0` - 新功能
- `1.0.0` - 第一个稳定版本

## 发布检查清单

发布前确保：

- [ ] 所有测试通过
- [ ] 更新了 `pyproject.toml` 中的版本号
- [ ] 更新了 `README.md`（如果需要）
- [ ] 代码格式化和 linting 通过
- [ ] 文档是最新的
- [ ] 示例代码可以运行
- [ ] Changelog 已更新（如果有）

## 本地测试构建

在发布前本地测试：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 构建包
uv build

# 检查 dist/ 目录
ls -lh dist/

# 本地安装测试
pip install dist/*.whl

# 测试导入
python -c "from gateway_sdk import GatewayClient; print('OK')"
```

## 回滚发布

如果发布出现问题：

1. **删除 PyPI 版本**（不推荐，PyPI 通常不允许）
   - PyPI 不允许删除已发布的版本
   - 只能发布新版本修复问题

2. **发布修复版本**
   ```bash
   # 修改版本号为补丁版本
   # 0.1.0 -> 0.1.1
   
   git tag v0.1.1
   git push origin v0.1.1
   ```

3. **在 GitHub Release 中标记为不稳定**
   - 编辑 GitHub Release
   - 勾选 "This is a pre-release"

## CI/CD 配置说明

### GitHub Actions Workflows

1. **`.github/workflows/test.yml`** - 测试工作流
   - 触发：Push 到 main 分支、Pull Request
   - 运行：Linters、类型检查、单元测试

2. **`.github/workflows/publish.yml`** - 发布工作流
   - 触发：Push tag（v*）
   - 运行：构建、发布到 PyPI、创建 GitHub Release

### 环境变量和 Secrets

需要配置的 Secrets：
- `PYPI_API_TOKEN` - PyPI API Token（必需）
- `GITHUB_TOKEN` - 自动提供（用于创建 Release）

## 常见问题

### Q: 如何测试 PyPI 发布？

A: 使用 TestPyPI：

1. 获取 TestPyPI token: https://test.pypi.org/manage/account/token/
2. 在 GitHub 添加 `TEST_PYPI_API_TOKEN` Secret
3. 修改 `.github/workflows/publish.yml`：
   ```yaml
   - name: Publish to TestPyPI
     run: |
       uv run twine upload --repository testpypi dist/*
   ```

### Q: 发布失败怎么办？

A: 检查以下几点：
1. PyPI API Token 是否正确配置
2. 版本号是否已存在（PyPI 不允许重复）
3. 包名是否可用
4. GitHub Actions 日志中的错误信息

### Q: 如何发布 Pre-release 版本？

A: 使用版本号后缀：
```toml
version = "0.1.0rc1"  # Release Candidate
version = "0.1.0a1"   # Alpha
version = "0.1.0b1"   # Beta
```

```bash
git tag v0.1.0rc1
git push origin v0.1.0rc1
```

## 更多信息

- [PyPI 官方文档](https://packaging.python.org/)
- [语义化版本规范](https://semver.org/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

