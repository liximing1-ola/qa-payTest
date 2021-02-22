# coding=utf-8
import yaml
from Common.config import config
import os


class Yaml:

    @staticmethod
    def read_yaml(yaml_fileName, yaml_name):
        """
        读取yaml
        :return: yaml_data
        """
        yaml_path = config.BASE_PATH + '/Common/' + yaml_fileName
        try:
            if not os.path.exists(yaml_path):
                return FileExistsError
            yaml_data = yaml.load(open(yaml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)  # 添加后不会报warning
            if yaml_data[yaml_name] is None:
                return TypeError
            else:
                return yaml_data[yaml_name]
        except Exception as e:
            print(e)


if __name__ == '__main__':
    y = Yaml.read_yaml('User.yml', 'pay_body_package')
    print(y)