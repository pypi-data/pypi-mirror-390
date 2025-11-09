import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class DocumentationGenerator:
    """为适配的bundle生成Harmony文档的工具类"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.docs_dir = base_path / "harmony_docs"
        self.docs_dir.mkdir(exist_ok=True)
        
    def generate_bundle_documentation(self, module_name: str) -> bool:
        """
        为指定模块生成Harmony适配文档
        
        Args:
            module_name: 模块名称
            
        Returns:
            bool: 文档生成是否成功
        """
        module_path = self.base_path / module_name
        if not module_path.exists():
            print(f"❌ 模块不存在: {module_name}")
            return False
            
        try:
            # 收集Harmony相关文件和代码
            harmony_files = self._find_harmony_files(module_path)
            harmony_code_stats = self._analyze_harmony_code(module_path, harmony_files)
            
            # 生成文档内容
            doc_content = self._generate_documentation_content(
                module_name, module_path, harmony_code_stats
            )
            
            # 保存文档
            doc_path = self.docs_dir / f"{module_name}_harmony_adaptation.md"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
                
            print(f"✅ 已生成文档: {doc_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成文档失败 {module_name}: {e}")
            return False
    
    def _find_harmony_files(self, module_path: Path) -> List[Dict[str, any]]:
        """查找模块中的Harmony相关文件"""
        harmony_files = []
        
        # 查找harmony目录
        harmony_dir = module_path / "harmony"
        if harmony_dir.exists():
            for file_path in harmony_dir.rglob("*"):
                if file_path.is_file():
                    harmony_files.append({
                        'type': 'harmony_dir',
                        'path': file_path.relative_to(module_path),
                        'full_path': file_path,
                        'size': file_path.stat().st_size
                    })
        
        # 查找package.json中的Harmony依赖
        package_json_path = module_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                harmony_deps = self._extract_harmony_dependencies(package_data)
                if harmony_deps:
                    harmony_files.append({
                        'type': 'package_json',
                        'path': Path("package.json"),
                        'full_path': package_json_path,
                        'dependencies': harmony_deps
                    })
            except Exception as e:
                print(f"⚠️  读取package.json失败: {e}")
        
        # 查找babel.config.js中的Harmony配置
        babel_config_path = module_path / "babel.config.js"
        if babel_config_path.exists():
            try:
                with open(babel_config_path, 'r', encoding='utf-8') as f:
                    babel_content = f.read()
                    
                harmony_plugins = self._extract_harmony_plugins(babel_content)
                if harmony_plugins:
                    harmony_files.append({
                        'type': 'babel_config',
                        'path': Path("babel.config.js"),
                        'full_path': babel_config_path,
                        'plugins': harmony_plugins
                    })
            except Exception as e:
                print(f"⚠️  读取babel.config.js失败: {e}")
        
        return harmony_files
    
    def _extract_harmony_dependencies(self, package_data: dict) -> List[str]:
        """从package.json中提取Harmony相关依赖"""
        harmony_deps = []
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        
        # 常见的Harmony相关依赖
        harmony_keywords = [
            'react-native',
            '@kds/',
            '@locallife/auto-adapt-harmony',
            '@kds/lottie-react-native'
        ]
        
        for dep_name in list(dependencies.keys()) + list(dev_dependencies.keys()):
            for keyword in harmony_keywords:
                if keyword in dep_name:
                    harmony_deps.append(f"{dep_name}: {dependencies.get(dep_name) or dev_dependencies.get(dep_name)}")
                    break
        
        return harmony_deps
    
    def _extract_harmony_plugins(self, babel_content: str) -> List[str]:
        """从babel.config.js中提取Harmony相关插件"""
        harmony_plugins = []
        
        # 查找插件配置
        plugin_pattern = r"'([^']*(?:auto-adapt-harmony|module-resolver|react-native)[^']*)'"
        matches = re.findall(plugin_pattern, babel_content)
        harmony_plugins.extend(matches)
        
        # 查找alias配置
        alias_pattern = r"'([^']*)':\s*'([^']*(?:react-native)[^']*)'"
        alias_matches = re.findall(alias_pattern, babel_content)
        for alias_from, alias_to in alias_matches:
            harmony_plugins.append(f"alias: {alias_from} -> {alias_to}")
        
        return harmony_plugins
    
    def _analyze_harmony_code(self, module_path: Path, harmony_files: List[Dict]) -> Dict[str, any]:
        """分析Harmony代码的统计信息"""
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'harmony_lines': 0,
            'conflict_markers': 0,
            'files_with_conflicts': [],
            'code_changes': [],
            'file_details': [],
            'harmony_code_snapshots': []  # 新增：Harmony代码快照
        }
        
        for file_info in harmony_files:
            if file_info['type'] == 'harmony_dir' and file_info['full_path'].is_file():
                stats['total_files'] += 1
                try:
                    with open(file_info['full_path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        stats['total_lines'] += len(lines)
                        stats['harmony_lines'] += len(lines)
                        
                        # 检查冲突标记
                        conflict_count = self._count_conflict_markers(content)
                        if conflict_count > 0:
                            stats['conflict_markers'] += conflict_count
                            stats['files_with_conflicts'].append({
                                'file': str(file_info['path']),
                                'conflicts': conflict_count
                            })
                        
                        # 检查代码变更
                        changes = self._detect_code_changes(lines)
                        if changes:
                            stats['code_changes'].extend(changes)
                        
                        # 收集Harmony代码快照
                        code_snapshot = self._extract_harmony_code_snapshot(file_info['full_path'], content)
                        if code_snapshot:
                            stats['harmony_code_snapshots'].append({
                                'file': str(file_info['path']),
                                'snapshot': code_snapshot
                            })
                        
                        stats['file_details'].append({
                            'file': str(file_info['path']),
                            'lines': len(lines),
                            'size': file_info['size'],
                            'conflicts': conflict_count
                        })
                        
                except Exception as e:
                    print(f"⚠️  读取文件失败 {file_info['path']}: {e}")
        
        return stats
    
    def _count_conflict_markers(self, content: str) -> int:
        """统计文件中的冲突标记数量"""
        conflict_patterns = [
            r'<<<<<<<\s',  # 冲突开始标记
            r'>>>>>>>\s',  # 冲突结束标记
            r'=======\s'   # 冲突分隔标记
        ]
        
        conflict_count = 0
        for pattern in conflict_patterns:
            matches = re.findall(pattern, content)
            conflict_count += len(matches)
        
        return conflict_count
    
    def _detect_code_changes(self, lines: List[str]) -> List[Dict]:
        """检测代码中的变更标记"""
        changes = []
        
        for i, line in enumerate(lines):
            # 检查是否有变更标记
            if 'TODO:' in line or 'FIXME:' in line or 'HARMONY:' in line:
                changes.append({
                    'line_number': i + 1,
                    'content': line.strip(),
                    'type': 'todo' if 'TODO:' in line else 'fixme' if 'FIXME:' in line else 'harmony'
                })
        
        return changes
    
    def _extract_harmony_code_snapshot(self, file_path: Path, content: str) -> str:
        """
        提取Harmony代码快照
        包含重要的Harmony相关代码块
        """
        lines = content.split('\n')
        snapshots = []
        
        # 查找重要的Harmony代码模式
        harmony_patterns = [
            r'import.*harmony',
            r'from.*harmony',
            r'export.*function.*harmony',
            r'// HARMONY:',
            r'/\* HARMONY:',
            r'@harmony',
            r'harmonySpecific',
            r'harmonyFunction',
            r'jumpUrl',
            r'react-native',
            r'linear-gradient',
            r'gesture-handler'
        ]
        
        for i, line in enumerate(lines):
            # 检查是否匹配Harmony模式
            for pattern in harmony_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # 提取包含该行的代码块
                    code_block = self._extract_code_block(lines, i)
                    if code_block and code_block not in snapshots:
                        snapshots.append(code_block)
                    break
        
        # 如果没有找到特定模式，提取文件开头的重要代码
        if not snapshots and lines:
            # 提取前10行作为快照
            important_lines = []
            for i, line in enumerate(lines[:15]):
                if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('/*'):
                    important_lines.append(f"{i+1:3d}: {line}")
                    if len(important_lines) >= 10:
                        break
            
            if important_lines:
                snapshots.append("重要代码片段:\n" + "\n".join(important_lines))
        
        return "\n\n".join(snapshots) if snapshots else ""
    
    def _extract_code_block(self, lines: List[str], start_line: int, context_lines: int = 3) -> str:
        """
        从指定行提取代码块
        """
        # 向前找函数开始
        start = start_line
        brace_count = 0
        in_function = False
        
        for i in range(start_line, max(0, start_line - 10), -1):
            line = lines[i].strip()
            if '{' in line:
                in_function = True
                break
            if re.match(r'(function|const|let|var)\s+\w+.*=>|function\s+\w+', line):
                start = i
                in_function = True
                break
        
        if not in_function:
            start = max(0, start_line - context_lines)
        
        # 向后找代码块结束
        end = min(len(lines), start_line + context_lines + 1)
        
        # 寻找函数结束的大括号
        for i in range(start_line, min(len(lines), start_line + 20)):
            line = lines[i]
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count <= 0:
                    end = i + 1
                    break
        
        # 提取代码块
        code_block = []
        for i in range(start, end):
            if i < len(lines):
                line_num = f"{i+1:3d}"
                code_block.append(f"{line_num}: {lines[i]}")
        
        if len(code_block) > 1:
            return "代码块:\n" + "\n".join(code_block)
        
        return ""
    
    def _generate_documentation_content(self, module_name: str, module_path: Path, stats: Dict) -> str:
        """生成文档内容"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# {module_name} Harmony适配文档

**生成时间:** {timestamp}
**模块路径:** {module_path}

## 概述

本文档记录了 {module_name} 模块的Harmony适配情况，包含Harmony相关代码的统计信息和需要人工校验的重点内容。

## 文件统计

- **总文件数:** {stats['total_files']}
- **总代码行数:** {stats['total_lines']}
- **Harmony代码行数:** {stats['harmony_lines']}
- **冲突标记数量:** {stats['conflict_markers']}

## 文件详情

"""
        
        # 添加文件详情表格
        if stats['file_details']:
            content += "| 文件路径 | 代码行数 | 文件大小 | 冲突数量 |\n"
            content += "|---------|---------|---------|---------|\n"
            for file_detail in stats['file_details']:
                content += f"| {file_detail['file']} | {file_detail['lines']} | {file_detail['size']} bytes | {file_detail['conflicts']} |\n"
            content += "\n"
        
        # 添加冲突文件列表
        if stats['files_with_conflicts']:
            content += "## 🔴 需要重点关注的冲突文件\n\n"
            for conflict_file in stats['files_with_conflicts']:
                content += f"- **{conflict_file['file']}** - {conflict_file['conflicts']} 个冲突标记\n"
            content += "\n"
        
        # 添加代码变更列表
        if stats['code_changes']:
            content += "## 📝 代码变更记录\n\n"
            for change in stats['code_changes']:
                change_type = "📝 TODO" if change['type'] == 'todo' else "🔧 FIXME" if change['type'] == 'fixme' else "🎯 HARMONY"
                content += f"- **第 {change['line_number']} 行** - {change_type}: {change['content']}\n"
            content += "\n"
        
        # 添加Harmony配置信息
        harmony_files = self._find_harmony_files(module_path)
        harmony_config = self._extract_harmony_config(harmony_files)
        
        if harmony_config:
            content += "## ⚙️ Harmony配置信息\n\n"
            
            if harmony_config.get('dependencies'):
                content += "### 依赖配置\n\n"
                for dep in harmony_config['dependencies']:
                    content += f"- {dep}\n"
                content += "\n"
            
            if harmony_config.get('plugins'):
                content += "### Babel插件配置\n\n"
                for plugin in harmony_config['plugins']:
                    content += f"- {plugin}\n"
                content += "\n"
        
        # 添加Harmony代码快照
        if stats.get('harmony_code_snapshots'):
            content += "## 💻 Harmony代码快照\n\n"
            content += "以下是检测到的重要Harmony代码片段，包含最新的代码实现:\n\n"
            
            for i, snapshot_info in enumerate(stats['harmony_code_snapshots'], 1):
                content += f"### {i}. {snapshot_info['file']}\n\n"
                content += "```typescript\n"
                content += f"{snapshot_info['snapshot']}\n"
                content += "```\n\n"
        
        # 添加Harmony目录结构
        harmony_dir = module_path / "harmony"
        if harmony_dir.exists():
            content += "## 📁 Harmony目录结构\n\n"
            content += self._generate_directory_tree(harmony_dir)
            content += "\n"
        
        # 添加人工校验建议
        content += """## 👀 人工校验建议

### 重点检查项
1. **冲突文件**: 以上标记为红色的文件包含Git冲突标记，需要人工解决
2. **代码变更**: 检查TODO/FIXME/HARMONY标记的代码是否正确实现
3. **代码快照**: 对比代码快照中的实现是否符合Harmony规范
4. **依赖版本**: 确认Harmony相关依赖版本是否兼容
5. **插件配置**: 验证Babel插件配置是否正确

### 校验步骤
1. 逐个检查冲突文件，解决所有`<<<<<<<`, `=======`, `>>>>>>>`标记
2. 对比代码快照，确保Harmony实现正确
3. 运行模块的单元测试，确保功能正常
4. 检查Harmony相关API的使用是否符合规范
5. 验证依赖版本是否存在兼容性问题

---
*本文档由krn-harmony-adapter自动生成，请根据实际情况进行人工校验*
"""
        
        return content
    
    def _extract_harmony_config(self, harmony_files: List[Dict]) -> Dict[str, List]:
        """提取Harmony配置信息"""
        config = {'dependencies': [], 'plugins': []}
        
        for file_info in harmony_files:
            if file_info['type'] == 'package_json' and 'dependencies' in file_info:
                config['dependencies'].extend(file_info['dependencies'])
            elif file_info['type'] == 'babel_config' and 'plugins' in file_info:
                config['plugins'].extend(file_info['plugins'])
        
        return config
    
    def _generate_directory_tree(self, directory: Path) -> str:
        """生成目录树结构"""
        tree = []
        
        def _walk_dir(dir_path: Path, prefix: str = ""):
            items = sorted(dir_path.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                
                if item.is_dir():
                    tree.append(f"{prefix}{connector}{item.name}/")
                    extension = "    " if is_last else "│   "
                    _walk_dir(item, prefix + extension)
                else:
                    tree.append(f"{prefix}{connector}{item.name}")
        
        _walk_dir(directory)
        return "\n".join(tree)
    
    def generate_summary_documentation(self, modules: List[str]) -> bool:
        """生成所有模块的汇总文档"""
        try:
            summary_content = f"""# Harmony适配汇总文档

**生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 适配模块列表

"""
            
            total_files = 0
            total_lines = 0
            total_conflicts = 0
            
            for module_name in modules:
                module_path = self.base_path / module_name
                harmony_files = self._find_harmony_files(module_path)
                stats = self._analyze_harmony_code(module_path, harmony_files)
                
                total_files += stats['total_files']
                total_lines += stats['harmony_lines']
                total_conflicts += stats['conflict_markers']
                
                # 添加模块摘要
                summary_content += f"### {module_name}\n\n"
                summary_content += f"- 文件数量: {stats['total_files']}\n"
                summary_content += f"- Harmony代码行数: {stats['harmony_lines']}\n"
                summary_content += f"- 冲突标记数量: {stats['conflict_markers']}\n"
                
                if stats['files_with_conflicts']:
                    summary_content += f"- **⚠️ 包含冲突的文件:** {len(stats['files_with_conflicts'])} 个\n"
                
                summary_content += f"- [详细文档](./{module_name}_harmony_adaptation.md)\n\n"
            
            summary_content += f"""## 总体统计

- **总模块数:** {len(modules)}
- **总文件数:** {total_files}
- **总Harmony代码行数:** {total_lines}
- **总冲突标记数:** {total_conflicts}

## 重点问题汇总

"""
            
            # 收集所有包含冲突的模块
            modules_with_conflicts = []
            for module_name in modules:
                module_path = self.base_path / module_name
                harmony_files = self._find_harmony_files(module_path)
                stats = self._analyze_harmony_code(module_path, harmony_files)
                
                if stats['files_with_conflicts']:
                    modules_with_conflicts.append({
                        'module': module_name,
                        'conflicts': stats['files_with_conflicts']
                    })
            
            if modules_with_conflicts:
                summary_content += "### 🔴 包含冲突的模块\n\n"
                for module_info in modules_with_conflicts:
                    summary_content += f"#### {module_info['module']}\n"
                    for conflict_file in module_info['conflicts']:
                        summary_content += f"- {conflict_file['file']}: {conflict_file['conflicts']} 个冲突\n"
                    summary_content += "\n"
            
            summary_content += """## 下一步行动建议

1. **优先处理冲突**: 立即解决所有标记为红色的冲突文件
2. **模块测试**: 对每个适配模块进行功能测试
3. **代码审查**: 重点检查包含TODO/FIXME标记的代码
4. **依赖验证**: 确认所有Harmony依赖版本兼容性

---
*本文档由krn-harmony-adapter自动生成*
"""
            
            summary_path = self.docs_dir / "harmony_adaptation_summary.md"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
                
            print(f"✅ 已生成汇总文档: {summary_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成汇总文档失败: {e}")
            return False