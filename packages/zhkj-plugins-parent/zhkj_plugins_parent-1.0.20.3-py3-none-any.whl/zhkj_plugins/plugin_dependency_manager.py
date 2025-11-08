# # zhkj_plugins/dependency_manager.py
#
# import logging
# from typing import Dict, List, Set, Optional, Any, Tuple
# from dataclasses import dataclass
# from collections import deque, defaultdict
# from enum import Enum
#
# logger = logging.getLogger("DependencyManager")
#
#
# class DependencyRelation(Enum):
#     """依赖关系类型"""
#     DEPENDS_ON = "depends_on"  # 依赖于
#     DEPENDED_BY = "depended_by"  # 被依赖
#     BOTH = "both"  # 双向依赖
#
#
# @dataclass
# class DependencyNode:
#     """依赖节点"""
#     name: str
#     version: str
#     is_service: bool
#     installed: bool
#     running: bool
#     dependencies: List[str]  # 依赖的插件列表
#     depended_by: List[str]  # 被哪些插件依赖
#     level: int = 0  # 在依赖树中的层级
#
#
# class DependencyManager:
#     """依赖管理器"""
#
#     def __init__(self):
#         self.dependency_graph: Dict[str, DependencyNode] = {}
#         self.reverse_dependency_graph: Dict[str, Set[str]] = defaultdict(set)
#
#     def build_dependency_graph(self, plugins: List[Any]) -> None:
#         """
#         构建依赖关系图
#         plugins: PluginConfig 列表
#         """
#         self.dependency_graph.clear()
#         self.reverse_dependency_graph.clear()
#
#         # 第一遍：创建节点
#         for plugin in plugins:
#             node = DependencyNode(
#                 name=plugin.name,
#                 version=plugin.current_version,
#                 is_service=plugin.is_service,
#                 installed=getattr(plugin, 'installed', False),
#                 running=getattr(plugin, 'running', False),
#                 dependencies=getattr(plugin, 'dependencies', []),
#                 depended_by=[]
#             )
#             self.dependency_graph[plugin.name] = node
#
#         # 第二遍：构建依赖关系
#         for plugin_name, node in self.dependency_graph.items():
#             for dep_name in node.dependencies:
#                 if dep_name in self.dependency_graph:
#                     self.dependency_graph[dep_name].depended_by.append(plugin_name)
#                     self.reverse_dependency_graph[dep_name].add(plugin_name)
#
#         # 第三遍：计算层级
#         self._calculate_dependency_levels()
#
#         logger.info(f"依赖关系图构建完成，共 {len(self.dependency_graph)} 个节点")
#
#     def _calculate_dependency_levels(self) -> None:
#         """计算每个节点在依赖树中的层级"""
#         # 找到根节点（没有被依赖的节点）
#         root_nodes = [name for name, node in self.dependency_graph.items()
#                       if not node.depended_by]
#
#         # 使用BFS计算层级
#         visited = set()
#         queue = deque()
#
#         for root in root_nodes:
#             self.dependency_graph[root].level = 0
#             queue.append(root)
#             visited.add(root)
#
#         while queue:
#             current_name = queue.popleft()
#             current_node = self.dependency_graph[current_name]
#
#             for dep_name in current_node.dependencies:
#                 if dep_name in self.dependency_graph and dep_name not in visited:
#                     dep_node = self.dependency_graph[dep_name]
#                     # 层级为父节点层级 + 1，取最大值（因为有多个父节点的情况）
#                     dep_node.level = max(dep_node.level, current_node.level + 1)
#                     queue.append(dep_name)
#                     visited.add(dep_name)
#
#         # 处理可能的循环依赖
#         unvisited = set(self.dependency_graph.keys()) - visited
#         for node_name in unvisited:
#             # 循环依赖中的节点，层级设为-1
#             self.dependency_graph[node_name].level = -1
#             logger.warning(f"检测到循环依赖中的节点: {node_name}")
#
#     def get_dependency_tree(self, plugin_name: str) -> Optional[Dict[str, Any]]:
#         """获取指定插件的完整依赖树"""
#         if plugin_name not in self.dependency_graph:
#             return None
#
#         def build_tree(current_name: str, visited: Set[str] = None) -> Dict[str, Any]:
#             if visited is None:
#                 visited = set()
#
#             if current_name in visited:
#                 return {"name": current_name, "circular": True}
#
#             visited.add(current_name)
#             node = self.dependency_graph[current_name]
#
#             tree = {
#                 "name": current_name,
#                 "version": node.version,
#                 "is_service": node.is_service,
#                 "installed": node.installed,
#                 "running": node.running,
#                 "level": node.level,
#                 "dependencies": []
#             }
#
#             for dep_name in node.dependencies:
#                 if dep_name in self.dependency_graph:
#                     dep_tree = build_tree(dep_name, visited.copy())
#                     tree["dependencies"].append(dep_tree)
#
#             return tree
#
#         return build_tree(plugin_name)
#
#     def get_reverse_dependency_tree(self, plugin_name: str) -> Optional[Dict[str, Any]]:
#         """获取指定插件的被依赖树（哪些插件依赖于此插件）"""
#         if plugin_name not in self.dependency_graph:
#             return None
#
#         def build_reverse_tree(current_name: str, visited: Set[str] = None) -> Dict[str, Any]:
#             if visited is None:
#                 visited = set()
#
#             if current_name in visited:
#                 return {"name": current_name, "circular": True}
#
#             visited.add(current_name)
#             node = self.dependency_graph[current_name]
#
#             tree = {
#                 "name": current_name,
#                 "version": node.version,
#                 "is_service": node.is_service,
#                 "installed": node.installed,
#                 "running": node.running,
#                 "level": node.level,
#                 "depended_by": []
#             }
#
#             for dep_by_name in node.depended_by:
#                 if dep_by_name in self.dependency_graph:
#                     dep_by_tree = build_reverse_tree(dep_by_name, visited.copy())
#                     tree["depended_by"].append(dep_by_tree)
#
#             return tree
#
#         return build_reverse_tree(plugin_name)
#
#     def get_safe_uninstall_candidates(self, plugin_name: str) -> Tuple[List[str], List[str]]:
#         """
#         获取可以安全卸载的插件候选列表
#         返回: (可以卸载的插件列表, 不能卸载的插件列表)
#         """
#         if plugin_name not in self.dependency_graph:
#             return [], []
#
#         # 使用BFS广度优先遍历依赖树
#         safe_to_remove = []
#         cannot_remove = []
#
#         # 从目标插件开始，按层级从高到低处理
#         target_level = self.dependency_graph[plugin_name].level
#
#         # 按层级分组
#         level_groups = defaultdict(list)
#         for name, node in self.dependency_graph.items():
#             if node.level >= 0:  # 排除循环依赖节点
#                 level_groups[node.level].append(name)
#
#         # 从最高层级开始处理
#         max_level = max(level_groups.keys()) if level_groups else 0
#
#         for level in range(max_level, target_level - 1, -1):
#             if level not in level_groups:
#                 continue
#
#             for current_name in level_groups[level]:
#                 node = self.dependency_graph[current_name]
#
#                 # 检查是否可以安全删除
#                 if self._can_safely_remove(current_name, safe_to_remove):
#                     safe_to_remove.append(current_name)
#                 else:
#                     cannot_remove.append(current_name)
#
#         # 确保目标插件在安全列表中（如果没有被其他插件依赖）
#         if plugin_name not in safe_to_remove and plugin_name not in cannot_remove:
#             if self._can_safely_remove(plugin_name, safe_to_remove):
#                 safe_to_remove.append(plugin_name)
#             else:
#                 cannot_remove.append(plugin_name)
#
#         return safe_to_remove, cannot_remove
#
#     def _can_safely_remove(self, plugin_name: str, already_removed: List[str]) -> bool:
#         """
#         检查插件是否可以安全删除
#         """
#         node = self.dependency_graph[plugin_name]
#
#         # 检查是否有其他插件依赖此插件（除了已经在删除列表中的）
#         remaining_dependents = [
#             dep_by for dep_by in node.depended_by
#             if dep_by not in already_removed
#         ]
#
#         return len(remaining_dependents) == 0
#
#     def get_install_order(self, plugin_name: str) -> List[str]:
#         """获取插件的安装顺序（依赖在前）"""
#         if plugin_name not in self.dependency_graph:
#             return []
#
#         install_order = []
#         visited = set()
#
#         def dfs(current_name: str):
#             if current_name in visited:
#                 return
#             visited.add(current_name)
#
#             node = self.dependency_graph[current_name]
#             for dep_name in node.dependencies:
#                 if dep_name in self.dependency_graph:
#                     dfs(dep_name)
#
#             install_order.append(current_name)
#
#         dfs(plugin_name)
#         return install_order
#
#     def get_start_order(self, plugin_name: str) -> List[str]:
#         """获取插件的启动顺序（依赖在前）"""
#         return self.get_install_order(plugin_name)
#
#     def get_stop_order(self, plugin_name: str) -> List[str]:
#         """获取插件的停止顺序（被依赖的在前）"""
#         if plugin_name not in self.dependency_graph:
#             return []
#
#         stop_order = []
#         visited = set()
#
#         def dfs(current_name: str):
#             if current_name in visited:
#                 return
#             visited.add(current_name)
#
#             # 先添加当前节点
#             stop_order.append(current_name)
#
#             # 然后处理依赖此插件的插件
#             node = self.dependency_graph[current_name]
#             for dep_by_name in node.depended_by:
#                 if dep_by_name in self.dependency_graph:
#                     dfs(dep_by_name)
#
#         dfs(plugin_name)
#         return stop_order
#
#     def find_circular_dependencies(self) -> List[List[str]]:
#         """查找所有循环依赖"""
#         cycles = []
#         visited = set()
#         recursion_stack = set()
#
#         def dfs(current_name: str, path: List[str]):
#             if current_name in recursion_stack:
#                 # 找到循环依赖
#                 cycle_start = path.index(current_name)
#                 cycle = path[cycle_start:]
#                 if cycle not in cycles:
#                     cycles.append(cycle)
#                 return
#
#             if current_name in visited:
#                 return
#
#             visited.add(current_name)
#             recursion_stack.add(current_name)
#             path.append(current_name)
#
#             node = self.dependency_graph.get(current_name)
#             if node:
#                 for dep_name in node.dependencies:
#                     if dep_name in self.dependency_graph:
#                         dfs(dep_name, path.copy())
#
#             recursion_stack.remove(current_name)
#             path.pop()
#
#         for plugin_name in self.dependency_graph:
#             if plugin_name not in visited:
#                 dfs(plugin_name, [])
#
#         return cycles
#
#     def get_dependency_impact(self, plugin_name: str) -> Dict[str, Any]:
#         """获取插件依赖影响分析"""
#         if plugin_name not in self.dependency_graph:
#             return {}
#
#         # 获取依赖树
#         dep_tree = self.get_dependency_tree(plugin_name)
#         # 获取被依赖树
#         reverse_tree = self.get_reverse_dependency_tree(plugin_name)
#
#         # 统计影响
#         total_dependencies = self._count_nodes(dep_tree) - 1  # 排除自身
#         total_depended_by = self._count_nodes(reverse_tree) - 1  # 排除自身
#
#         # 查找循环依赖
#         cycles = self.find_circular_dependencies()
#         involved_cycles = [cycle for cycle in cycles if plugin_name in cycle]
#
#         return {
#             "plugin": plugin_name,
#             "total_dependencies": total_dependencies,
#             "total_depended_by": total_depended_by,
#             "dependency_tree": dep_tree,
#             "reverse_dependency_tree": reverse_tree,
#             "involved_circular_dependencies": involved_cycles,
#             "install_order": self.get_install_order(plugin_name),
#             "safe_uninstall_candidates": self.get_safe_uninstall_candidates(plugin_name)[0]
#         }
#
#     def _count_nodes(self, tree: Dict[str, Any]) -> int:
#         """统计树中的节点数量"""
#         if not tree:
#             return 0
#
#         count = 1  # 当前节点
#         if "dependencies" in tree:
#             for dep in tree["dependencies"]:
#                 count += self._count_nodes(dep)
#         elif "depended_by" in tree:
#             for dep_by in tree["depended_by"]:
#                 count += self._count_nodes(dep_by)
#
#         return count
#
#     def print_dependency_tree(self, plugin_name: str) -> None:
#         """打印依赖树"""
#         tree = self.get_dependency_tree(plugin_name)
#         if not tree:
#             print(f"插件 {plugin_name} 不存在")
#             return
#
#         def print_tree(node: Dict[str, Any], level: int = 0):
#             indent = "  " * level
#             status = ""
#             if node.get('installed'):
#                 status += "✓"
#             else:
#                 status += "✗"
#             if node.get('running'):
#                 status += "▶"
#             else:
#                 status += "⏸"
#
#             if node.get('circular'):
#                 print(f"{indent}{status} {node['name']} (循环依赖)")
#             else:
#                 plugin_type = "服务" if node.get('is_service') else "应用"
#                 level_info = f"[L{node.get('level', 0)}]"
#                 print(f"{indent}{status} {node['name']} v{node.get('version', '?')} {level_info} [{plugin_type}]")
#
#             for dep in node.get('dependencies', []):
#                 print_tree(dep, level + 1)
#
#         print(f"\n插件 {plugin_name} 的依赖树:")
#         print_tree(tree)
#         print()
#
#     def print_reverse_dependency_tree(self, plugin_name: str) -> None:
#         """打印被依赖树"""
#         tree = self.get_reverse_dependency_tree(plugin_name)
#         if not tree:
#             print(f"插件 {plugin_name} 不存在")
#             return
#
#         def print_tree(node: Dict[str, Any], level: int = 0):
#             indent = "  " * level
#             status = ""
#             if node.get('installed'):
#                 status += "✓"
#             else:
#                 status += "✗"
#             if node.get('running'):
#                 status += "▶"
#             else:
#                 status += "⏸"
#
#             if node.get('circular'):
#                 print(f"{indent}{status} {node['name']} (循环依赖)")
#             else:
#                 plugin_type = "服务" if node.get('is_service') else "应用"
#                 level_info = f"[L{node.get('level', 0)}]"
#                 print(f"{indent}{status} {node['name']} v{node.get('version', '?')} {level_info} [{plugin_type}]")
#
#             for dep_by in node.get('depended_by', []):
#                 print_tree(dep_by, level + 1)
#
#         print(f"\n插件 {plugin_name} 的被依赖树:")
#         print_tree(tree)
#         print()
#
