import os
import subprocess
import sys
import threading
import time
import socket
from pathlib import Path
from typing import List, Optional, Callable, Any
import logging

from .models import PluginConfig
from ..utils import get_free_port, get_running_processes
from zhkj_plugins.plugin_manager.process_manager import ProcessManager
from zhkj_plugins.plugin_manager.port_manager import PortManager
from zhkj_plugins.plugin_manager.process_output_monitor import ProcessOutputMonitor

logger = logging.getLogger("PluginManager.Runtime")


class PluginRuntimeManager:
    def __init__(self, plugin_install_dir: Path, config_manager):
        self.plugin_install_dir = plugin_install_dir
        self.config_manager = config_manager

        # 初始化进程和端口管理器
        self.process_manager = ProcessManager()
        self.process_manager.initialize()
        self.port_manager = PortManager()

    def start_plugin(self, plugin_name: str, plugins: List[PluginConfig], wait_for_ready: bool = True,
                     timeout: int = 30, success_indicator=None, output_encoding="utf-8") -> bool:
        """启动插件"""
        if self.is_plugin_running(plugin_name, plugins):
            logger.info(f"插件已在运行: {plugin_name}")
            return True

        plugin = self._get_plugin_info(plugin_name, plugins)
        if not plugin:
            logger.error(f"插件不存在: {plugin_name}")
            return False

        plugin_dir = self.plugin_install_dir / plugin.extract_folder
        app_path = plugin_dir / plugin.app_relative_path

        if not plugin_dir.exists():
            logger.error(f"插件未安装: {plugin_name}，无法启动")
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
                logger.info(f"为服务插件 [{plugin_name}] 分配端口: {port}")

            logger.info(f"启动插件: {plugin_name} ({app_path})")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True if sys.platform == 'win32' else False,
            )

            # 实时读取并记录 stdout 和 stderr（手动指定编码解码）
            def log_stream(stream, stream_type: str):
                for line_bytes in iter(stream.readline, b""):  # 明确读取字节
                    if line_bytes:
                        try:
                            line = line_bytes.decode(output_encoding).strip()  # 使用传入的编码
                            logging["debug" if stream_type == "STDOUT" else "error"](f"[{stream_type}] {line}")
                        except:
                            pass
                stream.close()

            # 用线程分别处理 stdout 和 stderr，避免阻塞
            stdout_thread = threading.Thread(target=log_stream, args=(process.stdout, "STDOUT"))
            stderr_thread = threading.Thread(target=log_stream, args=(process.stderr, "STDERR"))

            stdout_thread.start()
            stderr_thread.start()

            # 注册到进程管理器
            self.process_manager.register_process(plugin_name, process)

            if plugin.plugin_type == "service" and port:
                self.port_manager.set_port(plugin_name, port)

            # 如果需要等待就绪
            if wait_for_ready:
                if plugin.plugin_type == "service":
                    # 服务插件：等待端口就绪
                    success = self._wait_for_port_ready(plugin_name, port, process, timeout)
                else:
                    # 非服务插件：区分一次性任务和常驻进程
                    success = self._wait_for_non_service_ready(plugin_name, plugins, process, timeout,
                                                               success_indicator)

                if success:
                    logger.info(f"插件 {plugin_name} 启动成功")
                    return True
                else:
                    logger.error(f"插件 {plugin_name} 启动超时或失败")
                    # 启动失败，清理资源
                    self.stop_plugin(plugin_name, plugins)
                    return False
            else:
                # 不等待就绪，直接返回
                logger.info(f"插件 {plugin_name} 已启动（未等待就绪）")
                return True

        except Exception as e:
            logger.error(f"启动插件失败: {str(e)}")
            if plugin.plugin_type == "service":
                self.port_manager.clear_port(plugin_name)
            return False

    def _wait_for_non_service_ready(self, plugin_name: str, plugins: List[PluginConfig], process: subprocess.Popen,
                                    timeout: int,
                                    success_indicator=None) -> bool:
        """等待非服务插件就绪"""
        logger.info(f"等待插件 {plugin_name} 就绪...")

        start_time = time.time()

        while timeout == -1 or time.time() - start_time < timeout:
            # 检查进程状态
            return_code = process.poll()

            # 如果进程已经退出
            if return_code is not None:
                if return_code == 0:
                    # 正常退出，视为成功
                    logger.info(f"插件 {plugin_name} 已执行完成（退出码: {return_code}）")
                    return True
                else:
                    # 异常退出，视为失败
                    logger.error(f"插件 {plugin_name} 执行失败（退出码: {return_code}）")
                    return False
            else:
                if self.is_plugin_running(plugin_name, plugins):
                    logger.info(f"插件 {plugin_name} 启动成功")
                    time.sleep(5)
                    return True

            logger.info("每隔0.5秒检查一次...")
            time.sleep(0.5)  # 每隔0.5秒检查一次

            # # 检查进程输出中是否包含成功标志
            # if success_indicator:
            #     monitor = ProcessOutputMonitor(process, plugin_name, success_indicator)
            #     if monitor.wait_for_success():
            #         return True

            # 检查其他启动成功的条件
            if self.is_plugin_running(plugin_name, plugins):
                logger.info(f"插件 {plugin_name} 启动成功")
                time.sleep(5)
                return True

            time.sleep(0.5)  # 每隔0.5秒检查一次

        # 超时处理
        return_code = process.poll()
        if return_code is not None:
            # 进程在超时前已退出
            if return_code == 0:
                logger.info(f"插件 {plugin_name} 已执行完成（超时前退出码: {return_code}）")
                return True
            else:
                logger.error(f"插件 {plugin_name} 执行失败（超时前退出码: {return_code}）")
                return False
        else:
            # 进程仍在运行，但等待超时
            logger.warning(f"等待插件 {plugin_name} 就绪超时，但进程仍在运行")
            return True

    def _wait_for_port_ready(self, plugin_name: str, port: int, process: subprocess.Popen, timeout: int) -> bool:
        """等待服务插件的端口就绪"""
        logger.info(f"等待服务插件 {plugin_name} 端口 {port} 就绪...")

        start_time = time.time()

        while timeout == -1 or time.time() - start_time < timeout:
            try:
                # 尝试连接端口
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:
                        logger.info(f"服务插件 {plugin_name} 端口 {port} 已就绪")
                        return True
            except Exception:
                pass

            # 检查进程是否还在运行
            return_code = process.poll()
            if return_code is not None:
                # 进程已退出
                logger.error(f"服务插件进程已退出: {plugin_name} (退出码: {return_code})")
                return return_code == 0  # 如果正常退出，视为成功

            time.sleep(0.5)  # 每隔0.5秒检查一次

        # 超时处理
        return_code = process.poll()
        if return_code is not None:
            # 进程在超时前已退出
            logger.info(f"服务插件 {plugin_name} 在超时前退出 (退出码: {return_code})")
            return return_code == 0
        else:
            logger.error(f"等待端口就绪超时: {plugin_name} (端口: {port})")
            return False

    def is_plugin_running(self, plugin_name: str, plugins: List[PluginConfig]) -> bool:
        """检查插件是否在运行"""
        plugin = self._get_plugin_info(plugin_name, plugins)
        if not plugin:
            logger.warning(f"插件不存在: {plugin_name}")
            return False

        plugin_dir = self.plugin_install_dir / plugin.extract_folder
        app_path = plugin_dir / plugin.app_relative_path
        if not app_path.exists():
            return False

        app_abs_path = str(app_path.resolve())
        return app_abs_path in get_running_processes()

    def get_service_port(self, plugin_name: str, plugins: List[PluginConfig]) -> Optional[int]:
        """获取服务插件端口"""
        plugin = self._get_plugin_info(plugin_name, plugins)
        if not plugin or not plugin.plugin_type == "service":
            logger.warning(f"不是服务类型插件: {plugin_name}")
            return None
        return self.port_manager.get_port(plugin_name)

    def stop_plugin(self, plugin_name: str, plugins: List[PluginConfig]) -> bool:
        """停止插件"""
        # 先从进程管理器中获取进程
        process = None
        for name, proc in self.process_manager.processes.items():
            if name == plugin_name:
                process = proc
                break

        if process:
            try:
                # 使用进程管理器的方法终止进程
                self.process_manager.terminate_process(plugin_name, process)
                self.process_manager.unregister_process(plugin_name)

                plugin = self._get_plugin_info(plugin_name, plugins)
                if plugin and plugin.plugin_type == "service":
                    self.port_manager.clear_port(plugin_name)

                logger.info(f"成功停止插件: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"停止插件失败: {str(e)}")
                return False
        else:
            # 回退到原来的进程查找方式
            return self._stop_plugin_fallback(plugin_name, plugins)

    def _stop_plugin_fallback(self, plugin_name: str, plugins: List[PluginConfig]) -> bool:
        """回退的进程停止方法"""
        import psutil
        plugin = self._get_plugin_info(plugin_name, plugins)
        if not plugin:
            return False

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
                        logger.info(f"已终止插件进程: {plugin_name} (PID: {pid})")
                        terminated = True

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if plugin.plugin_type == "service":
                self.port_manager.clear_port(plugin_name)

            if terminated:
                logger.info(f"成功停止插件: {plugin_name}")
            else:
                logger.warning(f"未找到插件进程: {plugin_name}")

            return True
        except Exception as e:
            logger.error(f"停止插件失败: {str(e)}")
            return False

    def cleanup(self) -> None:
        """清理所有资源"""
        logger.info("开始清理插件管理器资源...")

        # 停止所有运行中的插件
        running_plugins = self.process_manager.get_running_plugins()
        for plugin_name in running_plugins:
            logger.info(f"停止插件: {plugin_name}")
            # 这里需要插件列表，但在清理时可能不可用
            # 直接使用进程管理器停止
            self.process_manager.terminate_process(plugin_name, None)

        # 清理进程管理器
        self.process_manager.cleanup_all()

        # 清理端口管理器
        self.port_manager.clear_all()

        logger.info("插件管理器资源清理完成")

    def _get_plugin_info(self, plugin_name: str, plugins: List[PluginConfig]) -> Optional[PluginConfig]:
        """获取插件信息"""
        if plugins is None:
            return None
        return next((p for p in plugins if p.name == plugin_name), None)
