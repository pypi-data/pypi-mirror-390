#!/usr/bin/env python3
"""
文件夹打包工具 - 将文件夹打包为SQLite虚拟文件系统
"""

import os
from datetime import datetime
from .core import SQLiteVFS


class FolderPacker:
    def __init__(
        self, sqlite_vfs: SQLiteVFS, exclude_patterns=None, fs_name="packed_filesystem"
    ):
        self.sqlite_vfs = sqlite_vfs
        self.exclude_patterns = exclude_patterns or []
        self.total_files = 0
        self.total_size = 0
        self.fs_name = fs_name

    def should_exclude(self, filepath):
        """检查文件是否应该被排除"""
        filename = os.path.basename(filepath)
        for pattern in self.exclude_patterns:
            if pattern in filename:
                return True
        return False

    def pack_folder(self, source_folder):
        """打包整个文件夹"""
        print(f"开始打包文件夹: {source_folder}")

        # 记录开始时间
        start_time = datetime.now()

        self.sqlite_vfs.clean()

        # 插入文件系统元数据
        self.sqlite_vfs.add_vfs_metadata(self.fs_name)

        self.total_files = 0
        self.total_size = 0

        # 遍历文件夹
        for root, dirs, files in os.walk(source_folder):
            # 处理目录
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                rel_path = os.path.relpath(dir_path, source_folder)

                if self.should_exclude(rel_path):
                    continue

                self.sqlite_vfs.add_directory(rel_path, source_folder)

            # 处理文件
            for file_name in files:
                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, source_folder)

                if self.should_exclude(rel_path):
                    continue

                file_size = os.path.getsize(file_path)
                self.sqlite_vfs.add_file(file_path, rel_path)
                self.total_size += file_size
                self.total_files += 1

        # 更新统计信息
        self.sqlite_vfs.update_vfs_metadata(
            self.fs_name, self.total_files, self.total_size
        )

        # 计算耗时
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"打包完成!")
        print(f"文件数量: {self.total_files}")
        print(f"总大小: {self.total_size / 1024 / 1024:.2f} MB")
        print(f"耗时: {duration:.2f} 秒")
        print(f"数据库文件: {self.sqlite_vfs.db_path}")

    def add_file(self, abs_path, rel_path):
        """添加单个文件"""
        self.sqlite_vfs.add_file(abs_path, rel_path)
        self.total_size += os.path.getsize(abs_path)
        self.total_files += 1
        self.sqlite_vfs.update_vfs_metadata(
            self.fs_name, self.total_files, self.total_size
        )
        print(f"添加文件: {rel_path}")
        print(f"文件大小: {os.path.getsize(abs_path) / 1024 / 1024:.2f} MB")
        print(f"数据库文件: {self.sqlite_vfs.db_path}")
        self.sqlite_vfs.export_file_safe(rel_path, abs_path)
        print(f"已保存到: {abs_path}")
        print(f"已保存到: {self.sqlite_vfs.db_path}")

    def add_directory(self, abs_path, rel_path):
        """添加目录"""
        self.sqlite_vfs.add_directory(rel_path, abs_path)
        print(f"添加目录: {rel_path}")
        print(f"数据库文件: {self.sqlite_vfs.db_path}")
