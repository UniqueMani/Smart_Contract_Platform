"""
知识库初始化脚本
扫描PDF目录，解析PDF文件并构建向量数据库
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.rag_service import get_rag_service


def init_knowledge_base():
    """初始化知识库"""
    print("开始初始化知识库...")
    
    # 获取PDF目录
    pdfs_dir = Path(settings.pdfs_dir)
    if not pdfs_dir.exists():
        print(f"PDF目录不存在: {pdfs_dir}")
        print(f"请将PDF文件放入: {pdfs_dir.absolute()}")
        return
    
    # 获取RAG服务
    rag_service = get_rag_service()
    
    # 扫描PDF文件
    pdf_files = list(pdfs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"未找到PDF文件，请将PDF文件放入: {pdfs_dir.absolute()}")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 处理每个PDF文件
    total_chunks = 0
    for pdf_file in pdf_files:
        file_name = pdf_file.name
        file_path = str(pdf_file.absolute())
        
        print(f"\n处理文件: {file_name}")
        
        # 检查是否已处理
        if rag_service.is_file_processed(file_path):
            print(f"  文件已处理，跳过: {file_name}")
            continue
        
        try:
            # 提取文本
            print(f"  正在提取文本...")
            text = rag_service.extract_text_from_pdf(file_path)
            
            if not text or not text.strip():
                print(f"  警告: 文件 {file_name} 未提取到文本，跳过")
                continue
            
            print(f"  提取到 {len(text)} 个字符")
            
            # 添加到知识库
            print(f"  正在添加到知识库...")
            chunks_count = rag_service.add_document_to_knowledge_base(
                text=text,
                source_file=file_name,
                metadata={
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path)
                }
            )
            
            total_chunks += chunks_count
            print(f"  成功添加 {chunks_count} 个文档块")
            
        except Exception as e:
            print(f"  错误: 处理文件 {file_name} 时出错: {str(e)}")
            continue
    
    # 显示统计信息
    stats = rag_service.get_knowledge_base_stats()
    print(f"\n知识库初始化完成！")
    print(f"总文档块数: {stats['total_chunks']}")
    print(f"本次新增: {total_chunks} 个文档块")


if __name__ == "__main__":
    init_knowledge_base()

