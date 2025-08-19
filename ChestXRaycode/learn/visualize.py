import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import os
from tqdm import tqdm

from dataset import ChestXRayDataset, get_data_transforms
from model import create_model

class GradCAM:
    """Grad-CAM可视化类"""
    
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # 注册hook
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """保存前向传播的激活值"""
        self.activations = output
    
    def save_gradient(self, module, grad_input, grad_output):
        """保存反向传播的梯度"""
        self.gradients = grad_output[0]
    
    def generate_cam(self, input_image, class_idx=None):
        """生成Grad-CAM热力图"""
        self.model.eval()
        
        # 前向传播
        output = self.model(input_image)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        
        # 反向传播
        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0][class_idx] = 1
        output.backward(gradient=one_hot, retain_graph=True)
        
        # 计算权重
        gradients = self.gradients[0]  # [C, H, W]
        activations = self.activations[0]  # [C, H, W]
        
        weights = torch.mean(gradients, dim=(1, 2))  # [C]
        
        # 生成热力图
        cam = torch.zeros(activations.shape[1:], dtype=torch.float32)  # [H, W]
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # ReLU
        cam = F.relu(cam)
        
        # 归一化
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam.detach().cpu().numpy(), class_idx

def visualize_gradcam(model, image_path, device, class_names=['NORMAL', 'PNEUMONIA']):
    """可视化Grad-CAM"""
    # 获取目标层（ResNet的最后一个卷积层）
    if hasattr(model.backbone, 'layer4'):
        target_layer = model.backbone.layer4[-1].conv2
    else:
        print("无法找到目标层")
        return
    
    # 创建Grad-CAM对象
    gradcam = GradCAM(model, target_layer)
    
    # 加载和预处理图像
    _, test_transform = get_data_transforms()
    
    # 加载原始图像用于显示
    original_image = Image.open(image_path).convert('RGB')
    
    # 预处理图像
    input_tensor = test_transform(original_image).unsqueeze(0).to(device)
    
    # 生成Grad-CAM
    cam, predicted_class = gradcam.generate_cam(input_tensor)
    
    # 调整热力图大小以匹配原始图像
    original_size = original_image.size
    cam_resized = cv2.resize(cam, original_size)
    
    # 可视化结果
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 原始图像
    axes[0].imshow(original_image)
    axes[0].set_title('原始图像')
    axes[0].axis('off')
    
    # 热力图
    axes[1].imshow(cam_resized, cmap='jet')
    axes[1].set_title(f'Grad-CAM热力图\n预测: {class_names[predicted_class]}')
    axes[1].axis('off')
    
    # 叠加图像
    original_array = np.array(original_image) / 255.0
    cam_colored = plt.cm.jet(cam_resized)[:, :, :3]
    overlay = 0.6 * original_array + 0.4 * cam_colored
    axes[2].imshow(overlay)
    axes[2].set_title('叠加图像')
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return cam_resized, predicted_class

def visualize_feature_maps(model, image_path, device, layer_name='layer2'):
    """可视化特征图"""
    model.eval()
    
    # 加载和预处理图像
    _, test_transform = get_data_transforms()
    original_image = Image.open(image_path).convert('RGB')
    input_tensor = test_transform(original_image).unsqueeze(0).to(device)
    
    # 获取特征图
    with torch.no_grad():
        features = model.get_feature_maps(input_tensor)
    
    if layer_name not in features:
        print(f"找不到层 {layer_name}")
        return
    
    feature_maps = features[layer_name][0]  # [C, H, W]
    num_channels = feature_maps.shape[0]
    
    # 选择要显示的通道数
    num_display = min(16, num_channels)
    
    # 可视化
    fig, axes = plt.subplots(4, 4, figsize=(12, 12))
    fig.suptitle(f'{layer_name} 特征图', fontsize=16)
    
    for i in range(num_display):
        row = i // 4
        col = i % 4
        
        feature_map = feature_maps[i].cpu().numpy()
        axes[row, col].imshow(feature_map, cmap='viridis')
        axes[row, col].set_title(f'通道 {i}')
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()

def visualize_predictions(model, test_loader, device, num_samples=16, class_names=['NORMAL', 'PNEUMONIA']):
    """可视化预测结果"""
    model.eval()
    
    # 收集一些样本
    images = []
    labels = []
    predictions = []
    probabilities = []
    
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = F.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            for i in range(inputs.size(0)):
                if len(images) < num_samples:
                    # 反标准化图像用于显示
                    img = inputs[i].cpu()
                    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
                    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
                    img = img * std + mean
                    img = torch.clamp(img, 0, 1)
                    
                    images.append(img)
                    labels.append(targets[i].item())
                    predictions.append(preds[i].item())
                    probabilities.append(probs[i].cpu().numpy())
                else:
                    break
            
            if len(images) >= num_samples:
                break
    
    # 可视化
    rows = 4
    cols = 4
    fig, axes = plt.subplots(rows, cols, figsize=(16, 16))
    fig.suptitle('预测结果展示', fontsize=16)
    
    for i in range(num_samples):
        row = i // cols
        col = i % cols
        
        # 显示图像
        img = images[i].permute(1, 2, 0).numpy()
        axes[row, col].imshow(img)
        
        # 设置标题
        true_label = class_names[labels[i]]
        pred_label = class_names[predictions[i]]
        confidence = probabilities[i][predictions[i]]
        
        color = 'green' if labels[i] == predictions[i] else 'red'
        title = f'真实: {true_label}\n预测: {pred_label}\n置信度: {confidence:.3f}'
        axes[row, col].set_title(title, color=color, fontsize=10)
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()

def analyze_model_performance(model, test_loader, device, save_dir='analysis'):
    """深入分析模型性能"""
    os.makedirs(save_dir, exist_ok=True)
    
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    
    print("收集预测结果...")
    with torch.no_grad():
        for inputs, labels in tqdm(test_loader):
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            probs = F.softmax(outputs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    class_names = ['NORMAL', 'PNEUMONIA']
    
    # 1. 混淆矩阵
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.savefig(os.path.join(save_dir, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. 分类报告
    report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
    print("\n分类报告:")
    print(classification_report(all_labels, all_preds, target_names=class_names))
    
    # 3. 置信度分布
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    confidence_correct = all_probs[all_preds == all_labels].max(axis=1)
    confidence_wrong = all_probs[all_preds != all_labels].max(axis=1)
    
    plt.hist(confidence_correct, alpha=0.7, label='正确预测', bins=20, color='green')
    plt.hist(confidence_wrong, alpha=0.7, label='错误预测', bins=20, color='red')
    plt.xlabel('置信度')
    plt.ylabel('频次')
    plt.title('预测置信度分布')
    plt.legend()
    
    # 4. 各类别置信度
    plt.subplot(1, 2, 2)
    for i, class_name in enumerate(class_names):
        class_confidence = all_probs[all_labels == i, i]
        plt.hist(class_confidence, alpha=0.7, label=f'{class_name}', bins=20)
    
    plt.xlabel('置信度')
    plt.ylabel('频次')
    plt.title('各类别置信度分布')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'confidence_analysis.png'), dpi=300, bbox_inches='tight')
    plt.show()
    
    # 5. 错误案例分析
    wrong_indices = np.where(all_preds != all_labels)[0]
    if len(wrong_indices) > 0:
        print(f"\n错误预测案例数量: {len(wrong_indices)}")
        print(f"错误率: {len(wrong_indices) / len(all_labels) * 100:.2f}%")
    
    return report

def load_and_visualize(checkpoint_path, data_dir, image_path=None):
    """加载模型并进行可视化"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载检查点 (修复安全警告)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    
    # 创建模型
    model = create_model(num_classes=2, model_name='resnet50').to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    print(f"加载模型检查点，最佳精度: {checkpoint['best_acc']:.4f}")
    
    # 如果提供了图像路径，进行Grad-CAM可视化
    if image_path and os.path.exists(image_path):
        print("生成Grad-CAM可视化...")
        visualize_gradcam(model, image_path, device)
        
        print("生成特征图可视化...")
        visualize_feature_maps(model, image_path, device)
    
    # 创建测试数据加载器
    from dataset import create_data_loaders
    _, test_loader = create_data_loaders(data_dir, batch_size=32)
    
    # 可视化预测结果
    print("可视化预测结果...")
    visualize_predictions(model, test_loader, device)
    
    # 性能分析
    print("分析模型性能...")
    analyze_model_performance(model, test_loader, device)

if __name__ == "__main__":
    # 示例使用
    checkpoint_path = "checkpoints/best_model.pth"
    data_dir = "../../data/ChestXRay"
    
    # 选择一张图片进行可视化（可选）
    image_path = "../../data/ChestXRay/test/PNEUMONIA/person1_virus_11.jpeg"
    
    if os.path.exists(checkpoint_path):
        load_and_visualize(checkpoint_path, data_dir, image_path)
    else:
        print(f"找不到检查点文件: {checkpoint_path}")
        print("请先运行训练脚本生成模型") 