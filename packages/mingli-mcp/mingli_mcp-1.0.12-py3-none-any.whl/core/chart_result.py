"""
排盘结果数据模型
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ChartResult:
    """排盘结果数据类"""

    system: str  # 系统名称
    basic_info: Dict[str, Any]  # 基本信息
    palaces: List[Dict[str, Any]] = field(default_factory=list)  # 宫位信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "system": self.system,
            "basic_info": self.basic_info,
            "palaces": self.palaces,
            "metadata": self.metadata,
        }

    def to_markdown(self) -> str:
        """
        转换为Markdown格式（由具体系统实现覆盖）

        Returns:
            Markdown格式的排盘信息
        """
        md = f"# {self.system}排盘\n\n"
        md += "## 基本信息\n"
        for key, value in self.basic_info.items():
            md += f"- **{key}**: {value}\n"

        if self.palaces:
            md += "\n## 宫位信息\n"
            for palace in self.palaces:
                palace_name = palace.get("name", "未知宫位")
                md += f"\n### {palace_name}\n"
                for key, value in palace.items():
                    if key != "name":
                        md += f"- **{key}**: {value}\n"

        return md

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChartResult":
        """从字典创建"""
        return cls(
            system=data["system"],
            basic_info=data["basic_info"],
            palaces=data.get("palaces", []),
            metadata=data.get("metadata", {}),
        )
