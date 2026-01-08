# 工具脚本文档

本目录包含项目使用的工具脚本，用于系统初始化和维护。

## 📋 目录

- [脚本列表](#脚本列表)
- [init_knowledge_base.py](#init_knowledge_basepy)
- [使用指南](#使用指南)
- [故障排查](#故障排查)

## 📜 脚本列表

| 脚本名称 | 功能 | 使用频率 |
|---------|------|---------|
| `init_knowledge_base.py` | 初始化AI知识库 | 首次安装、更新文档时 |

## 🤖 init_knowledge_base.py

知识库初始化脚本，用于处理PDF文档并构建向量数据库。

### 功能说明

该脚本执行以下操作：

1. **扫描PDF文件**: 扫描 `knowledge_base/pdfs/` 目录下的所有PDF文件
2. **提取文本**: 使用 PyPDF2 提取PDF文本内容
3. **文本分块**: 将文本分割为适合检索的块（800字符，重叠150字符）
4. **向量化**: 生成文本向量嵌入
5. **存储**: 将向量存储到ChromaDB向量数据库
6. **增量更新**: 已处理的文件不会重复处理

### 使用方法

#### 基本用法

```bash
cd backend
python scripts/init_knowledge_base.py
```

#### 完整流程

```bash
# 1. 确保PDF文件已放入 knowledge_base/pdfs/ 目录
# 2. 运行脚本
cd backend
python scripts/init_knowledge_base.py

# 3. 查看输出
# 脚本会显示处理进度和结果
```

### 输出示例

```
正在初始化知识库...
扫描PDF文件: 6 个文件
处理文件: 中华人民共和国合同法_19990315.pdf
  - 提取文本: 成功
  - 分块数量: 245
  - 生成向量: 成功
  - 存储到数据库: 成功
...
知识库初始化完成！
总计处理: 6 个文件
总计块数: 1523 个
```

### 配置选项

脚本使用 `app/core/config.py` 中的配置：

- `knowledge_base_dir`: 知识库目录
- `pdfs_dir`: PDF文件目录
- `chroma_db_path`: ChromaDB数据库路径

### 依赖要求

确保已安装以下依赖：

```bash
pip install chromadb langchain langchain-community PyPDF2 sentence-transformers
```

### 注意事项

1. **首次运行**: 如果使用本地嵌入模型，首次运行时会自动下载模型，可能需要一些时间
2. **PDF格式**: 确保PDF文件是文本PDF（不是扫描图片）
3. **处理时间**: 处理大量PDF文件可能需要较长时间
4. **磁盘空间**: 向量数据库会占用一定磁盘空间
5. **增量更新**: 已处理的文件（基于文件哈希）不会重复处理

### 错误处理

脚本包含以下错误处理：

- PDF解析失败：跳过该文件，继续处理其他文件
- 向量化失败：使用ChromaDB默认嵌入
- 数据库错误：显示错误信息并退出

## 📖 使用指南

### 首次安装

1. 准备PDF文档，放入 `knowledge_base/pdfs/` 目录
2. 运行初始化脚本：

```bash
python scripts/init_knowledge_base.py
```

3. 验证知识库：

```bash
# 检查 chroma_db 目录是否生成
ls knowledge_base/chroma_db/
```

### 添加新文档

1. 将新PDF文件放入 `pdfs/` 目录
2. 运行脚本（会自动检测新文件）

```bash
python scripts/init_knowledge_base.py
```

### 更新知识库

如果需要完全重建知识库：

1. 删除 `chroma_db/` 目录
2. 更新 `pdfs/` 目录中的PDF文件
3. 重新运行脚本

### 验证知识库

运行AI审查功能测试知识库是否正常工作：

```bash
# 启动后端服务
uvicorn app.main:app --reload

# 在浏览器中测试AI审查功能
# 访问: http://localhost:5173
# 登录后进入合同详情页，点击"AI审查"按钮
```

## 🔧 故障排查

### 问题1: 模块导入失败

**错误**: `ModuleNotFoundError: No module named 'chromadb'`

**解决方案**:
```bash
pip install -r requirements.txt
```

### 问题2: PDF解析失败

**错误**: `PDF解析失败: ...`

**解决方案**:
- 确认PDF文件是文本PDF（不是扫描图片）
- 检查PDF文件是否损坏
- 尝试使用其他PDF文件

### 问题3: 嵌入模型下载失败

**错误**: 模型下载超时或失败

**解决方案**:
- 检查网络连接
- 脚本会自动降级使用ChromaDB默认嵌入
- 可以手动下载模型到本地

### 问题4: 数据库权限错误

**错误**: 无法创建或写入数据库

**解决方案**:
- 检查目录权限
- 确保有写入权限
- 检查磁盘空间

### 问题5: 内存不足

**错误**: 处理大文件时内存不足

**解决方案**:
- 分批处理PDF文件
- 增加系统内存
- 使用更小的分块大小（需要修改代码）

## 🔍 调试技巧

### 查看详细日志

修改脚本添加详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试单个文件

可以修改脚本只处理特定文件进行测试。

### 检查向量数据库

使用ChromaDB客户端检查数据库内容：

```python
import chromadb
client = chromadb.PersistentClient(path="knowledge_base/chroma_db")
collection = client.get_collection("contract_laws")
print(collection.count())
```

## 📚 相关文档

- [知识库文档](../knowledge_base/README.md)
- [AI审查功能使用说明](../AI审查功能使用说明.md)
- [ChromaDB文档](https://docs.trychroma.com/)
- [LangChain文档](https://python.langchain.com/)

## 🤝 贡献

欢迎改进脚本功能！

## 📄 许可证

MIT License
