#!/usr/bin/env python3
"""
SQLite虚拟文件系统实现
"""

import sqlite3
import os
import zlib
from datetime import datetime


class SQLiteVFS:
    def __init__(self, db_path, compress=False):
        self.db_path = db_path
        self.compress = compress
        self.conn = None
        self.total_files = 0
        self.total_size = 0
        self.open_files = {}
        self.connect()

    def connect(self):
        """连接到文件系统数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def clean(self):
        if self.conn is None:
            raise ValueError("数据库连接未建立")
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM files")
        cursor.execute("DELETE FROM filesystem_metadata")

    def add_vfs_metadata(self, name):
        """添加文件系统元数据"""
        if self.conn is None:
            raise ValueError("数据库连接未建立")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO filesystem_metadata (name)
            VALUES (?)
        """,
            (name,),
        )
        self.conn.commit()

    def update_vfs_metadata(self, name, total_files, total_size):
        """更新文件系统元数据"""
        if self.conn is None:
            raise ValueError("数据库连接未建立")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE filesystem_metadata
            SET total_files = ?, total_size = ?
            WHERE name = ?
        """,
            (total_files, total_size, name),
        )
        self.conn.commit()

    def _create_tables(self):
        """创建必要的表"""
        if self.conn is None:
            raise ValueError("数据库连接未建立")
        cursor = self.conn.cursor()

        # 创建文件系统元数据表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS filesystem_metadata (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_files INTEGER DEFAULT 0,
                total_size INTEGER DEFAULT 0
            )
        """
        )

        # 创建文件表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                parent_path TEXT,
                is_directory BOOLEAN NOT NULL DEFAULT 0,
                file_size INTEGER DEFAULT 0,
                created_time DATETIME,
                modified_time DATETIME,
                permissions INTEGER DEFAULT 0644,
                content BLOB,
                compressed BOOLEAN DEFAULT 0
            )
        """
        )

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_path)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_directory ON files(is_directory)"
        )

        self.conn.commit()

    def add_directory(self, rel_path, source_folder):
        """添加目录到数据库"""
        try:
            abs_path = os.path.join(source_folder, rel_path)
            stat = os.stat(abs_path)

            if self.conn is None:
                raise ValueError("数据库连接未建立")
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO files 
                (path, name, parent_path, is_directory, created_time, modified_time, permissions)
                VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
                (
                    rel_path.replace("\\", "/"),
                    os.path.basename(rel_path),
                    # 将 \ 替换为 /
                    os.path.dirname(rel_path).replace("\\", "/"),
                    datetime.fromtimestamp(stat.st_ctime),
                    datetime.fromtimestamp(stat.st_mtime),
                    stat.st_mode & 0o777,
                ),
            )

        except Exception as e:
            print(f"添加目录失败 {rel_path}: {e}")

        else:
            self.conn.commit()

    def add_file(self, abs_path, rel_path):
        """添加文件到数据库"""
        try:
            stat = os.stat(abs_path)
            file_size = stat.st_size

            # 读取文件内容
            with open(abs_path, "rb") as f:
                content = f.read()

            # 压缩处理
            compressed = False
            if self.compress and len(content) > 1024:  # 大于1KB的文件才压缩
                compressed_content = zlib.compress(content, level=6)
                if len(compressed_content) < len(content):
                    content = compressed_content
                    compressed = True

            if self.conn is None:
                raise ValueError("数据库连接未建立")
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO files 
                (path, name, parent_path, is_directory, file_size, 
                 created_time, modified_time, permissions, content, compressed)
                VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?)
            """,
                (
                    rel_path.replace("\\", "/"),
                    os.path.basename(rel_path),
                    os.path.dirname(rel_path).replace("\\", "/"),
                    file_size,
                    datetime.fromtimestamp(stat.st_ctime),
                    datetime.fromtimestamp(stat.st_mtime),
                    stat.st_mode & 0o777,
                    sqlite3.Binary(content),
                    compressed,
                ),
            )

            self.total_files += 1
            self.total_size += file_size

            print(f"添加文件: {rel_path} ({file_size} bytes)")

        except Exception as e:
            print(f"添加文件失败 {rel_path}: {e}")

    def get_file_info(self, path):
        """获取文件信息"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE path = ?", (path.lstrip("/"),))
        row = cursor.fetchone()
        if row:
            # 将时间字符串转换为datetime对象
            return self._parse_row_datetime(row)
        return None

    def list_directory(self, path):
        """列出目录内容"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        if path == "/":
            sql = """
                SELECT * FROM files 
                ORDER BY is_directory DESC, name ASC
            """
        else:
            sql = f"""
                SELECT * FROM files 
                WHERE path = '{path.lstrip("/")}'
                ORDER BY is_directory DESC, name ASC
            """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        # 将时间字符串转换为datetime对象
        return [self._parse_row_datetime(row) for row in rows]

    def _parse_row_datetime(self, row):
        """将行中的时间字符串转换为datetime对象"""
        from datetime import datetime

        parsed_row = dict(row)

        # 处理created_time
        if parsed_row["created_time"] and isinstance(parsed_row["created_time"], str):
            try:
                parsed_row["created_time"] = datetime.fromisoformat(
                    parsed_row["created_time"].replace("Z", "+00:00")
                )
            except ValueError:
                # 如果格式不匹配，尝试其他格式
                try:
                    parsed_row["created_time"] = datetime.strptime(
                        parsed_row["created_time"], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    # 如果无法解析，保持原样
                    pass

        # 处理modified_time
        if parsed_row["modified_time"] and isinstance(parsed_row["modified_time"], str):
            try:
                parsed_row["modified_time"] = datetime.fromisoformat(
                    parsed_row["modified_time"].replace("Z", "+00:00")
                )
            except ValueError:
                try:
                    parsed_row["modified_time"] = datetime.strptime(
                        parsed_row["modified_time"], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    pass

        return parsed_row

    def read_file(self, path, offset=0, size=None):
        """读取文件内容"""
        file_info = self.get_file_info(path)
        if not file_info:
            raise FileNotFoundError(f"文件不存在: {path}")

        if file_info["is_directory"]:
            raise IsADirectoryError(f"这是一个目录: {path}")

        content = file_info["content"]

        # 解压缩
        if file_info["compressed"]:
            content = zlib.decompress(content)

        if size is None:
            size = len(content) - offset

        return content[offset : offset + size]

    def mv_file(self, src, dest):
        """移动文件"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE files
            SET path = ?, name = ?, parent_path = ?
            WHERE path = ?
        """,
            (
                dest.lstrip("/"),
                os.path.basename(dest),
                os.path.dirname(dest).lstrip("/"),
                src.lstrip("/"),
            ),
        )
        self.conn.commit()

    def mk_dir(self, path):
        """创建目录"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO files 
            (path, name, parent_path, is_directory, created_time, modified_time, permissions)
            VALUES (?, ?, ?, 1, ?, ?, ?)
        """,
            (
                path.lstrip("/"),
                os.path.basename(path),
                os.path.dirname(path).lstrip("/"),
                datetime.now(),
                datetime.now(),
                0o755,
            ),
        )
        self.conn.commit()

    def mv_dir(self, src, dest):
        """移动目录"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")

        cursor = self.conn.cursor()

        if src == "/":
            # 移动根目录下所有内容到指定目录
            # 先处理目录，避免路径冲突
            cursor.execute(
                """
                UPDATE files
                SET path = ? || '/' || path,
                    parent_path = ? || '/' || parent_path
                WHERE path != '' AND is_directory = 1
                """,
                (dest.lstrip("/"), dest.lstrip("/")),
            )

            # 再处理文件
            cursor.execute(
                """
                UPDATE files
                SET path = ? || '/' || path,
                    parent_path = CASE 
                        WHEN parent_path = '' THEN ?
                        ELSE ? || '/' || parent_path
                    END
                WHERE is_directory = 0
                """,
                (dest.lstrip("/"), dest.lstrip("/"), dest.lstrip("/")),
            )
        else:
            # 移动指定目录到目标位置
            # 更新目录本身
            cursor.execute(
                """
                UPDATE files
                SET path = ?,
                    name = ?,
                    parent_path = ?
                WHERE path = ?
                """,
                (
                    dest.lstrip("/"),
                    os.path.basename(dest),
                    os.path.dirname(dest).lstrip("/"),
                    src.lstrip("/"),
                ),
            )

            # 更新目录下的所有内容
            cursor.execute(
                """
                UPDATE files
                SET path = ? || SUBSTR(path, ?),
                    parent_path = ? || SUBSTR(parent_path, ?)
                WHERE path LIKE ? || '%'
                """,
                (
                    dest.lstrip("/"),
                    len(src.lstrip("/")) + 1,
                    dest.lstrip("/"),
                    len(src.lstrip("/")) + 1,
                    src.lstrip("/"),
                ),
            )

        self.conn.commit()

    def get_stats(self):
        """获取文件系统统计信息"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM filesystem_metadata WHERE id = 1")
        return cursor.fetchone()

    def remove(self, path):
        """删除文件或目录"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        if self.is_dir(path):  # 检查是否为目录
            self._remove_directory(path)
        else:  # 检查是否为文件
            self._remove_file(path)

    def _remove_directory(self, path):
        """删除目录"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            DELETE FROM files
            WHERE path LIKE ? || '%'
        """,
            (path.lstrip("/"),),
        )
        self.total_files -= cursor.rowcount
        self.total_size -= cursor.rowcount
        self.conn.commit()

    def _remove_file(self, path):
        """删除文件"""
        if self.conn is None:
            raise ConnectionError("文件系统尚未连接")
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM files WHERE path = ?", (path.lstrip("/"),))
        self.total_files -= cursor.rowcount
        self.total_size -= cursor.rowcount
        self.conn.commit()

    def exists(self, path):
        """检查文件是否存在"""
        return self.get_file_info(path) is not None

    def is_dir(self, path):
        """检查是否为目录"""
        file_info = self.get_file_info(path)
        return file_info and file_info["is_directory"]

    def is_file(self, path):
        """检查是否为文件"""
        file_info = self.get_file_info(path)
        return file_info and not file_info["is_directory"]

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()

    def export_file(self, vfs_path, local_path):
        """从虚拟文件系统导出文件到本地文件系统"""
        try:
            file_info = self.get_file_info(vfs_path)
            if not file_info:
                raise FileNotFoundError(f"虚拟文件系统中找不到文件: {vfs_path}")

            if file_info["is_directory"]:
                raise IsADirectoryError(f"无法导出目录: {vfs_path}")

            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # 读取文件内容
            content = self.read_file(vfs_path)

            # 写入本地文件
            with open(local_path, "wb") as f:
                f.write(content)

            # 恢复文件属性（时间戳和权限）
            if file_info["created_time"]:
                if isinstance(file_info["created_time"], str):
                    # 如果是字符串，转换为datetime对象
                    from datetime import datetime

                    created_time = datetime.fromisoformat(
                        file_info["created_time"].replace("Z", "+00:00")
                    )
                else:
                    created_time = file_info["created_time"]
                created_timestamp = created_time.timestamp()
                os.utime(local_path, (created_timestamp, created_timestamp))
            if file_info["modified_time"]:
                if isinstance(file_info["modified_time"], str):
                    # 如果是字符串，转换为datetime对象
                    from datetime import datetime

                    modified_time = datetime.fromisoformat(
                        file_info["modified_time"].replace("Z", "+00:00")
                    )
                else:
                    modified_time = file_info["modified_time"]
                modified_timestamp = modified_time.timestamp()
                # 保持访问时间不变，只修改修改时间
                current_atime = os.path.getatime(local_path)
                os.utime(local_path, (current_atime, modified_timestamp))

            if file_info["permissions"]:
                os.chmod(local_path, file_info["permissions"])

            print(f"导出成功: {vfs_path} -> {local_path}")
            return True

        except Exception as e:
            print(f"导出文件失败: {e}")
            import traceback

            traceback.print_exc()  # 打印详细错误信息
            return False

    def export_directory(self, vfs_path, local_path):
        """从虚拟文件系统导出整个目录到本地文件系统"""
        try:
            # 处理根目录的特殊情况
            if vfs_path == "/":
                # 检查根目录是否存在
                if not self._has_root_directory():
                    # 如果根目录不存在，直接导出根目录下的所有内容
                    return self._export_root_contents(local_path)

            if not self.is_dir(vfs_path):
                # 检查是否是有效的目录路径
                if not self._is_valid_directory_path(vfs_path):
                    raise NotADirectoryError(f"路径不是目录: {vfs_path}")
                else:
                    # 可能是根目录的另一种表示
                    return self._export_root_contents(local_path)

            # 创建本地目录
            os.makedirs(local_path, exist_ok=True)

            # 遍历目录内容
            items = self.list_directory(vfs_path)
            exported_count = 0

            for item in items:
                item_vfs_path = item["path"]
                item_local_path = os.path.join(local_path, item["name"])

                if item["is_directory"]:
                    # 递归导出子目录
                    count = self.export_directory(item_vfs_path, item_local_path)
                    exported_count += count
                else:
                    # 导出文件
                    if self.export_file_safe(item_vfs_path, item_local_path):
                        exported_count += 1

            print(f"目录导出完成: {vfs_path} -> {local_path} ({exported_count} 个项目)")
            return exported_count

        except Exception as e:
            print(f"导出目录失败: {e}")
            return 0

    def _has_root_directory(self):
        """检查是否存在根目录记录"""
        if self.conn is None:
            return False
        cursor = self.conn.cursor()
        # 检查是否有路径为 "" 或 "/" 的目录
        cursor.execute(
            "SELECT COUNT(*) as count FROM files WHERE path = '' OR path = '/'"
        )
        result = cursor.fetchone()
        return result["count"] > 0

    def _export_root_contents(self, local_path):
        """导出根目录下的所有内容"""
        try:
            # 创建本地目录
            os.makedirs(local_path, exist_ok=True)

            # 获取所有父路径为空的文件/目录（这些就是根目录下的内容）
            if self.conn is None:
                return 0

            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM files 
                WHERE parent_path IS NULL OR parent_path = '' OR parent_path = '/'
                ORDER BY is_directory DESC, name ASC
            """
            )

            items = cursor.fetchall()
            exported_count = 0

            for item in items:
                item_vfs_path = item["path"]
                item_local_path = os.path.join(local_path, item["name"])

                if item["is_directory"]:
                    # 递归导出子目录
                    count = self.export_directory(item_vfs_path, item_local_path)
                    exported_count += count
                else:
                    # 导出文件
                    if self.export_file(item_vfs_path, item_local_path):
                        exported_count += 1

            print(f"根目录导出完成: -> {local_path} ({exported_count} 个项目)")
            return exported_count

        except Exception as e:
            print(f"导出根目录内容失败: {e}")
            return 0

    def _is_valid_directory_path(self, path):
        """检查是否是有效的目录路径"""
        if self.conn is None:
            return False
        cursor = self.conn.cursor()
        # 检查是否有以此路径为父路径的文件/目录
        cursor.execute(
            "SELECT COUNT(*) as count FROM files WHERE parent_path = ?",
            (path.lstrip("/"),),
        )
        result = cursor.fetchone()
        return result["count"] > 0

    def export_filesystem(self, export_root):
        """导出整个文件系统到指定目录"""
        try:
            print(f"开始导出文件系统到: {export_root}")

            # 确保导出目录存在
            os.makedirs(export_root, exist_ok=True)

            # 从根目录开始导出
            total_exported = self.export_directory("/", export_root)

            print(f"文件系统导出完成! 共导出 {total_exported} 个文件/目录")
            return total_exported

        except Exception as e:
            print(f"导出文件系统失败: {e}")
            return 0

    def export_file_safe(self, vfs_path, local_path):
        """安全导出文件 - 即使时间戳处理失败也能导出文件内容"""
        try:
            file_info = self.get_file_info(vfs_path)
            if not file_info:
                raise FileNotFoundError(f"虚拟文件系统中找不到文件: {vfs_path}")

            if file_info["is_directory"]:
                raise IsADirectoryError(f"无法导出目录: {vfs_path}")

            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # 读取文件内容
            content = self.read_file(vfs_path)

            # 写入本地文件
            with open(local_path, "wb") as f:
                f.write(content)

            # 尝试设置时间戳，但即使失败也不影响文件导出
            try:
                if file_info["created_time"]:
                    if isinstance(file_info["created_time"], str):
                        from datetime import datetime

                        created_time = datetime.fromisoformat(
                            file_info["created_time"].replace("Z", "+00:00")
                        )
                    else:
                        created_time = file_info["created_time"]
                    created_timestamp = created_time.timestamp()
                    os.utime(local_path, (created_timestamp, created_timestamp))
            except Exception as e:
                print(f"警告: 无法设置创建时间 {vfs_path}: {e}")

            try:
                if file_info["modified_time"]:
                    if isinstance(file_info["modified_time"], str):
                        from datetime import datetime

                        modified_time = datetime.fromisoformat(
                            file_info["modified_time"].replace("Z", "+00:00")
                        )
                    else:
                        modified_time = file_info["modified_time"]
                    modified_timestamp = modified_time.timestamp()
                    current_atime = os.path.getatime(local_path)
                    os.utime(local_path, (current_atime, modified_timestamp))
            except Exception as e:
                print(f"警告: 无法设置修改时间 {vfs_path}: {e}")

            try:
                if file_info["permissions"]:
                    os.chmod(local_path, file_info["permissions"])
            except Exception as e:
                print(f"警告: 无法设置权限 {vfs_path}: {e}")

            print(f"导出成功: {vfs_path} -> {local_path}")
            return True

        except Exception as e:
            print(f"导出文件失败 {vfs_path}: {e}")
            return False


# 使用示例
def demo_usage():
    # 创建文件系统实例
    vfs = SQLiteVFS("project.bin")
    vfs.connect()

    # 获取统计信息
    stats = vfs.get_stats()
    if not stats:
        return
    print(f"文件系统: {stats['name']}")
    print(f"文件数量: {stats['total_files']}")
    print(f"总大小: {stats['total_size'] / 1024 / 1024:.2f} MB")

    # 列出根目录
    print("\n根目录内容:")
    for item in vfs.list_directory("/"):
        file_type = "DIR" if item["is_directory"] else "FILE"
        print(f"  {file_type}: {item['name']} ({item['file_size']} bytes)")

    # 读取文件示例
    try:
        content = vfs.read_file(r"Lib\site-packages\_virtualenv.py")
        print(f"\n文件内容: {content.decode('utf-8')}")
    except Exception as e:
        print(f"读取文件失败: {e}")

    vfs.close()
