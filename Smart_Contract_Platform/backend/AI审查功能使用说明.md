# AI合同智能审查功能使用说明

## 功能概述

AI合同智能审查功能基于RAG（检索增强生成）技术，能够：
- 从PDF法律文档构建知识库
- 自动检索相关法律条款
- 使用DeepSeek API进行智能审查
- 标出错误、风险点和改进建议

## 环境配置

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置DeepSeek API

创建 `.env` 文件（在 `backend/` 目录下）：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 准备PDF文档

将PDF文件（如中华人民共和国合同法等）放入 `backend/knowledge_base/pdfs/` 目录。

**注意**：PDF文件应该是可读的文本PDF，不是扫描版图片。

### 4. 初始化知识库

运行初始化脚本：

```bash
cd backend
python scripts/init_knowledge_base.py
```

脚本会：
- 扫描 `knowledge_base/pdfs/` 目录下的所有PDF文件
- 提取文本并分块
- 生成向量嵌入
- 存储到ChromaDB

**首次运行**：如果使用本地嵌入模型，首次运行时会自动下载模型，可能需要一些时间。

## 使用流程

### 1. 在合同详情页使用

1. 登录系统（合同管理员、法务或管理员角色）
2. 进入合同详情页
3. 确保合同有详细条款内容
4. 点击"详细条款"卡片右上角的"AI审查"按钮
5. 等待审查完成（通常需要10-30秒）
6. 查看审查结果：
   - 合规性评分（0-100分）
   - 问题列表（类型、严重程度、位置、描述、建议）
   - 总体改进建议

### 2. 审查结果说明

- **合规性评分**：0-100分，分数越高表示越合规
- **问题类型**：
  - 违规：违反法律法规
  - 风险：存在法律风险
  - 不完善：条款不够完善
- **严重程度**：高/中/低
- **位置**：问题所在的条款位置
- **改进建议**：具体的修改建议

## 技术架构

### 后端服务

- `app/services/rag_service.py` - RAG知识库服务
- `app/services/ai_review.py` - AI审查服务
- `app/api/routers/ai_review.py` - API路由
- `app/schemas/ai_review.py` - 数据模型

### 前端界面

- `frontend/src/views/ContractDetail.vue` - 合同详情页（已添加AI审查功能）

## 故障排查

### 1. 知识库未初始化

**症状**：审查时提示"未找到相关法律条款"

**解决**：运行 `python scripts/init_knowledge_base.py` 初始化知识库

### 2. DeepSeek API调用失败

**症状**：审查时提示"DeepSeek API调用失败"

**解决**：
- 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确
- 检查网络连接
- 确认API密钥有效且有足够余额

### 3. PDF解析失败

**症状**：初始化知识库时提示"PDF解析失败"

**解决**：
- 确认PDF文件是文本PDF（不是扫描图片）
- 检查PDF文件是否损坏
- 尝试使用其他PDF文件

### 4. 嵌入模型加载失败

**症状**：初始化时提示"无法加载本地嵌入模型"

**解决**：
- 确认已安装 `sentence-transformers` 包
- 首次运行需要下载模型，请等待
- 如果网络问题，系统会自动使用ChromaDB默认嵌入

## 性能优化建议

1. **知识库更新**：当添加新的PDF文档时，重新运行初始化脚本
2. **缓存机制**：相同条款的审查结果可以缓存（未来功能）
3. **异步处理**：对于长条款，可以考虑异步处理（未来功能）

## 注意事项

1. **API成本**：每次审查都会调用DeepSeek API，会产生费用
2. **审查准确性**：AI审查结果仅供参考，最终决策需要人工审核
3. **数据安全**：合同条款会发送到DeepSeek API，请注意数据安全
4. **知识库维护**：定期更新PDF文档，保持知识库的时效性

