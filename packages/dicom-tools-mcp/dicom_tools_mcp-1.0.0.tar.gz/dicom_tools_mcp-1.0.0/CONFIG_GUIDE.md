# 配置指南

## 两种配置方式

### 方式一:环境变量(推荐用于 MCP)

在你的 MCP 配置文件中设置环境变量:

```json
{
  "mcpServers": {
    "dicom-tools": {
      "command": "uvx",
      "args": ["dicom-tools-mcp"],
      "env": {
        "BASE_URL": "http://192.168.4.220:26666",
        "ORTHANC_BASE_URL": "http://192.168.4.220:18997",
        "ORTHANC_COOKIE": "your-cookie-value",
        "MAX_WORKERS": "4",
        "MAX_RETRIES": "3",
        "DEFAULT_CONNECT_TIMEOUT": "10",
        "DEFAULT_READ_TIMEOUT": "300",
        "DEFAULT_RETRY_DELAY": "2",
        "DEFAULT_BATCH_SIZE": "10"
      }
    }
  }
}
```

**必需的环境变量:**
- `BASE_URL`: 分析服务器地址 (例如: http://192.168.4.220:26666)
- `ORTHANC_BASE_URL`: Orthanc 服务器地址 (例如: http://192.168.4.220:18997)
- `ORTHANC_COOKIE`: 认证 Cookie

**可选的环境变量(有默认值):**
- `MAX_WORKERS`: 最大并发工作线程数(默认: 4)
- `MAX_RETRIES`: 重试次数(默认: 3)
- `DEFAULT_CONNECT_TIMEOUT`: 连接超时秒数(默认: 10)
- `DEFAULT_READ_TIMEOUT`: 读取超时秒数(默认: 300)
- `DEFAULT_RETRY_DELAY`: 重试延迟秒数(默认: 2)
- `DEFAULT_BATCH_SIZE`: 批处理大小(默认: 10)

### 方式二:配置文件(推荐用于开发)

在**当前工作目录**或**项目根目录**创建 `config.json`:

```json
{
    "base_url": "http://192.168.4.220:26666",
    "orthanc_base_url": "http://192.168.4.220:18997",
    "cookie": "your-cookie-value",
    "max_workers": 4,
    "max_retries": 3,
    "DEFAULT_CONNECT_TIMEOUT": 10,
    "DEFAULT_READ_TIMEOUT": 300,
    "DEFAULT_RETRY_DELAY": 2,
    "DEFAULT_BATCH_SIZE": 10
}
```

## 配置优先级

1. **环境变量**(最高优先级)
2. **config.json 文件**(当前目录)
3. **config.json 文件**(开发环境项目根目录)

## 使用建议

- **MCP 部署**: 使用环境变量(方式一),配置在 MCP 配置文件的 `env` 字段中
- **本地开发**: 使用 config.json 文件(方式二),放在项目根目录
- **测试**: 使用环境变量,可以轻松切换不同的测试环境

## 故障排查

如果遇到 "Configuration not found" 错误:

1. 检查是否设置了所有必需的环境变量:
   - `BASE_URL`
   - `ORTHANC_BASE_URL`
   - `ORTHANC_COOKIE`
2. 检查当前工作目录是否有 `config.json` 文件
3. 确保配置文件的 JSON 格式正确
4. 查看错误信息中列出的搜索路径

如果显示上传成功但实际没有上传:

1. 检查 `BASE_URL` 是否正确设置(这是分析服务器地址,不是 Orthanc 地址)
2. 检查网络是否可以访问两个服务器地址
