# 在 VS Code Cline 中配置 DICOM MCP 工具

## 第一步：从 PyPI 安装包

在命令行中运行：

```bash
pip install dicom-tools-mcp
```

或者使用 uv（推荐）：

```bash
uv pip install dicom-tools-mcp
```

## 第二步：配置 Cline MCP 设置

在 VS Code 中，你需要编辑 Cline 的 MCP 配置文件。

### Windows 配置文件位置：
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

或者：

```
C:\Users\<你的用户名>\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

### 配置内容：

在配置文件中添加以下内容（**推荐使用 uvx**）：

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

**或者使用本地 Python（开发模式）：**

```json
{
  "mcpServers": {
    "dicom-tools": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "main"
      ],
      "cwd": "C:\\Users\\13167\\Desktop\\agent-mcp\\src - 副本",
      "env": {}
    }
  }
}
```

## 第三步：重启 VS Code

关闭并重新打开 VS Code，让配置生效。

## 第四步：在 Cline 中使用

重启后，在 Cline 对话中，你可以：

1. 查看可用的工具：
   - Cline 会自动连接到 MCP 服务器
   - 可以看到所有注册的 DICOM 工具

2. 使用工具示例：
   ```
   请扫描 D:\DICOM\patient_data 目录下的 DICOM 文件
   ```

   ```
   解析这个 DICOM 文件：D:\DICOM\sample.dcm
   ```

   ```
   生成 D:\DICOM\patient_data 的序列映射
   ```

## 配置选项说明

### 方案 1：使用 uvx（**最推荐**）

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

### 方案 2：使用本地项目（开发模式）

```json
{
  "mcpServers": {
    "dicom-tools": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "main"],
      "cwd": "C:\\Users\\13167\\Desktop\\agent-mcp\\src - 副本"
    }
  }
}
```

### 方案 3：使用已安装的包

首先确保包已安装：
```bash
pip install dicom-tools-mcp
```

然后配置：

```json
{
  "mcpServers": {
    "dicom-tools": {
      "type": "stdio",
      "command": "dicom-mcp"
    }
  }
}
```

## 验证配置

1. 打开 VS Code 的开发者工具：`Help` > `Toggle Developer Tools`
2. 查看控制台是否有 MCP 服务器连接成功的消息
3. 在 Cline 中尝试提问，看是否能调用工具

## 常见问题

### 问题 1：找不到模块

**解决方案**：确保 Python 环境正确，并且包已安装：
```bash
pip show dicom-tools-mcp
```

### 问题 2：MCP 服务器无法启动

**解决方案**：检查 `main.py` 中是否有 `main()` 函数：

```python
def main():
    """MCP 服务器入口点"""
    import asyncio
    asyncio.run(stdio_server()(server.run))

if __name__ == "__main__":
    main()
```

### 问题 3：权限问题

**解决方案**：确保配置文件路径可访问，使用管理员权限运行 VS Code。

## 环境变量配置（可选）

如果需要配置 Orthanc 服务器等，可以在 `env` 中添加：

```json
{
  "mcpServers": {
    "dicom-tools": {
      "type": "stdio",
      "command": "uvx",
      "args": ["dicom-tools-mcp"],
      "env": {
        "ORTHANC_URL": "http://localhost:8042",
        "ORTHANC_USERNAME": "admin",
        "ORTHANC_PASSWORD": "password"
      }
    }
  }
}
```
