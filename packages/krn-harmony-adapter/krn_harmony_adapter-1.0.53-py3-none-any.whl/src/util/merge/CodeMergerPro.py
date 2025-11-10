# -*- coding: utf-8 -*-
import ast
import difflib
import sys

class CodeMergerPro:
    
    def _merge_line_by_line(self, current_content: str, backup_content: str) -> str:
        """
        [辅助函数]
        使用 difflib 逐行合并。
        规则：冲突时，如果 backup 行含 'harmony'，则使用 backup。
        """
        try:
            current_lines = current_content.splitlines(True)
        except AttributeError:
            current_lines = []

        try:
            backup_lines = backup_content.splitlines(True)
        except AttributeError:
            backup_lines = []

        matcher = difflib.SequenceMatcher(None, current_lines, backup_lines)
        merged_result_lines = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                merged_result_lines.extend(current_lines[i1:i2])
            
            elif tag == 'replace':
                backup_chunk = "".join(backup_lines[j1:j2])
                if "harmony" in backup_chunk:
                    merged_result_lines.extend(backup_lines[j1:j2])
                else:
                    merged_result_lines.extend(current_lines[i1:i2])
            
            elif tag == 'delete':
                merged_result_lines.extend(current_lines[i1:i2])
            
            elif tag == 'insert':
                backup_chunk = "".join(backup_lines[j1:j2])
                if "harmony" in backup_chunk:
                    merged_result_lines.extend(backup_lines[j1:j2])
                else:
                    pass

        return "".join(merged_result_lines)


    def _get_code_blocks(self, content: str) -> (dict, str):
        """
        [辅助函数]
        使用 AST 将代码分为“块”（函数/类）和“其他”（imports/globals）。
        返回: (blocks_map, other_code_str)
            blocks_map: {"block_name": "source_code_string"}
            other_code_str: "所有其他代码的合并字符串"
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # 如果语法错误，无法解析，则全部视为“其他”代码
            return {}, content

        blocks = {}
        all_lines = content.splitlines(True)
        
        # 记录属于块的行号
        block_line_ranges = set()
        
        # 遍历顶层节点
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                try:
                    # 确定块的真实起始行（包括装饰器）
                    start_line = node.lineno
                    if hasattr(node, 'decorator_list') and node.decorator_list:
                         # 确保 start_line 是装饰器和函数体中最早的行
                         decorator_lines = [d.lineno for d in node.decorator_list]
                         start_line = min(decorator_lines + [node.lineno])
                    
                    end_line = node.end_lineno
                    
                    # 获取原始源代码（保留格式和注释）
                    # (使用 ast.get_source_segment(content, node) 需要 Python 3.8+)
                    block_source = "".join(all_lines[start_line-1 : end_line])
                    blocks[node.name] = block_source
                    
                    # 标记这些行属于一个块
                    for i in range(start_line, end_line + 1):
                        block_line_ranges.add(i)
                except Exception:
                    # 如果无法获取源码，则在下一步中将其视为“其他”代码
                    pass

        # 从所有行中过滤出不属于任何块的“其他”代码
        other_code_parts = []
        for i, line in enumerate(all_lines, 1): # 行号从1开始
            if i not in block_line_ranges:
                other_code_parts.append(line)
        
        return blocks, "".join(other_code_parts)


    def merge_code(self, current_content: str, backup_content: str) -> str:
        """
        按“函数/类”级别合并代码，并应用 'harmony' 优先规则。
        """
        
        # 1. 将两个版本的内容都解析为“块”和“其他”代码
        current_blocks, current_other = self._get_code_blocks(current_content)
        backup_blocks, backup_other = self._get_code_blocks(backup_content)

        # 2. 合并“其他”代码 (Imports, Globals)
        #    我们使用逐行合并策略来处理这部分
        merged_other_code = self._merge_line_by_line(current_other, backup_other)

        # 3. 合并“块”代码 (Functions, Classes)
        merged_blocks = []
        # 获取所有唯一的块名称
        all_block_names = set(current_blocks.keys()) | set(backup_blocks.keys())
        
        # 排序以保证合并顺序的确定性
        for name in sorted(list(all_block_names)):
            current_text = current_blocks.get(name)
            backup_text = backup_blocks.get(name)

            if current_text and backup_text:
                # Case 1: 块在两边都存在 (冲突或相同)
                if current_text == backup_text:
                    # 完全相同
                    merged_blocks.append(current_text)
                else:
                    # 冲突！应用 'harmony' 规则
                    if "harmony" in backup_text:
                        merged_blocks.append(backup_text) # 采用 backup
                    else:
                        merged_blocks.append(current_text) # 采用 current

            elif current_text:
                # Case 2: 块仅在 current 中存在
                # 规则：保留 current
                merged_blocks.append(current_text)
                
            elif backup_text:
                # Case 3: 块仅在 backup 中存在 (插入)
                # 规则：检查 'harmony'
                if "harmony" in backup_text:
                    merged_blocks.append(backup_text) # 插入
                else:
                    pass # 忽略 backup 的非 harmony 插入

        # 4. 组装最终的代码
        # 合并所有块，用换行符分隔（它们自带结尾换行）
        final_merged_blocks_str = "".join(merged_blocks)
        
        final_code = merged_other_code
        
        # 确保 "其他" 和 "块" 代码之间有空行
        if final_code and not final_code.endswith('\n'):
            final_code += '\n'
            
        final_code += final_merged_blocks_str
        
        return final_code
        
