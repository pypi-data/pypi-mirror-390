# Akshare 引入 Proxy 代理解决  IP 被限问题
## 安装部署 
```
# 安装python安装工具
pip install setuptools
pip install 
python setup.py check
python setup.py sdist bdist_wheel
twine upload dist/*

```
## 验证安装
```python
import akshare as ak
print(ak.__version__)
```
## 代理配置
```python
from akshare.utils.context import AkshareConfig
import akshare as ak

""" 创建代理字典 """
proxies = {
    "http": "http://xxx.con:xxx",
    "https": "https://xxx.con:xxx"
}
""" 创建代理字典 """
AkshareConfig.set_proxies(proxies)

stock_sse_summary_df = ak.stock_sse_summary()
print(stock_sse_summary_df)

```

## IP 代理搭建
### 免费代理
[https://github.com/AlexLiue/proxy_pool](https://github.com/AlexLiue/proxy_pool)

## 收费代理
[https://cheapproxy.net/](https://cheapproxy.net/)


## 代码更新管理脚本备注
```
# 克隆项目
git clone https://github.com/AlexLiue/akshare.git
# 查看分支
git remote -v

# 添加上游仓库地址
git remote add upstream https://github.com/akfamily/akshare.git

# 合并上游更新到本地项目 （先本地创建合并分支，然后合并）
git checkout develop
git fetch upstream
git merge upstream/main

# 提交
git add .
git commit -m '20250401'

# 合并更新到主分支
git checkout main
git pull origin master
git merge develop

# 提交主分支
git add .
git commit -m '20250401'
git tag v0.0.1
git push  origin master
```