# coding=utf-8
"""
YAML配置文件读取工具
"""
import yaml
import os
from common.Config import config


class YamlReader:
    """YAML文件读取器"""

    # 使用SafeLoader的节点列表
    SAFE_LOADER_NODES = ['ali', 'ali-slp']

    @classmethod
    def _get_yaml_path(cls, filename):
        """获取YAML文件完整路径"""
        return os.path.join(config.BASE_PATH, 'common', filename)

    @classmethod
    def _get_loader(cls):
        """根据环境获取YAML加载器"""
        import platform
        node = platform.node()
        if any(node == config.linux_node.get(n) for n in cls.SAFE_LOADER_NODES):
            return yaml.SafeLoader
        return None

    @classmethod
    def read(cls, filename, key):
        """
        读取YAML文件中的指定键值

        Args:
            filename: YAML文件名
            key: 要读取的键名

        Returns:
            键对应的值，不存在则返回None
        """
        yaml_path = cls._get_yaml_path(filename)
        print(yaml_path)

        if not os.path.exists(yaml_path):
            print(f"File not found: {yaml_path}")
            return None

        try:
            loader = cls._get_loader()
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.load(f, Loader=loader) if loader else yaml.load(f)

            return yaml_data.get(key) if yaml_data else None

        except Exception as e:
            print(f"Error reading YAML: {e}")
            return None


# 向后兼容
Yaml = YamlReader
YamlReader.read = YamlReader.read
