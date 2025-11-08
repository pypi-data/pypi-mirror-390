from typing import Callable, Optional

from . import PluginManager
from .plugin_manager.models import VersionInfo, PluginConfig
from .task_progress_manager import AsyncTaskManager, NestedProgressCallback


class PluginBase:
    def __init__(self, plugin_name: str, plugin_manager: PluginManager):
        self.name = plugin_name
        self.plugin_manager = plugin_manager
        self._install_status = {}
        self._update_status = {}

    def install(self, progress_callback: Optional[Callable[[int, int, float], None]] = None):
        top_cb = NestedProgressCallback(
            parent_callback=progress_callback,
            start_percent=0,
            end_percent=100,
            parent_step="安装插件",
        )
        return self.plugin_manager.install_plugin(self.name, progress_callback=top_cb)

    def async_install(self) -> str:
        # 避免重复执行
        if self.name in self._install_status:
            status = self._install_status[self.name]
            if status['status'] == "installing":
                task_id = self._install_status['task_id']
                task_info = AsyncTaskManager().get_task_progress(task_id=task_id)
                if task_info:
                    if task_info.status not in ("finished", "failed", "timeout"):
                        return self._install_status['task_id']
        task_id = AsyncTaskManager().create_task(self.install)
        self._install_status[self.name] = {
            "task_id": task_id,
        }
        return task_id

    def async_progress(self, task_id: str):
        return AsyncTaskManager().get_task_progress(task_id=task_id)

    def uninstall(self):
        return self.plugin_manager.uninstall_plugin(self.name)

    def start(self, wait_for_ready: bool = True, timeout: int = 30, success_indicator=None):
        return self.plugin_manager.start_plugin(self.name, wait_for_ready, timeout, success_indicator=success_indicator)

    def stop(self):
        return self.plugin_manager.stop_plugin(self.name)

    def is_running(self):
        return self.plugin_manager.is_plugin_running(self.name)

    def is_installed(self):
        return self.plugin_manager.is_plugin_installed(self.name)

    def info(self):
        return self.plugin_manager.plugin_info(self.name)

    def version(self):
        info = self.info()
        if not info:
            return None
        return info.current_version

    def check_update(self):
        return self.plugin_manager.check_plugin_update(self.name)

    def package(self, plugin_dir: str, plugin_config: PluginConfig = None, version_note: Optional[str] = None):
        return self.plugin_manager.package_plugin(self.name, plugin_dir, plugin_config, version_note)

    def update(self,
               version_info: VersionInfo,
               progress_callback: Optional[Callable[[int, int, float], None]] = None):
        top_cb = NestedProgressCallback(
            parent_callback=progress_callback,
            start_percent=0,
            end_percent=100,
            parent_step="安装插件",
        )
        return self.plugin_manager.update_plugin(self.name, version_info, top_cb)

    def upgrade(self,
                progress_callback: Optional[Callable[[int, int, float], None]] = None):
        has_new_version, version_info = self.check_update()
        if not has_new_version:
            print("暂无可更新版本")
            return True
        return self.update(version_info, progress_callback=progress_callback)

    def async_upgrade(self) -> str:
        # 避免重复执行
        if self.name in self._update_status:
            status = self._update_status[self.name]
            if status['status'] == "installing":
                task_id = self._update_status['task_id']
                task_info = AsyncTaskManager().get_task_progress(task_id=task_id)
                if task_info:
                    if task_info.status not in ("finished", "failed", "timeout"):
                        return self._update_status['task_id']
        task_id = AsyncTaskManager().create_task(self.upgrade)
        self._update_status[self.name] = {
            "task_id": task_id,
        }
        return task_id

    def list(self):
        return self.plugin_manager.list_plugins()
