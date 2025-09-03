用于爬取1688商品网页链接商品图片和信息，学习使用

安装依赖
pip3 install -r requirements_1688.txt

爬取单张图片
python enhanced_1688.py
存储在data文件夹，图片在images

编辑 input.txt - 添加你的1688商品链接，爬取多张图片
python simple_batch_1688.py
存储在batch_results文件夹，一次可能爬到百张，但是图片应该是存在云上的，可以直接根据得到的json文件里的链接访问
