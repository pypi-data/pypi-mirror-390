
# 自定义异常类
class PluginManagerError(Exception):
    """插件管理器基础异常"""
    pass


class PluginNotFoundError(PluginManagerError):
    """插件未找到异常"""
    pass


class PluginInstallError(PluginManagerError):
    """插件安装异常"""
    pass


class PluginUpdateError(PluginManagerError):
    """插件更新异常"""
    pass


class PluginStartError(PluginManagerError):
    """插件启动异常"""
    pass


class NetworkError(PluginManagerError):
    """网络异常"""
    pass
