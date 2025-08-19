#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
胸部X光片分类项目主程序
支持训练、评估、可视化等功能
"""

import argparse
import os
import sys
import torch

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

from dataset import create_data_loaders, visualize_samples, ChestXRayDataset
from model import create_model, count_parameters
from train import main as train_main, evaluate_model
from visualize import load_and_visualize, visualize_gradcam, visualize_feature_maps

def setup_environment():
    """设置环境"""
    # 设置中文字体支持
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置随机种子
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(42)

def data_exploration(args):
    """数据探索功能"""
    print("=" * 50)
    print("数据探索")
    print("=" * 50)
    
    # 创建数据集
    train_dataset = ChestXRayDataset(args.data_dir, split='train')
    test_dataset = ChestXRayDataset(args.data_dir, split='test')
    
    print(f"\n数据集统计:")
    print(f"训练集大小: {len(train_dataset)}")
    print(f"测试集大小: {len(test_dataset)}")
    
    # 统计类别分布
    train_normal = sum(1 for _, label in train_dataset.samples if label == 0)
    train_pneumonia = sum(1 for _, label in train_dataset.samples if label == 1)
    test_normal = sum(1 for _, label in test_dataset.samples if label == 0)
    test_pneumonia = sum(1 for _, label in test_dataset.samples if label == 1)
    
    print(f"\n训练集类别分布:")
    print(f"  正常: {train_normal} ({train_normal/len(train_dataset)*100:.1f}%)")
    print(f"  肺炎: {train_pneumonia} ({train_pneumonia/len(train_dataset)*100:.1f}%)")
    
    print(f"\n测试集类别分布:")
    print(f"  正常: {test_normal} ({test_normal/len(test_dataset)*100:.1f}%)")
    print(f"  肺炎: {test_pneumonia} ({test_pneumonia/len(test_dataset)*100:.1f}%)")
    
    # 可视化样本
    print("\n正在生成样本可视化...")
    visualize_samples(train_dataset, num_samples=8)

def model_info(args):
    """显示模型信息"""
    print("=" * 50)
    print(f"模型信息: {args.model_name}")
    print("=" * 50)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_model(
        num_classes=2,
        model_name=args.model_name,
        pretrained=args.pretrained,
        freeze_features=args.freeze_features
    ).to(device)
    
    print(f"设备: {device}")
    print(f"预训练: {'是' if args.pretrained else '否'}")
    print(f"冻结特征层: {'是' if args.freeze_features else '否'}")
    
    # 显示参数统计
    count_parameters(model)
    
    # 测试前向传播
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    with torch.no_grad():
        output = model(dummy_input)
    print(f"\n输入形状: {dummy_input.shape}")
    print(f"输出形状: {output.shape}")

def train_model(args):
    """训练模型"""
    print("=" * 50)
    print("开始训练模型")
    print("=" * 50)
    
    # 直接调用训练主函数
    train_main()

def evaluate_checkpoint(args):
    """评估已训练的模型"""
    print("=" * 50)
    print("评估模型")
    print("=" * 50)
    
    if not os.path.exists(args.checkpoint):
        print(f"错误: 找不到检查点文件 {args.checkpoint}")
        return
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型 (修复安全警告)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = create_model(num_classes=2, model_name='resnet50').to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    print(f"加载检查点: {args.checkpoint}")
    print(f"最佳精度: {checkpoint['best_acc']:.4f}")
    
    # 创建数据加载器
    _, test_loader = create_data_loaders(args.data_dir, batch_size=32)
    
    # 评估模型
    evaluate_model(model, test_loader, device)

def visualize_model(args):
    """可视化模型"""
    print("=" * 50)
    print("可视化模型")
    print("=" * 50)
    
    if not os.path.exists(args.checkpoint):
        print(f"错误: 找不到检查点文件 {args.checkpoint}")
        return
    
    # 使用可视化函数
    load_and_visualize(args.checkpoint, args.data_dir, args.image_path)

def predict_single(args):
    """对单张图片进行预测"""
    print("=" * 50)
    print("单张图片预测")
    print("=" * 50)
    
    if not os.path.exists(args.checkpoint):
        print(f"错误: 找不到检查点文件 {args.checkpoint}")
        return
    
    if not os.path.exists(args.image_path):
        print(f"错误: 找不到图片文件 {args.image_path}")
        return
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型 (修复安全警告)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = create_model(num_classes=2, model_name='resnet50').to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # 加载和预处理图像
    from dataset import get_data_transforms
    from PIL import Image
    import torch.nn.functional as F
    
    _, test_transform = get_data_transforms()
    image = Image.open(args.image_path).convert('RGB')
    input_tensor = test_transform(image).unsqueeze(0).to(device)
    
    # 预测
    with torch.no_grad():
        output = model(input_tensor)
        probs = F.softmax(output, dim=1)
        _, pred = torch.max(output, 1)
    
    class_names = ['NORMAL', 'PNEUMONIA']
    predicted_class = class_names[pred.item()]
    confidence = probs[0][pred.item()].item()
    
    print(f"图片路径: {args.image_path}")
    print(f"预测结果: {predicted_class}")
    print(f"置信度: {confidence:.4f}")
    print(f"概率分布:")
    for i, class_name in enumerate(class_names):
        print(f"  {class_name}: {probs[0][i].item():.4f}")
    
    # 可视化Grad-CAM
    if args.show_gradcam:
        print("\n生成Grad-CAM可视化...")
        visualize_gradcam(model, args.image_path, device)

def main():
    """主函数"""
    setup_environment()
    
    parser = argparse.ArgumentParser(description='胸部X光片分类项目')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 数据探索
    explore_parser = subparsers.add_parser('explore', help='探索数据集')
    explore_parser.add_argument('--data_dir', type=str, default='../../data/ChestXRay',
                               help='数据目录路径')
    
    # 模型信息
    info_parser = subparsers.add_parser('info', help='显示模型信息')
    info_parser.add_argument('--data_dir', type=str, default='../../data/ChestXRay',
                            help='数据目录路径')
    info_parser.add_argument('--model_name', type=str, default='resnet50',
                            choices=['resnet18', 'resnet34', 'resnet50', 'resnet101'],
                            help='模型名称')
    info_parser.add_argument('--pretrained', action='store_true', default=True,
                            help='使用预训练权重')
    info_parser.add_argument('--freeze_features', action='store_true',
                            help='冻结特征提取层')
    
    # 训练
    train_parser = subparsers.add_parser('train', help='训练模型')
    train_parser.add_argument('--data_dir', type=str, default='../../data/ChestXRay',
                             help='数据目录路径')
    
    # 评估
    eval_parser = subparsers.add_parser('eval', help='评估模型')
    eval_parser.add_argument('--data_dir', type=str, default='../../data/ChestXRay',
                            help='数据目录路径')
    eval_parser.add_argument('--checkpoint', type=str, default='checkpoints/best_model.pth',
                            help='模型检查点路径')
    
    # 可视化
    viz_parser = subparsers.add_parser('visualize', help='可视化模型和结果')
    viz_parser.add_argument('--data_dir', type=str, default='../../data/ChestXRay',
                           help='数据目录路径')
    viz_parser.add_argument('--checkpoint', type=str, default='checkpoints/best_model.pth',
                           help='模型检查点路径')
    viz_parser.add_argument('--image_path', type=str,
                           help='单张图片路径（用于可视化）')
    
    # 预测
    pred_parser = subparsers.add_parser('predict', help='对单张图片进行预测')
    pred_parser.add_argument('--data_dir', type=str, default='../../data/ChestXRay',
                            help='数据目录路径')
    pred_parser.add_argument('--checkpoint', type=str, default='checkpoints/best_model.pth',
                            help='模型检查点路径')
    pred_parser.add_argument('--image_path', type=str, required=True,
                            help='单张图片路径（必需）')
    pred_parser.add_argument('--show_gradcam', action='store_true',
                            help='显示Grad-CAM可视化')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # 检查数据目录
    if hasattr(args, 'data_dir') and not os.path.exists(args.data_dir):
        print(f"错误: 数据目录不存在 {args.data_dir}")
        return
    
    # 执行相应命令
    if args.command == 'explore':
        data_exploration(args)
    elif args.command == 'info':
        model_info(args)
    elif args.command == 'train':
        train_model(args)
    elif args.command == 'eval':
        evaluate_checkpoint(args)
    elif args.command == 'visualize':
        visualize_model(args)
    elif args.command == 'predict':
        predict_single(args)

if __name__ == "__main__":
    main() 