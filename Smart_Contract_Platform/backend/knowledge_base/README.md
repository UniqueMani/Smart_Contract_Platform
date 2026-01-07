# 知识库目录

## 目录结构

- `pdfs/` - 存放PDF文档（中华人民共和国合同法等法律文件）
- `chroma_db/` - ChromaDB向量数据库存储目录（自动生成）

## 使用方法

1. 将PDF文件放入 `pdfs/` 目录
2. 运行初始化脚本：
   ```bash
   cd backend
   python scripts/init_knowledge_base.py
   ```

## 注意事项

- PDF文件应该是可读的文本PDF
- 支持多个PDF文件，脚本会自动处理所有PDF
- 已处理的文件不会重复处理（基于文件哈希）
- 如需更新知识库，删除 `chroma_db/` 目录后重新运行初始化脚本

