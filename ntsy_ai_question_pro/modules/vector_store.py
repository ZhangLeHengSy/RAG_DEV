# modules/vector_store.py

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List, Dict
import os

class VectorStore:
    def __init__(self, config):
        self.config = config
        # model_path = config.EMBEDDING_MODEL
        model_path = os.path.join(os.getcwd(), "models", "text2vec-base-chinese")
        
        # 验证模型文件是否存在
        print(f"Looking for model at: {model_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
         # 验证模型文件夹中的必要文件
        # required_files = ['config.json', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json']
        # missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_path, f))]
        
        # if missing_files:
        #     raise FileNotFoundError(f"Missing required model files: {missing_files}")
        
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_path,
                model_kwargs={'device': config.EMBEDDING_DEVICE},
                encode_kwargs={'normalize_embeddings': True}
            )
            # 测试模型是否正常工作
            test_text = "测试文本"
            _ = self.embeddings.embed_query(test_text)
            print("Embedding model loaded successfully!")
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
            raise
        
    def create_collection(self, collection_name: str) -> bool:
        """创建新的知识库集合"""
        try:
            if collection_name not in self.vector_stores:
                self.vector_stores[collection_name] = FAISS.from_texts(
                    [""], self.embeddings
                )
                save_path = os.path.join(self.config.VECTOR_STORE_PATH, collection_name)
                self.vector_stores[collection_name].save_local(save_path)
                return True
            return False
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False

    def add_texts(self, collection_name: str, texts: List[str], metadatas: List[Dict] = None) -> bool:
        """向知识库添加文本"""
        try:
            if collection_name in self.vector_stores:
                self.vector_stores[collection_name].add_texts(texts, metadatas=metadatas)
                save_path = os.path.join(self.config.VECTOR_STORE_PATH, collection_name)
                self.vector_stores[collection_name].save_local(save_path)
                return True
            return False
        except Exception as e:
            print(f"Error adding texts: {e}")
            return False

    def similarity_search(self, collection_name: str, query: str, k: int = 4) -> List[Dict]:
        """相似度搜索"""
        try:
            if collection_name in self.vector_stores:
                docs = self.vector_stores[collection_name].similarity_search_with_score(query, k=k)
                return [{"content": doc[0].page_content, "metadata": doc[0].metadata, "score": doc[1]} 
                       for doc in docs]
            return []
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []