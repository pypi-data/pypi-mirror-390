#!/usr/bin/env python3
"""
DICOM 工具 MCP 服务器主文件

基于 MCP (Model Context Protocol) 的 DICOM 医学影像文件分析工具的Python实现。
"""
import shutil
from pathlib import Path

import logging
import sys
from typing import Any, Dict
import json
from argparse import Namespace
from src.models import DICOMDirectory
from src.utils import create_upload_config
from src.core import (
    get_series_info,
    should_upload_series,
    upload_series_metadata,
    upload_dicom_files
)
from getcookie import CookieManager
# 配置MCP服务器所需的导入
try:
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from pydantic import BaseModel
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import Response
except ImportError as e:
    print(f"错误: 缺少必要的MCP依赖库: {e}", file=sys.stderr)
    print("请运行: pip install mcp starlette uvicorn", file=sys.stderr)
    sys.exit(1)

# 导入DICOM工具
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))




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



def main():
    """输入用户名和密码修改config.json"""
    DEFAULT_CONFIG: Dict[str, Any] = {
        "max_workers": 10,
        "max_retries": 3,
        "DEFAULT_CONNECT_TIMEOUT": 3,
        "DEFAULT_READ_TIMEOUT": 5,
        "DEFAULT_RETRY_DELAY": 5,
        "DEFAULT_BATCH_SIZE": 6
    }

    import os
    name=os.getenv("name")
    password=os.getenv("password")
    tel=os.getenv("tel")
    base_url=os.getenv("base_url")

    from getcrpit import encrypt
    payload = {"username": name, "password": password, "phoneNumber": tel}
    plain = json.dumps(payload, ensure_ascii=False)
    cipher = encrypt(plain)
    cookie_manager = CookieManager(base_url, cipher)
    cookie = cookie_manager.get_cookie()
    if cookie:
        DEFAULT_CONFIG["cookie"]=cookie
        DEFAULT_CONFIG["base_url"]=base_url
        print(f":配置详情{DEFAULT_CONFIG}")

    return DEFAULT_CONFIG

def process_single_series(
        series,
        series_count: int,
        patient_name: str,
        series_type: int,
        base_url: str,
        cookie: str,
        upload_config: Namespace,
        api_url: str,
        use_series_uid: bool = False
) -> bool:
    """
    Process and upload a single DICOM series.

    Args:
        series: DICOM series object
        series_count: Series counter
        patient_name: Patient name
        series_type: Series type
        base_url: Base URL
        cookie: Authentication cookie
        upload_config: Upload configuration
        api_url: API URL for querying
        use_series_uid: Whether to use series UID as patient name

    Returns:
        bool: True if processed successfully, False otherwise
    """
    series_info = get_series_info(series)

    # 如果需要使用 series UID，则覆盖 patient_name
    if use_series_uid:
        patient_name = series_info["PatientID"]

    series_desc = (
        f"{series_info['SeriesDescription']} "
        f"({series_info['SliceNum']} 切片)"
    )
    print(f"\n{'=' * 60}")
    print(f"序列 {series_count}: {series_desc}")
    print(f"Patient Name: {patient_name}")
    print(f"{'=' * 60}")

    if not should_upload_series(series_info):
        print("X 序列不符合上传标准，跳过...")
        return False

    print("* 符合标准，开始上传流程...\n")

    # Step 1: Upload initial metadata (status 11)
    print("[1/3] 上传初始元数据...")
    metadata = upload_series_metadata(
        series_info, patient_name, series_type, 11, base_url, cookie, verbose=False
    )

    print("\n[2/3] 上传DICOM文件...")
    upload_dicom_files(series, upload_config, verbose=False)
    print("\n[3/3] 上传最终元数据...")
    metadata = upload_series_metadata(
        series_info, patient_name, series_type, 12, base_url, cookie, verbose=False
    )

    return True


def test(directory_path,DEFAULT_CONFIG,series_type):

    config = DEFAULT_CONFIG

    # Initialize basic parameters

    directory = directory_path
    base_url = config['base_url']
    if config['cookie'].startswith("ls="):
        cookie = config['cookie']
    else:
        cookie = "ls=" + config['cookie']
    # series_type = config['series_type']
    series_type = int(series_type)
    patient_name = config.get('patient_name', None)
    use_series_uid = patient_name is None  # 如果 patient_name 未设置，则使用 series UID
    if patient_name is None:
        patient_name = 'default'  # 默认值，会被 series UID 覆盖
    api_url = f"{base_url}/api/v2/getSeriesByStudyInstanceUID"

    # Create upload configuration
    upload_config = create_upload_config(config)

    # Initialize DICOM directory
    print(f"扫描 DICOM 目录: {directory}")
    dicom_directory = DICOMDirectory(directory)

    # Get all series
    all_series = list(dicom_directory.get_dicom_series())
    total_series = len(all_series)
    print(f"发现 {total_series} 个序列\n")

    # Process each series
    successful_uploads = 0
    skipped_series = 0
    failed_series = 0
    patient_num = []
    error_messages = []  # 收集错误信息

    for series_count, series in enumerate(all_series, start=1):
        series_info = get_series_info(series)
        patient_num.append(series_info["PatientID"])
        try:
            success = process_single_series(
                series=series,
                series_count=series_count,
                patient_name=patient_name,
                series_type=series_type,
                base_url=base_url,
                cookie=cookie,
                upload_config=upload_config,
                api_url=api_url,
                use_series_uid=use_series_uid
            )

            if success:
                successful_uploads += 1
            else:
                skipped_series += 1

        except Exception as e:
            error_msg = f"序列 {series_count} ({series_info.get('SeriesDescription', 'Unknown')}): {str(e)}"
            print(f"\n[错误] 处理序列 {series_count} 时出错: {e}\n")
            error_messages.append(error_msg)
            failed_series += 1
            continue

    # Print summary
    print("\n" + "=" * 60)
    print("处理汇总")
    print("=" * 60)
    print(f"总序列数:           {total_series}")
    print(f"成功上传:           {successful_uploads}")
    print(f"跳过 (不符合标准):  {skipped_series}")
    print(f"失败 (错误):        {failed_series}")
    print(f'患者数：{len(set(patient_num))}')
    print("=" * 60)

    # 构建返回结果
    dic = {
        "totalseries": total_series,
        "successful_uploads": successful_uploads,
        "skipped_series": skipped_series,
        "failed_series": failed_series,
        "totalPatients": len(set(patient_num)),
        "patients": list(set(patient_num)),
        "upload_url": f"{config['base_url']}/study/studylist"
    }

    # 判断上传结果
    if failed_series > 0:
        # 有失败的序列
        dic["status"] = "partial_failure"
        dic["message"] = f"上传部分失败：{failed_series}/{total_series} 个序列上传失败"
        dic["errors"] = error_messages  # 添加错误详情
    elif successful_uploads == 0:
        # 没有任何成功上传
        dic["status"] = "all_failed"
        dic["message"] = "上传完全失败：没有序列成功上传"
        dic["errors"] = error_messages if error_messages else ["所有序列都不符合上传标准或发生错误"]
    else:
        # 全部成功
        dic["status"] = "success"
        dic["message"] = f"上传成功：{successful_uploads}/{total_series} 个序列已上传"

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(dic, ensure_ascii=False, indent=2)
            }
        ]
    }


def copy_dicom(src_path: str, dest_dir: str) -> Path:
    src = Path(src_path)
    dest_folder = Path(dest_dir)
    if not src.exists():
        raise FileNotFoundError(f"源文件不存在: {src}")
    dest_folder.mkdir(parents=True, exist_ok=True)

    dest = dest_folder / src.name
    if dest.exists():
        stem = src.stem
        suffix = src.suffix
        i = 1
        while True:
            candidate = dest_folder / f"{stem}_copy{i}{suffix}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1

    shutil.copy2(src, dest)
    return dest


def separate_series_by_patient(directory_path):
    dicom_directory = DICOMDirectory(directory_path)
    all_series = list(dicom_directory.get_dicom_series())

    # 按患者分组
    patient_series_map = {}
    for series in all_series:
        info = get_series_info(series)
        pid = info["PatientID"]
        patient_series_map.setdefault(pid, []).append(series)

    # 为每个患者和序列创建目录并复制文件
    base_path = Path(directory_path)
    sucess_num=0
    main_dir=[]
    for pid, series_list in patient_series_map.items():
        p_dir = base_path / pid
        p_dir.mkdir(parents=True, exist_ok=True)
        main_dir.append(str(p_dir))
        for series in series_list:
            info = get_series_info(series)
            series_uid = info.get("SeriesInstanceUID", "unknown_series")
            s_dir = p_dir / series_uid
            s_dir.mkdir(parents=True, exist_ok=True)

            for instance in getattr(series, "instances", []):
                # 支持常见的实例路径属性名
                src = (
                    getattr(instance, "filepath", None)
                    or getattr(instance, "file_path", None)
                    or getattr(instance, "path", None)
                )
                if not src:
                    logger.warning(f"实例缺少路径: patient={pid}, series={series_uid}")
                    continue

                try:
                    copy_dicom(src, s_dir)
                    sucess_num+=1
                except Exception as e:
                    logger.exception(f"复制失败: {src} -> {s_dir}: {e}")


    dic={
        "totalPatients": len(patient_series_map),
        "totalSeries": len(all_series),
        "totalFilesCopied": sucess_num,
        "newDirectory": main_dir
    }
    return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(dic, ensure_ascii=False)
                }
            ]
    }

async def Analysis_dicom_directory_tool(directory_path,series_type):
    "seriers_type:1主动脉9为二尖瓣"
    try:
        return test(directory_path,main(),series_type)
    except Exception as e:
        import traceback
        error_info = f"处理过程中发生错误: {str(e)}\n详细信息:\n{traceback.format_exc()}"
        return {
            "content": [
                {
                    "type": "text",
                    "text": error_info
                }
            ]
        }

async def separate_series_by_patient_tool(directory_path):
    directory_path=fr'{directory_path}'
    try:
        return separate_series_by_patient(directory_path)
    except Exception as e:
        import traceback
        error_info = f"处理过程中发生错误: {str(e)}\n详细信息:\n{traceback.format_exc()}"
        return {
            "content": [
                {
                    "type": "text",
                    "text": error_info
                }
            ]
        }



if __name__ == "__main__":
    #print(test(fr'C:\Users\13167\Desktop\新建文件夹\3 hao\dicom',main(),9))
    separate_series_by_patient(fr'C:\Users\13167\Desktop\新建文件夹')