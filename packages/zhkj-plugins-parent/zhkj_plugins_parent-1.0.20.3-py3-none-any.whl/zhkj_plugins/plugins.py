# import atexit
# import os
# import signal
# import sys
# import time
# import zipfile
# import subprocess
# import shutil
# import requests
# import psutil
# import socket
# import yaml
# import json
# import hashlib
# from pathlib import Path
# from typing import List, Dict, Optional, Set, Any, Callable, Tuple, Union
# from dataclasses import dataclass, asdict
# from datetime import datetime
# import threading
# from importlib.metadata import version as _version, PackageNotFoundError
# import logging
# from contextlib import contextmanager
# import tempfile
# 
# from zhkj_plugins.exceptions import *
# from zhkj_plugins.port_manager import PortManager
# from zhkj_plugins.process_manager import ProcessManager
# from zhkj_plugins.process_output_monitor import ProcessOutputMonitor
# from zhkj_plugins.remote_config import RemoteSettings
# from zhkj_plugins.wrap import singleton
# 
# # 配置日志
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger("PluginManager")
# 
# 
# # 版本信息数据类
# @dataclass
# class VersionInfo:
#     version: str
#     download_url: str
#     release_notes: str
#     release_date: str
#     file_size: int
#     md5_hash: str = ""
# 
#     def to_dict(self) -> Dict[str, Any]:
#         """转换为字典"""
#         return asdict(self)
# 
#     @classmethod
#     def from_dict(cls, data: Dict[str, Any]) -> 'VersionInfo':
#         """从字典创建实例"""
#         return cls(**data)
# 
# 
# # 插件配置数据类
# @dataclass
# class PluginConfig:
#     name: str
#     extract_folder: str
#     app_relative_path: str
#     is_service: bool = False  # 是否为服务类型插件
#     current_version: str = "1.0.0"  # 当前版本
# 
#     def to_dict(self) -> Dict[str, Any]:
#         """转换为字典"""
#         return asdict(self)
# 
#     @classmethod
#     def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfig':
#         """从字典创建实例"""
#         return cls(**data)
# 
# 
# @singleton
# class PluginManager:
#     def __init__(self, config: Dict[str, Any] = None, config_path: str = "config.yaml"):
#         """通过 YAML 配置文件初始化插件管理器"""
#         self.config_path = Path(config_path)
#         self.config = config if config is not None else self._load_yaml_config()
#         self.plugin_install_dir = Path(self.config.get('plugin_install_dir', 'plugins'))
#         self.auto_check_updates = self.config.get('auto_check_updates', True)
#         self.version_checks_url = self.config.get('version_checks_url', '')
#         self.settings_url = self.config.get('settings_url', '')
#         self.settings_update_interval = self.config.get('settings_update_interval', 600)
#         self.settings_update_timeout = self.config.get('settings_update_timeout', 10)
#         self.settings_plugins_version_key = self.config.get('settings_plugins_version_key', 'plugins_version')
# 
#         self.port_manager = PortManager()
#         self.version_cache_file = self.plugin_install_dir / "version_cache.json"
#         self.version_cache = self._load_version_cache()
#         self._version_checks_cache = None
#         self._version_checks_last_fetch = 0
#         self._lock = threading.RLock()  # 可重入锁，用于线程安全
# 
#         # 确保目录存在
#         self._ensure_dir(self.plugin_install_dir)
# 
#         # 加载插件配置
#         self.plugins = self._load_plugin_configs()
# 
#         # 启动自动更新检查（后台线程）
#         if self.auto_check_updates:
#             self._start_auto_update_check()
# 
#         # 初始化进程管理器
#         self.process_manager = ProcessManager()
#         self.process_manager.initialize()
# 
#         # 注册退出清理函数
#         atexit.register(self.cleanup)
# 
#         # 设置信号处理
#         signal.signal(signal.SIGINT, self._signal_handler)
#         signal.signal(signal.SIGTERM, self._signal_handler)
# 
#     def _signal_handler(self, signum, frame):
#         """信号处理函数"""
#         logger.info(f"接收到信号 {signum}，开始清理进程...")
#         self.cleanup()
#         sys.exit(0)
# 
#     def _load_yaml_config(self) -> Dict[str, Any]:
#         """加载并解析 YAML 配置文件"""
#         if not self.config_path.exists():
#             default_config = {
#                 'plugin_install_dir': 'plugins',
#                 'auto_check_updates': True,
#                 'version_checks_url': ''
#             }
#             self._save_config_to_file(default_config)
#             return default_config
# 
#         try:
#             with open(self.config_path, 'r', encoding='utf-8') as f:
#                 config = yaml.safe_load(f) or {}
#                 logger.info(f"成功加载配置文件: {self.config_path}")
#                 return config
#         except yaml.YAMLError as e:
#             logger.error(f"YAML 配置解析错误: {str(e)}")
#             raise PluginManagerError(f"YAML 配置解析错误: {str(e)}")
#         except Exception as e:
#             logger.error(f"加载配置文件失败: {str(e)}")
#             raise PluginManagerError(f"加载配置文件失败: {str(e)}")
# 
#     def _load_plugin_configs(self) -> List[PluginConfig]:
#         """从插件目录加载所有插件的配置"""
#         plugins = []
# 
#         if not self.plugin_install_dir.exists():
#             logger.warning(f"插件目录不存在: {self.plugin_install_dir}")
#             return plugins
# 
#         try:
#             for plugin_dir in self.plugin_install_dir.iterdir():
#                 if plugin_dir.is_dir() and not plugin_dir.name.startswith("_"):
#                     config_file = plugin_dir / "plugin.yaml"
#                     if config_file.exists():
#                         plugin_config = self._load_plugin_config_from_file(config_file)
#                         if plugin_config:
#                             plugins.append(plugin_config)
#                             logger.info(f"加载插件配置: {plugin_config.name}")
#         except Exception as e:
#             logger.error(f"扫描插件目录失败: {str(e)}")
# 
#         logger.info(f"共加载 {len(plugins)} 个插件配置")
#         return plugins
# 
#     def _load_plugin_config_from_file(self, config_path: Path) -> Optional[PluginConfig]:
#         """从文件加载插件配置"""
#         try:
#             with open(config_path, 'r', encoding='utf-8') as f:
#                 plugin_data = yaml.safe_load(f)
# 
#             if plugin_data and 'name' in plugin_data:
#                 plugin_config = PluginConfig(
#                     name=plugin_data['name'],
#                     extract_folder=plugin_data['extract_folder'],
#                     app_relative_path=plugin_data['app_relative_path'],
#                     is_service=plugin_data.get('is_service', False),
#                     current_version=plugin_data.get('current_version', '1.0.0')
#                 )
#                 return plugin_config
#             else:
#                 logger.warning(f"插件配置文件格式错误: {config_path}")
#         except Exception as e:
#             logger.error(f"加载插件配置文件失败 {config_path}: {str(e)}")
# 
#         return None
# 
#     def _save_plugin_config(self, plugin_config: PluginConfig, plugin_dir=None) -> bool:
#         """保存单个插件的配置到其目录下的 plugin.yaml 文件"""
#         if plugin_dir is None:
#             plugin_dir = self.plugin_install_dir / plugin_config.extract_folder
#         config_file = plugin_dir / "plugin.yaml"
# 
#         # 确保插件目录存在
#         if not self._ensure_dir(plugin_dir):
#             return False
# 
#         config_data = plugin_config.to_dict()
# 
#         try:
#             with open(config_file, 'w', encoding='utf-8') as f:
#                 yaml.dump(config_data, f, allow_unicode=True, indent=2)
#             logger.info(f"保存插件配置: {plugin_config.name} -> {config_file}")
#             return True
#         except Exception as e:
#             logger.error(f"保存插件配置失败 {plugin_config.name}: {str(e)}")
#             return False
# 
#     def _fetch_version_checks(self) -> Dict[str, Any]:
#         """从远程获取版本检查配置"""
#         if not self.version_checks_url:
#             if self.settings_url:
#                 try:
#                     remote_settings = RemoteSettings(
#                         self.settings_url,
#                         self.settings_update_interval,
#                         self.settings_update_timeout
#                     )
#                     return remote_settings.get_dict(self.settings_plugins_version_key)
#                 except Exception as e:
#                     logger.error(f"获取远程版本检查配置失败: {str(e)}")
#                     return {}
#             return {}
# 
#         # 检查缓存是否有效（5分钟缓存）
#         current_time = time.time()
#         if (self._version_checks_cache is not None and
#                 current_time - self._version_checks_last_fetch < 300):
#             return self._version_checks_cache
# 
#         try:
#             logger.info("正在获取远程版本检查配置...")
#             response = requests.get(self.version_checks_url, timeout=10)
#             response.raise_for_status()
#             version_checks = response.json()
# 
#             # 更新缓存
#             self._version_checks_cache = version_checks
#             self._version_checks_last_fetch = current_time
#             logger.info("远程版本检查配置获取成功")
#             return version_checks
#         except requests.RequestException as e:
#             logger.error(f"获取远程版本检查配置失败: {str(e)}")
#             raise NetworkError(f"网络请求失败: {str(e)}")
#         except Exception as e:
#             logger.error(f"处理版本检查配置失败: {str(e)}")
#             return {}
# 1
# 
#     def _load_version_cache(self) -> Dict[str, Any]:
#         """加载版本缓存"""
#         if not self.version_cache_file.exists():
#             return {}
# 
#         try:
#             with open(self.version_cache_file, 'r', encoding='utf-8') as f:
#                 cache = json.load(f)
#                 logger.info("成功加载版本缓存")
#                 return cache
#         except Exception as e:
#             logger.error(f"加载版本缓存失败: {str(e)}")
#             return {}
# 
#     def _save_version_cache(self) -> bool:
#         """保存版本缓存"""
#         try:
#             with open(self.version_cache_file, 'w', encoding='utf-8') as f:
#                 json.dump(self.version_cache, f, indent=2, ensure_ascii=False)
#             logger.info("版本缓存保存成功")
#             return True
#         except Exception as e:
#             logger.error(f"保存版本缓存失败: {str(e)}")
#             return False
# 
#     def _ensure_dir(self, dir_path: Path) -> bool:
#         """确保目录存在"""
#         try:
#             if not dir_path.exists():
#                 dir_path.mkdir(parents=True, exist_ok=True)
#                 logger.info(f"创建目录: {dir_path}")
#             return True
#         except Exception as e:
#             logger.error(f"创建目录失败 {dir_path}: {str(e)}")
#             return False
# 
#     def _get_free_port(self) -> int:
#         """获取随机可用端口"""
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.bind(('', 0))
#                 port = s.getsockname()[1]
#                 logger.debug(f"获取到空闲端口: {port}")
#                 return port
#         except Exception as e:
#             logger.error(f"获取空闲端口失败: {str(e)}")
#             # 返回一个默认端口范围
#             return 8080  # 实际应用中应该使用更智能的备用策略
# 
#     def _start_auto_update_check(self) -> None:
#         """启动自动更新检查后台线程"""
# 
#         def check_updates_background():
#             while True:
#                 try:
#                     # 每6小时检查一次更新
#                     time.sleep(6 * 3600)
#                     self.check_all_updates(background=True)
#                 except Exception as e:
#                     logger.error(f"后台更新检查失败: {str(e)}")
#                     time.sleep(300)  # 出错后等待5分钟再重试
# 
#         thread = threading.Thread(target=check_updates_background, daemon=True)
#         thread.start()
#         logger.info("自动更新检查线程已启动")
# 
#     def _save_config_to_file(self, config: Dict[str, Any] = None) -> bool:
#         """保存配置到文件"""
#         if config is None:
#             config = self.config
# 
#         try:
#             with open(self.config_path, 'w', encoding='utf-8') as f:
#                 yaml.dump(config, f, allow_unicode=True, indent=2)
#             logger.info(f"配置文件已保存: {self.config_path}")
#             return True
#         except Exception as e:
#             logger.error(f"保存配置文件失败: {str(e)}")
#             return False
# 
#     @contextmanager
#     def _temp_directory(self) -> Path:
#         """临时目录上下文管理器"""
#         temp_dir = None
#         try:
#             temp_dir = Path(tempfile.mkdtemp())
#             yield temp_dir
#         finally:
#             if temp_dir and temp_dir.exists():
#                 try:
#                     shutil.rmtree(temp_dir)
#                 except Exception as e:
#                     logger.warning(f"清理临时目录失败 {temp_dir}: {str(e)}")
# 
#     def download_with_progress(
#             self,
#             url: str,
#             save_path: str,
#             progress_callback: Optional[Callable[[int, int, float], None]] = None,
#             chunk_size: int = 8192,
#             timeout: int = 30,
#             max_retries: int = 3
#     ) -> bool:
#         """
#         带进度回调的文件下载函数
#         """
#         save_path_obj = Path(save_path)
# 
#         for attempt in range(max_retries):
#             try:
#                 # 确保保存目录存在
#                 self._ensure_dir(save_path_obj.parent)
# 
#                 # 发送 HEAD 请求获取文件总大小
#                 head_response = requests.head(url, timeout=timeout)
#                 head_response.raise_for_status()
#                 total_size = int(head_response.headers.get('Content-Length', 0))
# 
#                 # 发送 GET 请求开始下载（流式传输）
#                 with requests.get(url, stream=True, timeout=timeout) as response:
#                     response.raise_for_status()
# 
#                     if total_size == 0:
#                         total_size = int(response.headers.get('Content-Length', 0))
# 
#                     downloaded_size = 0
#                     start_time = time.time()
#                     last_time = start_time
#                     last_downloaded = 0
# 
#                     with open(save_path, 'wb') as f:
#                         for chunk in response.iter_content(chunk_size=chunk_size):
#                             if chunk:
#                                 f.write(chunk)
#                                 downloaded_size += len(chunk)
# 
#                                 current_time = time.time()
#                                 time_diff = current_time - last_time
#                                 if time_diff > 0.1:
#                                     speed = (downloaded_size - last_downloaded) / (time_diff * 1024)
#                                     last_time = current_time
#                                     last_downloaded = downloaded_size
# 
#                                     if progress_callback:
#                                         try:
#                                             progress_callback(downloaded_size, total_size, speed)
#                                         except Exception as e:
#                                             logger.warning(f"进度回调执行失败: {str(e)}")
# 
#                     if progress_callback:
#                         total_time = time.time() - start_time
#                         avg_speed = (downloaded_size / (total_time * 1024)) if total_time > 0 else 0
#                         try:
#                             progress_callback(downloaded_size, total_size, avg_speed)
#                         except Exception as e:
#                             logger.warning(f"最终进度回调执行失败: {str(e)}")
# 
#                 logger.info(f"下载完成: {save_path}")
#                 return True
# 
#             except requests.RequestException as e:
#                 logger.warning(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
#                 if attempt == max_retries - 1:
#                     logger.error(f"下载失败，已达到最大重试次数: {url}")
#                     if save_path_obj.exists():
#                         save_path_obj.unlink()  # 删除可能不完整的文件
#                     return False
#                 time.sleep(2 ** attempt)  # 指数退避
#             except Exception as e:
#                 logger.error(f"下载过程中发生未知错误: {str(e)}")
#                 if save_path_obj.exists():
#                     save_path_obj.unlink()
#                 return False
# 
#         return False
# 
#     def _extract_archive(self, archive_path: Path, extract_dir: Path) -> bool:
#         """解压归档文件"""
#         try:
#             if archive_path.suffix.lower() == '.zip':
#                 with zipfile.ZipFile(archive_path, 'r') as zip_ref:
#                     # 首先验证zip文件
#                     bad_file = zip_ref.testzip()
#                     if bad_file:
#                         raise zipfile.BadZipFile(f"ZIP文件损坏: {bad_file}")
# 
#                     zip_ref.extractall(extract_dir)
#                 logger.info(f"ZIP解压完成: {extract_dir}")
#                 return True
#             else:
#                 logger.error(f"不支持的压缩格式: {archive_path.suffix}")
#                 return False
#         except zipfile.BadZipFile as e:
#             logger.error(f"ZIP文件损坏: {str(e)}")
#             return False
#         except Exception as e:
#             logger.error(f"解压失败: {str(e)}")
#             return False
# 
#     def _calculate_file_md5(self, file_path: Path) -> str:
#         """计算文件的MD5哈希值"""
#         try:
#             hash_md5 = hashlib.md5()
#             with open(file_path, "rb") as f:
#                 for chunk in iter(lambda: f.read(4096), b""):
#                     hash_md5.update(chunk)
#             return hash_md5.hexdigest()
#         except Exception as e:
#             logger.error(f"计算文件MD5失败 {file_path}: {str(e)}")
#             return ""
# 
#     def _compare_versions(self, version1: str, version2: str) -> int:
#         """比较两个版本号"""
#         try:
#             v1_parts = list(map(int, version1.split('.')))
#             v2_parts = list(map(int, version2.split('.')))
# 
#             # 补齐版本号长度
#             max_len = max(len(v1_parts), len(v2_parts))
#             v1_parts.extend([0] * (max_len - len(v1_parts)))
#             v2_parts.extend([0] * (max_len - len(v2_parts)))
# 
#             for i in range(max_len):
#                 if v1_parts[i] > v2_parts[i]:
#                     return 1
#                 elif v1_parts[i] < v2_parts[i]:
#                     return -1
#             return 0
#         except Exception as e:
#             logger.error(f"版本号比较失败 '{version1}' vs '{version2}': {str(e)}")
#             return 0  # 出错时视为相等
# 
#     def is_plugin_installed(self, plugin_name: str) -> bool:
#         """检查插件是否已安装"""
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             return False
# 
#         plugin_dir = self.plugin_install_dir / plugin.extract_folder
#         return plugin_dir.exists() and (plugin_dir / "plugin.yaml").exists()
# 
#     def check_plugin_update(self, plugin_name: str) -> Tuple[bool, Optional[VersionInfo]]:
#         """检查插件是否有更新"""
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             logger.warning(f"插件不存在: {plugin_name}")
#             return False, None
# 
#         # 从远程获取版本检查信息
#         remote_info = self._get_version_check_info(plugin_name)
# 
#         if not remote_info:
#             logger.info(f"插件 {plugin_name} 未配置版本检查URL")
#             return False, None
# 
#         try:
#             remote_version = remote_info.get('version', '')
#             remote_url = remote_info.get('download_url', '')
#             release_notes = remote_info.get('release_notes', '')
#             release_date = remote_info.get('release_date', '')
#             file_size = remote_info.get('file_size', 0)
#             md5_hash = remote_info.get('md5_hash', '')
# 
#             if not remote_version or not remote_url:
#                 logger.warning(f"远程版本信息不完整: {plugin_name}")
#                 return False, None
# 
#             # 比较版本
#             current_version = plugin.current_version
#             version_comparison = self._compare_versions(remote_version, current_version)
# 
#             if version_comparison > 0:
#                 # 有新版本
#                 version_info = VersionInfo(
#                     version=remote_version,
#                     download_url=remote_url,
#                     release_notes=release_notes,
#                     release_date=release_date,
#                     file_size=file_size,
#                     md5_hash=md5_hash
#                 )
#                 logger.info(f"发现插件 {plugin_name} 新版本: {current_version} -> {remote_version}")
#                 return True, version_info
#             else:
#                 logger.info(f"插件 {plugin_name} 已是最新版本: {current_version}")
#                 return False, None
# 
#         except Exception as e:
#             logger.error(f"检查插件 {plugin_name} 更新失败: {str(e)}")
#             return False, None
# 
#     def check_all_updates(self, background: bool = False) -> Dict[str, VersionInfo]:
#         """检查所有插件的更新"""
#         updates = {}
# 
#         if not background:
#             logger.info("开始检查所有插件更新...")
# 
#         for plugin in self.plugins:
#             try:
#                 has_update, version_info = self.check_plugin_update(plugin.name)
#                 if has_update and version_info:
#                     updates[plugin.name] = version_info
#                     if not background:
#                         logger.info(
#                             f"🔔 插件 {plugin.name} 有新版本: {plugin.current_version} -> {version_info.version}")
#             except Exception as e:
#                 logger.error(f"检查插件 {plugin.name} 更新时出错: {str(e)}")
# 
#         # 更新缓存
#         self.version_cache['last_update_check'] = datetime.now().isoformat()
#         self.version_cache['available_updates'] = {
#             plugin_name: {
#                 'version': info.version,
#                 'release_date': info.release_date
#             } for plugin_name, info in updates.items()
#         }
#         self._save_version_cache()
# 
#         if not background:
#             if updates:
#                 logger.info(f"发现 {len(updates)} 个插件有更新")
#             else:
#                 logger.info("所有插件都是最新版本")
# 
#         return updates
# 
#     def update_plugin(
#             self,
#             plugin_name: str,
#             version_info: VersionInfo,
#             progress_callback: Optional[Callable[[int, int, float], None]] = None
#     ) -> bool:
#         """更新指定插件到新版本"""
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             logger.error(f"插件不存在: {plugin_name}")
#             return False
# 
#         logger.info(f"开始更新插件 {plugin_name}: {plugin.current_version} -> {version_info.version}")
# 
#         # 停止运行中的插件
#         if self.is_plugin_running(plugin_name):
#             logger.info(f"停止运行中的插件: {plugin_name}")
#             if not self.stop_plugin(plugin_name):
#                 logger.error("停止插件失败，无法更新")
#                 return False
# 
#         # 使用临时目录进行更新操作
#         with self._temp_directory() as temp_dir:
#             # 下载新版本
#             temp_archive = temp_dir / f"{plugin.name}_update.zip"
# 
#             if not self.download_with_progress(version_info.download_url, str(temp_archive), progress_callback):
#                 logger.error(f"下载新版本失败: {plugin_name}")
#                 return False
# 
#             # 验证文件完整性（如果提供了MD5）
#             if version_info.md5_hash:
#                 downloaded_md5 = self._calculate_file_md5(temp_archive)
#                 if downloaded_md5 != version_info.md5_hash.lower():
#                     logger.error(f"文件校验失败: MD5不匹配")
#                     return False
# 
#             # 在临时目录中解压验证
#             extract_temp_dir = temp_dir / "extracted"
#             if not self._extract_archive(temp_archive, extract_temp_dir):
#                 logger.error(f"解压新版本失败: {plugin_name}")
#                 return False
# 
#             # 备份旧版本
#             plugin_dir = self.plugin_install_dir / plugin.extract_folder
#             backup_success = False
#             backup_dir = None
# 
#             if plugin_dir.exists():
#                 try:
#                     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#                     backup_dir = self.plugin_install_dir / f"{plugin.extract_folder}_backup_{timestamp}"
#                     shutil.copytree(plugin_dir, backup_dir)
#                     backup_success = True
#                     logger.info(f"已创建备份: {backup_dir}")
#                 except Exception as e:
#                     logger.warning(f"备份失败: {str(e)}")
# 
#             try:
#                 # 删除旧版本
#                 if plugin_dir.exists():
#                     shutil.rmtree(plugin_dir)
# 
#                 # 移动新版本到目标位置
#                 shutil.move(str(extract_temp_dir), str(plugin_dir))
# 
#                 # 更新插件配置中的版本号
#                 plugin.current_version = version_info.version
#                 if not self._save_plugin_config(plugin):
#                     logger.warning(f"保存插件配置失败，但文件已更新: {plugin_name}")
# 
#                 # 删除备份
#                 if backup_success and backup_dir and backup_dir.exists():
#                     shutil.rmtree(backup_dir)
# 
#                 logger.info(f"插件 {plugin_name} 更新完成: {version_info.version}")
#                 return True
# 
#             except Exception as e:
#                 logger.error(f"更新过程出错: {str(e)}")
#                 # 恢复备份
#                 if backup_success and backup_dir and backup_dir.exists():
#                     try:
#                         if plugin_dir.exists():
#                             shutil.rmtree(plugin_dir)
#                         shutil.move(str(backup_dir), str(plugin_dir))
#                         logger.info(f"已从备份恢复插件: {plugin_name}")
#                     except Exception as restore_error:
#                         logger.error(f"恢复备份失败: {str(restore_error)}")
#                 return False
# 
#     def auto_update_plugins(self) -> Dict[str, bool]:
#         """自动更新所有有更新的插件"""
#         updates = self.check_all_updates(background=True)
#         results = {}
# 
#         for plugin_name, version_info in updates.items():
#             try:
#                 plugin = self.plugin_info(plugin_name)
#                 version_check_info = self._get_version_check_info(plugin_name)
#                 auto_update = version_check_info.get('auto_update', False)
# 
#                 if plugin and auto_update:
#                     logger.info(f"自动更新插件: {plugin_name}")
#                     success = self.update_plugin(plugin_name, version_info)
#                     results[plugin_name] = success
#                 else:
#                     logger.info(f"插件 {plugin_name} 有更新但未启用自动更新")
#                     results[plugin_name] = False
#             except Exception as e:
#                 logger.error(f"自动更新插件 {plugin_name} 失败: {str(e)}")
#                 results[plugin_name] = False
# 
#         return results
# 
#     def install_plugin(self, plugin_name: str, url: str = None,
#                        progress_callback: Optional[Callable[[int, int, float], None]] = None) -> bool:
#         """安装指定插件"""
#         # 首先检查插件是否已安装
#         if self.is_plugin_installed(plugin_name):
#             logger.info(f"插件已安装: {plugin_name}")
#             return True
# 
#         # 如果没有提供URL，尝试从远程版本检查配置中获取
#         if not url:
#             version_check_info = self._get_version_check_info(plugin_name)
#             url = version_check_info.get('download_url')
#             if not url:
#                 logger.error(f"无法获取插件 {plugin_name} 的下载地址")
#                 return False
# 
#         logger.info(f"开始安装插件: {plugin_name}")
# 
#         # 使用临时目录进行安装
#         with self._temp_directory() as temp_dir:
#             temp_archive = temp_dir / f"{plugin_name}.zip"
# 
#             # 下载插件
#             if not self.download_with_progress(url, str(temp_archive), progress_callback=progress_callback):
#                 logger.error(f"下载插件失败: {plugin_name}")
#                 return False
# 
#             # 解压到临时目录
#             extract_temp_dir = temp_dir / "extracted"
#             if not self._extract_archive(temp_archive, extract_temp_dir):
#                 logger.error(f"解压插件失败: {plugin_name}")
#                 return False
# 
#             # 在解压目录中查找 plugin.yaml
#             plugin_config_path = self._find_plugin_config(extract_temp_dir)
#             if not plugin_config_path:
#                 logger.error(f"在压缩包中未找到 plugin.yaml 文件: {plugin_name}")
#                 return False
# 
#             # 读取插件配置
#             plugin_config = self._load_plugin_config_from_file(plugin_config_path)
#             if not plugin_config:
#                 logger.error(f"无法读取插件配置文件: {plugin_name}")
#                 return False
# 
#             # 验证插件名称是否匹配
#             if plugin_config.name != plugin_name:
#                 logger.error(f"插件名称不匹配: 配置中为 {plugin_config.name}, 期望为 {plugin_name}")
#                 return False
# 
#             # 移动文件到最终目录
#             plugin_dir = self.plugin_install_dir / plugin_config.extract_folder
#             if plugin_dir.exists():
#                 logger.info(f"目标目录已存在，先删除: {plugin_dir}")
#                 try:
#                     shutil.rmtree(plugin_dir, ignore_errors=True)
#                 except Exception as e:
#                     logger.error(f"删除现有目录失败: {str(e)}")
#                     return False
# 
#             try:
#                 # 移动整个解压内容到插件目录
#                 shutil.move(str(extract_temp_dir), str(plugin_dir))
#                 logger.info(f"插件文件已移动到: {plugin_dir}")
#             except Exception as e:
#                 logger.error(f"移动插件文件失败: {str(e)}")
#                 return False
# 
#             # 将插件配置添加到管理器
#             with self._lock:
#                 if not any(p.name == plugin_config.name for p in self.plugins):
#                     self.plugins.append(plugin_config)
#                     logger.info(f"添加插件配置到管理器: {plugin_config.name}")
# 
#             # 确保插件配置已保存到插件目录
#             if not self._save_plugin_config(plugin_config):
#                 logger.warning(f"保存插件配置失败，但插件文件已安装: {plugin_name}")
# 
#             logger.info(f"插件安装完成: {plugin_name}")
#             return True
# 
#     def _find_plugin_config(self, directory: Path) -> Optional[Path]:
#         """在目录中递归查找 plugin.yaml 文件"""
#         try:
#             for file_path in directory.rglob("plugin.yaml"):
#                 if file_path.is_file():
#                     return file_path
#             return None
#         except Exception as e:
#             logger.error(f"查找插件配置文件失败 {directory}: {str(e)}")
#             return None
# 
#     def install_all_plugins(self,
#                             progress_callback: Optional[Callable[[int, int, float], None]] = None) -> Dict[str, bool]:
#         """安装所有插件 - 从远程版本检查配置中获取下载地址"""
#         logger.info("开始安装所有插件...")
#         results = {}
# 
#         for plugin in self.plugins:
#             try:
#                 # 从远程版本检查配置中获取下载地址
#                 version_check_info = self._get_version_check_info(plugin.name)
#                 url = version_check_info.get('download_url')
#                 if url:
#                     success = self.install_plugin(plugin.name, url, progress_callback=progress_callback)
#                     results[plugin.name] = success
#                 else:
#                     logger.warning(f"插件 {plugin.name} 未配置下载地址，跳过安装")
#                     results[plugin.name] = False
#             except Exception as e:
#                 logger.error(f"安装插件 {plugin.name} 失败: {str(e)}")
#                 results[plugin.name] = False
# 
#         logger.info("所有插件安装操作完成")
#         return results
# 
#     def start_plugin(self, plugin_name: str, wait_for_ready: bool = True, timeout: int = 30,
#                      success_indicator=None) -> bool:
#         """启动插件"""
#         if self.is_plugin_running(plugin_name):
#             logger.info(f"插件已在运行: {plugin_name}")
#             return True
# 
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             logger.error(f"插件不存在: {plugin_name}")
#             return False
# 
#         plugin_dir = self.plugin_install_dir / plugin.extract_folder
#         app_path = plugin_dir / plugin.app_relative_path
# 
#         if not plugin_dir.exists():
#             logger.error(f"插件未安装: {plugin_name}，无法启动")
#             return False
# 
#         if not app_path.exists():
#             logger.error(f"插件程序不存在: {app_path}")
#             return False
# 
#         try:
#             cmd = [str(app_path)]
#             port = None
#             if plugin.is_service:
#                 port = self._get_free_port()
#                 cmd.extend([f"--port={port}"])  # 传递端口参数
#                 logger.info(f"为服务插件 [{plugin_name}] 分配端口: {port}")
# 
#             logger.info(f"启动插件: {plugin_name} ({app_path})")
# 
#             # 启动进程
#             if os.name == 'nt':
#                 process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
#                                            stderr=subprocess.PIPE, shell=True)
#             elif os.name == 'posix':
#                 process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
#                                            stderr=subprocess.PIPE)
# 
#             # 注册到进程管理器
#             self.process_manager.register_process(plugin_name, process)
# 
#             if plugin.is_service and port:
#                 self.port_manager.set_port(plugin_name, port)
# 
#             # 如果需要等待就绪
#             if wait_for_ready:
#                 if plugin.is_service:
#                     # 服务插件：等待端口就绪
#                     success = self._wait_for_port_ready(plugin_name, port, process, timeout)
#                 else:
#                     # 非服务插件：区分一次性任务和常驻进程
#                     success = self._wait_for_non_service_ready(plugin_name, process, timeout, success_indicator)
# 
#                 if success:
#                     logger.info(f"插件 {plugin_name} 启动成功")
#                     return True
#                 else:
#                     logger.error(f"插件 {plugin_name} 启动超时或失败")
#                     # 启动失败，清理资源
#                     self.stop_plugin(plugin_name)
#                     return False
#             else:
#                 # 不等待就绪，直接返回
#                 logger.info(f"插件 {plugin_name} 已启动（未等待就绪）")
#                 return True
# 
#         except Exception as e:
#             logger.error(f"启动插件失败: {str(e)}")
#             if plugin.is_service:
#                 self.port_manager.clear_port(plugin_name)
#             return False
# 
#     def _wait_for_non_service_ready(self, plugin_name: str, process: subprocess.Popen, timeout: int,
#                                     success_indicator=None) -> bool:
#         """等待非服务插件就绪"""
#         logger.info(f"等待插件 {plugin_name} 就绪...")
# 
#         start_time = time.time()
# 
#         while timeout == -1 or time.time() - start_time < timeout:
#             # 检查进程状态
#             return_code = process.poll()
# 
#             # 如果进程已经退出
#             if return_code is not None:
#                 if return_code == 0:
#                     # 正常退出，视为成功
#                     logger.info(f"插件 {plugin_name} 已执行完成（退出码: {return_code}）")
#                     return True
#                 else:
#                     # 异常退出，视为失败
#                     logger.error(f"插件 {plugin_name} 执行失败（退出码: {return_code}）")
#                     return False
# 
#             # 检查进程输出中是否包含成功标志
#             if success_indicator:
#                 monitor = ProcessOutputMonitor(process, plugin_name, success_indicator)
#                 if monitor.wait_for_success():
#                     return True
# 
#             # 检查其他启动成功的条件
#             if self.is_plugin_running(plugin_name):  # 自定义的检查函数
#                 logger.info(f"插件 {plugin_name} 启动成功")
#                 return True
# 
#             time.sleep(0.5)  # 每隔0.5秒检查一次
# 
#         # 超时处理
#         return_code = process.poll()
#         if return_code is not None:
#             # 进程在超时前已退出
#             if return_code == 0:
#                 logger.info(f"插件 {plugin_name} 已执行完成（超时前退出码: {return_code}）")
#                 return True
#             else:
#                 logger.error(f"插件 {plugin_name} 执行失败（超时前退出码: {return_code}）")
#                 return False
#         else:
#             # 进程仍在运行，但等待超时
#             logger.warning(f"等待插件 {plugin_name} 就绪超时，但进程仍在运行")
#             return True
# 
#     def _wait_for_port_ready(self, plugin_name: str, port: int, process: subprocess.Popen, timeout: int) -> bool:
#         """等待服务插件的端口就绪"""
#         logger.info(f"等待服务插件 {plugin_name} 端口 {port} 就绪...")
# 
#         start_time = time.time()
# 
#         while timeout == -1 or time.time() - start_time < timeout:
#             try:
#                 # 尝试连接端口
#                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#                     sock.settimeout(1)
#                     result = sock.connect_ex(('localhost', port))
#                     if result == 0:
#                         logger.info(f"服务插件 {plugin_name} 端口 {port} 已就绪")
#                         return True
#             except Exception:
#                 pass
# 
#             # 检查进程是否还在运行
#             return_code = process.poll()
#             if return_code is not None:
#                 # 进程已退出
#                 logger.error(f"服务插件进程已退出: {plugin_name} (退出码: {return_code})")
#                 return return_code == 0  # 如果正常退出，视为成功
# 
#             time.sleep(0.5)  # 每隔0.5秒检查一次
# 
#         # 超时处理
#         return_code = process.poll()
#         if return_code is not None:
#             # 进程在超时前已退出
#             logger.info(f"服务插件 {plugin_name} 在超时前退出 (退出码: {return_code})")
#             return return_code == 0
#         else:
#             logger.error(f"等待端口就绪超时: {plugin_name} (端口: {port})")
#             return False
# 
#     def _get_running_processes(self) -> Set[str]:
#         """获取运行中的进程"""
#         processes = set()
#         for proc in psutil.process_iter(['exe', 'cmdline']):
#             try:
#                 if proc.info['exe']:
#                     processes.add(str(Path(proc.info['exe']).resolve()))
#                 elif proc.info['cmdline']:
#                     cmd_path = Path(proc.info['cmdline'][0]).resolve()
#                     if cmd_path.exists():
#                         processes.add(str(cmd_path))
#             except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#                 continue
#         return processes
# 
#     def is_plugin_running(self, plugin_name: str) -> bool:
#         """检查插件是否在运行"""
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             logger.warning(f"插件不存在: {plugin_name}")
#             return False
# 
#         plugin_dir = self.plugin_install_dir / plugin.extract_folder
#         app_path = plugin_dir / plugin.app_relative_path
#         if not app_path.exists():
#             return False
# 
#         app_abs_path = str(app_path.resolve())
#         return app_abs_path in self._get_running_processes()
# 
#     def get_service_port(self, plugin_name: str) -> Optional[int]:
#         """获取服务插件端口"""
#         plugin = self.plugin_info(plugin_name)
#         if not plugin or not plugin.is_service:
#             logger.warning(f"不是服务类型插件: {plugin_name}")
#             return None
#         return self.port_manager.get_port(plugin_name)
# 
#     def stop_plugin(self, plugin_name: str) -> bool:
#         """停止插件"""
#         # 先从进程管理器中获取进程
#         process = None
#         for name, proc in self.process_manager.processes.items():
#             if name == plugin_name:
#                 process = proc
#                 break
# 
#         if process:
#             try:
#                 # 使用进程管理器的方法终止进程
#                 self.process_manager.terminate_process(plugin_name, process)
#                 self.process_manager.unregister_process(plugin_name)
# 
#                 plugin = self.plugin_info(plugin_name)
#                 if plugin and plugin.is_service:
#                     self.port_manager.clear_port(plugin_name)
# 
#                 logger.info(f"成功停止插件: {plugin_name}")
#                 return True
#             except Exception as e:
#                 logger.error(f"停止插件失败: {str(e)}")
#                 return False
#         else:
#             # 回退到原来的进程查找方式
#             return self._stop_plugin_fallback(plugin_name)
# 
#     def _stop_plugin_fallback(self, plugin_name: str) -> bool:
#         """回退的进程停止方法"""
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             return False
# 
#         app_abs_path = str((self.plugin_install_dir / plugin.extract_folder / plugin.app_relative_path).resolve())
# 
#         try:
#             terminated = False
#             for proc in psutil.process_iter(['pid', 'exe', 'cmdline']):
#                 try:
#                     # 多种方式匹配进程
#                     if (proc.info['exe'] and str(Path(proc.info['exe']).resolve()) == app_abs_path) or \
#                             (proc.info['cmdline'] and app_abs_path in ' '.join(proc.info['cmdline'])):
#                         pid = proc.pid
#                         self.process_manager.stop_process_tree(pid)
#                         logger.info(f"已终止插件进程: {plugin_name} (PID: {pid})")
#                         terminated = True
# 
#                 except (psutil.NoSuchProcess, psutil.AccessDenied):
#                     continue
# 
#             if plugin.is_service:
#                 self.port_manager.clear_port(plugin_name)
# 
#             if terminated:
#                 logger.info(f"成功停止插件: {plugin_name}")
#             else:
#                 logger.warning(f"未找到插件进程: {plugin_name}")
# 
#             return True
#         except Exception as e:
#             logger.error(f"停止插件失败: {str(e)}")
#             return False
# 
#     def cleanup(self) -> None:
#         """清理所有资源"""
#         logger.info("开始清理插件管理器资源...")
# 
#         # 停止所有运行中的插件
#         running_plugins = self.process_manager.get_running_plugins()
#         for plugin_name in running_plugins:
#             logger.info(f"停止插件: {plugin_name}")
#             self.stop_plugin(plugin_name)
# 
#         # 清理进程管理器
#         self.process_manager.cleanup_all()
# 
#         # 清理端口管理器
#         self.port_manager.clear_all()
# 
#         logger.info("插件管理器资源清理完成")
# 
#     def __del__(self):
#         """析构函数，确保资源清理"""
#         try:
#             self.cleanup()
#         except Exception as e:
#             logger.error(f"析构函数清理失败: {str(e)}")
# 
#     def uninstall_plugin(self, plugin_name: str) -> bool:
#         """卸载插件"""
#         if self.is_plugin_running(plugin_name):
#             logger.info(f"插件正在运行，先停止插件: {plugin_name}")
#             if not self.stop_plugin(plugin_name):
#                 logger.error("停止插件失败，无法卸载")
#                 return False
# 
#         plugin = self.plugin_info(plugin_name)
#         if not plugin:
#             logger.error(f"插件不存在: {plugin_name}")
#             return False
# 
#         plugin_dir = self.plugin_install_dir / plugin.extract_folder
#         if not plugin_dir.exists():
#             logger.info(f"插件未安装: {plugin_name}")
#             return True
# 
#         try:
#             shutil.rmtree(plugin_dir)
#             logger.info(f"插件卸载完成: {plugin_name}")
# 
#             # 从插件列表中移除
#             with self._lock:
#                 self.plugins = [p for p in self.plugins if p.name != plugin_name]
# 
#             return True
#         except Exception as e:
#             logger.error(f"卸载插件失败: {str(e)}")
#             return False
# 
#     def plugin_info(self, plugin_name: str) -> Optional[PluginConfig]:
#         """获取插件信息"""
#         with self._lock:
#             return next((p for p in self.plugins if p.name == plugin_name), None)
# 
#     def list_plugins(self) -> List[Dict[str, Any]]:
#         """列出所有插件状态"""
#         plugins_info = []
# 
#         for plugin in self.plugins:
#             plugin_dir = self.plugin_install_dir / plugin.extract_folder
#             install_status = self.is_plugin_installed(plugin.name)
#             run_status = self.is_plugin_running(plugin.name)
#             port = self.port_manager.get_port(plugin.name) or "-"
#             plugin_type = "服务" if plugin.is_service else "应用"
# 
#             # 从远程获取自动更新设置
#             version_check_info = self._get_version_check_info(plugin.name)
#             auto_update = version_check_info.get('auto_update', False)
# 
#             plugin_info = {
#                 'name': plugin.name,
#                 'version': plugin.current_version,
#                 'type': plugin_type,
#                 'install_status': "已安装" if install_status else "未安装",
#                 'run_status': "运行中" if run_status else "未运行",
#                 'auto_update': "是" if auto_update else "否",
#                 'port': str(port),
#                 'path': str(plugin_dir)
#             }
#             plugins_info.append(plugin_info)
# 
#         return plugins_info
# 
#     def print_plugin_list(self) -> None:
#         """打印插件列表"""
#         plugins_info = self.list_plugins()
# 
#         print("\n插件列表:")
#         print("-" * 120)
#         print(
#             f"{'名称':<15} {'版本':<10} {'类型':<8} {'安装状态':<10} {'运行状态':<10} {'自动更新':<8} {'端口':<6} {'安装路径':<40}")
#         print("-" * 120)
#         for info in plugins_info:
#             print(
#                 f"{info['name']:<15} {info['version']:<10} {info['type']:<8} {info['install_status']:<10} "
#                 f"{info['run_status']:<10} {info['auto_update']:<8} {info['port']:<6} {info['path']:<40}"
#             )
#         print("-" * 120 + "\n")
# 
#     def package_plugin(self, plugin_name: str, plugin_dir: str, version: str = None, is_service: bool=False) -> Optional[Dict[str, Any]]:
#         """打包插件为zip文件"""
#         plugin_path = Path(plugin_dir)
# 
#         # 检测插件实际路径是否存在
#         if not plugin_path.exists():
#             logger.error(f"插件目录不存在: {plugin_dir}")
#             return None
# 
#         package_output_dir = Path(
#             self.config.get('package_output_dir', 'packages/' + plugin_name if plugin_name else "packages"))
#         if not self._ensure_dir(package_output_dir):
#             return None
# 
#         # 读取plugin.yaml
#         plugin_config_path = package_output_dir / "plugin.yaml"
#         if not plugin_config_path.exists():
#             logger.error(f"plugin.yaml 不存在于 {package_output_dir}")
#             return None
# 
#         plugin_config = self._load_plugin_config_from_file(plugin_config_path)
#         if not plugin_config:
#             return None
# 
#         if not plugin_name:
#             plugin_name = plugin_config.name
#             if not plugin_name:
#                 logger.error("plugin.yaml 中未找到插件名称")
#                 return None
# 
#         # 如果没有version就读取pyproject.toml的版本
#         if version is None:
#             try:
#                 version = _version(plugin_name)
#             except PackageNotFoundError:
#                 logger.warning(f"无法从pyproject.toml读取版本号，使用默认版本")
#                 version = "1.0.0"
# 
#         # 更新plugin.yaml中的版本号
#         plugin_config.current_version = version
#         plugin_config.is_service = is_service
#         if not self._save_plugin_config(plugin_config, plugin_path):
#             logger.warning(f"更新plugin.yaml失败，但继续打包")
# 
#         zip_filename = f"{plugin_name}-{version}.zip"
#         zip_path = package_output_dir / zip_filename
# 
#         # 检查zip文件是否已存在，如果存在则创建备份
#         if zip_path.exists():
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             backup_filename = f"{plugin_name}-{version}-backup-{timestamp}.zip"
#             backup_path = package_output_dir / backup_filename
# 
#             try:
#                 shutil.copy2(zip_path, backup_path)
#                 logger.info(f"已存在的zip文件已备份为: {backup_filename}")
#             except Exception as e:
#                 logger.warning(f"备份已存在的zip文件失败: {str(e)}")
# 
#         try:
#             with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#                 # 遍历插件目录中的所有文件和子目录
#                 for file_path in plugin_path.rglob('*'):
#                     if file_path.is_file():
#                         # 计算在zip文件中的相对路径
#                         arcname = file_path.relative_to(plugin_path)
#                         zipf.write(file_path, arcname)
#                         logger.debug(f"添加文件: {arcname}")
# 
#             logger.info(f"插件打包成功: {zip_path}")
#         except Exception as e:
#             logger.error(f"打包插件失败: {str(e)}")
#             return None
# 
#         # 计算文件哈希值
#         md5_hash = self._calculate_file_md5(zip_path)
#         file_size = zip_path.stat().st_size
# 
#         # 构建version_check内容
#         download_base_url = self.config.get('download_base_url', '')
#         if not download_base_url:
#             logger.warning("download_base_url未配置")
# 
#         download_url = f"{download_base_url}/{zip_filename}" if download_base_url else f"./packages/{zip_filename}"
# 
#         version_check_info = {
#             "version": version,
#             "download_url": download_url,
#             "release_notes": f"Release {version}",
#             "release_date": datetime.now().strftime("%Y-%m-%d"),
#             "file_size": file_size,
#             "md5_hash": md5_hash
#         }
# 
#         # 保存版本检查配置到 <插件名>-<版本号>.json 文件
#         version_check_filename = f"{plugin_name}-{version}.json"
#         version_check_path = package_output_dir / version_check_filename
# 
#         try:
#             with open(version_check_path, 'w', encoding='utf-8') as f:
#                 json.dump(version_check_info, f, indent=2, ensure_ascii=False)
#             logger.info(f"版本检查配置已保存到: {version_check_path}")
#         except Exception as e:
#             logger.error(f"保存版本检查配置文件失败: {str(e)}")
# 
#         logger.info("\n" + "=" * 50)
#         logger.info("版本检查配置内容 (可添加到远程版本检查配置中):")
#         logger.info("=" * 50)
#         logger.info(json.dumps(version_check_info, indent=2, ensure_ascii=False))
#         logger.info("=" * 50)
# 
#         return {
#             "plugin_name": plugin_name,
#             "version": version,
#             "zip_path": str(zip_path),
#             "download_url": download_url,
#             "file_size": file_size,
#             "md5_hash": md5_hash
#         }
