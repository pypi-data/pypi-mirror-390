# PyPI 上传指南

您的包已经成功构建!构建文件位于 `dist/` 目录中:
- `dicom_tools_mcp-0.1.0.tar.gz` (源代码分发)
- `dicom_tools_mcp-0.1.0-py3-none-any.whl` (wheel 包)

## 上传步骤

### 1. 注册 PyPI 账号

如果您还没有 PyPI 账号:
- 正式环境: https://pypi.org/account/register/
- 测试环境 (推荐先测试): https://test.pypi.org/account/register/

### 2. 创建 API Token

登录后,在账户设置中创建 API token:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

**重要**: 复制并保存 token,它只会显示一次!

### 3. 上传到 TestPyPI (推荐先测试)

```powershell
# 上传到测试环境
python -m twine upload --repository testpypi dist/*
```

输入用户名: `__token__`
输入密码: 粘贴您的 API token (包含 `pypi-` 前缀)

### 4. 验证测试包

```powershell
# 从 TestPyPI 安装并测试
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dicom-tools-mcp
```

### 5. 上传到正式 PyPI

确认测试无误后:

```powershell
# 上传到正式 PyPI
python -m twine upload dist/*
```

输入用户名: `__token__`
输入密码: 粘贴您的正式 PyPI API token

### 6. 验证上传成功

访问: https://pypi.org/project/dicom-tools-mcp/

## 配置 ~/.pypirc (可选,避免每次输入密码)

在用户主目录创建 `.pypirc` 文件:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-你的正式PyPI_token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-你的测试PyPI_token
```

**注意**: 确保 `.pypirc` 文件权限设置为仅您可读!

## 更新版本发布新版本

1. 修改 `pyproject.toml` 中的版本号
2. 删除 `dist/` 目录
3. 重新构建: `python -m build`
4. 上传新版本: `python -m twine upload dist/*`

## 重要提醒

在上传前,请确保:
- [ ] 更新 `pyproject.toml` 中的作者信息和邮箱
- [ ] 更新 `pyproject.toml` 中的项目 URL (GitHub 仓库地址)
- [ ] 完善 `README.md` 文档
- [ ] 测试包的安装和基本功能

## 常见问题

### 包名已被使用
如果包名 `dicom-tools-mcp` 已被使用,需要修改 `pyproject.toml` 中的 `name` 字段。

### 上传失败
- 检查 token 是否正确复制
- 确保 token 有上传权限
- 包名是否符合 PyPI 命名规范

### 删除已上传的版本
PyPI 不允许删除已上传的版本,只能标记为删除。请谨慎上传!
