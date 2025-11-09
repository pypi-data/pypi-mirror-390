import os
import torch
from typing import Dict, List, Any


class AIConfig:
    """AI服务配置类"""

    def __init__(self):
        # 模型配置
        self.model_name = "Qwen/Qwen3-4B-Instruct-2507"
        self.local_model_path = "./models/Qwen2-0.5B-Instruct"
        self.use_local_model = True
        self.device = "auto"
        self.torch_dtype = torch.float32
        self.low_cpu_mem_usage = True

        # 服务配置
        self.host = "0.0.0.0"
        self.port = 5000

        # 生成配置
        self.default_max_tokens = 200
        self.default_max_new_tokens = 200
        self.default_temperature = 0.7
        self.system_prompts: List[str] = []

    def update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_model_path(self) -> str:
        """获取模型路径"""
        if self.use_local_model and os.path.exists(self.local_model_path):
            return self.local_model_path
        return self.model_name
