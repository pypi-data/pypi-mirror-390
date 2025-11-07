# DICOM 工具 MCP 服务器

基于 MCP (Model Context Protocol) 的 DICOM 医学影像文件分析工具的 Python 实现。

## 功能特性

- 🔍 **DICOM 目录扫描**：快速扫描目录下的所有 DICOM 文件，提供统计摘要
- 📊 **序列映射**：生成患者-序列的详细映射关系
- 📝 **文件解析**：解析单个 DICOM 文件，提取完整元数据
- 📤 **数据导出**：支持 JSON 格式导出 DICOM 元数据
- 🏥 **批量分析**：智能分析 DICOM 目录并上传到 Orthanc 服务器

## 项目结构

```
.
├── main.py                 # MCP 服务器主文件
├── process.py              # DICOM 目录批量分析处理
├── config.json             # 配置文件（服务器地址、认证等）
├── requirements.txt        # Python 依赖包列表
├── dicom_tools/           # DICOM 工具模块
│   ├── scanner.py         # 目录扫描工具
│   ├── parser.py          # DICOM 文件解析器
│   ├── mapping.py         # 序列映射工具
│   ├── exporter.py        # JSON 导出工具
│   ├── types.py           # 类型定义
│   └── utils.py           # 工具函数
└── src/                   # 核心业务逻辑
    ├── api/               # API 接口层
    │   ├── dicom_api.py   # DICOM 文件上传 API
    │   ├── metadata_api.py # 元数据上传 API
    │   └── query_api.py   # 查询 API
    ├── core/              # 核心处理逻辑
    │   ├── series_processor.py # 序列处理器
    │   └── uploader.py    # 上传器
    ├── models/            # 数据模型
    │   └── dicom_models.py # DICOM 数据模型
    └── utils/             # 工具函数
        ├── config_loader.py # 配置加载器
        └── progress.py    # 进度条工具
```

## 安装

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装依赖

```bash
uv sync
```

## 配置

本工具支持两种配置方式，详细说明请查看 [配置指南](CONFIG_GUIDE.md)。

### 方式一:环境变量(推荐用于 MCP)

在 MCP 配置文件中设置环境变量:

```json
{
  "mcpServers": {
    "dicom-tools": {
      "command": "uvx",
      "args": ["dicom-tools-mcp"],
      "env": {
        "ORTHANC_BASE_URL": "http://your-server:8042",
        "ORTHANC_COOKIE": "your-cookie-value"
      }
    }
  }
}
```

### 方式二:配置文件(推荐用于开发)

创建 `config.json` 文件:

```json
{
  "orthanc_base_url": "http://your-orthanc:8042",
  "cookie": "your-authentication-cookie",
  "max_workers": 4,
  "max_retries": 3,
  "DEFAULT_CONNECT_TIMEOUT": 10,
  "DEFAULT_READ_TIMEOUT": 300,
  "DEFAULT_RETRY_DELAY": 2,
  "DEFAULT_BATCH_SIZE": 10
}
```

**配置优先级**: 环境变量 > 配置文件

## 使用方法

### 作为 MCP 服务器运行
跟更新config.json文件后运行
```bash
uv run main.py --base-url "http://192.168.4.17:29999" --orthanc-url "http://192.168.4.17:18997" --cookie "LoMSnZMGUXfQETiBHu-gUVeHlWBiSOifDVNYwcjqCwqiBSk2nnVAJuf4LM6Q48uj"
```
### 在vscodecline运行
```bash
{
  "mcpServers": {
    "dicom-tools-python": {
      "autoApprove": [
        "scan-dicom-directory",
        "get-dicom-series-mapping",
        "get-dicom-file-mapping",
        "export-dicom-json",
        "parse-dicom-file"
      ],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "main.py",
        "--base-url",
        "http://192.168.4.220:26666",
        "--orthanc-url",
        "http://192.168.4.220:18997",
        "--cookie",
        "ls=6ebM3MNdxq1kH0SnFa14UqkS9aEaYuIh6nPW2POoLCsuFDFm_s6qyCvDuexEI0K3"
      ],
      "cwd": "C:/Users/13167/Desktop/agent-mcp/src"
    }
  }
}
```
服务器将通过标准输入/输出 (stdio) 与 MCP 客户端通信。

### 可用的工具

#### 1. scan-dicom-directory
扫描指定目录下的所有 DICOM 文件，返回统计摘要。

**参数：**
- `directory_path` (string): 要扫描的目录路径

**示例：**
```json
{
  "directory_path": "/path/to/dicom/folder"
}
```

#### 2. get-dicom-series-mapping
生成患者-序列的详细映射关系，包含每个序列的文件列表。

**参数：**
- `directory_path` (string): 要扫描的目录路径

#### 3. get-dicom-file-mapping
生成优化的文件路径映射。

**参数：**
- `directory_path` (string): 要扫描的目录路径

#### 4. parse-dicom-file
解析单个 DICOM 文件，提取完整元数据。

**参数：**
- `file_path` (string): DICOM 文件路径

#### 5. export-dicom-json
将 DICOM 文件导出为 JSON 格式。

**参数：**
- `file_path` (string): DICOM 文件路径

#### 6. analysis-dicom-directory
批量分析 DICOM 目录并上传到服务器。

**参数：**
- `directory_path` (string): 要分析的目录路径
- `series_type` (string): 序列类型筛选（可选）

## 主要依赖

- **mcp**: Model Context Protocol 服务器框架
- **pydicom**: DICOM 文件读取和解析
- **requests**: HTTP 请求处理
- **pydantic**: 数据验证和模型定义
- **tqdm**: 进度条显示

## 开发

### 添加新工具

1. 在 `dicom_tools/` 目录下创建新的工具模块
2. 在 `main.py` 中注册新工具
3. 实现工具的处理逻辑

### 测试

确保您的 DICOM 文件目录结构正确，然后运行服务器进行测试。

## 注意事项

- 确保有足够的磁盘空间和内存来处理大型 DICOM 数据集
- 配置文件中的 cookie 需要定期更新以保持认证有效
- 建议在处理大量文件时调整 `max_workers` 参数以优化性能

## 许可证

本项目遵循相应的开源许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issue 联系我们。
