# coding=utf-8
"""
全局配置管理模块

使用方式:
    from common.Config import config
    url = config.pay_url
    uid = config.payUid
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class AppConfig:
    """应用配置"""
    bb_dev: str = 'https://dev.iambanban.com/'
    pt_ali_dev: str = 'https://pt-dev.iambanban.com/'
    pt_ali_main: str = 'https://pt-dev.iambanban.com/_testcase/'
    starify: str = 'http://116.62.125.230/'
    slp: str = 'https://116.62.125.230/'
    rush: str = 'https://192.168.11.55/'


@dataclass
class CodeConfig:
    """代码路径配置"""
    bb_php_path: str = '/home/webroot/banban'
    bb_go_path: str = '/home/webroot/bb-consume'
    pt_php_path: str = '/home/webroot/release_oversea/banban'
    bb_git_branch: str = 'release-for-vpc'
    bb_go_git_branch: str = 'master'
    pt_git_branch: str = 'main'
    slp_php_path: str = "/var/www/slp/slp-php"
    slp_common_rpc_path: str = "/var/www/slp/slp-common-rpc"
    slp_git_branch: str = "dev"


@dataclass
class AppNameConfig:
    """应用名称映射"""
    _1: str = '1'  # 伴伴
    _2: str = '2'  # PT
    谁是凶手: str = 'games'
    不夜星球: str = 'slp'
    冲鸭: str = 'rush'

    def __getitem__(self, key):
        """支持 config.appName['1'] 访问方式"""
        attr = f'_{key}' if key.isdigit() else key
        return getattr(self, attr, key)


@dataclass
class LinuxNodeConfig:
    """服务器节点配置"""
    ali: str = 'iZbp1fveowr7j693hrwb48Z'
    ali_starify: str = 'iZbp15ildwog86lw08ptpnZ'
    ali_slp: str = 'iZbp15ildwog86lw08ptpnZ'

    def __getitem__(self, key):
        """支持下划线或中划线访问"""
        return getattr(self, key.replace('-', '_'), None)


@dataclass
class BBUserConfig:
    """伴伴用户配置"""
    payUid: int = 103273407
    testUid: int = 105002312
    pack_cal_uid: int = 105002313
    vipRoomRid: int = 200089706
    gsUid: int = 105002325
    prettyRid: int = 200089942
    fleetRid: int = 200091067


@dataclass
class LiveRoleConfig:
    """直播角色配置"""
    pack_ceo: int = 105002314
    pack_master_NoPack: int = 105002319
    pack_cal_uid: int = 105002313
    live_rid: int = 193185577
    auto_rid: int = 193185484

    def __getitem__(self, key):
        """支持下标访问"""
        return getattr(self, key, None)


@dataclass
class PTUserConfig:
    """PT用户配置"""
    payUid: int = 800350557
    testUid: int = 800022872
    brokerUid: int = 800018895
    fleet_uid: int = 800041062


@dataclass
class PTRoomConfig:
    """PT房间配置"""
    business_joy: int = 105699329
    vip_rid: int = 105698376
    th_union: int = 105708881
    en_fleet: int = 105717544
    id_fleet: int = 105711999
    ms_fleet: int = 105725790
    business_joy_ar: int = 105726673
    union_ar: int = 105713367
    business_joy_vi: int = 105726676
    union_vi: int = 105718889


@dataclass
class Config:
    """全局配置类"""

    # ============ 基础路径 ============
    BASE_PATH: str = field(default_factory=lambda: os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    # ============ 应用配置 ============
    appInfo: AppConfig = field(default_factory=AppConfig)
    codeInfo: CodeConfig = field(default_factory=CodeConfig)
    appName: AppNameConfig = field(default_factory=AppNameConfig)
    linux_node: LinuxNodeConfig = field(default_factory=LinuxNodeConfig)

    # ============ 分成比例 ============
    rate: float = 0.62

    # ============ 用户配置 ============
    bb_user: BBUserConfig = field(default_factory=BBUserConfig)
    live_role: LiveRoleConfig = field(default_factory=LiveRoleConfig)
    pt_user: PTUserConfig = field(default_factory=PTUserConfig)
    pt_room: PTRoomConfig = field(default_factory=PTRoomConfig)

    # ============ 礼物配置 ============
    giftId: Dict[str, int] = field(default_factory=lambda: {
        "5": 5,      # 棒棒糖*100钻
        "7": 7,      # 大宝剑*1000钻
        "11": 11,    # 老司机*3000钻(券-500钻石)
        "46": 46,    # 幸运星*600钻
        "47": 47,    # 五色星*2100钻
        "54": 54,    # 小天使*9900钻（商城购买）
        "62": 62,    # 人气券*20（金币）
        "362": 362,  # 啵啵奶茶*1000（金豆）
    })

    pt_giftId: Dict[str, int] = field(default_factory=lambda: {
        "10": 10,    # 么么哒*6币
        "46": 46,    # 幸运星*6币
        "47": 47,    # 五色星*21币
        "773": 773,  # 小飞机盲盒
        "774": 774,  # 飞马盲盒
    })

    # ============ 便捷访问属性 ============
    @property
    def payUid(self) -> int:
        """打赏者UID（伴伴）"""
        return self.bb_user.payUid

    @property
    def rewardUid(self) -> int:
        """被打赏者UID（非一代宗师）"""
        return self.bb_user.testUid

    @property
    def masterUid(self) -> int:
        """被打赏者UID（一代宗师）"""
        return 100500338

    @property
    def gsUid(self) -> int:
        """公会用户UID"""
        return self.bb_user.gsUid

    @property
    def pt_payUid(self) -> int:
        """PT打赏者UID"""
        return self.pt_user.payUid

    @property
    def pt_testUid(self) -> int:
        """PT测试UID"""
        return self.pt_user.testUid

    @property
    def pt_brokerUid(self) -> int:
        """PT公会成员UID"""
        return self.pt_user.brokerUid

    @property
    def pt_fleetUid(self) -> int:
        """PT家族UID"""
        return self.pt_user.fleet_uid

    # ============ URL配置 ============
    @property
    def pt_host(self) -> str:
        """PT测试域名"""
        return self.appInfo.pt_ali_main

    @property
    def pay_url(self) -> str:
        """支付接口URL"""
        return f"{self.appInfo.bb_dev}pay/create?package="

    @property
    def slp_pay_url(self) -> str:
        """SLP支付接口URL"""
        return f"{self.appInfo.slp}pay/create?package=com.yhl.sleepless.android"

    @property
    def bb_qqLogin_url(self) -> str:
        """伴伴QQ登录URL"""
        return f"{self.appInfo.bb_dev}account/qqlogin"

    @property
    def pt_mobile_login_url(self) -> str:
        """PT手机号登录URL"""
        return f"{self.pt_host}account/passwordLogin"

    @property
    def starify_mobile_login_url(self) -> str:
        """Starify手机号登录URL"""
        return f"{self.appInfo.starify}go/starify/login/mobileLogin"

    @property
    def slp_mobile_login_url(self) -> str:
        """SLP手机号登录URL"""
        return f"{self.appInfo.slp}account/login"


# 全局配置实例
config = Config()

if __name__ == '__main__':
    print(config.pay_url)
    print(f"payUid: {config.payUid}")
    print(f"giftId['5']: {config.giftId['5']}")
