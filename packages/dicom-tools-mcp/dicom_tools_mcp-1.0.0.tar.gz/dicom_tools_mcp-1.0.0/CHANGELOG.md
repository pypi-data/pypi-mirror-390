# 更新日志

## [0.1.9] - 2025-11-06

### 修复
- **修复 Windows 编码问题**: 解决了 `UnicodeEncodeError: 'gbk' codec can't encode character` 错误
  - 在 `main.py` 中设置标准输出/错误流为 UTF-8 编码
  - 移除了所有特殊 Unicode 字符(✓, ✗, ⚠, ⏳)替换为纯文本标记
  - 改进了 Windows 系统兼容性

### 改进
- 进度条描述使用纯文本: `[完成]`, `[失败]`, `[警告]`, `[错误]`, `[处理中]`
- 更好的跨平台支持

## [0.1.8] - 2025-11-06

### 修复
- 移除 `main.py` 中不再需要的 `update_config` 函数和命令行参数
- 简化启动流程,完全使用环境变量配置

### 改进
- 清理了不必要的导入 (`argparse`, `Path`)
- 代码更加简洁明了

## [0.1.7] - 2025-11-06

### 重大改进
- **环境变量配置优先**: 现在优先使用环境变量进行配置(推荐用于 MCP 部署)
- **修复配置文件查找问题**: 解决了打包后找不到 `config.json` 的问题

### 新增
- 支持通过环境变量配置所有参数:
  - `ORTHANC_BASE_URL`: Orthanc 服务器地址(必需)
  - `ORTHANC_COOKIE`: 认证 Cookie(必需)
  - `MAX_WORKERS`: 最大工作线程数(可选,默认 4)
  - `MAX_RETRIES`: 重试次数(可选,默认 3)
  - `DEFAULT_CONNECT_TIMEOUT`: 连接超时(可选,默认 10)
  - `DEFAULT_READ_TIMEOUT`: 读取超时(可选,默认 300)
  - `DEFAULT_RETRY_DELAY`: 重试延迟(可选,默认 2)
  - `DEFAULT_BATCH_SIZE`: 批处理大小(可选,默认 10)

### 改进
- 配置文件查找优先级调整:
  1. 环境变量(最高优先级)
  2. 当前工作目录的 `config.json`
  3. 项目根目录的 `config.json`
  4. 安装包目录的 `config.json`
- 更清晰的错误提示信息

### 文档
- 新增 `CONFIG_GUIDE.md` - 详细配置指南
- 新增 `MCP_USAGE_EXAMPLE.md` - MCP 使用示例
- 更新 `README.md` - 添加环境变量配置说明

## [0.1.6] - 之前版本

### 功能
- DICOM 目录扫描和分析
- 序列映射和文件映射
- DICOM 文件解析
- JSON 导出
- 批量上传到 Orthanc 服务器
- MCP 协议支持

---

## 使用建议

### 从旧版本升级

如果您从 0.1.6 或更早版本升级:

1. **清除缓存**:
   ```bash
   uv cache clean dicom-tools-mcp
   ```

2. **更新 MCP 配置**,添加环境变量:
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

3. **重启客户端** (Claude Desktop 或 VS Code)

### 配置方式

- **生产环境/MCP 部署**: 使用环境变量(v0.1.7+)
- **开发环境**: 使用 `config.json` 文件

详见 [CONFIG_GUIDE.md](CONFIG_GUIDE.md)
