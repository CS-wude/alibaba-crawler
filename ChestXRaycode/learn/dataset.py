import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

class ChestXRayDataset(Dataset):
    """胸部X光片数据集类"""
    
    def __init__(self, data_dir, split='train', transform=None):
        """
        Args:
            data_dir (string): 数据根目录路径
            split (string): 'train' 或 'test'
            transform (callable, optional): 应用于样本的变换
        """
        self.data_dir = data_dir
        self.split = split
        self.transform = transform
        
        # 类别映射
        self.classes = ['NORMAL', 'PNEUMONIA']
        self.class_to_idx = {'NORMAL': 0, 'PNEUMONIA': 1}
        
        # 获取所有图片路径和标签
        self.samples = []
        split_dir = os.path.join(data_dir, split)
        
        for class_name in self.classes:
            class_dir = os.path.join(split_dir, class_name)
            if os.path.exists(class_dir):
                for img_name in os.listdir(class_dir):
                    if img_name.lower().endswith(('.jpeg', '.jpg', '.png')):
                        img_path = os.path.join(class_dir, img_name)
                        label = self.class_to_idx[class_name]
                        self.samples.append((img_path, label))
        
        print(f"在 {split} 集合中找到 {len(self.samples)} 个样本")
        
        # 统计各类别数量
        normal_count = sum(1 for _, label in self.samples if label == 0)
        pneumonia_count = sum(1 for _, label in self.samples if label == 1)
        print(f"正常: {normal_count}, 肺炎: {pneumonia_count}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # 加载图片
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"无法加载图片 {img_path}: {e}")
            # 返回一个默认的黑色图片
            image = Image.new('RGB', (224, 224), (0, 0, 0))
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        return image, label

def get_data_transforms(input_size=224):
    """获取数据变换"""
    
    # 训练时的数据增强
    train_transforms = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 测试时不进行数据增强
    test_transforms = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    return train_transforms, test_transforms

def create_data_loaders(data_dir, batch_size=32, num_workers=4):
    """创建数据加载器"""
    
    train_transforms, test_transforms = get_data_transforms()
    
    # 创建数据集
    train_dataset = ChestXRayDataset(data_dir, split='train', transform=train_transforms)
    test_dataset = ChestXRayDataset(data_dir, split='test', transform=test_transforms)
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, test_loader

def visualize_samples(dataset, num_samples=8):
    """可视化数据样本"""
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    fig.suptitle('胸部X光片样本', fontsize=16)
    
    # 创建一个不包含标准化的变换用于可视化
    vis_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    
    for i in range(num_samples):
        idx = np.random.randint(len(dataset))
        img_path, label = dataset.samples[idx]
        
        # 加载原始图片用于可视化
        image = Image.open(img_path).convert('RGB')
        image = vis_transform(image)
        
        row = i // 4
        col = i % 4
        
        axes[row, col].imshow(image.permute(1, 2, 0))
        axes[row, col].set_title(f'{dataset.classes[label]}')
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 测试数据加载器
    data_dir = "../../data/ChestXRay"
    
    # 创建数据加载器
    train_loader, test_loader = create_data_loaders(data_dir, batch_size=16)
    
    print(f"训练批次数量: {len(train_loader)}")
    print(f"测试批次数量: {len(test_loader)}")
    
    # 查看一个批次的数据
    for images, labels in train_loader:
        print(f"图片张量形状: {images.shape}")
        print(f"标签张量形状: {labels.shape}")
        print(f"标签样本: {labels[:8]}")
        break
    
    # 可视化样本
    train_dataset = ChestXRayDataset(data_dir, split='train')
    visualize_samples(train_dataset) 