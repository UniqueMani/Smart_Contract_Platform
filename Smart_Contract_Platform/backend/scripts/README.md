# 脚本目录

## init_knowledge_base.py

知识库初始化脚本，用于处理PDF文档并构建向量数据库。

### 使用方法

```bash
cd backend
python scripts/init_knowledge_base.py
```

### 功能

- 扫描 `knowledge_base/pdfs/` 目录下的所有PDF文件
- 提取PDF文本内容
- 将文本分割为适合检索的块
- 生成向量嵌入并存储到ChromaDB
- 支持增量更新（已处理的文件不会重复处理）

### 注意事项

- 首次运行时会自动下载嵌入模型（如果使用本地模型）
- 确保PDF文件是文本PDF，不是扫描图片
- 处理大量PDF文件可能需要较长时间

