# MCP 配置示例

## Claude Desktop 配置

在 Claude Desktop 的配置文件中添加以下内容:

**文件位置**: 
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dicom-tools": {
      "command": "uvx",
      "args": ["dicom-tools-mcp"],
      "env": {
        "BASE_URL": "http://192.168.4.220:26666",
        "ORTHANC_BASE_URL": "http://192.168.4.220:18997",
        "ORTHANC_COOKIE": "your-cookie-value-here"
      }
    }
  }
}
```

## VS Code Cline 配置

在 Cline 的 MCP 设置中添加:

**文件位置**: VS Code 设置 -> Cline -> MCP Settings

```json
{
  "mcpServers": {
    "dicom-tools": {
      "command": "uvx",
      "args": ["dicom-tools-mcp"],
      "env": {
        "BASE_URL": "http://192.168.4.220:26666",
        "ORTHANC_BASE_URL": "http://192.168.4.220:18997",
        "ORTHANC_COOKIE": "your-cookie-value-here"
      }
    }
  }
}
```

## 配置说明

### 必需的环境变量

- **BASE_URL**: 分析服务器地址
  - 示例: `http://192.168.4.220:26666`
  - 用途: 上传分析数据和获取分析结果
  
- **ORTHANC_BASE_URL**: Orthanc 服务器地址
  - 示例: `http://192.168.4.220:18997`
  - 用途: 存储 DICOM 文件
  
- **ORTHANC_COOKIE**: 认证 Cookie
  - 获取方式: 浏览器开发者工具 -> Network -> 查看请求头中的 Cookie
  - 示例: `ls=6ebM3MNdxq1kH0SnFa14UqkS9aEaYuIh6nPW2POoLCsuFDFm_s6qyCvDuexEI0K3`

### 可选的环境变量(有默认值)

```json
{
  "env": {
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
```

## 安装和更新

### 首次安装

不需要手动安装,`uvx` 会自动下载和安装包。

### 更新到最新版本

如果已经安装了旧版本,需要清除 uv 缓存:

```bash
# Windows PowerShell
uv cache clean
uvx --refresh dicom-tools-mcp

# 或者直接清除特定包
uv cache clean dicom-tools-mcp
```

### 验证安装

配置完成后,重启 Claude Desktop 或 VS Code,然后在对话中可以使用以下工具:

- `Analysis_dicom_directory`: 分析 DICOM 目录并上传
- `scan_dicom_directory`: 扫描 DICOM 目录
- `get_dicom_series_mapping`: 获取序列映射
- `parse_dicom_file`: 解析单个 DICOM 文件
- `export_dicom_json`: 导出为 JSON

## 故障排查

### 问题: Configuration not found

**解决方案**: 确保在 MCP 配置中设置了 `ORTHANC_BASE_URL` 和 `ORTHANC_COOKIE` 环境变量。

### 问题: 旧版本仍在使用

**解决方案**: 
```bash
uv cache clean dicom-tools-mcp
uvx --refresh dicom-tools-mcp
```

然后重启客户端(Claude Desktop 或 VS Code)。

### 问题: 连接 Orthanc 失败

**解决方案**: 
1. 检查 `ORTHANC_BASE_URL` 是否正确
2. 检查 `ORTHANC_COOKIE` 是否有效(Cookie 可能会过期)
3. 确保网络可以访问 Orthanc 服务器

## 示例对话

配置完成后,你可以这样使用:

```
你: 帮我分析这个目录的 DICOM 文件并上传到 Orthanc: D:\DICOM\patient001

Claude: [使用 Analysis_dicom_directory 工具分析和上传]

你: 扫描一下这个目录看有多少 DICOM 文件: E:\Medical\Images

Claude: [使用 scan_dicom_directory 工具扫描]
```
