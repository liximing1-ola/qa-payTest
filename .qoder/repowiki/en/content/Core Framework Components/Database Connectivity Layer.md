# Database Connectivity Layer

<cite>
**Referenced Files in This Document**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [Config.py](file://common/Config.py)
- [sqlScript.py](file://common/sqlScript.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [test_pt_bean.py](file://caseOversea/test_pt_bean.py)
- [test_check.py](file://caseSlp/test_check.py)
- [test_starify_contractPay.py](file://caseStarify/test_starify_contractPay.py)
- [requirements.txt](file://requirements.txt)
- [config_dev.php](file://others/config_dev.php)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the database connectivity layer used by the test automation framework. It covers:
- MySQL connection management across multiple platforms (Banban, PT Overseas, Starify, SLP)
- Redis caching integration
- Transaction handling and rollback semantics
- Connection lifecycle and validation
- Multi-platform architecture and usage patterns
- Security, connection limits, and performance monitoring considerations

The layer is implemented via platform-specific connector classes that encapsulate database operations and provide a unified interface for tests to prepare and verify state.

## Project Structure
The database connectivity layer is organized under the common package with platform-specific connectors and shared utilities:
- Platform connectors: MySQL connectors for each platform
- Shared utilities: Redis connector and generic SQL helpers
- Tests: Example usage across platforms

```mermaid
graph TB
subgraph "Common Connectors"
A["conMysql.py<br/>Banban MySQL"]
B["conPtMysql.py<br/>PT Overseas MySQL"]
C["conSlpMysql.py<br/>SLP MySQL"]
D["conStarifyMysql.py<br/>Starify MySQL"]
E["conRedis.py<br/>Redis Connector"]
F["sqlScript.py<br/>Generic MySQL Helpers"]
end
subgraph "Tests"
T1["test_pay_business.py"]
T2["test_pt_bean.py"]
T3["test_check.py"]
T4["test_starify_contractPay.py"]
end
subgraph "Config"
G["Config.py"]
H["requirements.txt"]
I["config_dev.php"]
end
T1 --> A
T2 --> B
T3 --> C
T4 --> D
T1 --> G
T2 --> G
T3 --> G
T4 --> G
E -.-> T1
E -.-> T2
E -.-> T3
E -.-> T4
A -.-> F
B -.-> F
C -.-> F
D -.-> F
H --> A
H --> B
H --> C
H --> D
H --> E
I --> A
I --> B
I --> C
I --> D
```

**Diagram sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [sqlScript.py](file://common/sqlScript.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [test_pt_bean.py](file://caseOversea/test_pt_bean.py)
- [test_check.py](file://caseSlp/test_check.py)
- [test_starify_contractPay.py](file://caseStarify/test_starify_contractPay.py)
- [Config.py](file://common/Config.py)
- [requirements.txt](file://requirements.txt)
- [config_dev.php](file://others/config_dev.php)

**Section sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [sqlScript.py](file://common/sqlScript.py)
- [Config.py](file://common/Config.py)
- [requirements.txt](file://requirements.txt)
- [config_dev.php](file://others/config_dev.php)

## Core Components
- MySQL connectors per platform:
  - Banban: [conMysql.py](file://common/conMysql.py)
  - PT Overseas: [conPtMysql.py](file://common/conPtMysql.py)
  - SLP: [conSlpMysql.py](file://common/conSlpMysql.py)
  - Starify: [conStarifyMysql.py](file://common/conStarifyMysql.py)
- Shared utilities:
  - Generic MySQL helpers: [sqlScript.py](file://common/sqlScript.py)
  - Redis connector: [conRedis.py](file://common/conRedis.py)
- Configuration:
  - Test configuration constants and UIDs: [Config.py](file://common/Config.py)
  - Dependencies and libraries: [requirements.txt](file://requirements.txt)
  - Legacy PHP DB/Redis configs: [config_dev.php](file://others/config_dev.php)

Key capabilities:
- Select/update/delete operations for user balances, commodities, profiles, rooms, and platform-specific tables
- Transaction safety with explicit rollback and commit
- Connection validation via ping and database selection
- Redis connection pooling and key operations

**Section sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [sqlScript.py](file://common/sqlScript.py)
- [Config.py](file://common/Config.py)
- [requirements.txt](file://requirements.txt)
- [config_dev.php](file://others/config_dev.php)

## Architecture Overview
The connectivity layer follows a per-platform connector pattern with shared utilities:
- Each connector initializes a persistent connection and cursor
- Operations are exposed as static methods for convenience
- Transactions are handled explicitly with rollback/commit blocks
- Tests import platform connectors and configuration to orchestrate preconditions and verifications

```mermaid
sequenceDiagram
participant Test as "Test Case"
participant Conn as "Platform MySQL Connector"
participant DB as "MySQL Server"
participant Conf as "Config"
Test->>Conf : Load platform UIDs and endpoints
Test->>Conn : Prepare test data (update/select/delete)
Conn->>DB : Execute SQL with cursor
DB-->>Conn : Result rows or affected rows
Conn-->>Test : Data values or status
Test->>Conn : Optional cleanup (delete/update)
Conn->>DB : Commit or rollback as needed
```

**Diagram sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [Config.py](file://common/Config.py)

## Detailed Component Analysis

### MySQL Connectors (Per Platform)
Each platform defines a connector class that:
- Stores credentials and target database
- Establishes a connection with autocommit enabled
- Selects the target database and validates connectivity
- Exposes static methods for common operations

```mermaid
classDiagram
class ConMysql_Banban {
+selectUserInfoSql(...)
+updateMoneySql(...)
+deleteUserAccountSql(...)
+insertXsUserCommodity(...)
+checkXsCommodity(...)
+checkUserXsBroker(...)
+checkUserXsMentorLevel(...)
}
class ConMysql_PT {
+selectUserInfoSql(...)
+updateMoneySql(...)
+deleteUserAccountSql(...)
+insertXsUserCommodity(...)
+updateUserBigArea(...)
+updateUserLanguage(...)
}
class ConMysql_SLP {
+selectUserInfoSql(...)
+updateMoneySql(...)
+deleteUserAccountSql(...)
+updateUserInfoSql(...)
+checkRidFactoryType(...)
+selectZxPayData(...)
}
class ConMysql_Starify {
+selectUserInfoSql(...)
+updateMoneySql(...)
+updateWealthSql(...)
+updateCharmSql(...)
+deleteUserAccountSql(...)
+insertXsUserCommodity(...)
+deleteProducerSinger(...)
+selectProducerSinger(...)
+updateSingerWorth(...)
}
```

**Diagram sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)

Operational highlights:
- Connection initialization and validation:
  - Autocommit enabled
  - Database selected
  - Ping with reconnect enabled
- Transaction handling:
  - Try-except blocks around DML statements
  - Explicit rollback on failure
  - Explicit commit on success
- Data access patterns:
  - Static methods accept platform-specific parameters (UIDs, money types, etc.)
  - Fetch-one/fetch-all helpers return normalized values or defaults

Usage examples in tests:
- Banban business room payments: [test_pay_business.py](file://case/test_pay_business.py)
- PT bean exchange: [test_pt_bean.py](file://caseOversea/test_pt_bean.py)
- SLP boundary checks: [test_check.py](file://caseSlp/test_check.py)
- Starify contract payments: [test_starify_contractPay.py](file://caseStarify/test_starify_contractPay.py)

**Section sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [test_pt_bean.py](file://caseOversea/test_pt_bean.py)
- [test_check.py](file://caseSlp/test_check.py)
- [test_starify_contractPay.py](file://caseStarify/test_starify_contractPay.py)

### Redis Connector
The Redis connector provides:
- Connection pool creation with configurable host/port
- Helper methods to manage sets and hash fields

```mermaid
flowchart TD
Start(["Call Redis Helper"]) --> GetConn["Create Connection Pool"]
GetConn --> UseRedis["Get Redis Client"]
UseRedis --> OpType{"Operation Type"}
OpType --> |Set| AddKey["Add/Set Key"]
OpType --> |Hash| DelKey["Delete Hash Fields"]
AddKey --> End(["Done"])
DelKey --> End
```

**Diagram sources**
- [conRedis.py](file://common/conRedis.py)

**Section sources**
- [conRedis.py](file://common/conRedis.py)

### Generic MySQL Helpers
The generic helpers offer:
- Connection factory with host/user/password/db selection
- Common DML operations with explicit transaction control

```mermaid
flowchart TD
Start(["Generic MySQL Helper"]) --> Factory["Create Connection"]
Factory --> Exec["Execute SQL"]
Exec --> Result{"Success?"}
Result --> |Yes| Commit["Commit"]
Result --> |No| Rollback["Rollback"]
Commit --> End(["Close/Return"])
Rollback --> End
```

**Diagram sources**
- [sqlScript.py](file://common/sqlScript.py)

**Section sources**
- [sqlScript.py](file://common/sqlScript.py)

## Dependency Analysis
External dependencies relevant to database connectivity:
- PyMySQL: MySQL driver
- redis: Redis client

```mermaid
graph LR
Tests["Test Cases"] --> Conn["Platform Connectors"]
Conn --> PyMySQL["PyMySQL"]
Conn --> RedisLib["redis"]
Conn --> Config["Config"]
PyMySQL --> MySQL["MySQL Server"]
RedisLib --> RedisSrv["Redis Server"]
```

**Diagram sources**
- [requirements.txt](file://requirements.txt)
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [Config.py](file://common/Config.py)

**Section sources**
- [requirements.txt](file://requirements.txt)
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [Config.py](file://common/Config.py)

## Performance Considerations
- Connection reuse: Each connector maintains a single persistent connection and cursor, reducing overhead.
- Autocommit behavior: Enabled at connection time; explicit commits occur after operations.
- Batch updates: Some connectors iterate over UIDs and issue multiple updates; consider batching or minimizing sleeps where present.
- Cursor usage: Dedicated cursors per connector; ensure proper resource handling.
- Network locality: Hosts are configured per platform; keep database connections local to reduce latency.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and remedies:
- Connection failures
  - Verify host/port and credentials in connector configuration
  - Confirm database selection and connectivity via ping
- Transaction anomalies
  - Ensure rollback is invoked on exceptions and commit occurs otherwise
  - Check autocommit settings and explicit commit boundaries
- Data mismatches
  - Validate UID correctness from configuration
  - Confirm money-type parameters and table/column names per platform
- Redis connectivity
  - Confirm host/port and pool creation
  - Validate key operations (set/add vs hash/del)

**Section sources**
- [conMysql.py](file://common/conMysql.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [conRedis.py](file://common/conRedis.py)
- [Config.py](file://common/Config.py)

## Conclusion
The database connectivity layer provides a consistent, per-platform abstraction over MySQL and Redis, enabling reliable test data preparation and verification. Each connector encapsulates connection lifecycle, transaction control, and platform-specific operations, while shared utilities support common patterns. Adhering to explicit rollback/commit semantics and validating connections ensures robustness across Banban, PT Overseas, Starify, and SLP environments.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Example Workflows

#### Banban Business Room Payments
```mermaid
sequenceDiagram
participant TC as "Test Case"
participant CFG as "Config"
participant BAN as "conMysql"
participant API as "Payment API"
participant DB as "MySQL"
TC->>CFG : Load payUid/rewardUid
TC->>BAN : updateMoneySql(payUid, initial balance)
TC->>BAN : updateMoneySql(rewardUid, reset)
TC->>API : Send payment request
API-->>TC : Response
TC->>BAN : selectUserInfoSql(single_money, rewardUid)
TC->>BAN : selectUserInfoSql(pay_room_money, payUid)
TC->>BAN : Cleanup (optional)
```

**Diagram sources**
- [test_pay_business.py](file://case/test_pay_business.py)
- [conMysql.py](file://common/conMysql.py)
- [Config.py](file://common/Config.py)

**Section sources**
- [test_pay_business.py](file://case/test_pay_business.py)
- [conMysql.py](file://common/conMysql.py)
- [Config.py](file://common/Config.py)

#### PT Bean Exchange
```mermaid
sequenceDiagram
participant TC as "Test Case"
participant PT as "conPtMysql"
participant API as "Payment API"
participant DB as "MySQL"
TC->>PT : checkXsGiftConfig()
TC->>PT : updateMoneySql(pt_payUid, money=300)
TC->>API : exchange_gold request
API-->>TC : Response
TC->>PT : selectUserInfoSql(sum_money, pt_payUid)
TC->>PT : selectUserInfoSql(single_money, pt_payUid, gold_coin)
```

**Diagram sources**
- [test_pt_bean.py](file://caseOversea/test_pt_bean.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [Config.py](file://common/Config.py)

**Section sources**
- [test_pt_bean.py](file://caseOversea/test_pt_bean.py)
- [conPtMysql.py](file://common/conPtMysql.py)
- [Config.py](file://common/Config.py)

#### SLP Boundary Checks
```mermaid
flowchart TD
Start(["SLP Negative Balance Tests"]) --> Prep["Clear balances & commodities"]
Prep --> Tx1["Attempt chat-gift with insufficient funds"]
Tx1 --> Verify1["Assert failure and zero balance"]
Prep --> Tx2["Attempt package with insufficient funds"]
Tx2 --> Verify2["Assert failure and zero balance"]
Prep --> Tx3["Attempt with exact balance"]
Tx3 --> Verify3["Assert success and zero remaining"]
End(["Done"])
```

**Diagram sources**
- [test_check.py](file://caseSlp/test_check.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [Config.py](file://common/Config.py)

**Section sources**
- [test_check.py](file://caseSlp/test_check.py)
- [conSlpMysql.py](file://common/conSlpMysql.py)
- [Config.py](file://common/Config.py)

#### Starify Contract Payments
```mermaid
sequenceDiagram
participant TC as "Test Case"
participant ST as "conStarifyMysql"
participant API as "Starify Payment API"
participant DB as "MySQL"
TC->>ST : updateMoneySql(a_uid, default_money)
TC->>ST : updateMoneySql(b_uid, default_money)
TC->>ST : updateMoneySql(c_uid, 0)
TC->>ST : updateWealthSql(a_uid, 0)
TC->>ST : updateWealthSql(b_uid, 0)
TC->>ST : deleteProducerSinger(c_uid)
TC->>ST : updateSingerWorth(c_uid, 100)
TC->>API : audition_contract (direct sign)
TC->>API : audition_contract (bid rounds)
TC->>ST : selectUserInfoSql(star_coin, participants)
TC->>ST : selectProducerSinger(a_uid/b_uid)
```

**Diagram sources**
- [test_starify_contractPay.py](file://caseStarify/test_starify_contractPay.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [Config.py](file://common/Config.py)

**Section sources**
- [test_starify_contractPay.py](file://caseStarify/test_starify_contractPay.py)
- [conStarifyMysql.py](file://common/conStarifyMysql.py)
- [Config.py](file://common/Config.py)

### Security and Operational Notes
- Credentials: Stored in connector configuration; avoid hardcoding secrets in tests.
- Connection limits: Single persistent connection per connector; scale horizontally by using multiple connector instances or external pooling where needed.
- Validation: Use ping and database selection during initialization.
- Monitoring: Track operation latencies and error rates at the test harness level; consider adding metrics hooks around connector methods.

[No sources needed since this section provides general guidance]