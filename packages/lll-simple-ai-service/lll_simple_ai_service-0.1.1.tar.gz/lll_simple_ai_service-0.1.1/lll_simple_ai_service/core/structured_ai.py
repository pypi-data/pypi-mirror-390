from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Any, Callable
import os
import torch
from outlines import models

from .schemas import SchemaManager
from ..config.default_config import AIConfig


class StructuredAIModel:
    """结构化AI模型引擎"""

    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.schema_manager = SchemaManager(self.config)
        self.model = None

    def initialize(self):
        """初始化模型和生成器"""
        if not self._check_model_exists():
            raise FileNotFoundError(f"模型不存在: {self.config.get_model_path()}")

        # 使用 transformers 加载模型
        model = AutoModelForCausalLM.from_pretrained(
            self.config.get_model_path(),
            torch_dtype=torch.float32,
            device_map=self.config.device,
            local_files_only=True,
            low_cpu_mem_usage=self.config.low_cpu_mem_usage,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            self.config.get_model_path(), local_files_only=True
        )

        # 包装为 outlines 模型
        self.model = models.from_transformers(model, tokenizer)

    def _check_model_exists(self) -> bool:
        """检查模型是否存在"""
        model_path = self.config.get_model_path()
        if os.path.exists(model_path):
            return True

        # 如果是HF模型名，检查缓存
        cache_path = os.path.expanduser(
            f"~/.cache/huggingface/hub/models--{model_path.replace('/', '--')}"
        )
        return os.path.exists(cache_path)

    def add_custom_task(
        self,
        task_type: str,
        schema: Dict[str, Any],
        input_template: str,
        format_inputs_func: Callable,
    ):
        """添加自定义任务"""
        self.schema_manager.add_schema(
            task_type, schema, input_template, format_inputs_func
        )

    def generate(self, task_type: str, inputs: Dict, **kwargs) -> Dict[str, Any]:
        """生成结构化输出"""

        schema = self.schema_manager.get_schema(task_type)
        if not schema:
            return {"error": f"未知任务类型: {task_type}"}

        if not self.model:
            return {"error": f"模型不存在: {task_type}"}

        # 生成提示词
        prompt = self.schema_manager.generate_prompt(task_type, inputs)
        if not prompt:
            return {"error": f"生成提示词失败: {task_type}"}

        try:
            print(f"prompt: {prompt}")

            # 合并默认参数
            generate_kwargs = {
                "max_tokens": kwargs.get("max_tokens", self.config.default_max_tokens),
                "max_new_tokens": kwargs.get(
                    "max_new_tokens", self.config.default_max_new_tokens
                ),
                "temperature": kwargs.get(
                    "temperature", self.config.default_temperature
                ),
            }

            result = self.model(prompt, schema, **generate_kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_tasks(self) -> list:
        """获取可用任务列表"""
        return self.schema_manager.list_tasks()
