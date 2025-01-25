# app/routes/knowledge.py
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/')
def index():
    return render_template('knowledge.html')

@knowledge_bp.route('/api/knowledge/list')
def list_knowledge_bases():
    # 从向量存储中获取知识库列表
    bases = list(current_app.vector_store.vector_stores.keys())
    return jsonify([{"name": base} for base in bases])

@knowledge_bp.route('/api/knowledge/create', methods=['POST'])
async def create_knowledge_base():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Knowledge base name is required"}), 400
        
    result = current_app.knowledge_service.create_knowledge_base(name)
    
    if result:
        return jsonify({"message": f"Knowledge base '{name}' created successfully"})
    else:
        return jsonify({"error": "Failed to create knowledge base"}), 500

@knowledge_bp.route('/api/knowledge/upload', methods=['POST'])
async def upload_files():
    knowledge_base = request.form.get('knowledge_base')
    if not knowledge_base:
        return jsonify({"error": "Knowledge base name is required"}), 400
        
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400
        
    files = request.files.getlist('files[]')
    file_data = []
    
    # 确保上传目录存在
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    try:
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_data.append({
                    "filename": filename,
                    "path": file_path
                })
        
        # 处理上传的文件
        results = await current_app.knowledge_service.process_files(knowledge_base, file_data)
        
        # 清理临时文件
        for file_info in file_data:
            try:
                os.remove(file_info['path'])
            except OSError:
                pass
        
        return jsonify(results)
        
    except Exception as e:
        # 确保清理任何已上传的临时文件
        for file_info in file_data:
            try:
                os.remove(file_info['path'])
            except OSError:
                pass
        return jsonify({"error": str(e)}), 500

@knowledge_bp.route('/api/knowledge/delete', methods=['POST'])
async def delete_knowledge_base():
    """删除知识库"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Knowledge base name is required"}), 400
        
    try:
        if name in current_app.vector_store.vector_stores:
            del current_app.vector_store.vector_stores[name]
            # 删除向量存储文件
            storage_path = os.path.join(current_app.config['VECTOR_STORE_PATH'], name)
            if os.path.exists(storage_path):
                import shutil
                shutil.rmtree(storage_path)
            return jsonify({"message": f"Knowledge base '{name}' deleted successfully"})
        else:
            return jsonify({"error": "Knowledge base not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@knowledge_bp.route('/api/knowledge/<name>/info')
def get_knowledge_base_info(name):
    """获取知识库信息"""
    try:
        if name in current_app.vector_store.vector_stores:
            store = current_app.vector_store.vector_stores[name]
            return jsonify({
                "name": name,
                "document_count": len(store.index_to_docstore_id),
                "created_at": os.path.getctime(os.path.join(current_app.config['VECTOR_STORE_PATH'], name))
            })
        else:
            return jsonify({"error": "Knowledge base not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500