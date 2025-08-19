#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
胸部X光片分类项目 - 快速开始脚本
一键体验项目的主要功能
"""

import os
import sys
import subprocess

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def run_command(description, command):
    """运行命令并显示结果"""
    print(f"\n🚀 {description}")
    print(f"执行命令: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 成功!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 失败!")
            if result.stderr:
                print(result.stderr)
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def check_environment():
    """检查环境"""
    print_header("环境检查")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查必要库
    required_packages = ['torch', 'torchvision', 'PIL', 'matplotlib', 'sklearn', 'tqdm']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查数据目录
    data_dir = "../../data/ChestXRay"
    if os.path.exists(data_dir):
        print(f"✅ 数据目录: {data_dir}")
        
        # 检查数据子目录
        train_dir = os.path.join(data_dir, "train")
        test_dir = os.path.join(data_dir, "test")
        
        if os.path.exists(train_dir) and os.path.exists(test_dir):
            print("✅ 训练和测试目录存在")
            
            # 统计数据
            train_normal = len(os.listdir(os.path.join(train_dir, "NORMAL"))) if os.path.exists(os.path.join(train_dir, "NORMAL")) else 0
            train_pneumonia = len(os.listdir(os.path.join(train_dir, "PNEUMONIA"))) if os.path.exists(os.path.join(train_dir, "PNEUMONIA")) else 0
            test_normal = len(os.listdir(os.path.join(test_dir, "NORMAL"))) if os.path.exists(os.path.join(test_dir, "NORMAL")) else 0
            test_pneumonia = len(os.listdir(os.path.join(test_dir, "PNEUMONIA"))) if os.path.exists(os.path.join(test_dir, "PNEUMONIA")) else 0
            
            print(f"📊 训练集: 正常({train_normal}) 肺炎({train_pneumonia})")
            print(f"📊 测试集: 正常({test_normal}) 肺炎({test_pneumonia})")
        else:
            print("❌ 数据子目录结构不正确")
            return False
    else:
        print(f"❌ 数据目录不存在: {data_dir}")
        return False
    
    return True

def demo_workflow():
    """演示完整工作流程"""
    
    if not check_environment():
        print("\n❌ 环境检查失败，请先解决上述问题")
        return
    
    print_header("胸部X光片分类项目 - 完整演示")
    
    # 1. 数据探索
    run_command(
        "数据探索 - 查看数据集基本信息",
        "python main.py explore"
    )
    
    # 2. 模型信息
    run_command(
        "模型信息 - 查看ResNet50模型结构",
        "python main.py info --model_name resnet50"
    )
    
    # 3. 快速训练演示（使用较少的epoch）
    print("\n🤔 是否要进行快速训练演示？(这将花费几分钟时间)")
    choice = input("输入 'y' 继续，其他键跳过: ").lower()
    
    if choice == 'y':
        # 创建一个临时的快速训练脚本
        quick_train_script = """
import sys
sys.path.append('.')
from train import main as train_main
from config import QuickTrainConfig

# 使用快速训练配置
import train
original_config = train.config if hasattr(train, 'config') else None

# 修改训练主函数使用快速配置
def quick_train():
    config = {
        'data_dir': '../../data/ChestXRay',
        'batch_size': 16,
        'num_epochs': 2,  # 只训练2个epoch做演示
        'learning_rate': 0.001,
        'model_name': 'resnet18',  # 使用较小的模型
        'pretrained': True,
        'freeze_features': False,
        'use_focal_loss': True,
        'num_workers': 2,
        'save_dir': 'demo_checkpoints'
    }
    
    import os
    import torch
    from dataset import create_data_loaders
    from model import create_model, FocalLoss
    from train import Trainer
    import torch.optim as optim
    from torch.optim import lr_scheduler
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 创建数据加载器
    train_loader, test_loader = create_data_loaders(
        config['data_dir'], 
        batch_size=config['batch_size'],
        num_workers=config['num_workers']
    )
    
    # 创建模型
    model = create_model(
        num_classes=2,
        model_name=config['model_name'],
        pretrained=config['pretrained'],
        freeze_features=config['freeze_features']
    ).to(device)
    
    # 损失函数和优化器
    criterion = FocalLoss(alpha=1, gamma=2)
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])
    scheduler = lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    
    # 创建训练器
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        save_dir=config['save_dir']
    )
    
    # 开始训练
    print("开始快速训练演示...")
    trained_model = trainer.train(num_epochs=config['num_epochs'])
    print("快速训练演示完成!")

if __name__ == "__main__":
    quick_train()
"""
        
        # 保存临时脚本
        with open("temp_quick_train.py", "w", encoding="utf-8") as f:
            f.write(quick_train_script)
        
        run_command(
            "快速训练演示 (2个epoch, ResNet18)",
            "python temp_quick_train.py"
        )
        
        # 删除临时脚本
        if os.path.exists("temp_quick_train.py"):
            os.remove("temp_quick_train.py")
    
    # 4. 检查是否有已训练的模型
    checkpoint_paths = ["checkpoints/best_model.pth", "demo_checkpoints/best_model.pth"]
    available_checkpoint = None
    
    for path in checkpoint_paths:
        if os.path.exists(path):
            available_checkpoint = path
            break
    
    if available_checkpoint:
        print(f"\n✅ 找到已训练模型: {available_checkpoint}")
        
        # 模型评估
        run_command(
            "模型评估 - 测试集性能",
            f"python main.py eval --checkpoint {available_checkpoint}"
        )
        
        # 查找一张测试图片
        test_image_path = None
        test_dirs = [
            "../../data/ChestXRay/test/PNEUMONIA",
            "../../data/ChestXRay/test/NORMAL"
        ]
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                images = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if images:
                    test_image_path = os.path.join(test_dir, images[0])
                    break
        
        if test_image_path:
            # 单张图片预测
            run_command(
                f"单张图片预测 - {test_image_path}",
                f"python main.py predict --image_path '{test_image_path}' --checkpoint {available_checkpoint}"
            )
        
        # 可视化
        print("\n🤔 是否要生成可视化图表？(可能需要图形界面支持)")
        choice = input("输入 'y' 继续，其他键跳过: ").lower()
        
        if choice == 'y':
            run_command(
                "生成可视化分析",
                f"python main.py visualize --checkpoint {available_checkpoint}"
            )
    else:
        print("\n⚠️  没有找到已训练的模型")
        print("要获得完整体验，请先运行: python main.py train")

def interactive_menu():
    """交互式菜单"""
    print_header("胸部X光片分类项目 - 交互式菜单")
    
    while True:
        print("\n请选择功能:")
        print("1. 🔍 环境检查")
        print("2. 📊 数据探索") 
        print("3. 🏗️  模型信息")
        print("4. 🚀 完整演示")
        print("5. 💡 快速训练")
        print("6. 📝 查看帮助")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-6): ").strip()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            check_environment()
        elif choice == '2':
            run_command("数据探索", "python main.py explore")
        elif choice == '3':
            model_name = input("请输入模型名称 (resnet18/resnet34/resnet50/resnet101) [默认: resnet50]: ").strip()
            if not model_name:
                model_name = "resnet50"
            run_command(f"查看{model_name}模型信息", f"python main.py info --model_name {model_name}")
        elif choice == '4':
            demo_workflow()
        elif choice == '5':
            print("⚠️  完整训练可能需要较长时间")
            confirm = input("确认开始训练？(y/N): ").lower()
            if confirm == 'y':
                run_command("开始训练", "python main.py train")
        elif choice == '6':
            run_command("查看帮助", "python main.py --help")
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    print("🏥 欢迎使用胸部X光片分类项目!")
    print("这是一个基于PyTorch的医学图像分类系统")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_workflow()
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_environment()
    else:
        interactive_menu() 