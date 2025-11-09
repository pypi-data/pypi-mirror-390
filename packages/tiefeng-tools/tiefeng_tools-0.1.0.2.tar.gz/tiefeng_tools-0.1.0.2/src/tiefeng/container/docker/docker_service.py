from typing import Any

import docker
from docker.models.containers import Container
from docker.models.images import Image
from docker.models.networks import Network
from docker.models.volumes import Volume
from docker.types import CancellableStream


class DockerService:
    """Docker客户端服务类"""

    def __init__(self, base_url:str="tcp://127.0.0.1:2375", tls:bool=False):
        self.client = docker.DockerClient(base_url=base_url, tls=tls)

    def get_containers(self, all=True) -> list[Container]:
        """获取所有容器, 类似：docker ps"""
        return self.client.containers.list(all=all)

    def get_container(self, id_or_name:str) -> Container:
        """获取指定容器通过id或名称"""
        return self.client.containers.get(id_or_name)

    def get_images(self) -> list[Image]:
        """获取所有镜像"""
        return self.client.images.list()

    def get_image(self, id_or_name:str) -> Image:
        """获取指定镜像通过id或名称"""
        return self.client.images.get(id_or_name)

    def get_networks(self) -> list[Network]:
        """获取所有网络"""
        return self.client.networks.list()

    def get_network(self, id_or_name:str) -> Network:
        """获取指定网络通过id或名称"""
        return self.client.networks.get(id_or_name)

    def get_volumes(self) -> list[Volume]:
        """获取所有卷"""
        return self.client.volumes.list()

    def get_volume(self, id_or_name:str) -> Volume:
        """获取指定卷通过id或名称"""
        return self.client.volumes.get(id_or_name)

    def get_events(self) -> CancellableStream:
        """获取所有事件"""
        return self.client.events()

    def get_version(self) -> dict[str, Any]:
        """获取版本信息"""
        return self.client.version()


if __name__ == '__main__':
    docker_service = DockerService()
    # print(docker_service.get_containers())
    # print(docker_service.get_images())
    # print(docker_service.get_networks())
    # print(docker_service.get_volumes())
    # print(docker_service.get_events())
    # print(docker_service.get_version())
    container = docker_service.get_container("c3ae2c4bd021")
    container.restart()
    logs = container.logs()
    print(container.name)
