import os
import time
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import seaborn as sns
from tqdm import tqdm

from dataset import create_data_loaders
from model import create_model, FocalLoss

class Trainer:
    """训练器类"""
    
    def __init__(self, model, train_loader, test_loader, criterion, optimizer, scheduler, device, save_dir='checkpoints'):
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.save_dir = save_dir
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 记录训练历史
        self.train_losses = []
        self.train_accs = []
        self.test_losses = []
        self.test_accs = []
        self.best_acc = 0.0
        self.best_model_wts = None
    
    def train_epoch(self):
        """训练一个epoch"""
        self.model.train()
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0
        
        # 使用tqdm显示进度条
        pbar = tqdm(self.train_loader, desc='训练', leave=False)
        for inputs, labels in pbar:
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)
            
            # 零化参数梯度
            self.optimizer.zero_grad()
            
            # 前向传播
            with torch.set_grad_enabled(True):
                outputs = self.model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = self.criterion(outputs, labels)
                
                # 反向传播和优化
                loss.backward()
                self.optimizer.step()
            
            # 统计
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            total_samples += inputs.size(0)
            
            # 更新进度条
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{running_corrects.double() / total_samples:.4f}'
            })
        
        epoch_loss = running_loss / total_samples
        epoch_acc = running_corrects.double() / total_samples
        
        return epoch_loss, epoch_acc.item()
    
    def validate_epoch(self):
        """验证一个epoch"""
        self.model.eval()
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0
        all_preds = []
        all_labels = []
        all_probs = []
        
        # 使用tqdm显示进度条
        pbar = tqdm(self.test_loader, desc='验证', leave=False)
        for inputs, labels in pbar:
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)
            
            # 前向传播
            with torch.set_grad_enabled(False):
                outputs = self.model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = self.criterion(outputs, labels)
                
                # 获取概率用于AUC计算
                probs = torch.softmax(outputs, dim=1)
            
            # 统计
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            total_samples += inputs.size(0)
            
            # 保存预测结果
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            
            # 更新进度条
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{running_corrects.double() / total_samples:.4f}'
            })
        
        epoch_loss = running_loss / total_samples
        epoch_acc = running_corrects.double() / total_samples
        
        return epoch_loss, epoch_acc.item(), all_preds, all_labels, all_probs
    
    def train(self, num_epochs=25):
        """训练模型"""
        print(f"开始训练，使用设备: {self.device}")
        print(f"训练集大小: {len(self.train_loader.dataset)}")
        print(f"测试集大小: {len(self.test_loader.dataset)}")
        print("-" * 50)
        
        since = time.time()
        
        for epoch in range(num_epochs):
            print(f'Epoch {epoch+1}/{num_epochs}')
            print('-' * 20)
            
            # 训练阶段
            train_loss, train_acc = self.train_epoch()
            self.train_losses.append(train_loss)
            self.train_accs.append(train_acc)
            
            # 验证阶段
            test_loss, test_acc, test_preds, test_labels, test_probs = self.validate_epoch()
            self.test_losses.append(test_loss)
            self.test_accs.append(test_acc)
            
            # 学习率调度
            if self.scheduler:
                self.scheduler.step()
            
            print(f'训练损失: {train_loss:.4f} 训练精度: {train_acc:.4f}')
            print(f'验证损失: {test_loss:.4f} 验证精度: {test_acc:.4f}')
            
            # 保存最佳模型
            if test_acc > self.best_acc:
                self.best_acc = test_acc
                self.best_model_wts = copy.deepcopy(self.model.state_dict())
                
                # 保存检查点
                checkpoint = {
                    'epoch': epoch + 1,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'best_acc': self.best_acc,
                    'train_losses': self.train_losses,
                    'train_accs': self.train_accs,
                    'test_losses': self.test_losses,
                    'test_accs': self.test_accs,
                }
                torch.save(checkpoint, os.path.join(self.save_dir, 'best_model.pth'))
                print(f'保存新的最佳模型，精度: {test_acc:.4f}')
            
            print()
        
        time_elapsed = time.time() - since
        print(f'训练完成，用时: {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
        print(f'最佳验证精度: {self.best_acc:.4f}')
        
        # 加载最佳模型权重
        if self.best_model_wts is not None:
            self.model.load_state_dict(self.best_model_wts)
        
        return self.model
    
    def plot_training_history(self):
        """绘制训练历史"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # 损失曲线
        epochs = range(1, len(self.train_losses) + 1)
        ax1.plot(epochs, self.train_losses, 'b-', label='训练损失')
        ax1.plot(epochs, self.test_losses, 'r-', label='验证损失')
        ax1.set_title('训练和验证损失')
        ax1.set_xlabel('Epochs')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # 精度曲线
        ax2.plot(epochs, self.train_accs, 'b-', label='训练精度')
        ax2.plot(epochs, self.test_accs, 'r-', label='验证精度')
        ax2.set_title('训练和验证精度')
        ax2.set_xlabel('Epochs')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.save_dir, 'training_history.png'), dpi=300, bbox_inches='tight')
        plt.show()

def evaluate_model(model, test_loader, device, class_names=['NORMAL', 'PNEUMONIA']):
    """评估模型并生成详细报告"""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    
    print("正在评估模型...")
    with torch.no_grad():
        for inputs, labels in tqdm(test_loader):
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            probs = torch.softmax(outputs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    # 转换为numpy数组
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    # 打印分类报告
    print("\n分类报告:")
    print(classification_report(all_labels, all_preds, target_names=class_names))
    
    # 混淆矩阵
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.show()
    
    # ROC曲线
    if len(class_names) == 2:  # 二分类
        fpr, tpr, _ = roc_curve(all_labels, all_probs[:, 1])
        auc_score = roc_auc_score(all_labels, all_probs[:, 1])
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC曲线 (AUC = {auc_score:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('假正率 (False Positive Rate)')
        plt.ylabel('真正率 (True Positive Rate)')
        plt.title('ROC曲线')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.show()
        
        print(f"\nAUC分数: {auc_score:.4f}")
    
    return all_preds, all_labels, all_probs

def main():
    """主训练函数"""
    # 配置参数
    config = {
        'data_dir': '../../data/ChestXRay',
        'batch_size': 32,
        'num_epochs': 20,
        'learning_rate': 0.001,
        'model_name': 'resnet50',  # 'resnet18', 'resnet34', 'resnet50', 'resnet101'
        'pretrained': True,
        'freeze_features': False,
        'use_focal_loss': True,
        'num_workers': 4,
        'save_dir': 'checkpoints'
    }
    
    print("配置参数:")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("-" * 50)
    
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 创建数据加载器
    print("创建数据加载器...")
    train_loader, test_loader = create_data_loaders(
        config['data_dir'], 
        batch_size=config['batch_size'],
        num_workers=config['num_workers']
    )
    
    # 创建模型
    print("创建模型...")
    model = create_model(
        num_classes=2,
        model_name=config['model_name'],
        pretrained=config['pretrained'],
        freeze_features=config['freeze_features']
    ).to(device)
    
    # 损失函数
    if config['use_focal_loss']:
        criterion = FocalLoss(alpha=1, gamma=2)
        print("使用Focal Loss")
    else:
        # 计算类别权重
        train_dataset = train_loader.dataset
        normal_count = sum(1 for _, label in train_dataset.samples if label == 0)
        pneumonia_count = sum(1 for _, label in train_dataset.samples if label == 1)
        total = normal_count + pneumonia_count
        
        # 类别权重：样本少的类别权重大
        weights = torch.tensor([total / (2 * normal_count), total / (2 * pneumonia_count)]).to(device)
        criterion = nn.CrossEntropyLoss(weight=weights)
        print(f"使用加权交叉熵损失，权重: {weights}")
    
    # 优化器
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])
    
    # 学习率调度器
    scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
    
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
    print("开始训练...")
    trained_model = trainer.train(num_epochs=config['num_epochs'])
    
    # 绘制训练历史
    trainer.plot_training_history()
    
    # 评估模型
    print("\n最终评估:")
    evaluate_model(trained_model, test_loader, device)
    
    print("训练完成！模型已保存到 checkpoints/ 目录")

if __name__ == "__main__":
    main() 