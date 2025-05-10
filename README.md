# AI智能代码辅助

<!-- [en](./docs/README_en.md) -->

## 特点

#### Agent设计模式
在`agents\`目录下，将LLM包装成agents,具有高可扩展性

#### RAG
将codebase每一个file储存为vectors，以便于RAG agent找到最高相关性的代码

#### QA界面

#### 系统设计界面

#### 预训练界面


## 设置
1. 创建conda虚拟环境
```bash
conda create -n deep_code python=3.12
conda activate deep_code
```

2. 根据GPU的CUDA版本或者CPU安装PyTorch.

示例：
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

3. 安装第三方库
```bash
pip install -r requirements.txt
```

## 使用教程


## 相关论文

