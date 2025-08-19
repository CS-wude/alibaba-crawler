#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
胸部X光片分类项目配置文件
"""

import os

class Config:
    """配置类"""
    
    # ===== 数据相关设置 =====
    DATA_DIR = '../../data/ChestXRay'
    NUM_CLASSES = 2
    CLASS_NAMES = ['NORMAL', 'PNEUMONIA']
    
    # 图片设置
    IMAGE_SIZE = 224
    INPUT_CHANNELS = 3
    
    # 数据增强设置
    TRAIN_AUGMENT = {
        'horizontal_flip_prob': 0.5,
        'rotation_degrees': 10,
        'brightness': 0.2,
        'contrast': 0.2,
    }
    
    # 数据标准化参数（ImageNet预训练模型标准）
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]
    
    # ===== 模型相关设置 =====
    MODEL_NAME = 'resnet50'  # 'resnet18', 'resnet34', 'resnet50', 'resnet101'
    PRETRAINED = True
    FREEZE_FEATURES = False
    
    # ===== 训练相关设置 =====
    BATCH_SIZE = 32
    NUM_EPOCHS = 20
    LEARNING_RATE = 0.001
    
    # 优化器设置
    OPTIMIZER = 'adam'  # 'adam', 'sgd', 'adamw'
    WEIGHT_DECAY = 1e-4
    
    # 学习率调度器设置
    SCHEDULER = 'step'  # 'step', 'cosine', 'plateau'
    STEP_SIZE = 7
    GAMMA = 0.1
    
    # 损失函数设置
    USE_FOCAL_LOSS = True
    FOCAL_ALPHA = 1.0
    FOCAL_GAMMA = 2.0
    
    # ===== 系统设置 =====
    NUM_WORKERS = 4
    PIN_MEMORY = True
    
    # 设备设置
    DEVICE = 'auto'  # 'auto', 'cpu', 'cuda'
    
    # ===== 保存和日志设置 =====
    SAVE_DIR = 'checkpoints'
    LOG_DIR = 'logs'
    RESULT_DIR = 'results'
    
    # 保存设置
    SAVE_BEST_ONLY = True
    SAVE_FREQUENCY = 5  # 每5个epoch保存一次
    
    # ===== 验证和测试设置 =====
    EVAL_FREQUENCY = 1  # 每个epoch都验证
    
    # ===== 可视化设置 =====
    VIS_SAMPLES = 16
    FEATURE_LAYER = 'layer2'  # 用于特征图可视化的层
    
    # Grad-CAM设置
    GRADCAM_LAYER = 'layer4'  # ResNet的最后一个卷积块
    
    @classmethod
    def get_device(cls):
        """获取计算设备"""
        import torch
        
        if cls.DEVICE == 'auto':
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif cls.DEVICE == 'cuda':
            if torch.cuda.is_available():
                return torch.device("cuda")
            else:
                print("警告: CUDA不可用，使用CPU")
                return torch.device("cpu")
        else:
            return torch.device("cpu")
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        dirs = [cls.SAVE_DIR, cls.LOG_DIR, cls.RESULT_DIR]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    @classmethod
    def print_config(cls):
        """打印配置信息"""
        print("=" * 60)
        print("配置信息")
        print("=" * 60)
        
        print(f"数据目录: {cls.DATA_DIR}")
        print(f"类别数量: {cls.NUM_CLASSES}")
        print(f"类别名称: {cls.CLASS_NAMES}")
        print(f"图片大小: {cls.IMAGE_SIZE}x{cls.IMAGE_SIZE}")
        
        print(f"\n模型设置:")
        print(f"  模型名称: {cls.MODEL_NAME}")
        print(f"  预训练: {cls.PRETRAINED}")
        print(f"  冻结特征层: {cls.FREEZE_FEATURES}")
        
        print(f"\n训练设置:")
        print(f"  批次大小: {cls.BATCH_SIZE}")
        print(f"  训练轮数: {cls.NUM_EPOCHS}")
        print(f"  学习率: {cls.LEARNING_RATE}")
        print(f"  优化器: {cls.OPTIMIZER}")
        print(f"  使用Focal Loss: {cls.USE_FOCAL_LOSS}")
        
        print(f"\n系统设置:")
        print(f"  设备: {cls.get_device()}")
        print(f"  工作进程数: {cls.NUM_WORKERS}")
        print(f"  保存目录: {cls.SAVE_DIR}")
        
        print("=" * 60)

# 创建不同场景的配置
class QuickTrainConfig(Config):
    """快速训练配置（用于测试）"""
    NUM_EPOCHS = 5
    BATCH_SIZE = 16
    MODEL_NAME = 'resnet18'

class HighAccuracyConfig(Config):
    """高精度训练配置"""
    NUM_EPOCHS = 50
    LEARNING_RATE = 0.0001
    MODEL_NAME = 'resnet101'
    BATCH_SIZE = 16  # 更大的模型需要更小的批次

class CPUConfig(Config):
    """CPU训练配置"""
    DEVICE = 'cpu'
    BATCH_SIZE = 16
    NUM_WORKERS = 2
    MODEL_NAME = 'resnet18'

# 根据需要选择配置
def get_config(config_name='default'):
    """获取指定的配置"""
    configs = {
        'default': Config,
        'quick': QuickTrainConfig,
        'high_accuracy': HighAccuracyConfig,
        'cpu': CPUConfig,
    }
    
    if config_name not in configs:
        print(f"警告: 未知配置 '{config_name}'，使用默认配置")
        config_name = 'default'
    
    return configs[config_name]

if __name__ == "__main__":
    # 测试配置
    print("默认配置:")
    Config.print_config()
    
    print("\n\n快速训练配置:")
    QuickTrainConfig.print_config()
    
    print("\n\n高精度配置:")
    HighAccuracyConfig.print_config()
    
    print("\n\nCPU配置:")
    CPUConfig.print_config() 