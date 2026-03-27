# coding=utf-8
"""
SLP MySQL 数据库操作模块

提供 SLP 平台的数据库连接管理和常用业务操作方法。
使用单例模式管理数据库连接，支持自动重连。
"""
import ast
import time
from typing import Optional, Tuple, Dict, Any, List, Union
import pymysql


class DatabaseConfig:
    """数据库配置"""
    ALI: Dict[str, str] = {
        'host': '127.0.0.1',
        'port': '3306',
        'user': 'root',
        'password': 'root',
        'database': 'xianshi',
        'charset': 'utf8'
    }


class MySQLConnection:
    """MySQL连接管理器（单例模式）"""
    
    _connection: Optional[pymysql.Connection] = None
    _cursor: Optional[pymysql.Cursor] = None
    
    @classmethod
    def get_connection(cls) -> pymysql.Connection:
        """获取数据库连接
        
        Returns:
            MySQL连接对象
        """
        if cls._connection is None or not cls._connection.open:
            config = DatabaseConfig.ALI
            cls._connection = pymysql.connect(
                host=config['host'],
                port=int(config['port']),
                user=config['user'],
                password=config['password'],
                charset=config['charset'],
                autocommit=True
            )
            cls._connection.select_db(config['database'])
        cls._connection.ping(reconnect=True)
        return cls._connection
    
    @classmethod
    def get_cursor(cls):
        """获取游标
        
        Returns:
            MySQL 游标对象
        """
        con = cls.get_connection()
        return cls._cursor if cls._cursor else con.cursor()


class conMysql:
    """MySQL 操作类"""
    
    # ============ 查询方法 ============
    
    @staticmethod
    def selectUserInfoSql(accountType: str, uid: str = "200000126", 
                         money_type: str = 'money_cash_b', 
                         cid: int = 263, 
                         payuid: str = "200000128") -> Optional[Union[int, float, Dict, List]]:
        """查询用户信息
        
        Args:
            accountType: 账户类型
            uid: 用户 ID
            money_type: 货币类型
            cid: 物品 ID
            payuid: 支付用户 ID
            
        Returns:
            查询结果
        """
        cursor = MySQLConnection.get_cursor()
        
        try:
            if accountType == 'bean':  # 查询用户账户扩展表金豆余额
                sql = f"SELECT money_coupon FROM xs_user_money_extend WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'cash':  # 查询用户账户扩展表现金余额
                sql = f"SELECT cash FROM xs_user_money_extend WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'sum_money':  # 查询用户所有账户数据之和
                sql = f"SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'single_money':  # 查询用户单个账户数据
                sql = f"SELECT {money_type} FROM xs_user_money WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res and len(res) > 0 else None
                
            elif accountType == 'sum_commodity':  # 查询用户背包物品总数
                sql = f"SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return int(res[0]) if res else 0
                
            elif accountType == 'num_commodity':  # 查询用户背包物品数量
                sql = f"SELECT num FROM xs_user_commodity WHERE cid={cid} AND uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'pay_room_money':  # 用户 VIP 等级经验
                sql = f"SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'popularity':  # 用户人气等级经验
                sql = f"SELECT popularity FROM xs_user_popularity WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'id_commodity':  # 查询用户背包物品 ID
                sql = f"SELECT id FROM xs_user_commodity WHERE cid={cid} AND uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res and len(res) > 0 else None
                
            elif accountType == 'level':  # 查询用户爵位等级
                sql = f"SELECT level FROM xs_user_title_new WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res and len(res) > 0 else None
                
            elif accountType == 'growth':  # 查询用户成长值
                sql = f"SELECT growth FROM xs_user_title_new WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res and len(res) > 0 else None
                
            elif accountType == 'user_index':  # 查询用户 salt
                sql = f"SELECT salt FROM xs_user_index WHERE uid={uid}"
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res and len(res) > 0 else None
                
            elif accountType == 'relation_id':  # 查询用户守护关系 id
                sql = (f"SELECT id FROM xs_relation_defend "
                       f"WHERE uid={payuid} AND defend_uid={uid} AND relation_id={cid}")
                cursor.execute(sql)
                res = cursor.fetchone()
                return res[0] if res else 0
                
            elif accountType == 'relation_config':  # 查询守护关系配置
                sql = ("SELECT id, name, money_value, break_money, upgrade_money "
                       f"FROM xs_relation_config WHERE id={uid}")
                cursor.execute(sql)
                res = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                data_dict = [dict(zip(columns, row)) for row in res]
                return data_dict[0] if data_dict else None
                
            elif accountType == 'union':  # 查询联盟房
                sql = f"SELECT rid FROM xs_chatroom WHERE property='union' LIMIT 1"
                cursor.execute(sql)
                res = cursor.fetchone()
                if res is None:
                    raise EnvironmentError('库表无联盟房')
                return res[0]
                
            elif accountType == 'vip':  # 查询个人房
                sql = f"SELECT rid FROM xs_chatroom WHERE property='vip' LIMIT 1"
                cursor.execute(sql)
                res = cursor.fetchone()
                if res is None:
                    raise EnvironmentError('库表无个人房')
                return res[0]
                
            elif accountType == 'pay_change':  # 查询用户消费记录数据
                sql = f"SELECT reason FROM xs_pay_change WHERE uid={uid} ORDER BY id DESC LIMIT 1"
                cursor.execute(sql)
                res = cursor.fetchone()
                if res:
                    res_dict = ast.literal_eval(res[0])
                    reason_value = str(money_type)
                    return res_dict.get(reason_value, 0)
                return 0
                
            else:
                print(f'{accountType} Error')
                return None
                
        except Exception as error:
            print(f'Select error: {error}')
            return None

    # ============ 删除方法 ============
    
    @staticmethod
    def deleteUserAccountSql(tableName: str, uid: str) -> None:
        """删除用户账户数据
        
        Args:
            tableName: 表名
            uid: 用户 ID
        """
        cursor = MySQLConnection.get_cursor()
        con = MySQLConnection.get_connection()
        
        sql_map = {
            'user_commodity': f"DELETE FROM xs_user_commodity WHERE uid={uid}",
            'user_title': f"DELETE FROM xs_user_title WHERE uid={uid} LIMIT 5",
            'broker_user': f"DELETE FROM xs_broker_user WHERE uid={uid} LIMIT 1",
            'chatroom': f"DELETE FROM xs_chatroom WHERE uid={uid} LIMIT 1",
            'user_box': f"DELETE FROM xs_user_box WHERE uid={uid} LIMIT 1",
        }
        
        update_map = {
            'pay_room_money': f"UPDATE xs_user_profile SET pay_room_money=0 WHERE uid={uid} LIMIT 1",
            'user_title_new': f"UPDATE xs_user_title_new SET subscribe_time=0 WHERE uid={uid} LIMIT 1",
        }
        
        if tableName in sql_map:
            try:
                cursor.execute(sql_map[tableName])
            except Exception as error:
                con.rollback()
                print(f'Delete fail: {error}')
            finally:
                con.commit()
                
        elif tableName in update_map:
            try:
                cursor.execute(update_map[tableName])
            except Exception as error:
                con.rollback()
                print(f'Update fail: {error}')
            finally:
                con.commit()
        else:
            print(f'{tableName} Error')

    # ============ 更新方法 ============
    
    @staticmethod
    def updateUserRidInfoSql(property_rid: str, rid: int, area: str = 'en') -> None:
        """更新房间属性
        
        Args:
            property_rid: 属性 RID
            rid: 房间 ID
            area: 区域
        """
        sql = f"UPDATE xs_chatroom SET property='{property_rid}', area='{area}' WHERE rid={rid}"
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    @staticmethod
    def updateUserBigArea(*uids: str, bigarea_id: int = 2) -> None:
        """更新用户大区
        
        Args:
            *uids: 用户 ID 列表
            bigarea_id: 大区 ID
        """
        cursor = MySQLConnection.get_cursor()
        con = MySQLConnection.get_connection()
        
        for uid in uids:
            sql = f"UPDATE xs_user_bigarea SET bigarea_id={bigarea_id} WHERE uid IN ({uid})"
            try:
                cursor.execute(sql)
                con.commit()
            except Exception as error:
                con.rollback()
                print(f'Update bigarea fail: {error}')

    @staticmethod
    def updateUserLanguage(*uids: str, language: str = 'zh_CN', area_code: str = 'CN') -> None:
        """更新用户语言
        
        Args:
            *uids: 用户 ID 列表
            language: 语言
            area_code: 区域代码
        """
        cursor = MySQLConnection.get_cursor()
        con = MySQLConnection.get_connection()
        
        for uid in uids:
            sql = f"UPDATE xs_user_settings SET language='{language}', area_code='{area_code}' WHERE uid IN ({uid})"
            try:
                cursor.execute(sql)
                con.commit()
            except Exception as error:
                con.rollback()
                print(f'Update language fail: {error}')

    @staticmethod
    def updateUserMoneyClearSql(*uids: str) -> None:
        """清空用户账户余额
        
        Args:
            *uids: 用户 ID 列表
        """
        cursor = MySQLConnection.get_cursor()
        con = MySQLConnection.get_connection()
        
        for uid in uids:
            sql = ("UPDATE xs_user_money SET money=0, money_b=0, money_cash=0, "
                   "money_cash_b=0, gold_coin=0, money_debts=0, money_order=0, "
                   f"money_order_b=0 WHERE uid={uid}")
            try:
                cursor.execute(sql)
                con.commit()
            except Exception as error:
                con.rollback()
                print(f'Clear money fail: {error}')

    @staticmethod
    def updateMoneySql(uid: str, money: int = 0, money_cash: int = 0, 
                       money_cash_b: int = 0, money_b: int = 0, 
                       gold_coin: int = 0, money_debts: int = 0) -> None:
        """更新用户账户余额
        
        Args:
            uid: 用户 ID
            money: 金豆
            money_cash: 现金
            money_cash_b: 现金 B
            money_b: 金豆 B
            gold_coin: 金币
            money_debts: 债务
        """
        sql = (f"UPDATE xs_user_money SET money={money}, money_b={money_b}, "
               f"money_cash={money_cash}, money_cash_b={money_cash_b}, "
               f"gold_coin={gold_coin}, money_debts={money_debts} "
               f"WHERE uid={uid} LIMIT 1")
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    @staticmethod
    def updateXsUserpopularity(uid: str) -> None:
        """更新用户人气数据
        
        Args:
            uid: 用户 ID
        """
        sql = f"UPDATE xs_user_popularity SET popularity=0 WHERE uid={uid}"
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    @staticmethod
    def updateXsUserprofile_pay_room_money(uid: str) -> None:
        """更新用户 VIP 数据
        
        Args:
            uid: 用户 ID
        """
        sql = f"UPDATE xs_user_profile SET pay_room_money=0 WHERE uid={uid}"
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    # ============ 插入方法 ============
    
    @staticmethod
    def insertXsUserCommodity(uid: str, cid: int, num: int, state: int = 0) -> None:
        """用户背包增加数据
        
        Args:
            uid: 用户 ID
            cid: 物品 ID
            num: 数量
            state: 状态
        """
        sql = f"INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES ({uid}, {cid}, {num}, {state})"
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    @staticmethod
    def insertXsUserBox(uid: str, gift_cid: int = 2505, box_type: str = 'copper') -> None:
        """更新箱子刷新物品
        
        Args:
            uid: 用户 ID
            gift_cid: 礼物 ID
            box_type: 箱子类型
        """
        sql = f"INSERT INTO xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) VALUES ({gift_cid}, {gift_cid}, {uid}, '{box_type}')"
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    # ============ 检查配置 ============
    
    @staticmethod
    def checkXsGiftConfig(gift_ids: Tuple[int, ...]) -> None:
        """检查礼物配置
        
        Args:
            gift_ids: 礼物 ID 元组
        """
        sql = f"UPDATE xs_gift SET deleted=0 WHERE id IN {gift_ids}"
        MySQLConnection.get_cursor().execute(sql)
        MySQLConnection.get_connection().commit()

    # ============ 专用查询方法 ============
    
    @staticmethod
    def select_greedy_prize(uid: str, round_id: int) -> Tuple:
        """查询摩天轮开奖数据
        
        Args:
            uid: 用户 ID
            round_id: 回合 ID
            
        Returns:
            (counter, prize) 元组
        """
        sql = f"SELECT counter, prize FROM xs_greedy_round_player_v2 WHERE uid={uid} AND round_id={round_id}"
        res = MySQLConnection.get_cursor().execute(sql)
        return res if res else 0

    @staticmethod
    def select_user_chatroom(property: str, bigarea_id: int = 1) -> int:
        """查询大区房间信息
        
        Args:
            property: 属性
            bigarea_id: 大区 ID
            
        Returns:
            房间 RID
        """
        sql = (f"SELECT rid FROM xs_chatroom a "
               f"LEFT JOIN xs_user_bigarea b ON a.uid=b.uid "
               f"WHERE a.property='{property}' AND b.bigarea_id={bigarea_id} LIMIT 1")
        res = MySQLConnection.get_cursor().execute(sql)
        return res[0] if res else 0

    @staticmethod
    def sqlXsUserpopularity(uid: str) -> int:
        """查询用户人气数据
        
        Args:
            uid: 用户 ID
            
        Returns:
            人气值
        """
        sql = f"SELECT popularity FROM xs_user_popularity WHERE uid={uid}"
        res = MySQLConnection.get_cursor().execute(sql)
        return res[0] if res else 0

    @staticmethod
    def sqlXsUserprofile_pay_room_money(uid: str) -> int:
        """查询用户 VIP 数据
        
        Args:
            uid: 用户 ID
            
        Returns:
            VIP 经验值
        """
        sql = f"SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}"
        res = MySQLConnection.get_cursor().execute(sql)
        return res[0] if res else 0
