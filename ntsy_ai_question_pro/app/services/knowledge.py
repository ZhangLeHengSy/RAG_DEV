# app/services/knowledge.py

import os
from typing import List, Dict
from werkzeug.utils import secure_filename
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import markdown

class KnowledgeService:
    def __init__(self, config, vector_store):
        self.config = config
        self.vector_store = vector_store

    def create_knowledge_base(self, name: str) -> bool:
        """创建新的知识库"""
        return self.vector_store.create_collection(name)

    def _read_file(self, file_path: str) -> List[str]:
        """读取不同格式的文件内容"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return [f.read()]
                
        elif ext == '.pdf':
            reader = PdfReader(file_path)
            return [page.extract_text() for page in reader.pages]
            
        elif ext == '.docx':
            doc = Document(file_path)
            return ['\n'.join([paragraph.text for paragraph in doc.paragraphs])]
            
        elif ext == '.xlsx':
            df = pd.read_excel(file_path)
            return [df.to_string()]
            
        elif ext == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                html = markdown.markdown(content)
                return [html]
                
        return []

    async def process_files(self, knowledge_base: str, files: List[Dict]) -> Dict:
        """处理上传的文件"""
        results = {"success": [], "failed": []}
        
        for file in files:
            try:
                filename = secure_filename(file['filename'])
                file_path = os.path.join(self.config.UPLOAD_FOLDER, filename)
                
                # 保存文件
                with open(file_path, 'wb') as f:
                    f.write(file['body'])
                
                # 读取文件内容
                texts = self._read_file(file_path)
                
                # 添加到向量存储
                metadata = {
                    "filename": filename,
                    "source": file_path,
                }
                
                if self.vector_store.add_texts(knowledge_base, texts, [metadata] * len(texts)):
                    results["success"].append(filename)
                else:
                    results["failed"].append(filename)
                    
                # 清理临时文件
                os.remove(file_path)
                
            except Exception as e:
                results["failed"].append(filename)
                print(f"Error processing file {filename}: {e}")
                
        return results