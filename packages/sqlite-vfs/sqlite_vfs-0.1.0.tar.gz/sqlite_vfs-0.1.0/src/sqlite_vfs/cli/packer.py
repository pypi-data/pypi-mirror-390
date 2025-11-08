#!/usr/bin/env python3
"""
文件夹打包工具 - 将文件夹打包为SQLite虚拟文件系统
"""

import os
import argparse
from ..folder_packer import FolderPacker
from ..core import SQLiteVFS


def pack():
    parser = argparse.ArgumentParser(description="将文件夹打包为SQLite虚拟文件系统")
    parser.add_argument("source_folder", help="要打包的源文件夹路径")
    parser.add_argument("output_db", help="输出的SQLite数据库文件路径")
    parser.add_argument("--name", default="packed_filesystem", help="文件系统名称")
    parser.add_argument("--compress", action="store_true", help="启用压缩")
    parser.add_argument("--exclude", nargs="*", help="要排除的文件模式")

    args = parser.parse_args()

    if not os.path.exists(args.source_folder):
        print(f"错误: 源文件夹不存在: {args.source_folder}")
        return

    # 创建打包器
    packer = FolderPacker(
        sqlite_vfs=SQLiteVFS(args.output_db, args.compress),
        exclude_patterns=args.exclude or [],
        fs_name=args.name,
    )

    try:
        packer.pack_folder(args.source_folder)
    finally:
        packer.sqlite_vfs.close()


if __name__ == "__main__":
    pack()
