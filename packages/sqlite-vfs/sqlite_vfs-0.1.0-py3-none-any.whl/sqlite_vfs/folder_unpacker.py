#!/usr/bin/env python3
"""
文件夹解包工具 - 从SQLite虚拟文件系统导出文件
"""

from .core import SQLiteVFS


class FolderUnpacker:
    def __init__(self, sqlite_vfs: SQLiteVFS):
        self.sqlite_vfs = sqlite_vfs

    def check_database(self):
        """检查数据库结构和内容"""
        try:
            if self.sqlite_vfs.conn is None:
                return False, "数据库未连接"

            cursor = self.sqlite_vfs.conn.cursor()

            # 检查表是否存在
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='files'"
            )
            if not cursor.fetchone():
                return False, "files表不存在"

            # 检查是否有数据
            cursor.execute("SELECT COUNT(*) as count FROM files")
            result = cursor.fetchone()
            file_count = result["count"]

            # 检查根目录内容
            cursor.execute(
                """
                SELECT COUNT(*) as count FROM files 
                WHERE parent_path IS NULL OR parent_path = '' OR parent_path = '/'
            """
            )
            root_count = cursor.fetchone()["count"]

            return (
                True,
                f"数据库正常，共有 {file_count} 个文件/目录，根目录下有 {root_count} 个项目",
            )

        except Exception as e:
            return False, f"数据库检查失败: {e}"

    def unpack_filesystem(self, export_folder):
        """解包整个文件系统"""
        # 先检查数据库
        status, message = self.check_database()
        print(f"数据库状态: {message}")

        if not status:
            print("数据库存在问题，无法导出")
            return 0

        return self.sqlite_vfs.export_filesystem(export_folder)

    def unpack_file(self, vfs_path, local_path):
        """解包单个文件"""
        return self.sqlite_vfs.export_file(vfs_path, local_path)

    def unpack_directory(self, vfs_path, local_path):
        """解包目录"""
        return self.sqlite_vfs.export_directory(vfs_path, local_path)

    def list_root(self):
        """列出根目录内容"""
        try:
            if self.sqlite_vfs.conn is None:
                return []

            cursor = self.sqlite_vfs.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM files 
                WHERE parent_path IS NULL OR parent_path = '' OR parent_path = '/'
                ORDER BY is_directory DESC, name ASC
            """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"列出根目录失败: {e}")
            return []
