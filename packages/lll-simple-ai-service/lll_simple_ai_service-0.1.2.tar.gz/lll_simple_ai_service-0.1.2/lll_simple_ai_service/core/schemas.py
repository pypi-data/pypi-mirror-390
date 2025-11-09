import logging
from typing import Dict, Any, Optional, Callable
from ..config.default_config import AIConfig


class SchemaManager:
    """任务Schema管理器"""

    def __init__(self, config: AIConfig = None):
        currentConfig = config or AIConfig()
        self.logger = logging.getLogger("SchemaManager")
        self.task_registry = {}
        self.system_prompts = currentConfig.system_prompts

    def add_schema(
        self,
        task_type: str,
        schema: Dict,
        input_template: str,
        format_inputs_func: Callable,
    ):
        """注册完整任务配置"""
        self.task_registry[task_type] = {
            "output_schema": schema,
            "input_template": input_template,
            "format_inputs_func": format_inputs_func,
        }

    def get_schema(self, task_type: str) -> Optional[Dict[str, Any]]:
        """获取schema"""
        task_config = self.task_registry.get(task_type, None)

        if not task_config:
            self.logger.warning(f"未找到任务类型的schema: {task_type}")
            return None

        output_schema = task_config.get("output_schema")

        if not output_schema:
            self.logger.warning(f"未找到任务类型的output_schema: {task_type}")
            return None

        return output_schema

    def add_system_prompt(self, text):
        """添加固定的系统提示词前缀"""
        system_part = "".join([f"{prompt}\n" for prompt in self.system_prompts])
        return f"<|im_start|>system\n{system_part}<|im_end|>\n{text}"

    def generate_prompt(self, task_type: str, inputs: Dict) -> str:
        """根据输入数据生成智能提示词"""
        task_config = self.task_registry.get(task_type, None)

        if not task_config:
            self.logger.warning(f"未找到任务类型的schema: {task_type}")
            return None

        input_template = task_config.get("input_template")

        if not input_template:
            self.logger.warning(f"任务 {task_type} 没有输入模板")
            return None

        format_inputs_func = task_config.get("format_inputs_func")

        if not format_inputs_func:
            self.logger.warning(f"任务 {task_type} 没有模板解析函数")
            return None

        # 渲染模板
        try:
            from jinja2 import Template

            formatted_inputs = format_inputs_func(inputs)
            formatted_prompt = Template(input_template).render(**formatted_inputs)

            # 添加系统提示词
            full_prompt = self.add_system_prompt(formatted_prompt)
            return full_prompt

        except Exception as e:
            self.logger.error(f"生成任务 {task_type} 的提示词时出错: {e}")
            return None

    def list_tasks(self) -> list:
        """列出所有可用的任务类型"""
        all_tasks = set(self.task_registry.keys())
        return list(all_tasks)
