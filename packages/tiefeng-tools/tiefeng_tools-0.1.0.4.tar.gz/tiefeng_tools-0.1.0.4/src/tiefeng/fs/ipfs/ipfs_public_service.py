import requests
from typing import Optional, Union, IO, Dict
from pathlib import Path


class IpfsPublicService:
    """IPFS公共网关服务类，支持通过多个网关访问IPFS内容"""

    def __init__(
            self,
            gateways: list[str] = None,
            local_node_api: str = "http://127.0.0.1:5001/api/v0",  # 本地节点API地址
            pinata_api_key: Optional[str] = None,
            pinata_secret_api_key: Optional[str] = None
    ):
        """
        初始化IPFS服务

        :param gateways: 公共网关列表（用于下载）
        :param local_node_api: 本地IPFS节点的API地址（用于上传）
        :param pinata_api_key: Pinata API密钥（可选，用于第三方上传）
            Pinata 使用步骤：
                1、注册账号：https://app.pinata.cloud/
                2、创建 API 密钥：在「Account」→「API Keys」中生成（权限至少勾选pinFileToIPFS）
                3、将密钥填入代码中的pinata_api_key和pinata_secret_api_key
        :param pinata_secret_api_key: Pinata 密钥（可选）
        """
        # 初始化下载网关
        if gateways is None:
            self.gateways = [
                'https://gw.alipayobjects.com/ipfs/',
                'https://apac.orbitor.dev/ipfs/',
                'https://ipfs.ecolatam.com/ipfs/',
                'https://trustless-gateway.link/ipfs/',
                'https://ipfs.orbitor.dev/ipfs/',
                'https://eu.orbitor.dev/ipfs/',
                'https://latam.orbitor.dev/ipfs/',
                'https://4everland.io/ipfs/',
                'https://dget.top/ipfs/',
                # 下面的地址在国内不可用
                # "https://ipfs.io/ipfs/",
                # "https://dweb.link/ipfs/",
                # "https://cloudflare-ipfs.com/ipfs/",
                # "https://gw.ipfs-lens.io/ipfs/",
            ]
        else:
            self.gateways = [g if g.endswith('/') else f"{g}/" for g in gateways]

        self.local_node_api = local_node_api
        self.pinata_headers = None
        if pinata_api_key and pinata_secret_api_key:
            self.pinata_headers = {
                "pinata_api_key": pinata_api_key,
                "pinata_secret_api_key": pinata_secret_api_key
            }

        self.available_gateways = []  # 可用网关缓存
        self.timeout = 30
    def _get_headers(self):
        if self.pinata_headers:
            return self.pinata_headers
        headers = {
            'Accept': 'application/vnd.ipld.raw'
        }
        return headers

    def _get_valid_gateway(self) -> Optional[str]:
        """获取第一个可用的网关（优先检测缓存，无缓存则全量检测）"""
        # 先检查缓存的可用网关
        for gateway in self.available_gateways:
            if self._check_gateway(gateway):
                return gateway

        # 缓存为空或失效，重新检测所有网关
        self.available_gateways = []
        for gateway in self.gateways:
            if self._check_gateway(gateway):
                self.available_gateways.append(gateway)
                return gateway
        return None

    def _check_gateway(self, gateway: str) -> bool:
        """检测网关是否可用（通过访问IPFS根目录测试）"""
        try:
            test_cid = "QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn"  # IPFS官方测试文件CID
            response = requests.head(
                f"{gateway}{test_cid}",
                timeout=self.timeout,
                allow_redirects=True,
                headers=self._get_headers()
            )
            return response.status_code in (200, 302)
        except Exception as e:
            return False

    def download_file(self, cid: str, output_path: Union[str, Path],
                      chunk_size: int = 1024 * 1024) -> bool:
        """
        从IPFS下载文件到本地

        :param cid: 文件的IPFS CID
        :param output_path: 本地保存路径（含文件名）
        :param chunk_size: 下载块大小（默认1MB）
        :return: 成功返回True，失败返回False
        """
        output_path = Path(output_path)
        # 创建输出目录（如果不存在）
        output_path.parent.mkdir(parents=True, exist_ok=True)

        gateway = self._get_valid_gateway()
        if not gateway:
            print("无可用的IPFS网关")
            return False

        url = f"{gateway}{cid}"
        try:
            with requests.get(url, stream=True, timeout=self.timeout, headers=self._get_headers()) as response:
                response.raise_for_status()  # 抛出HTTP错误
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:  # 过滤空块
                            f.write(chunk)
            print(f"文件已成功下载到: {output_path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"通过网关 {gateway} 下载失败: {str(e)}")
            # 移除失效网关并重试
            if gateway in self.available_gateways:
                self.available_gateways.remove(gateway)
            return self.download_file(cid, output_path, chunk_size)  # 递归重试

    def read_content(self, cid: str, encoding: str = "utf-8") -> Optional[str]:
        """
        直接读取IPFS文本内容（适合小文件）

        :param cid: 内容的IPFS CID
        :param encoding: 文本编码（默认utf-8）
        :return: 内容字符串，失败返回None
        """
        gateway = self._get_valid_gateway()
        if not gateway:
            print("无可用的IPFS网关")
            return None

        url = f"{gateway}{cid}"
        try:
            response = requests.get(url, timeout=self.timeout, headers=self._get_headers())
            response.raise_for_status()
            return response.content.decode(encoding)
        except requests.exceptions.RequestException as e:
            print(f"通过网关 {gateway} 读取内容失败: {str(e)}")
            if gateway in self.available_gateways:
                self.available_gateways.remove(gateway)
            return self.read_content(cid, encoding)  # 递归重试

    def stream_content(self, cid: str) -> Optional[IO[bytes]]:
        """
        流式获取IPFS内容（适合大文件或需要逐块处理的场景）

        :param cid: 内容的IPFS CID
        :return: 字节流对象，失败返回None
        """
        gateway = self._get_valid_gateway()
        if not gateway:
            print("无可用的IPFS网关")
            return None

        url = f"{gateway}{cid}"
        try:
            response = requests.get(url, stream=True, timeout=self.timeout, headers=self._get_headers())
            response.raise_for_status()
            return response.raw  # 返回原始字节流
        except requests.exceptions.RequestException as e:
            print(f"通过网关 {gateway} 获取流失败: {str(e)}")
            if gateway in self.available_gateways:
                self.available_gateways.remove(gateway)
            return self.stream_content(cid)  # 递归重试

    def upload_via_local_node(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        通过本地IPFS节点上传文件（需先启动节点：ipfs daemon）

        :param file_path: 本地文件路径
        :return: 上传后的CID，失败返回None
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"文件不存在：{file_path}")
            return None

        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{self.local_node_api}/add",
                    files={"file": f},
                    timeout=self.timeout
                )
            response.raise_for_status()
            cid = response.json()["Hash"]
            print(f"本地节点上传成功，CID：{cid}")
            return cid
        except Exception as e:
            print(f"本地节点上传失败（请确保ipfs daemon已启动）：{e}")
            return None

    def upload_via_pinata(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """
        通过Pinata服务上传文件（需要注册Pinata账号获取API密钥）

        :param file_path: 本地文件路径
        :return: 包含CID和pinata响应的字典，失败返回None
        """
        if not self.pinata_headers:
            print("请提供Pinata API密钥")
            return None

        file_path = Path(file_path)
        if not file_path.exists():
            print(f"文件不存在：{file_path}")
            return None

        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://api.pinata.cloud/pinning/pinFileToIPFS",
                    files={"file": (file_path.name, f)},
                    headers=self.pinata_headers,
                    timeout=self.timeout
                )
            response.raise_for_status()
            result = response.json()
            cid = result["IpfsHash"]
            print(f"Pinata上传成功，CID：{cid}")
            return {
                "cid": cid,
                "pinata_response": result
            }
        except Exception as e:
            print(f"Pinata上传失败：{e}")
            return None

# 使用示例
if __name__ == "__main__":
    # 初始化服务
    ipfs_service = IpfsPublicService()

    # 示例1：下载文件（使用公开测试CID）
    test_cid = "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"  # IPFS官方示例文本
    ipfs_service.download_file(
        cid=test_cid,
        output_path="./ipfs_downloads/example.txt"
    )

    # 示例2：直接读取文本内容
    content = ipfs_service.read_content(cid=test_cid)
    if content:
        print("\n读取到的内容：")
        print(content[:500] + "..." if len(content) > 500 else content)

    # 示例3：流式处理内容（适合大文件）
    stream = ipfs_service.stream_content(cid=test_cid)
    if stream:
        print("\n流式读取内容：")
        while chunk := stream.read(1024):  # 每次读取1KB
            print(chunk.decode("utf-8"), end="")
        stream.close()


    ############# 上传文件 #############
    # 初始化服务（如需使用Pinata，需填写API密钥）
    # ipfs = IpfsPublicService(
    #     # pinata_api_key="你的Pinata API Key",
    #     # pinata_secret_api_key="你的Pinata Secret Key"
    # )

    # 1. 上传文件（二选一）
    # 方式A：通过本地节点上传（需先运行 `ipfs daemon`）
    # local_cid = ipfs.upload_via_local_node("test.txt")  # 替换为你的文件

    # 方式B：通过Pinata上传（需取消上面的注释并填写密钥）
    # pinata_result = ipfs.upload_via_pinata("test.txt")
    # if pinata_result:
    #     pinata_cid = pinata_result["cid"]
