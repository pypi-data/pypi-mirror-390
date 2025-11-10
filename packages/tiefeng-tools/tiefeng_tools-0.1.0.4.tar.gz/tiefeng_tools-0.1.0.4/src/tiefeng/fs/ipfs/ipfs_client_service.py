"""
安装：pip install ipfshttpclient -i https://pypi.tuna.tsinghua.edu.cn/simple
"""
import ipfshttpclient

class IpfsClientService:

    def __init__(self, addr:str='/ip4/127.0.0.1/tcp/5001/http'):
        # 连接本地 IPFS 节点
        self.client = ipfshttpclient.connect(addr)

    def add_file(self, file_path:str):
        """添加文件到 IPFS"""
        res = self.client.add(file_path)
        return res["Hash"]

    def get_file(self, cid:str, output_path:str):
        """从 IPFS 获取文件"""
        with open(output_path, "wb") as f:
            f.write(self.client.cat(cid))

    def pin_file(self, cid:str):
        """固定文件（防止被垃圾回收）"""
        self.client.pin.add(cid)

# 示例用法
if __name__ == "__main__":
    ipfs_service = IpfsClientService()
    cid = ipfs_service.add_file("test.txt")
    print(f"CID: {cid}")
    ipfs_service.get_file(cid, "downloaded.txt")
    # ipfs_service.pin_file(cid)

