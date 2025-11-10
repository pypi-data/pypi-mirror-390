#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM 工具 MCP 服务器主文件

基于 MCP (Model Context Protocol) 的 DICOM 医学影像文件分析工具的Python实现。
"""

import os
import asyncio
import json
import logging
import sys
from typing import Any, Dict

# 设置标准输出编码为 UTF-8 (Windows 兼容性)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置MCP服务器所需的导入
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from pydantic import BaseModel
except ImportError as e:
    print(f"错误: 缺少必要的MCP依赖库: {e}", file=sys.stderr)
    print("请运行: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# 导入DICOM工具
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dicom_tools.scanner import scan_dicom_directory_tool
from dicom_tools.parser import parse_dicom_file_tool
from dicom_tools.mapping import series_mapping_tool, file_mapping_tool
from dicom_tools.exporter import export_dicom_json_tool
from upload import Analysis_dicom_directory_tool, separate_series_by_patient_tool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("dicom-tools-python")


# 工具参数模型
class DirectoryPathArgs(BaseModel):
    directory_path: str


class DirectoryPathWithSeriesArgs(BaseModel):
    directory_path: str
    series_type: str


class FilePathArgs(BaseModel):
    file_path: str

class fileforsep(BaseModel):
    fileforsep: str

@server.list_tools()
async def list_tools() -> list[Tool]:
    """注册所有可用的DICOM工具"""
    return [
        Tool(
            name="scan-dicom-directory",
            description="扫描指定目录下的所有 DICOM 文件，返回统计摘要（总数据量、患者数、序列数等高层信息）",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "要扫描的目录路径"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="get-dicom-series-mapping",
            description="生成患者-序列的详细映射关系，包含每个序列的文件列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "要扫描的目录路径"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="export-dicom-json",
            description="导出完整的DICOM扫描结果为JSON格式，包含所有患者、序列和文件信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "要扫描的目录路径"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="parse-dicom-file",
            description="解析单个 DICOM 文件，提取 PatientID、PatientName、SeriesInstanceUID、SeriesDescription 等关键信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "DICOM 文件的路径"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="Analysis_dicom_directory",
            description="扫描指定文件夹的dicom文件，自动上传进行分析，返回上传的信息和对应的url",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "DICOM 文件夹"
                    },
                    "series_type": {
                        "type": "string",
                        "description": "分析方法：1是主动脉，9是二尖瓣"
                    }
                },
                "required": ["directory_path", "series_type"]
            }
        ),
        Tool(
            name="fileforsep",
            description="对文件夹进行整理，可以将若干的dicom数据拆分成为多个子文件夹，按照病人和序列整理。",
            inputSchema={
                "type": "object",
                "properties": {
                    "fileforsep": {
                        "type": "string",
                        "description": "需要整理的文件夹路径"
                    }
                },
                "required": ["fileforsep"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用请求"""
    try:
        logger.info(f"调用工具: {name}, 参数: {arguments}")

        if name == "scan-dicom-directory":
            args = DirectoryPathArgs(**arguments)
            result = await scan_dicom_directory_tool(args.directory_path)

        elif name == "get-dicom-series-mapping":
            args = DirectoryPathArgs(**arguments)
            result = await series_mapping_tool(args.directory_path)

        elif name == "get-dicom-file-mapping":
            args = DirectoryPathArgs(**arguments)
            result = await file_mapping_tool(args.directory_path)

        elif name == "export-dicom-json":
            args = DirectoryPathArgs(**arguments)
            result = await export_dicom_json_tool(args.directory_path)

        elif name == "parse-dicom-file":
            args = FilePathArgs(**arguments)
            result = await parse_dicom_file_tool(args.file)

        elif name == "Analysis_dicom_directory":
            args = DirectoryPathWithSeriesArgs(**arguments)
            result = await Analysis_dicom_directory_tool(args.directory_path, args.series_type)
        elif name == "fileforsep":
            args = fileforsep(**arguments)
            result = await separate_series_by_patient_tool(args.fileforsep)
        else:
            raise ValueError(f"未知工具: {name}")

        # 转换结果格式为MCP标准格式
        return [
            TextContent(
                type="text",
                text=content["text"]
            )
            for content in result["content"]
            if content["type"] == "text"
        ]

    except Exception as e:
        logger.error(f"工具调用失败: {name}, 错误: {e}", exc_info=True)

        error_response = {
            "error": True,
            "message": f"工具 {name} 执行失败: {str(e)}"
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(error_response, ensure_ascii=False)
            )
        ]


async def main():
    """启动MCP服务器"""
    try:
        logger.info("启动 DICOM 工具 MCP 服务器 ...")

        # 使用stdio传输启动服务器
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行失败: {e}", exc_info=True)
        sys.exit(1)


def run():
    """同步入口函数，用于 uvx 调用"""
    # 设置事件循环策略（Windows兼容性）
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # 运行服务器
    asyncio.run(main())


if __name__ == "__main__":
    run()