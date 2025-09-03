@echo off
echo ========================================
echo 1688商品信息提取器 - 依赖安装脚本
echo ========================================

echo.
echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo 升级pip到最新版本...
python -m pip install --upgrade pip

echo.
echo 安装核心依赖包...
pip install -r requirements_1688.txt

echo.
echo 检查Selenium安装...
python -c "import selenium; print(f'Selenium版本: {selenium.__version__}')"

echo.
echo 安装webdriver-manager（自动管理浏览器驱动）...
pip install webdriver-manager

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================

echo.
echo 接下来你需要：
echo 1. 确保已安装Firefox浏览器
echo 2. 编辑 input.txt 文件添加1688商品链接
echo 3. 运行程序：
echo    - python enhanced_1688.py （单个商品）
echo    - python simple_batch_1688.py （批量处理）
echo.

pause
