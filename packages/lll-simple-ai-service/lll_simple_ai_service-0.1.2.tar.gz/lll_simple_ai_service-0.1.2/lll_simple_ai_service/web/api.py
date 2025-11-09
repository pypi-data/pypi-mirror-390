from flask import Flask, request, jsonify
import threading
import logging
from ..core.structured_ai import StructuredAIModel
from ..config.default_config import AIConfig


def create_app(config: AIConfig = None):
    """创建Flask应用"""
    app = Flask(__name__)

    # 初始化AI引擎
    ai_config = config or AIConfig()
    ai_engine = StructuredAIModel(ai_config)
    logger = logging.getLogger("AIService")

    # 在应用启动时初始化
    with app.app_context():
        # 在第一个请求前初始化AI模型
        def _initialize():
            try:
                app.logger.info("模型初始化")
                ai_engine.initialize()
                app.logger.info("模型初始化成功")
            except Exception as e:
                app.logger.error(f"模型初始化失败: {e}")

        thread = threading.Thread(target=_initialize)
        thread.daemon = True
        thread.start()

    @app.route("/health", methods=["GET"])
    def health_check():
        model_loaded = ai_engine.model is not None
        return jsonify(
            {
                "status": "healthy" if model_loaded else "initializing",
                "model_loaded": model_loaded,
                "available_tasks": ai_engine.get_available_tasks(),
                "config": {
                    "model_path": ai_engine.config.get_model_path(),
                    "use_local_model": ai_engine.config.use_local_model,
                },
            }
        )

    @app.route("/generate", methods=["POST"])
    def generate_structured():
        data = request.json

        task_type = data.get("task_type")

        if not task_type:
            return jsonify({"success": False, "error": "缺少task_type参数"})

        result = ai_engine.generate(
            task_type=task_type,
            inputs=data,
            max_tokens=data.get("max_tokens"),
            temperature=data.get("temperature"),
        )

        return jsonify(result)

    return app, ai_engine
