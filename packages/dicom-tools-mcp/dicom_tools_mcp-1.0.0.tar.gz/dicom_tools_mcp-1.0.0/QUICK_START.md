# DICOM MCP 工具 - Cline 配置指南

## 🚀 推荐配置（使用 uvx）

将以下配置复制到你的 Cline MCP 设置文件中：

**配置文件路径：**
```
C:\Users\13167\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

**配置内容：**
```json
{
  "mcpServers": {
    "dicom-tools": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "dicom-tools-mcp"
      ],
      "env": {}
    }
  }
}
```

## 📝 使用步骤

### 1. 确保包已上传到 PyPI
如果还没上传，运行：
```bash
python -m twine upload dist/*
```

### 2. 编辑 Cline 配置文件
- 打开上面的配置文件路径
- 如果文件不存在，创建它
- 粘贴上面的 JSON 配置

### 3. 重启 VS Code
完全关闭并重新打开 VS Code

### 4. 测试
在 Cline 中输入：
```
请扫描 D:\DICOM 目录下的 DICOM 文件
```

## 🔧 配置说明

- **`type: "stdio"`** - 使用标准输入输出通信
- **`command: "uvx"`** - 使用 uvx 运行包（自动下载和运行）
- **`args`** - 包名称 `dicom-tools-mcp`
- **`env`** - 环境变量（可选）

## 💡 优势

使用 `uvx` 的好处：
- ✅ 无需手动安装包
- ✅ 自动管理依赖
- ✅ 始终使用最新版本
- ✅ 隔离的运行环境

## 🔍 验证

1. 打开 VS Code 开发者工具：`Help` > `Toggle Developer Tools`
2. 查看控制台，应该看到 MCP 服务器连接成功
3. 在 Cline 中可以看到可用的 DICOM 工具

## ⚠️ 注意事项

如果你的包上传到 TestPyPI 而不是 PyPI，需要使用：
```json
{
  "mcpServers": {
    "dicom-tools": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--index-url",
        "https://test.pypi.org/simple/",
        "--extra-index-url",
        "https://pypi.org/simple/",
        "dicom-tools-mcp"
      ],
      "env": {}
    }
  }
}
```
