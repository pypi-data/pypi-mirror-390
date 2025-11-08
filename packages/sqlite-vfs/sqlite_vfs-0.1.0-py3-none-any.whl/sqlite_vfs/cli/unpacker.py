#!/usr/bin/env python3
"""
文件夹解包工具 - 从SQLite虚拟文件系统导出文件
"""

import os
import argparse
from ..core import SQLiteVFS
from ..folder_unpacker import FolderUnpacker


def unpack():
    parser = argparse.ArgumentParser(description="从SQLite虚拟文件系统导出文件")
    parser.add_argument("db_file", help="SQLite数据库文件路径")
    parser.add_argument("export_folder", help="导出目标文件夹路径")
    parser.add_argument("--path", help="要导出的特定文件或目录路径（默认导出全部）")
    parser.add_argument(
        "--list-root", action="store_true", help="列出根目录内容而不导出"
    )
    parser.add_argument("--debug", action="store_true", help="显示调试信息")
    parser.add_argument(
        "--ignore-timestamps",
        action="store_true",
        help="忽略时间戳错误，只导出文件内容",
    )

    args = parser.parse_args()

    if not os.path.exists(args.db_file):
        print(f"错误: 数据库文件不存在: {args.db_file}")
        return

    # 创建解包器
    unpacker = FolderUnpacker(sqlite_vfs=SQLiteVFS(args.db_file))

    try:
        if args.list_root:
            # 只列出根目录内容
            print("根目录内容:")
            items = unpacker.list_root()
            for item in items:
                file_type = "DIR" if item["is_directory"] else "FILE"
                print(f"  {file_type}: {item['name']} (路径: {item['path']})")
            return

        if args.path:
            # 导出特定路径
            if unpacker.sqlite_vfs.is_dir(args.path):
                local_dir = os.path.join(
                    args.export_folder, os.path.basename(args.path)
                )
                unpacker.unpack_directory(args.path, local_dir)
            else:
                local_file = os.path.join(
                    args.export_folder, os.path.basename(args.path)
                )
                if args.ignore_timestamps:
                    unpacker.sqlite_vfs.export_file_safe(args.path, local_file)
                else:
                    unpacker.unpack_file(args.path, local_file)
        else:
            # 导出整个文件系统
            if args.ignore_timestamps:
                # 使用安全导出方法
                unpacker.sqlite_vfs.export_filesystem = (
                    lambda export_root: unpacker.sqlite_vfs.export_filesystem(
                        export_root
                    )
                )
            unpacker.unpack_filesystem(args.export_folder)

    finally:
        unpacker.sqlite_vfs.close()


if __name__ == "__main__":
    unpack()
