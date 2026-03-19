# Data Validation and Transaction Logging

<cite>
**Referenced Files in This Document**
- [Assert.py](file://common/Assert.py)
- [Logs.py](file://common/Logs.py)
- [sqlScript.py](file://common/sqlScript.py)
- [conMysql.py](file://common/conMysql.py)
- [Config.py](file://common/Config.py)
- [test_pay_bean.py](file://case/test_pay_bean.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [Consts.py](file://common/Consts.py)
- [run_all_case.py](file://run_all_case.py)
- [basicData.py](file://common/basicData.py)
- [method.py](file://common/method.py)
- [Request.py](file://common/Request.py)
- [Session.py](file://common/Session.py)
- [testPayConcurrent.py](file://testPayConcurrent.py)
- [testConcurrent.py](file://testConcurrent.py)
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
This document explains the data validation and transaction logging mechanisms used in the payment test suite. It covers:
- SQL script execution framework and transaction safety
- Parameter binding via payload builders
- Assertion engine for payment outcomes and account balances
- Logging strategies for audit trails, error tracking, and notifications
- Validation patterns for concurrent transactions and race condition mitigation
- Consistency checks across platforms and environments

## Project Structure
The repository organizes test cases per product area under dedicated folders, with shared utilities for database access, HTTP requests, assertions, logging, and configuration.

```mermaid
graph TB
subgraph "Test Cases"
BB["case/test_pay_bean.py"]
BUS["case/test_pay_business.py"]
end
subgraph "Common Utilities"
REQ["common/Request.py"]
BASIC["common/basicData.py"]
CONM["common/conMysql.py"]
SQLS["common/sqlScript.py"]
ASRT["common/Assert.py"]
LOGS["common/Logs.py"]
CONF["common/Config.py"]
SESS["common/Session.py"]
METH["common/method.py"]
CONST["common/Consts.py"]
end
BB --> REQ
BUS --> REQ
BB --> BASIC
BUS --> BASIC
BB --> CONM
BUS --> CONM
BB --> ASRT
BUS --> ASRT
BB --> LOGS
BUS --> LOGS
BB --> CONF
BUS --> CONF
BB --> SESS
BUS --> SESS
BB --> METH
BUS --> METH
BB --> CONST
BUS --> CONST
```

**Diagram sources**
- [test_pay_bean.py](file://case/test_pay_bean.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [Request.py](file://common/Request.py)
- [basicData.py](file://common/basicData.py)
- [conMysql.py](file://common/conMysql.py)
- [sqlScript.py](file://common/sqlScript.py)
- [Assert.py](file://common/Assert.py)
- [Logs.py](file://common/Logs.py)
- [Config.py](file://common/Config.py)
- [Session.py](file://common/Session.py)
- [method.py](file://common/method.py)
- [Consts.py](file://common/Consts.py)

**Section sources**
- [run_all_case.py](file://run_all_case.py)
- [Config.py](file://common/Config.py)

## Core Components
- Assertion Engine: Provides standardized checks for HTTP status, JSON body fields, equality, length thresholds, and ranges.
- Database Access Layer: Centralized MySQL helpers for reads, writes, and cleanup across multiple schemas.
- Payload Builders: Encode structured request payloads for various payment scenarios.
- HTTP Client: Wraps session-based requests with token injection and timing metrics.
- Logging: Rotating logs with console and file handlers for audit and diagnostics.
- Configuration: Centralized endpoints, UIDs, gift IDs, and environment-specific settings.
- Concurrency Utilities: Helpers for concurrent load testing and transaction safety.

**Section sources**
- [Assert.py](file://common/Assert.py)
- [conMysql.py](file://common/conMysql.py)
- [sqlScript.py](file://common/sqlScript.py)
- [basicData.py](file://common/basicData.py)
- [Request.py](file://common/Request.py)
- [Logs.py](file://common/Logs.py)
- [Config.py](file://common/Config.py)
- [Session.py](file://common/Session.py)
- [method.py](file://common/method.py)
- [Consts.py](file://common/Consts.py)

## Architecture Overview
End-to-end flow for payment validation:
- Payload construction → HTTP request → Assertions → Database verification → Logging and notifications

```mermaid
sequenceDiagram
participant T as "TestCase"
participant P as "Payload Builder<br/>basicData.encodeData"
participant R as "HTTP Client<br/>Request.post_request_session"
participant S as "Server API"
participant A as "Assertions<br/>Assert.assert_*"
participant DB as "DB Layer<br/>conMysql"
participant L as "Logger<br/>Logs.get_log"
T->>P : Build payload (payType, money, uids, giftId)
P-->>T : URL-encoded payload
T->>R : POST payload to pay/create
R->>S : Send request with token
S-->>R : Response {code, body, time}
R-->>T : Response dict
T->>A : assert_code/assert_body/assert_equal
T->>DB : selectUserInfoSql / updateMoneySql / insertXsUserCommodity
DB-->>T : Query results
T->>L : Log results and reasons
```

**Diagram sources**
- [basicData.py](file://common/basicData.py)
- [Request.py](file://common/Request.py)
- [Assert.py](file://common/Assert.py)
- [conMysql.py](file://common/conMysql.py)
- [Logs.py](file://common/Logs.py)

## Detailed Component Analysis

### SQL Script Execution Framework and Transaction Safety
- Connection and isolation:
  - Persistent connection with autocommit enabled in the primary MySQL client.
  - Explicit rollback on exceptions and commit in finally blocks for write operations.
- Parameter binding:
  - Payloads are built programmatically and passed to the server; database operations use parameterized queries to avoid injection.
- Transaction rollback strategies:
  - On exceptions during updates/deletes/inserts, rollback is invoked followed by commit to ensure consistency.
- Result verification:
  - Dedicated selectors for balances, commodity counts, and derived sums; assertions compare actual vs expected values.

```mermaid
flowchart TD
Start(["DB Operation"]) --> Exec["Execute SQL"]
Exec --> Ok{"Success?"}
Ok --> |Yes| Commit["Commit"]
Ok --> |No| Rollback["Rollback"]
Rollback --> Commit
Commit --> End(["Done"])
```

**Diagram sources**
- [conMysql.py](file://common/conMysql.py)
- [sqlScript.py](file://common/sqlScript.py)

**Section sources**
- [conMysql.py](file://common/conMysql.py)
- [sqlScript.py](file://common/sqlScript.py)

### Parameter Binding and Payload Validation
- Payload builder supports multiple payment scenarios (room gifts, chat gifts, shop buys, defends, etc.) with consistent parameterization.
- Encodes JSON-like structures into URL-encoded form data, ensuring special characters are normalized.
- Validation rules:
  - Money and quantity fields validated against expected ranges.
  - Gift IDs and room IDs sourced from configuration for correctness.
  - Multi-user scenarios construct comma-separated lists for recipients and positions.

```mermaid
flowchart TD
A["Select payType"] --> B{"Scenario"}
B --> |package| P1["Build package payload"]
B --> |package-more| P2["Build multi-receiver payload"]
B --> |chat-gift| P3["Build chat gift payload"]
B --> |shop-buy| P4["Build shop buy payload"]
B --> |defend| P5["Build defend payload"]
P1 --> E["URL-encode"]
P2 --> E
P3 --> E
P4 --> E
P5 --> E
E --> R["Send HTTP request"]
```

**Diagram sources**
- [basicData.py](file://common/basicData.py)
- [Request.py](file://common/Request.py)

**Section sources**
- [basicData.py](file://common/basicData.py)
- [Config.py](file://common/Config.py)

### Assertion Engine Capabilities
- Status code checks, body field assertions, equality comparisons, substring presence checks, and inclusive range validations.
- Failure reasons recorded centrally for reporting and Slack notifications.
- Optional sleep adjustments for RPC latency in specific environments.

```mermaid
classDiagram
class AssertEngine {
+assert_code(actual, expected)
+assert_equal(actual, expected)
+assert_body(body, key, expected, reason)
+assert_in_text(body, expected)
+assert_between(actual, low, high)
+assert_len(actual, expected)
}
class Consts {
+case_list
+fail_case_reason
+result
}
AssertEngine --> Consts : "records failure reasons"
```

**Diagram sources**
- [Assert.py](file://common/Assert.py)
- [Consts.py](file://common/Consts.py)

**Section sources**
- [Assert.py](file://common/Assert.py)
- [Consts.py](file://common/Consts.py)

### Logging Strategies for Audit Trails, Error Tracking, and Notifications
- Rotating file handler with midnight rotation and configurable backup count.
- Structured log entries include timestamp, module path, line number, and level.
- Console handler for INFO-level visibility.
- Aggregated results and failures posted to Slack channels with contextual messages.

```mermaid
graph TB
L["Logs.get_log"] --> FH["FileHandler<br/>TimedRotatingFileHandler"]
L --> CH["ConsoleHandler"]
RUN["run_all_case.main"] --> L
RUN --> SL["Slack Bot"]
```

**Diagram sources**
- [Logs.py](file://common/Logs.py)
- [run_all_case.py](file://run_all_case.py)

**Section sources**
- [Logs.py](file://common/Logs.py)
- [run_all_case.py](file://run_all_case.py)

### Validation Patterns for Concurrent Transactions and Race Conditions
- Concurrency harness uses greenlets to simulate simultaneous requests.
- Pre/post conditions ensure deterministic state (e.g., clearing commodities, setting balances).
- Assertions verify final counts and sums to detect inconsistencies.

```mermaid
sequenceDiagram
participant TC as "TestConcurrent"
participant ENC as "Encode Payload"
participant THR as "Greenlets"
participant SRV as "Server"
participant DB as "DB Layer"
participant AS as "Assertions"
TC->>ENC : Build payload
TC->>THR : Spawn N greenlets
loop N times
THR->>SRV : POST request
SRV-->>THR : Response
THR->>AS : assert_code/assert_equal
THR->>DB : selectUserInfoSql
end
THR-->>TC : Aggregate results
```

**Diagram sources**
- [testConcurrent.py](file://testConcurrent.py)
- [testPayConcurrent.py](file://testPayConcurrent.py)
- [basicData.py](file://common/basicData.py)
- [conMysql.py](file://common/conMysql.py)
- [Assert.py](file://common/Assert.py)

**Section sources**
- [testConcurrent.py](file://testConcurrent.py)
- [testPayConcurrent.py](file://testPayConcurrent.py)

### End-to-End Payment Validation Examples
- Bean payments, exchange flows, and business room splits are exercised across test suites.
- Each test:
  - Prepares baseline data (balances, commodities)
  - Sends payment request
  - Asserts response fields
  - Verifies database state changes
  - Records outcome and reasons

```mermaid
sequenceDiagram
participant Case as "TestCase"
participant DB as "DB Layer"
participant Req as "HTTP Client"
participant Ass as "Assertions"
Case->>DB : Prepare baseline
Case->>Req : Send payment request
Req-->>Case : Response
Case->>Ass : Validate response and DB state
Case->>DB : Verify final state
```

**Diagram sources**
- [test_pay_bean.py](file://case/test_pay_bean.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [conMysql.py](file://common/conMysql.py)
- [Request.py](file://common/Request.py)
- [Assert.py](file://common/Assert.py)

**Section sources**
- [test_pay_bean.py](file://case/test_pay_bean.py)
- [test_pay_business.py](file://case/test_pay_business.py)

## Dependency Analysis
- Test cases depend on shared utilities for request building, HTTP transport, DB access, assertions, and logging.
- Configuration centralizes endpoints and identifiers used across tests.
- Run orchestrator aggregates results and posts notifications.

```mermaid
graph LR
CONF["Config.py"] --> BB["test_pay_bean.py"]
CONF --> BUS["test_pay_business.py"]
BASIC["basicData.py"] --> BB
BASIC --> BUS
REQ["Request.py"] --> BB
REQ --> BUS
CONM["conMysql.py"] --> BB
CONM --> BUS
ASRT["Assert.py"] --> BB
ASRT --> BUS
LOGS["Logs.py"] --> RUN["run_all_case.py"]
RUN --> BB
RUN --> BUS
SESS["Session.py"] --> REQ
METH["method.py"] --> RUN
CONST["Consts.py"] --> RUN
```

**Diagram sources**
- [Config.py](file://common/Config.py)
- [test_pay_bean.py](file://case/test_pay_bean.py)
- [test_pay_business.py](file://case/test_pay_business.py)
- [basicData.py](file://common/basicData.py)
- [Request.py](file://common/Request.py)
- [conMysql.py](file://common/conMysql.py)
- [Assert.py](file://common/Assert.py)
- [Logs.py](file://common/Logs.py)
- [run_all_case.py](file://run_all_case.py)
- [Session.py](file://common/Session.py)
- [method.py](file://common/method.py)
- [Consts.py](file://common/Consts.py)

**Section sources**
- [run_all_case.py](file://run_all_case.py)
- [Config.py](file://common/Config.py)

## Performance Considerations
- Request timing is captured per response for performance monitoring.
- Logging includes elapsed time metrics for quick diagnosis.
- Concurrency tests help surface contention and race conditions; ensure DB operations are idempotent and properly isolated.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Assertion failures:
  - Review recorded failure reasons and adjust expectations or preconditions.
  - Confirm environment-specific delays and adjust sleep if necessary.
- Database anomalies:
  - Verify rollback/commit sequences around write operations.
  - Ensure cleanup steps are executed after tests to avoid cross-test interference.
- Logging:
  - Inspect rotating log files for stack traces and structured entries.
  - Confirm Slack notifications for aggregated results and failures.
- Token/session issues:
  - Regenerate tokens via session manager and re-run tests.

**Section sources**
- [Assert.py](file://common/Assert.py)
- [conMysql.py](file://common/conMysql.py)
- [Logs.py](file://common/Logs.py)
- [Session.py](file://common/Session.py)
- [run_all_case.py](file://run_all_case.py)

## Conclusion
The test suite integrates robust validation and logging around payment flows. SQL operations enforce transaction safety, payload builders ensure consistent parameterization, and assertions verify outcomes across accounts and rooms. Concurrency utilities expose potential race conditions, while logging and notifications support continuous monitoring and auditing.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices
- Configuration of endpoints, UIDs, and gift IDs is centralized for cross-platform consistency.
- Run orchestrator supports multiple apps and branches, posting results to Slack.

**Section sources**
- [Config.py](file://common/Config.py)
- [run_all_case.py](file://run_all_case.py)