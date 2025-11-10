from docker.models.services import Service

from tiefeng.container.docker.docker_service import DockerService


class DockerSwarmClient(DockerService):
    """Docker Swarm客户端服务类"""
    def __init__(self, base_url:str="tcp://127.0.0.1:2377", tls:bool=False):
        super().__init__(base_url, tls)

    def get_nodes(self):
        """获取所有节点"""
        return self.client.nodes.list()

    def get_node(self, id_or_name: str):
        """获取指定节点通过id或名称"""
        return self.client.nodes.get(id_or_name)

    def get_swarm(self):
        """获取集群信息"""
        return self.client.swarm.attrs

    def get_info(self):
        """获取集群信息"""
        return self.client.info()

    def get_ping(self):
        """获取集群状态"""
        return self.client.ping()

    def get_secrets(self):
        """获取所有密钥"""
        return self.client.secrets.list()

    def get_secret(self, id_or_name:str):
        """获取指定密钥通过id或名称"""
        return self.client.secrets.get(id_or_name)

    def get_services(self) ->list[Service]:
        """获取所有服务"""
        return self.client.services.list()

    def get_service(self, id_or_name:str) -> Service:
        """获取指定服务通过id或名称"""
        return self.client.services.get(id_or_name)

    def stop_service(self, id_or_name:str):
        """停止服务"""
        service = self.get_service(id_or_name)
        service.scale(0)

    def start_service(self, id_or_name:str):
        """启动服务"""
        service = self.get_service(id_or_name)
        service.scale(1)

    def get_configs(self):
        """获取所有配置"""
        return self.client.configs.list()

    def get_config(self, id_or_name:str):
        """获取指定配置通过id或名称"""
        return self.client.configs.get(id_or_name)


if __name__ == '__main__':
    docker_client = DockerSwarmClient()
    print(docker_client.get_nodes())
    print(docker_client.get_node("1"))
    print(docker_client.get_swarm())
    print(docker_client.get_info())
    print(docker_client.get_ping())