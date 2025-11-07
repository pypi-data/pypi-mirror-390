import os
import subprocess
import sys
import threading
import time
import socket
from pathlib import Path
from typing import Optional, List
import logging

from .models import PluginConfig
from .plugin_utils import get_service_port_by_process, get_plugin_info
from ..utils import get_free_port, get_running_processes
from zhkj_plugins.plugin_manager.process_manager import ProcessManager
from zhkj_plugins.plugin_manager.port_manager import PortManager

logger = logging.getLogger("PluginManager.Runtime")


class PluginRuntimeManager:
    def __init__(self, plugin_install_dir: Path, config_manager):
        self.plugin_install_dir = plugin_install_dir
        self.config_manager = config_manager

        # 初始化进程和端口管理器
        self.process_manager = ProcessManager()
        self.process_manager.initialize(plugin_install_dir)
        self.port_manager = PortManager()

    def start_plugin(self, plugin: PluginConfig, wait_for_ready: bool = True,
                     timeout: int = 30, success_indicator=None, output_encoding="utf-8") -> bool:
        """启动插件"""
        if self.is_plugin_running(plugin):
            logger.info(f"插件已在运行: {plugin.name}")
            return True

        plugin_dir = self.plugin_install_dir / plugin.extract_folder
        app_path = plugin_dir / plugin.app_relative_path

        if not plugin_dir.exists():
            logger.error(f"插件未安装: {plugin.name}，无法启动")
            return False

        if not app_path.exists():
            logger.error(f"插件程序不存在: {app_path}")
            return False

        try:
            cmd = [str(app_path)]
            port = None
            if plugin.plugin_type == "service":
                port = get_free_port()
                cmd.extend([f"--port={port}"])  # 传递端口参数
                logger.info(f"为服务插件 [{plugin.name}] 分配端口: {port}")

            logger.info(f"启动插件: {plugin.name} ({app_path})")

            process = self.start_plugin_with_safe_logging(plugin, cmd, output_encoding)

            # 注册到进程管理器
            self.process_manager.register_process(plugin.name, process)

            if plugin.plugin_type == "service" and port:
                self.port_manager.set_port(plugin.name, port)

            # 如果需要等待就绪
            if wait_for_ready:
                if plugin.plugin_type == "service":
                    # 服务插件：等待端口就绪
                    success = self._wait_for_port_ready(plugin, port, process, timeout)
                else:
                    # 非服务插件：区分一次性任务和常驻进程
                    success = self._wait_for_non_service_ready(plugin, process, timeout,
                                                               success_indicator)

                if success:
                    logger.info(f"插件 {plugin.name} 启动成功")
                    return True
                else:
                    logger.error(f"插件 {plugin.name} 启动超时或失败")
                    # 启动失败，清理资源
                    self.stop_plugin(plugin)
                    return False
            else:
                # 不等待就绪，直接返回
                logger.info(f"插件 {plugin.name} 已启动（未等待就绪）")
                return True

        except Exception as e:
            logger.error(f"启动插件失败: {str(e)}")
            if plugin.plugin_type == "service":
                self.port_manager.clear_port(plugin.name)
            return False

    def make_stream_non_blocking(self, stream):
        """
        跨平台设置流为非阻塞模式
        - 类 Unix 系统：使用 fcntl
        - Windows 系统：使用 msvcrt
        """
        if not stream:
            return stream

        try:
            fd = stream.fileno()
            if sys.platform == 'win32':
                # Windows 平台：使用 msvcrt 设置非阻塞
                import msvcrt
                msvcrt.setmode(fd, os.O_BINARY | os.O_NONBLOCK)  # 二进制模式 + 非阻塞
            else:
                # 类 Unix 平台：使用 fcntl
                import fcntl
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        except Exception as e:
            logger.warning(f"设置非阻塞模式失败: {e}")
        return stream

    def log_stream(self, process: subprocess.Popen,
                   stream,
                   stream_type: str,
                   plugin_name: str,
                   output_encoding: str = "utf-8",
                   max_buffer_size: int = 1024 * 1024):  # 1MB缓冲区上限
        """
        安全读取并记录子进程输出流

        :param process: 子进程对象，用于检查进程是否存活
        :param stream: 要读取的流（stdout/stderr）
        :param stream_type: 流类型标识（STDOUT/STDERR）
        :param plugin_name: 插件名称，用于日志标识
        :param output_encoding: 输出编码
        :param max_buffer_size: 最大缓冲区大小，防止内存溢出
        """
        buffer = b""
        log_method = logger.debug if stream_type == "STDOUT" else logger.error
        stream = self.make_stream_non_blocking(stream)

        try:
            while True:
                # 检查进程是否已结束且流已关闭
                if process.poll() is not None:
                    # 读取剩余数据
                    data = stream.read()
                    if data:
                        buffer += data
                    break

                # 非阻塞读取（避免线程无限阻塞）
                try:
                    data = stream.read(4096)  # 每次读取4KB
                except (BlockingIOError, OSError):
                    # 非阻塞模式下无数据时抛出的异常
                    time.sleep(0.01)  # 短暂休眠，减少CPU占用
                    continue

                if not data:
                    time.sleep(0.01)
                    continue

                # 累积数据到缓冲区
                buffer += data
                # 检查缓冲区大小，防止内存溢出
                if len(buffer) > max_buffer_size:
                    logger.warning(f"插件[{plugin_name}] {stream_type}缓冲区超过上限，强制刷新")
                    lines = buffer.split(b'\n')
                    # 最后一个元素可能是不完整的行，留到下次处理
                    for line in lines[:-1]:
                        self._log_line(line, log_method, output_encoding, plugin_name, stream_type)
                    buffer = lines[-1] if lines[-1] else b""

                # 处理完整的行
                if b'\n' in buffer:
                    lines = buffer.split(b'\n')
                    # 最后一个元素可能是不完整的行，留到下次处理
                    for line in lines[:-1]:
                        self._log_line(line, log_method, output_encoding, plugin_name, stream_type)
                    buffer = lines[-1] if lines[-1] else b""

            # 处理剩余数据（进程结束后）
            if buffer:
                self._log_line(buffer, log_method, output_encoding, plugin_name, stream_type)

        except Exception as e:
            logger.error(f"插件[{plugin_name}] {stream_type}日志处理出错: {e}")
        finally:
            try:
                stream.close()
            except Exception:
                pass

    def _log_line(self, line_bytes: bytes,
                  log_method,
                  encoding: str,
                  plugin_name: str,
                  stream_type: str):
        """处理单行日志的解码和输出"""
        if not line_bytes:
            return
        try:
            line = line_bytes.decode(encoding).rstrip('\r\n')  # 移除换行符
            if line:  # 跳过空行
                log_method(f"插件[{plugin_name}] [{stream_type}] {line}")
        except UnicodeDecodeError:
            # 解码失败时使用十六进制显示
            log_method(f"插件[{plugin_name}] [{stream_type}] 无法解码的字节: {line_bytes.hex()}")
        except Exception as e:
            logger.error(f"插件[{plugin_name}] 日志行处理失败: {e}")

    def start_plugin_with_safe_logging(self, plugin, cmd: list, output_encoding: str = "utf-8") -> Optional[
        subprocess.Popen]:
        """
        启动插件并安全处理输出日志

        :param plugin: 插件配置对象
        :param cmd: 启动命令列表
        :param output_encoding: 输出编码
        :return: 子进程对象，失败时返回None
        """
        try:
            # 使用PIPE捕获输出，但通过安全的日志线程处理
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True if sys.platform == 'win32' else False,
                bufsize=1024,  # 适度缓冲区大小
                close_fds=False if sys.platform == 'win32' else True  # 关闭不必要的文件描述符
            )

            # 启动日志处理线程，使用守护线程确保主进程退出时能自动结束
            stdout_thread = threading.Thread(
                target=self.log_stream,
                args=(process, process.stdout, "STDOUT", plugin.name, output_encoding),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self.log_stream,
                args=(process, process.stderr, "STDERR", plugin.name, output_encoding),
                daemon=True
            )

            stdout_thread.start()
            stderr_thread.start()

            # 记录线程信息，便于后续监控（可选）
            process.stdout_thread = stdout_thread
            process.stderr_thread = stderr_thread

            logger.info(f"插件[{plugin.name}] 启动成功，PID: {process.pid}")
            return process

        except Exception as e:
            logger.error(f"插件[{plugin.name}] 启动失败: {e}")
            return None

    def _wait_for_non_service_ready(self, plugin: PluginConfig, process: subprocess.Popen,
                                    timeout: int,
                                    success_indicator=None) -> bool:
        """等待非服务插件就绪"""
        logger.info(f"等待插件 {plugin.name} 就绪...")

        start_time = time.time()

        while timeout == -1 or time.time() - start_time < timeout:
            # 检查进程状态
            return_code = process.poll()

            # 如果进程已经退出
            if return_code is not None:
                if return_code == 0:
                    # 正常退出，视为成功
                    logger.info(f"插件 {plugin.name} 已执行完成（退出码: {return_code}）")
                    return True
                else:
                    # 异常退出，视为失败
                    logger.error(f"插件 {plugin.name} 执行失败（退出码: {return_code}）")
                    return False
            else:
                if self.is_plugin_running(plugin):
                    logger.info(f"插件 {plugin.name} 启动成功")
                    time.sleep(5)
                    return True

            logger.info("每隔0.5秒检查一次...")
            time.sleep(0.5)  # 每隔0.5秒检查一次

            # 检查其他启动成功的条件
            if self.is_plugin_running(plugin):
                logger.info(f"插件 {plugin.name} 启动成功")
                time.sleep(5)
                return True

            time.sleep(0.5)  # 每隔0.5秒检查一次

        # 超时处理
        return_code = process.poll()
        if return_code is not None:
            # 进程在超时前已退出
            if return_code == 0:
                logger.info(f"插件 {plugin.name} 已执行完成（超时前退出码: {return_code}）")
                return True
            else:
                logger.error(f"插件 {plugin.name} 执行失败（超时前退出码: {return_code}）")
                return False
        else:
            # 进程仍在运行，但等待超时
            logger.warning(f"等待插件 {plugin.name} 就绪超时，但进程仍在运行")
            return True

    def _wait_for_port_ready(self, plugin: PluginConfig, port: int, process: subprocess.Popen, timeout: int) -> bool:
        """等待服务插件的端口就绪"""
        logger.info(f"等待服务插件 {plugin.name} 端口 {port} 就绪...")

        start_time = time.time()

        while timeout == -1 or time.time() - start_time < timeout:
            try:
                # 尝试连接端口
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:
                        logger.info(f"服务插件 {plugin.name} 端口 {port} 已就绪")
                        return True
            except Exception:
                pass

            # 检查进程是否还在运行
            return_code = process.poll()
            if return_code is not None:
                # 进程已退出
                logger.error(f"服务插件进程已退出: {plugin.name} (退出码: {return_code})")
                return return_code == 0  # 如果正常退出，视为成功

            time.sleep(0.5)  # 每隔0.5秒检查一次

        # 超时处理
        return_code = process.poll()
        if return_code is not None:
            # 进程在超时前已退出
            logger.info(f"服务插件 {plugin.name} 在超时前退出 (退出码: {return_code})")
            return return_code == 0
        else:
            logger.error(f"等待端口就绪超时: {plugin.name} (端口: {port})")
            return False

    def is_plugin_running(self, plugin: PluginConfig) -> bool:
        """检查插件是否在运行"""
        plugin_dir = self.plugin_install_dir / plugin.extract_folder
        app_path = plugin_dir / plugin.app_relative_path
        if not app_path.exists():
            return False

        app_abs_path = str(app_path.resolve())
        exists = app_abs_path in get_running_processes()
        if plugin.plugin_type == "service":
            port = self.get_service_port(plugin)
            if port:
                self.port_manager.set_port(plugin.name, port=port)
        return exists

    def get_service_port(self, plugin: PluginConfig) -> Optional[int]:
        """获取服务插件端口"""
        if not plugin.plugin_type == "service":
            logger.warning(f"不是服务类型插件: {plugin.name}")
            return None
        port = self.port_manager.get_port(plugin.name)
        if port is None:
            return get_service_port_by_process(self.plugin_install_dir, plugin)
        return port

    def stop_plugin(self, plugin: PluginConfig) -> bool:
        """停止插件"""
        # 先从进程管理器中获取进程
        process = None
        for name, proc in self.process_manager.processes.items():
            if name == plugin.name:
                process = proc
                break

        if process:
            try:
                # 使用进程管理器的方法终止进程
                self.process_manager.terminate_process(plugin, process)
                self.process_manager.unregister_process(plugin.name)

                if self.port_manager.get_port(plugin.name):
                    self.port_manager.clear_port(plugin.name)

                logger.info(f"成功停止插件: {plugin.name}")
                return True
            except Exception as e:
                logger.error(f"停止插件失败: {str(e)}")
                return False
        else:
            # 回退到原来的进程查找方式
            return self._stop_plugin_fallback(plugin)

    def _stop_plugin_fallback(self, plugin: PluginConfig) -> bool:
        """回退的进程停止方法"""
        import psutil
        app_abs_path = str((self.plugin_install_dir / plugin.extract_folder / plugin.app_relative_path).resolve())

        try:
            terminated = False
            for proc in psutil.process_iter(['pid', 'exe', 'cmdline']):
                try:
                    # 多种方式匹配进程
                    if (proc.info['exe'] and str(Path(proc.info['exe']).resolve()) == app_abs_path) or \
                            (proc.info['cmdline'] and app_abs_path in ' '.join(proc.info['cmdline'])):
                        pid = proc.pid
                        self.process_manager.stop_process_tree(pid)
                        logger.info(f"已终止插件进程: {plugin.name} (PID: {pid})")
                        terminated = True

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if plugin.plugin_type == "service":
                self.port_manager.clear_port(plugin.name)

            if terminated:
                logger.info(f"成功停止插件: {plugin.name}")
            else:
                logger.warning(f"未找到插件进程: {plugin.name}")

            return True
        except Exception as e:
            logger.error(f"停止插件失败: {str(e)}")
            return False

    def cleanup(self, plugins: List[PluginConfig]) -> None:
        """清理所有资源"""
        logger.info("开始清理插件管理器资源...")

        # 停止所有运行中的插件
        for plugin in plugins:
            logger.info(f"停止插件: {plugin.name}")
            self.process_manager.terminate_process(plugin)

        # 清理进程管理器
        self.process_manager.cleanup_all(plugins)

        # 清理端口管理器
        self.port_manager.clear_all()

        logger.info("插件管理器资源清理完成")
