from __future__ import annotations

from typing import List, Dict
from dataclasses import asdict
import time

# 框架依赖
from triclick_doc_toolset.framework import Command, Context, CommandRegistry

# 解析与标题/标签工具
from triclick_doc_toolset.common.word import (
    extract_docx_content_with_metadata,
    assemble_title_lines,
)
from triclick_doc_toolset.common.rules import (
    apply_normalize_duplicate_labels_rule,
)

# 为拼接多行标题引入 docx 读取
import re


class DocxFileParseCommand(Command):
    """
    框架命令子类：按“标题-表格-脚注/段落”分块（仅元数据）。
    仅使用 `extract_docx_content_with_metadata` 进行解析。
    """

    def is_satisfied(self, context: Context) -> bool:
        return context.has_document()

    def execute(self, context: Context) -> Context:
        # 解析输入路径（支持文件或文件夹），仅处理 .docx
        paths = context.resolve_document_paths(patterns=["*.docx"])
        if not paths:
            context.add_error("No DOCX files resolved from context")
            return context

        # 使用通用工具进行标题组装与标签归一化

        # 将解析得到的 TableItem 列表转为结构化字典，并写入 Context.sections
        parsed_sections: List[Dict] = []
        for p in paths:
            _start = time.perf_counter()
            sections = extract_docx_content_with_metadata(str(p))
            for sec in sections:
                d = asdict(sec)
                # 组装标题（按索引序拼接非空行，遇空行停止）
                full_title = assemble_title_lines(str(p), sec.title_indices)
                if full_title:
                    d["title"] = full_title
                    # 若存在规范化后的 label，则将标题前缀替换为该 label，确保一致性
                    label = (d.get("label") or "").strip()
                    if label and re.match(r"(?i)^(table|listing|figure)\s+", label):
                        try:
                            d["title"] = re.sub(
                                r"(?i)^(?:[A-Za-z]\.|\d+\.)?\s*(table|listing|figure)\s+\S+",
                                label,
                                d["title"]
                            )
                        except Exception:
                            # 容错：保持原标题
                            pass
                d["source_file"] = str(p)
                parsed_sections.append(d)
            _elapsed = time.perf_counter() - _start
            print(f"[{self.name}] 文件处理 {str(p)} 耗时 {_elapsed:.2f}s")

        # 规则：重复标签归一化（通过 self.rules 控制）
        # 查找名为 "normalize_duplicate_labels" 的规则并应用
        rule = next((r for r in self.rules if (r.get("name") == "normalize_duplicate_labels" and r.get("enabled") is True)), None)
        if rule:
            params = rule.get("params") or {}
            suffix_fmt = str(params.get("suffix_format", ".{n}"))
            apply_normalize_duplicate_labels_rule(parsed_sections, suffix_fmt)

        # 更新上下文
        context.doc_type = "docx"
        context.sections = parsed_sections
        context.processing_summary["title_table_footnote_partition"] = {
            "files_processed": len(paths),
            "sections_extracted": len(parsed_sections),
            "mode": "metadata_only",
        }
        return context


# 注册到命令注册表，便于 Pipeline 通过 YAML 创建
CommandRegistry.register("DocxFileParseCommand", DocxFileParseCommand)