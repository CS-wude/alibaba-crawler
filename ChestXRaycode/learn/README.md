# 胸部X光片分类项目

一个基于PyTorch的胸部X光片分类系统，用于检测正常肺部和肺炎病例。该项目使用深度学习技术，特别是卷积神经网络(CNN)来进行医学图像分析。

## 📋 项目特性

- **深度学习模型**: 使用预训练的ResNet模型进行迁移学习
- **数据增强**: 实现了多种数据增强技术提高模型泛化能力  
- **可视化工具**: 包含Grad-CAM热力图、特征图可视化等
- **完整工作流**: 从数据探索到模型训练、评估和预测的完整流程
- **灵活配置**: 支持多种模型配置和训练策略
- **医学图像分析**: 专门针对胸部X光片分类任务优化

## 🏗️ 项目结构

```
ChestXRay/learn/
├── dataset.py          # 数据加载和预处理
├── model.py            # 模型定义
├── train.py            # 训练脚本
├── visualize.py        # 可视化工具
├── main.py             # 主程序入口
├── config.py           # 配置文件
├── requirements.txt    # Python依赖
└── README.md          # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

确保你已经激活了正确的conda环境：

```bash
conda activate pytorch_cpu_env
```

### 2. 安装依赖

```bash
cd ChestXRay/learn
pip install -r requirements.txt
```

### 3. 数据探索

首先了解数据集的基本情况：

```bash
python main.py explore
```

这将显示：
- 数据集大小统计
- 类别分布情况
- 样本图像可视化

### 4. 查看模型信息

```bash
python main.py info --model_name resnet50
```

### 5. 开始训练

```bash
python main.py train
```

训练过程中会：
- 自动保存最佳模型
- 显示训练进度
- 生成训练历史图表
- 计算各种评估指标

### 6. 评估模型

```bash
python main.py eval --checkpoint checkpoints/best_model.pth
```

### 7. 预测单张图片

```bash
python main.py predict --image_path ../../data/ChestXRay/test/PNEUMONIA/person1_virus_11.jpeg --show_gradcam
```

### 8. 可视化分析

```bash
python main.py visualize --checkpoint checkpoints/best_model.pth
```

## 📊 数据集信息

### 数据结构
```
data/ChestXRay/
├── train/
│   ├── NORMAL/      # 正常肺部X光片
│   └── PNEUMONIA/   # 肺炎X光片  
└── test/
    ├── NORMAL/      # 正常肺部X光片（测试集）
    └── PNEUMONIA/   # 肺炎X光片（测试集）
```

### 数据统计
- **训练集**: ~5,200张图片
- **测试集**: ~620张图片
- **类别**: 2类（正常、肺炎）
- **图片格式**: JPEG
- **图片大小**: 不固定（训练时会调整为224x224）

## 🎯 模型架构

### 支持的模型
- **ResNet18**: 轻量级，训练快速
- **ResNet34**: 平衡性能和速度
- **ResNet50**: 默认选择，性能较好
- **ResNet101**: 最高性能，需要更多资源

### 模型特点
- 使用ImageNet预训练权重
- 自定义分类头，包含Dropout层防止过拟合
- 支持特征层冻结选项
- 使用Focal Loss处理类别不平衡

## ⚙️ 配置选项

### 训练配置
```python
# 主要超参数
BATCH_SIZE = 32
NUM_EPOCHS = 20
LEARNING_RATE = 0.001
MODEL_NAME = 'resnet50'
USE_FOCAL_LOSS = True
```

### 预定义配置
- **默认配置**: 标准训练设置
- **快速训练**: 用于测试，使用ResNet18，5个epoch
- **高精度配置**: 使用ResNet101，50个epoch
- **CPU配置**: 针对CPU训练优化

使用特定配置：
```python
from config import get_config
config = get_config('quick')  # 'default', 'quick', 'high_accuracy', 'cpu'
```

## 📈 训练监控

### 训练过程中的输出
- 实时显示损失和精度
- 进度条显示训练进度
- 自动保存最佳模型
- 学习率调度

### 生成的文件
```
checkpoints/
├── best_model.pth        # 最佳模型权重
└── training_history.png  # 训练历史图表

results/
├── confusion_matrix.png     # 混淆矩阵
├── confidence_analysis.png  # 置信度分析
└── roc_curve.png           # ROC曲线
```

## 🔍 可视化功能

### 1. Grad-CAM热力图
显示模型关注的区域，帮助理解模型决策：

```python
from visualize import visualize_gradcam
visualize_gradcam(model, image_path, device)
```

### 2. 特征图可视化
查看卷积层学到的特征：

```python
from visualize import visualize_feature_maps
visualize_feature_maps(model, image_path, device, layer_name='layer2')
```

### 3. 预测结果展示
批量显示预测结果，包含正确和错误的案例。

### 4. 性能分析
- 混淆矩阵
- ROC曲线和AUC分数
- 置信度分布分析
- 错误案例统计

## 🛠️ 高级用法

### 自定义训练循环

```python
from train import Trainer
from model import create_model, FocalLoss
from dataset import create_data_loaders

# 创建数据加载器
train_loader, test_loader = create_data_loaders(data_dir, batch_size=32)

# 创建模型
model = create_model(num_classes=2, model_name='resnet50')

# 创建训练器
trainer = Trainer(
    model=model,
    train_loader=train_loader,
    test_loader=test_loader,
    criterion=FocalLoss(),
    optimizer=optimizer,
    scheduler=scheduler,
    device=device
)

# 开始训练
trained_model = trainer.train(num_epochs=20)
```

### 批量预测

```python
from model import create_model
import torch

# 加载模型
model = create_model(num_classes=2)
checkpoint = torch.load('checkpoints/best_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])

# 批量预测
for images, labels in test_loader:
    outputs = model(images)
    predictions = torch.argmax(outputs, dim=1)
```

### 自定义数据增强

```python
from torchvision import transforms

custom_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])
```

## 📝 性能基准

### 预期性能指标
- **准确率**: 85-95%
- **AUC分数**: 0.90-0.98
- **训练时间**: 
  - ResNet18: ~10分钟/epoch (CPU)
  - ResNet50: ~25分钟/epoch (CPU)

### 影响性能的因素
1. **数据质量**: 图片清晰度和标注准确性
2. **数据增强**: 适当的增强可以提高泛化能力
3. **模型选择**: 更深的网络通常性能更好
4. **超参数调优**: 学习率、批次大小等的选择

## 🐛 常见问题

### Q: 训练时内存不足怎么办？
A: 
- 减小batch_size
- 使用更小的模型（如ResNet18）
- 减少num_workers

### Q: 训练速度太慢？
A: 
- 使用GPU加速
- 减小图片尺寸
- 使用更小的模型
- 启用混合精度训练

### Q: 模型过拟合？
A: 
- 增加数据增强
- 调整Dropout比例
- 使用正则化
- 减少模型复杂度

### Q: 预测准确率不高？
A: 
- 检查数据质量
- 尝试不同的数据增强策略
- 调整学习率
- 使用不同的损失函数

## 📚 扩展学习

### 相关资源
- [PyTorch官方文档](https://pytorch.org/docs/)
- [迁移学习教程](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [医学图像分析论文](https://arxiv.org/abs/1711.05225)

### 进阶功能
- 集成多个模型（Ensemble）
- 使用注意力机制
- 添加数据预处理流水线
- 实现在线学习

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目仅用于学习和研究目的。

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**注意**: 本项目仅用于教育和研究目的，不能用于实际医疗诊断。任何医疗决策都应该咨询专业医生。 