import zipfile
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import logging
from contextlib import contextmanager

from .models import PluginConfig

logger = logging.getLogger("PluginManager.ArchiveHandler")

class ArchiveHandler:
    def __init__(self):
        pass

    def extract_archive(self, archive_path: Path, extract_dir: Path) -> bool:
        """解压归档文件"""
        try:
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    # 首先验证zip文件
                    bad_file = zip_ref.testzip()
                    if bad_file:
                        raise zipfile.BadZipFile(f"ZIP文件损坏: {bad_file}")

                    zip_ref.extractall(extract_dir)
                logger.info(f"ZIP解压完成: {extract_dir}")
                return True
            else:
                logger.error(f"不支持的压缩格式: {archive_path.suffix}")
                return False
        except zipfile.BadZipFile as e:
            logger.error(f"ZIP文件损坏: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"解压失败: {str(e)}")
            return False

    def package_plugin(self, plugin_name: str, plugin_dir: Path, output_dir: Path,
                      plugin_config: PluginConfig = None) -> Optional[Path]:
        """打包插件为zip文件"""
        if not plugin_dir.exists():
            logger.error(f"插件目录不存在: {plugin_dir}")
            return None

        # 确保输出目录存在
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        zip_filename = f"{plugin_name}-{plugin_config.current_version}.zip"
        zip_path = output_dir / zip_filename

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历插件目录中的所有文件和子目录
                for file_path in plugin_dir.rglob('*'):
                    if file_path.is_file():
                        # 计算在zip文件中的相对路径
                        arcname = file_path.relative_to(plugin_dir)
                        zipf.write(file_path, arcname)
                        logger.debug(f"添加文件: {arcname}")

            logger.info(f"插件打包成功: {zip_path}")
            return zip_path
        except Exception as e:
            logger.error(f"打包插件失败: {str(e)}")
            return None

    @contextmanager
    def temp_directory(self):
        """临时目录上下文管理器"""
        temp_dir = None
        try:
            temp_dir = Path(tempfile.mkdtemp())
            yield temp_dir
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"清理临时目录失败 {temp_dir}: {str(e)}")