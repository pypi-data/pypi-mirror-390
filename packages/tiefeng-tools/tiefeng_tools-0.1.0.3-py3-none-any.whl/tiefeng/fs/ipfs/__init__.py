"""
前提：安装并启动 IPFS 节点
        1. 首先需要在本地安装 IPFS 客户端（go-ipfs）： 下载地址：(IPFS 官方安装指南)[https://docs.ipfs.tech/install/command-line/]
        2. 安装后初始化节点：ipfs init
        3. 启动节点服务（默认 API 地址为 http://127.0.0.1:5001）：ipfs daemon
使用方法1： IPFS 节点提供 HTTP API 接口，可通过 Python 的 requests 库直接调用。
        安装requests： pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
使用方法2：使用第三方库 ipfshttpclient
    1、安装：pip install ipfshttpclient -i https://pypi.tuna.tsinghua.edu.cn/simple

"""