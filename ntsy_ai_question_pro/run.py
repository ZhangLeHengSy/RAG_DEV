# run.py
from flask import Flask
from app.routes.chat import chat_bp
from app.routes.knowledge import knowledge_bp
from app.routes.index import index_bp  # 添加这行
from app.services.chat import ChatService
from modules.llm_wrapper import LLMWrapper
from modules.vector_store import VectorStore
from config.config import Config
from dotenv import load_dotenv
import os

def create_app():
    # 加载环境变量
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 创建必要的目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VECTOR_STORE_PATH'], exist_ok=True)
    
    # 初始化服务
    vector_store = VectorStore(Config)
    llm_wrapper = LLMWrapper(Config)
    
    app.chat_service = ChatService(Config, llm_wrapper, vector_store)
    
    # 注册蓝图
    app.register_blueprint(index_bp)  # 注册根路由蓝图
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=8066, debug=True)