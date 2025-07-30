# WSL环境基础开发环境安装命令

# 1. 更新包列表
sudo apt update

# 2. 安装Python3、pip和相关工具
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# 3. 安装Node.js和npm (方法1: 通过官方源)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 或者使用方法2: 直接从Ubuntu仓库安装
# sudo apt install -y nodejs npm

# 4. 验证安装
python3 --version
pip3 --version
node --version
npm --version

# 5. 升级pip到最新版本
pip3 install --upgrade pip --user

# 6. 安装常用的Python包管理工具
pip3 install --user virtualenv

# 可选：安装yarn (更快的包管理器)
npm install -g yarn

# 完成后验证
echo "Python3: $(python3 --version)"
echo "pip3: $(pip3 --version)"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"