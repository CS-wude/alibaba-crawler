import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import matplotlib.pyplot as plt

class ChestXRayClassifier(nn.Module):
    """胸部X光片分类器，基于预训练的ResNet"""
    
    def __init__(self, num_classes=2, model_name='resnet50', pretrained=True, freeze_features=False):
        """
        Args:
            num_classes (int): 分类类别数量
            model_name (str): 预训练模型名称 ('resnet18', 'resnet34', 'resnet50', 'resnet101')
            pretrained (bool): 是否使用预训练权重
            freeze_features (bool): 是否冻结特征提取层
        """
        super(ChestXRayClassifier, self).__init__()
        
        self.num_classes = num_classes
        self.model_name = model_name
        
        # 加载预训练模型 (修复deprecation警告)
        if model_name == 'resnet18':
            if pretrained:
                self.backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            else:
                self.backbone = models.resnet18(weights=None)
            feature_dim = 512
        elif model_name == 'resnet34':
            if pretrained:
                self.backbone = models.resnet34(weights=models.ResNet34_Weights.IMAGENET1K_V1)
            else:
                self.backbone = models.resnet34(weights=None)
            feature_dim = 512
        elif model_name == 'resnet50':
            if pretrained:
                self.backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
            else:
                self.backbone = models.resnet50(weights=None)
            feature_dim = 2048
        elif model_name == 'resnet101':
            if pretrained:
                self.backbone = models.resnet101(weights=models.ResNet101_Weights.IMAGENET1K_V1)
            else:
                self.backbone = models.resnet101(weights=None)
            feature_dim = 2048
        else:
            raise ValueError(f"不支持的模型: {model_name}")
        
        # 冻结特征提取层（可选）
        if freeze_features:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # 替换最后的全连接层
        self.backbone.fc = nn.Identity()  # 移除原始的分类层
        
        # 自定义分类头
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )
        
        # 初始化新添加的层
        self._initialize_weights()
    
    def _initialize_weights(self):
        """初始化分类头的权重"""
        for m in self.classifier.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        # 通过backbone提取特征
        features = self.backbone(x)
        
        # 通过分类头进行分类
        output = self.classifier(features)
        
        return output
    
    def get_feature_maps(self, x):
        """获取特征图用于可视化"""
        features = {}
        
        # 逐层前向传播并保存特征图
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        features['conv1'] = x
        
        x = self.backbone.maxpool(x)
        
        x = self.backbone.layer1(x)
        features['layer1'] = x
        
        x = self.backbone.layer2(x)
        features['layer2'] = x
        
        x = self.backbone.layer3(x)
        features['layer3'] = x
        
        x = self.backbone.layer4(x)
        features['layer4'] = x
        
        return features

class FocalLoss(nn.Module):
    """Focal Loss 用于处理类别不平衡"""
    
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

def create_model(num_classes=2, model_name='resnet50', pretrained=True, freeze_features=False):
    """创建模型的便捷函数"""
    model = ChestXRayClassifier(
        num_classes=num_classes,
        model_name=model_name,
        pretrained=pretrained,
        freeze_features=freeze_features
    )
    return model

def count_parameters(model):
    """计算模型参数数量"""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"总参数数量: {total_params:,}")
    print(f"可训练参数数量: {trainable_params:,}")
    print(f"冻结参数数量: {total_params - trainable_params:,}")
    
    return total_params, trainable_params

def visualize_model_architecture(model, input_size=(1, 3, 224, 224)):
    """可视化模型架构"""
    print("=" * 50)
    print("模型架构:")
    print("=" * 50)
    print(model)
    print("=" * 50)
    
    # 计算参数数量
    count_parameters(model)
    
    # 测试前向传播
    dummy_input = torch.randn(input_size)
    try:
        with torch.no_grad():
            output = model(dummy_input)
        print(f"输入形状: {dummy_input.shape}")
        print(f"输出形状: {output.shape}")
        print("前向传播测试成功!")
    except Exception as e:
        print(f"前向传播测试失败: {e}")

if __name__ == "__main__":
    # 测试模型
    print("测试不同的模型配置...")
    
    # 测试 ResNet50
    print("\n1. ResNet50 (预训练, 不冻结):")
    model1 = create_model(model_name='resnet50', pretrained=True, freeze_features=False)
    visualize_model_architecture(model1)
    
    print("\n2. ResNet18 (预训练, 冻结特征层):")
    model2 = create_model(model_name='resnet18', pretrained=True, freeze_features=True)
    visualize_model_architecture(model2)
    
    # 测试 Focal Loss
    print("\n3. 测试 Focal Loss:")
    focal_loss = FocalLoss(alpha=1, gamma=2)
    dummy_logits = torch.randn(8, 2)  # batch_size=8, num_classes=2
    dummy_targets = torch.randint(0, 2, (8,))
    loss = focal_loss(dummy_logits, dummy_targets)
    print(f"Focal Loss 值: {loss.item():.4f}")
    
    print("\n模型测试完成!") 