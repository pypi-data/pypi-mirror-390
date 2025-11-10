import requests

class IpfsService:
    """IPFS服务类"""
    def __init__(self, ipfs_api_url:str = "http://127.0.0.1:5001/api/v0"):
        self.api_url = ipfs_api_url

    def add_file(self, file_path:str):
        """添加文件到 IPFS，返回 CID"""
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{self.api_url}/add",
                files={"file": f}
            )
        return response.json()["Hash"]

    def get_file(self, cid:str, output_path:str):
        """从 IPFS 获取文件并保存"""
        response = requests.post(
            f"{self.api_url}/cat?arg={cid}",
            stream=True
        )
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

    def pin_file(self, cid:str):
        """固定文件（防止被垃圾回收）"""
        response = requests.post(f"{self.api_url}/pin/add?arg={cid}")
        return response.json()


# 示例用法
if __name__ == "__main__":
    ipfs_service = IpfsService()
    # 添加文件
    cid = ipfs_service.add_file("test.txt")
    print(f"文件 CID: {cid}")
    # 获取文件
    ipfs_service.get_file(cid, "downloaded_test.txt")
    # 固定文件
    ipfs_service.pin_file(cid)