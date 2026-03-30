# Planet Journey Tests

<cite>
**本文档引用的文件**
- [README.md](file://README.md)
- [run_all_case.py](file://run_all_case.py)
- [Robot.py](file://Robot.py)
- [common/Config.py](file://common/Config.py)
- [common/Consts.py](file://common/Consts.py)
- [common/Request.py](file://common/Request.py)
- [common/Assert.py](file://common/Assert.py)
- [common/Session.py](file://common/Session.py)
- [common/conMysql.py](file://common/conMysql.py)
- [common/Logs.py](file://common/Logs.py)
- [autoGitPull.py](file://autoGitPull.py)
- [common/getToken.py](file://common/getToken.py)
- [requirements.txt](file://requirements.txt)
- [case/test_pay_shopBuy.py](file://case/test_pay_shopBuy.py)
- [case/test_pay_openBox.py](file://case/test_pay_openBox.py)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构概览](#架构概览)
5. [详细组件分析](#详细组件分析)
6. [依赖分析](#依赖分析)
7. [性能考虑](#性能考虑)
8. [故障排除指南](#故障排除指南)
9. [结论](#结论)

## 简介

Planet Journey支付测试自动化框架是一个全面的测试解决方案，专门用于验证支付模块的各种场景。该框架支持多种支付场景的自动化测试，包括金豆支付、金币支付、商城购买、房间支付等。

### 主要特性

- **多应用支持**：支持伴伴、Planet Journey（PT）、不夜星球等多个应用的测试
- **多环境配置**：支持开发、测试、生产等不同环境的配置管理
- **自动化通知**：集成机器人通知系统，支持微信和Slack消息推送
- **数据库集成**：内置数据库连接和操作功能，支持复杂的测试数据准备
- **断言验证**：提供丰富的断言方法，支持多种验证场景
- **并发测试**：支持并发测试执行，提高测试效率

## 项目结构

```mermaid
graph TB
subgraph "项目根目录"
A[README.md] --> B[requirements.txt]
A --> C[run_all_case.py]
A --> D[Robot.py]
A --> E[autoGitPull.py]
end
subgraph "测试用例目录"
F[case/] --> G[test_pay_shopBuy.py]
F --> H[test_pay_openBox.py]
F --> I[其他支付测试用例...]
J[caseOversea/] --> K[海外版测试用例]
L[caseSlp/] --> M[SLP平台测试用例]
N[caseStarify/] --> O[Starify平台测试用例]
P[caseGames/] --> Q[游戏平台测试用例]
R[caseLuckyPlay/] --> S[玩法测试用例]
end
subgraph "公共模块"
T[common/] --> U[Config.py]
T --> V[Request.py]
T --> W[Assert.py]
T --> X[Session.py]
T --> Y[conMysql.py]
T --> Z[Logs.py]
T --> AA[getToken.py]
T --> AB[Consts.py]
end
C --> F
C --> T
D --> T
E --> T
```

**图表来源**
- [README.md:1-103](file://README.md#L1-L103)
- [run_all_case.py:1-240](file://run_all_case.py#L1-L240)

### 目录组织说明

- **case/**：核心支付测试用例目录，包含各种支付场景的测试
- **caseOversea/**：海外版本测试用例，支持多地区支付场景
- **caseSlp/**：SLP平台专用测试用例
- **caseStarify/**：Starify平台测试用例
- **caseGames/**：游戏相关支付测试
- **caseLuckyPlay/**：各种玩法测试用例
- **common/**：公共模块，包含框架的核心功能

**章节来源**
- [README.md:7-103](file://README.md#L7-L103)
- [run_all_case.py:18-45](file://run_all_case.py#L18-L45)

## 核心组件

### 配置管理系统

配置管理是整个测试框架的基础，负责管理各种环境配置和全局设置。

```mermaid
classDiagram
class Config {
+BASE_PATH : str
+appInfo : AppConfig
+codeInfo : CodeConfig
+appName : AppNameConfig
+linux_node : LinuxNodeConfig
+rate : float
+bb_user : BBUserConfig
+live_role : LiveRoleConfig
+pt_user : PTUserConfig
+pt_room : PTRoomConfig
+giftId : Dict[str, int]
+pt_giftId : Dict[str, int]
+pay_url : str
+slp_pay_url : str
+bb_qqLogin_url : str
+pt_mobile_login_url : str
+starify_mobile_login_url : str
+slp_mobile_login_url : str
}
class AppConfig {
+bb_dev : str
+app_ali_dev : str
+app_ali_main : str
+starify : str
+slp : str
+rush : str
}
class CodeConfig {
+bb_php_path : str
+bb_go_path : str
+app_php_path : str
+bb_git_branch : str
+bb_go_git_branch : str
+app_git_branch : str
+slp_php_path : str
+slp_common_rpc_path : str
+slp_git_branch : str
}
class AppNameConfig {
+_1 : str
+_2 : str
+谁是凶手 : str
+不夜星球 : str
+__getitem__(key) : str
}
Config --> AppConfig
Config --> CodeConfig
Config --> AppNameConfig
```

**图表来源**
- [common/Config.py:15-241](file://common/Config.py#L15-L241)

### HTTP请求封装

统一的HTTP请求处理，支持多种认证方式和错误处理。

```mermaid
classDiagram
class Request {
+DEFAULT_HEADERS : Dict[str, str]
+DEFAULT_TIMEOUT : float
+post_request_session(url, data, token_name, timeout) : Dict[str, Any]
+_build_headers(token_name) : Dict[str, str]
+_ensure_https(url) : str
+_parse_response(response) : Dict[str, Any]
}
class Session {
+ENV_CONFIGS : Dict[str, Dict[str, Any]]
+getSession(env) : Optional[Dict[str, str]]
+checkUserToken(operate, app_name, token, uid) : Optional[str]
+_login(env_config, env) : Dict[str, Any]
+_handle_response(res, env) : Optional[Dict[str, str]]
+_use_backup_plan(env, error_msg) : Dict[str, str]
}
Request --> Session : "使用"
```

**图表来源**
- [common/Request.py:27-107](file://common/Request.py#L27-L107)
- [common/Session.py:19-191](file://common/Session.py#L19-L191)

### 断言验证系统

提供多种断言方法，支持复杂的验证场景。

```mermaid
classDiagram
class Assert {
+RPC_DELAY : float
+assert_code(actual_code, expected_code) : bool
+assert_len(actual_len, expect_len) : bool
+assert_equal(actual_result, expect_result) : bool
+assert_in_text(body, expected_msg) : bool
+assert_body(body, body_msg, expected_msg, reason) : bool
+assert_between(actual_result, lower_limit, upper_limit) : bool
+_delay_for_rpc() : void
+_record_failure(reason) : void
+_assert_wrapper(func) : Callable
}
class Consts {
+case_list : dict
+case_list_b : dict
+case_list_c : dict
+fail_case_reason : list
+result : str
+startTime : int
+endTime : int
+success_num : int
+fail_num : int
}
Assert --> Consts : "记录失败原因"
```

**图表来源**
- [common/Assert.py:16-167](file://common/Assert.py#L16-L167)
- [common/Consts.py:1-17](file://common/Consts.py#L1-17)

**章节来源**
- [common/Config.py:121-241](file://common/Config.py#L121-L241)
- [common/Request.py:1-119](file://common/Request.py#L1-L119)
- [common/Assert.py:1-167](file://common/Assert.py#L1-L167)
- [common/Consts.py:1-17](file://common/Consts.py#L1-L17)

## 架构概览

```mermaid
graph TB
subgraph "测试执行层"
A[run_all_case.py] --> B[unittest.TextTestRunner]
A --> C[测试套件发现]
end
subgraph "业务逻辑层"
D[TestPayShopBuy] --> E[支付请求处理]
D --> F[数据库状态验证]
G[TestPayOpenBox] --> E
G --> F
end
subgraph "基础设施层"
H[Request.py] --> I[HTTP请求]
H --> J[Token管理]
K[Session.py] --> L[用户认证]
K --> M[备选方案]
N[conMysql.py] --> O[数据库操作]
P[Assert.py] --> Q[断言验证]
R[Logs.py] --> S[日志记录]
end
subgraph "通知系统"
T[Robot.py] --> U[微信通知]
T --> V[Slack通知]
W[autoGitPull.py] --> T
end
A --> D
A --> G
D --> H
G --> H
H --> N
H --> K
D --> P
G --> P
A --> R
A --> W
W --> T
```

**图表来源**
- [run_all_case.py:48-77](file://run_all_case.py#L48-L77)
- [common/Request.py:71-107](file://common/Request.py#L71-L107)
- [common/Session.py:126-153](file://common/Session.py#L126-L153)
- [common/conMysql.py:8-204](file://common/conMysql.py#L8-L204)

### 测试执行流程

```mermaid
sequenceDiagram
participant Runner as "测试运行器"
participant Loader as "用例加载器"
participant Test as "测试用例"
participant Request as "HTTP请求"
participant DB as "数据库"
participant Assert as "断言验证"
participant Logger as "日志记录"
Runner->>Loader : discover(pattern="test_*.py")
Loader-->>Runner : TestSuite
Runner->>Test : setUp()
Test->>Request : post_request_session()
Request-->>Test : response
Test->>Assert : 断言验证
Assert-->>Test : 验证结果
Test->>DB : 数据库查询
DB-->>Test : 查询结果
Test->>Assert : 数据库断言
Assert-->>Test : 验证结果
Test->>Logger : 记录测试结果
Logger-->>Runner : 日志输出
Runner->>Runner : 处理测试结果
```

**图表来源**
- [run_all_case.py:48-77](file://run_all_case.py#L48-L77)
- [case/test_pay_shopBuy.py:45-79](file://case/test_pay_shopBuy.py#L45-L79)

## 详细组件分析

### 商城购买测试组件

商城购买测试组件验证了商城购买道具的各种场景，包括单个购买、批量购买、礼物赠送等功能。

```mermaid
classDiagram
class TestPayShopBuy {
+gift_cid : Dict[str, int]
+_prepare_test_data(setup_steps) : void
+_validate_db_state(checks) : void
+test_01_shopPayChangeMoney() : void
+test_02_shopPayChangeBuyMore() : void
+test_03_shopGiftToUser() : void
+test_04_shopGiftToUserNoEnough() : void
}
class UserMoneyOperations {
+update(uid, money, money_cash, money_cash_b, money_b, gold_coin) : void
}
class UserCommodityOperations {
+insert(uid, cid, num, state) : void
}
class conMysql {
+selectUserInfoSql(accountType, uid, money_type, cid) : Any
+deleteUserAccountSql(tableName, uid) : void
+updateUserMoneyClearSql(uid1, uid2) : void
+insertXsUserBox(uid, gift_cid, box_type) : void
}
TestPayShopBuy --> UserMoneyOperations : "准备测试数据"
TestPayShopBuy --> UserCommodityOperations : "准备测试数据"
TestPayShopBuy --> conMysql : "数据库验证"
```

**图表来源**
- [case/test_pay_shopBuy.py:13-191](file://case/test_pay_shopBuy.py#L13-L191)
- [common/conMysql.py:28-204](file://common/conMysql.py#L28-L204)

#### 测试流程分析

```mermaid
flowchart TD
Start([开始测试]) --> PrepareData["准备测试数据<br/>- 更新用户余额<br/>- 清空背包数据"]
PrepareData --> SendRequest["发送支付请求<br/>encodeData() + post_request_session()"]
SendRequest --> ValidateResponse["验证响应<br/>- 状态码验证<br/>- 返回值验证"]
ValidateResponse --> DBCheck["数据库状态验证<br/>- 余额检查<br/>- 物品数量检查"]
DBCheck --> RecordResult["记录测试结果<br/>case_list[des] = result"]
RecordResult --> End([测试完成])
PrepareData -.-> PrepareData2["准备测试数据<br/>- 清空双方余额"]
PrepareData2 --> SendRequest2["发送礼物赠送请求"]
SendRequest2 --> ValidateResponse2["验证响应"]
ValidateResponse2 --> DBCheck2["数据库验证<br/>- 背包物品减少<br/>- 收礼者余额增加"]
DBCheck2 --> RecordResult2["记录测试结果"]
RecordResult2 --> End
```

**图表来源**
- [case/test_pay_shopBuy.py:45-191](file://case/test_pay_shopBuy.py#L45-L191)

**章节来源**
- [case/test_pay_shopBuy.py:13-191](file://case/test_pay_shopBuy.py#L13-L191)

### 开箱子测试组件

开箱子测试组件验证了背包内开箱子的各种场景，包括单次开箱、批量开箱、房间内送箱等功能。

```mermaid
classDiagram
class TestPayOpenBox {
+_prepare_test_data(setup_steps) : void
+_validate_db_state(checks) : void
+test_01_openBoxPayChange() : void
+test_02_openMoreBoxPayChange() : void
+test_03_giveBoxPayChange() : void
+test_04_giveBoxMorePeople() : void
}
class UserCommodityOperations {
+insert(uid, cid, num, state) : void
}
class conMysql {
+insertXsUserBox(uid, gift_cid, box_type) : void
+selectUserInfoSql(accountType, uid, money_type, cid) : Any
}
TestPayOpenBox --> UserCommodityOperations : "准备测试数据"
TestPayOpenBox --> conMysql : "数据库操作"
```

**图表来源**
- [case/test_pay_openBox.py:12-193](file://case/test_pay_openBox.py#L12-L193)
- [common/conMysql.py:389-401](file://common/conMysql.py#L389-L401)

#### 开箱场景验证

```mermaid
sequenceDiagram
participant Test as "测试用例"
participant Data as "测试数据准备"
participant Box as "箱子操作"
participant DB as "数据库验证"
participant Assert as "断言验证"
Test->>Data : 准备测试数据
Data->>DB : 清空用户背包
Data->>DB : 插入箱子物品
Data->>DB : 设置用户余额
Test->>Box : 发送开箱请求
Box-->>Test : 返回开箱结果
Test->>Assert : 验证响应状态
Assert-->>Test : 断言通过
Test->>DB : 查询余额变化
DB-->>Test : 返回余额数据
Test->>Assert : 验证余额
Assert-->>Test : 断言通过
Test->>DB : 查询物品数量
DB-->>Test : 返回物品数据
Test->>Assert : 验证物品数量
Assert-->>Test : 断言通过
```

**图表来源**
- [case/test_pay_openBox.py:40-80](file://case/test_pay_openBox.py#L40-L80)

**章节来源**
- [case/test_pay_openBox.py:12-193](file://case/test_pay_openBox.py#L12-L193)

### 通知系统组件

通知系统负责测试结果的通知和消息推送。

```mermaid
classDiagram
class Robot {
+ROBOT_URLS : Dict[str, Dict[str, str]]
+send_request(url, data, headers) : Optional[Response]
+send_text(url, content, at_all) : Optional[Response]
+send_markdown(url, content) : Optional[Response]
+send_news(url, title, description, picurl, link) : Optional[Response]
+send_slack(url, title, reason, color) : Optional[Response]
+robot(mode, reason, title, bot, color, to) : None
}
class GitUpdater {
+APP_CONFIGS : Dict[str, Dict[str, Any]]
+NOTIFICATION_MODES : Dict[str, str]
+autoGitPull(app_info, env, bot, to) : bool
+_get_config(app_info) : Dict[str, Any]
+_send_notification(app_info, commit_info, bot, to) : void
+_pull_code(path, app_info) : void
+_get_commits(repo) : List[str]
}
Robot --> GitUpdater : "被调用"
```

**图表来源**
- [Robot.py:13-169](file://Robot.py#L13-L169)
- [autoGitPull.py:23-136](file://autoGitPull.py#L23-L136)

**章节来源**
- [Robot.py:1-170](file://Robot.py#L1-L170)
- [autoGitPull.py:1-169](file://autoGitPull.py#L1-L169)

## 依赖分析

### 核心依赖关系

```mermaid
graph TB
subgraph "测试框架依赖"
A[pytest] --> B[unittest]
C[allure-pytest] --> A
D[requests] --> E[HTTP请求]
F[PyMySQL] --> G[数据库操作]
H[gevent] --> I[并发处理]
end
subgraph "配置管理依赖"
J[PyYAML] --> K[YAML配置]
L[GitPython] --> M[Git操作]
end
subgraph "安全依赖"
N[cryptography] --> O[加密功能]
P[PyJWT] --> Q[JWT处理]
end
subgraph "工具库依赖"
R[Markdown] --> S[文档生成]
T[psutil] --> U[系统监控]
end
A --> J
D --> N
H --> T
```

**图表来源**
- [requirements.txt:1-91](file://requirements.txt#L1-L91)

### 组件耦合度分析

| 组件 | 内聚性 | 耦合度 | 依赖关系 |
|------|--------|--------|----------|
| Config | 高 | 低 | 基础配置 |
| Request | 中 | 中 | Session, Config |
| Session | 中 | 中 | Config, YAML |
| Assert | 高 | 低 | Consts |
| conMysql | 高 | 中 | Config |
| Robot | 中 | 中 | Requests |
| GitUpdater | 中 | 中 | GitPython, Robot |

**章节来源**
- [requirements.txt:1-91](file://requirements.txt#L1-L91)

## 性能考虑

### 并发测试优化

框架支持并发测试执行，通过以下机制优化性能：

1. **连接池管理**：合理管理数据库连接，避免连接泄漏
2. **请求超时控制**：设置合理的请求超时时间，防止阻塞
3. **资源清理**：测试结束后及时清理临时数据和连接
4. **日志异步**：使用异步日志记录，减少I/O阻塞

### 数据库性能优化

```mermaid
flowchart TD
Start([数据库操作开始]) --> CheckPool["检查连接池状态"]
CheckPool --> PoolAvailable{"连接可用？"}
PoolAvailable --> |是| UseConnection["使用现有连接"]
PoolAvailable --> |否| CreateConnection["创建新连接"]
UseConnection --> ExecuteQuery["执行SQL查询"]
CreateConnection --> ExecuteQuery
ExecuteQuery --> CloseConnection["关闭连接"]
CloseConnection --> End([数据库操作结束])
```

**图表来源**
- [common/conMysql.py:8-26](file://common/conMysql.py#L8-L26)

## 故障排除指南

### 常见问题及解决方案

#### 1. Token获取失败

**问题症状**：测试执行时报错提示Token无效或过期

**解决方案**：
- 检查Session配置是否正确
- 验证备选方案是否正常工作
- 确认数据库中的用户信息是否存在

#### 2. 数据库连接异常

**问题症状**：数据库操作报连接超时或连接拒绝

**解决方案**：
- 检查数据库服务状态
- 验证连接配置参数
- 确认防火墙设置

#### 3. HTTP请求超时

**问题症状**：支付请求长时间无响应

**解决方案**：
- 增加请求超时时间
- 检查网络连接
- 验证目标服务器状态

#### 4. 断言失败

**问题症状**：测试用例执行失败，断言不通过

**解决方案**：
- 检查测试数据准备是否正确
- 验证期望值设置
- 查看失败原因记录

**章节来源**
- [common/Session.py:105-153](file://common/Session.py#L105-L153)
- [common/conMysql.py:8-26](file://common/conMysql.py#L8-L26)
- [common/Request.py:98-106](file://common/Request.py#L98-L106)

## 结论

Planet Journey支付测试自动化框架是一个功能完整、结构清晰的测试解决方案。该框架具有以下特点：

### 优势

1. **模块化设计**：各个组件职责明确，便于维护和扩展
2. **配置灵活**：支持多环境配置，适应不同的测试需求
3. **自动化程度高**：从测试执行到结果通知全程自动化
4. **数据完整性**：完善的数据库操作和验证机制
5. **错误处理完善**：全面的异常处理和故障恢复机制

### 改进建议

1. **测试数据管理**：可以考虑引入更强大的测试数据生成工具
2. **报告增强**：可以集成更丰富的测试报告生成功能
3. **监控集成**：可以添加实时监控和告警功能
4. **容器化部署**：可以考虑支持Docker容器化部署

该框架为支付模块的自动化测试提供了坚实的基础，能够有效提高测试效率和质量，减少人工干预，确保支付功能的稳定性和可靠性。