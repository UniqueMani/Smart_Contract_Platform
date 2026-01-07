"""
RAG知识库服务
处理PDF文档、文本分块、向量化和检索
"""
import os
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from PyPDF2 import PdfReader

from app.core.config import settings


class RAGService:
    """RAG知识库服务类"""
    
    def __init__(self):
        """初始化RAG服务"""
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.chroma_client.get_or_create_collection(
            name="contract_law_knowledge",
            metadata={"description": "合同法律知识库"}
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # 每个块800字符
            chunk_overlap=150,  # 重叠150字符
            length_function=len,
            separators=["\n\n", "\n", "。", "，", " ", ""]
        )
        
        # 初始化嵌入模型（使用本地模型，避免额外API调用）
        # 注意：首次运行时会自动下载模型，可能需要一些时间
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"警告：无法加载本地嵌入模型，将使用ChromaDB默认嵌入: {e}")
            print(f"提示：如果这是首次运行，请确保已安装 sentence-transformers 包")
            self.embeddings = None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")
    
    def split_text(self, text: str) -> List[str]:
        """将文本分割为块"""
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def get_file_hash(self, file_path: str) -> str:
        """计算文件哈希值，用于判断文件是否已处理"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def is_file_processed(self, file_path: str) -> bool:
        """检查文件是否已处理"""
        file_hash = self.get_file_hash(file_path)
        # 检查集合中是否已有该文件的元数据
        results = self.collection.get(
            where={"source_file": os.path.basename(file_path)},
            limit=1
        )
        return len(results['ids']) > 0
    
    def add_document_to_knowledge_base(self, text: str, source_file: str, metadata: Optional[Dict] = None):
        """将文档添加到知识库"""
        # 分割文本
        chunks = self.split_text(text)
        
        # 准备数据
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_file}_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            
            chunk_metadata = {
                "source_file": source_file,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                chunk_metadata.update(metadata)
            metadatas.append(chunk_metadata)
        
        # 如果有嵌入模型，生成嵌入向量
        if self.embeddings:
            embeddings_list = self.embeddings.embed_documents(documents)
            embeddings = embeddings_list
        
        # 添加到ChromaDB
        if embeddings:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            # 使用ChromaDB默认嵌入
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
        return len(chunks)
    
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关文档块"""
        # 如果有嵌入模型，生成查询向量
        query_embedding = None
        if self.embeddings:
            query_embedding = self.embeddings.embed_query(query)
        
        # 执行搜索
        if query_embedding:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
        
        # 格式化结果
        chunks = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                chunks.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return chunks
    
    def get_knowledge_base_stats(self) -> Dict:
        """获取知识库统计信息"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }


# 全局RAG服务实例
_rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    """获取RAG服务实例（单例模式）"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

