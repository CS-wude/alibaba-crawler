#!/bin/bash

# 胸部X光片AI分析系统 - 快速部署脚本
# 版本: v1.0
# 用途: 自动化部署开发/生产环境

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="chestxray-ai"
APP_DIR="/opt/$APP_NAME"
VENV_NAME="venv"
PYTHON_VERSION="3.8"
DOMAIN_NAME="your-domain.com"
ADMIN_EMAIL="admin@example.com"

# 函数定义
print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "🏥 胸部X光片AI分析系统 - 快速部署脚本"
    echo "=================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要以root用户运行此脚本"
        exit 1
    fi
}

detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_error "无法检测操作系统"
        exit 1
    fi
    
    print_info "检测到操作系统: $OS $VERSION"
}

install_system_dependencies() {
    print_info "安装系统依赖..."
    
    case $OS in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev \
                               python3-pip git curl wget unzip build-essential nginx supervisor \
                               software-properties-common apt-transport-https ca-certificates
            ;;
        centos|rhel|fedora)
            sudo yum update -y
            sudo yum install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-devel \
                               python3-pip git curl wget unzip gcc gcc-c++ nginx supervisor
            ;;
        *)
            print_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
    
    print_step "系统依赖安装完成"
}

setup_python_environment() {
    print_info "设置Python环境..."
    
    # 检查Python版本
    if ! command -v python$PYTHON_VERSION &> /dev/null; then
        print_error "Python $PYTHON_VERSION 未安装"
        exit 1
    fi
    
    # 创建虚拟环境
    python$PYTHON_VERSION -m venv $VENV_NAME
    source $VENV_NAME/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    print_step "Python环境设置完成"
}

install_python_dependencies() {
    print_info "安装Python依赖..."
    
    source $VENV_NAME/bin/activate
    
    # 安装PyTorch (CPU版本)
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    
    # 检查是否存在requirements文件
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    fi
    
    if [[ -f "web_requirements.txt" ]]; then
        pip install -r web_requirements.txt
    fi
    
    # 安装生产环境依赖
    pip install gunicorn supervisor flask-caching redis
    
    print_step "Python依赖安装完成"
}

check_model_file() {
    print_info "检查模型文件..."
    
    if [[ -f "checkpoints/best_model.pth" ]]; then
        print_step "模型文件已存在"
    else
        print_warning "模型文件不存在，需要训练模型"
        read -p "是否现在训练模型？(y/n): " train_model
        if [[ $train_model == "y" || $train_model == "Y" ]]; then
            print_info "开始训练模型..."
            source $VENV_NAME/bin/activate
            python main.py train
            print_step "模型训练完成"
        else
            print_warning "跳过模型训练，请稍后手动训练"
        fi
    fi
}

setup_ollama() {
    print_info "设置Ollama..."
    
    read -p "是否安装Ollama？(y/n): " install_ollama
    if [[ $install_ollama == "y" || $install_ollama == "Y" ]]; then
        # 安装Ollama
        if ! command -v ollama &> /dev/null; then
            curl -fsSL https://ollama.ai/install.sh | sh
            print_step "Ollama安装完成"
        else
            print_info "Ollama已安装"
        fi
        
        # 启动Ollama服务
        if ! pgrep -x "ollama" > /dev/null; then
            print_info "启动Ollama服务..."
            nohup ollama serve > ollama.log 2>&1 &
            sleep 5
        fi
        
        # 下载推荐模型
        read -p "是否下载推荐的AI模型？(y/n): " download_models
        if [[ $download_models == "y" || $download_models == "Y" ]]; then
            print_info "下载AI模型中..."
            ollama pull llama3.1:8b || ollama pull llama2:7b || print_warning "模型下载失败"
            print_step "AI模型下载完成"
        fi
    else
        print_info "跳过Ollama安装"
    fi
}

create_directories() {
    print_info "创建必要目录..."
    
    mkdir -p static/uploads static/reports templates logs
    chmod 755 static/uploads static/reports
    
    print_step "目录创建完成"
}

test_application() {
    print_info "测试应用..."
    
    source $VENV_NAME/bin/activate
    
    # 测试基本功能
    if python -c "from web_app import app; print('Web应用导入成功')"; then
        print_step "Web应用测试通过"
    else
        print_error "Web应用测试失败"
        exit 1
    fi
    
    # 测试AI系统
    if python -c "from multimodal_service import MedicalMultimodalAI; print('AI系统导入成功')"; then
        print_step "AI系统测试通过"
    else
        print_warning "AI系统可能有问题，请检查"
    fi
}

setup_production() {
    print_info "设置生产环境..."
    
    read -p "是否配置生产环境？(y/n): " setup_prod
    if [[ $setup_prod != "y" && $setup_prod != "Y" ]]; then
        return
    fi
    
    # 创建应用目录
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    
    # 复制文件到生产目录
    cp -r . $APP_DIR/
    
    # 创建Gunicorn配置
    cat > $APP_DIR/gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
timeout = 300
preload_app = True
user = "www-data"
group = "www-data"
accesslog = "/var/log/chestxray-ai/access.log"
errorlog = "/var/log/chestxray-ai/error.log"
loglevel = "info"
EOF
    
    # 创建启动脚本
    cat > $APP_DIR/start.sh << EOF
#!/bin/bash
cd $APP_DIR
source $VENV_NAME/bin/activate
exec gunicorn -c gunicorn.conf.py web_app:app
EOF
    chmod +x $APP_DIR/start.sh
    
    # 创建systemd服务
    sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=ChestXRay AI Analysis System
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/$VENV_NAME/bin
ExecStart=$APP_DIR/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建日志目录
    sudo mkdir -p /var/log/$APP_NAME
    sudo chown www-data:www-data /var/log/$APP_NAME
    
    # 设置权限
    sudo chown -R www-data:www-data $APP_DIR
    
    # 启动服务
    sudo systemctl daemon-reload
    sudo systemctl enable $APP_NAME
    sudo systemctl start $APP_NAME
    
    print_step "生产环境配置完成"
}

setup_nginx() {
    print_info "配置Nginx..."
    
    read -p "是否配置Nginx反向代理？(y/n): " setup_nginx_proxy
    if [[ $setup_nginx_proxy != "y" && $setup_nginx_proxy != "Y" ]]; then
        return
    fi
    
    read -p "请输入域名 (默认: localhost): " domain
    domain=${domain:-localhost}
    
    # 创建Nginx配置
    sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $domain;
    
    client_max_body_size 20M;
    
    location /static {
        alias $APP_DIR/static;
        expires 1d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    
    # 测试配置
    sudo nginx -t
    
    # 重启Nginx
    sudo systemctl restart nginx
    
    print_step "Nginx配置完成"
    
    # SSL配置
    read -p "是否配置SSL证书？(需要有效域名) (y/n): " setup_ssl
    if [[ $setup_ssl == "y" || $setup_ssl == "Y" ]]; then
        if command -v certbot &> /dev/null; then
            sudo certbot --nginx -d $domain --non-interactive --agree-tos -m $ADMIN_EMAIL
            print_step "SSL证书配置完成"
        else
            print_warning "Certbot未安装，请手动配置SSL"
        fi
    fi
}

create_management_scripts() {
    print_info "创建管理脚本..."
    
    # 状态检查脚本
    cat > status.sh << 'EOF'
#!/bin/bash
echo "=== 胸部X光片AI系统状态 ==="
echo "应用服务状态:"
sudo systemctl status chestxray-ai --no-pager -l

echo -e "\nOllama服务状态:"
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama运行中"
else
    echo "❌ Ollama未运行"
fi

echo -e "\nNginx状态:"
sudo systemctl status nginx --no-pager -l

echo -e "\n端口监听状态:"
netstat -tlnp | grep -E ":(80|443|5000|11434)"

echo -e "\n磁盘使用:"
df -h /opt/chestxray-ai

echo -e "\n内存使用:"
free -h
EOF
    chmod +x status.sh
    
    # 日志查看脚本
    cat > logs.sh << 'EOF'
#!/bin/bash
case $1 in
    app|application)
        tail -f /var/log/chestxray-ai/error.log
        ;;
    access)
        tail -f /var/log/chestxray-ai/access.log
        ;;
    nginx)
        tail -f /var/log/nginx/error.log
        ;;
    ollama)
        tail -f ollama.log
        ;;
    *)
        echo "用法: $0 [app|access|nginx|ollama]"
        echo "  app     - 应用错误日志"
        echo "  access  - 访问日志"
        echo "  nginx   - Nginx错误日志"
        echo "  ollama  - Ollama日志"
        ;;
esac
EOF
    chmod +x logs.sh
    
    # 重启脚本
    cat > restart.sh << 'EOF'
#!/bin/bash
echo "重启胸部X光片AI系统..."
sudo systemctl restart chestxray-ai
sudo systemctl restart nginx
echo "重启完成"
./status.sh
EOF
    chmod +x restart.sh
    
    print_step "管理脚本创建完成"
}

show_completion_info() {
    print_header
    print_step "🎉 部署完成！"
    echo ""
    print_info "系统信息:"
    echo "  📁 应用目录: $(pwd)"
    echo "  🌐 访问地址: http://localhost:5000"
    echo "  📊 健康检查: http://localhost:5000/health"
    echo ""
    print_info "管理命令:"
    echo "  📈 查看状态: ./status.sh"
    echo "  📋 查看日志: ./logs.sh app"
    echo "  🔄 重启服务: ./restart.sh"
    echo ""
    print_info "测试步骤:"
    echo "  1. 访问Web界面"
    echo "  2. 上传X光片测试图像"
    echo "  3. 切换Ollama/增强版报告模式"
    echo "  4. 查看分析结果"
    echo ""
    print_warning "重要提醒:"
    echo "  - 首次使用请上传测试图片验证功能"
    echo "  - 生产环境请配置防火墙和SSL"
    echo "  - 定期备份模型文件和配置"
    echo "  - 监控系统资源使用情况"
    echo ""
}

main() {
    print_header
    
    # 检查运行权限
    check_root
    
    # 检测操作系统
    detect_os
    
    # 询问部署模式
    echo "请选择部署模式:"
    echo "1) 开发环境 (推荐新用户)"
    echo "2) 生产环境"
    echo "3) 仅安装依赖"
    read -p "请选择 [1-3]: " deploy_mode
    
    case $deploy_mode in
        1|"")
            print_info "选择开发环境部署"
            install_system_dependencies
            setup_python_environment
            install_python_dependencies
            create_directories
            check_model_file
            setup_ollama
            test_application
            create_management_scripts
            ;;
        2)
            print_info "选择生产环境部署"
            install_system_dependencies
            setup_python_environment
            install_python_dependencies
            create_directories
            check_model_file
            setup_ollama
            test_application
            setup_production
            setup_nginx
            create_management_scripts
            ;;
        3)
            print_info "仅安装依赖"
            install_system_dependencies
            setup_python_environment
            install_python_dependencies
            ;;
        *)
            print_error "无效选择"
            exit 1
            ;;
    esac
    
    show_completion_info
}

# 捕获中断信号
trap 'print_error "部署被中断"; exit 1' INT TERM

# 运行主函数
main "$@" 