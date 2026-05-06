# StepMap 架构洞察（Architecture）

## 1. 当前阶段定位

- 当前处于 `implementation-plan` 的步骤 1 完成态：仓库骨架已建立，功能代码尚未开始。
- 架构目标是先固定边界和命名，再逐步填充实现，降低后续返工成本。

## 2. 顶层目录职责

- `frontend/`
  - 作用：承载 Web 前端应用（React + TypeScript + Vite）。
  - 当前状态：已建立入口目录与说明文档，等待步骤 2+ 的配置与工程初始化。

- `backend/`
  - 作用：承载后端服务（FastAPI + PostgreSQL + SQLAlchemy）。
  - 当前状态：已按分层建立 `app` 与 `alembic` 目录，便于后续模型、接口、服务分工。

- `infra/`
  - 作用：存放环境与部署相关资源（容器、脚本、自动化支持）。
  - 当前状态：`docker` 与 `scripts` 子目录已预留。

- `memory-bank/`
  - 作用：项目知识库与协作文档中心，约束后续开发步骤与范围。
  - 当前状态：需求、技术栈、实施计划、进度、架构文档均在此统一维护。

## 3. 关键文件作用说明

- `README.md`
  - 作用：仓库入口文档。
  - 价值：给新开发者 1 分钟内理解项目结构、运行说明占位和领域术语。

- `frontend/README.md`
  - 作用：前端工作区说明。
  - 价值：明确前端入口在 `frontend/src/`，避免目录误用。

- `backend/README.md`
  - 作用：后端工作区说明。
  - 价值：提前固化后端核心实体命名（Trip、Footprint、MovieJob），保障前后端词汇一致。

- `infra/README.md`
  - 作用：基础设施工作区说明。
  - 价值：声明 `docker` 与 `scripts` 为后续环境自动化落点。

- `frontend/src/.gitkeep`、`frontend/public/.gitkeep`
  - 作用：在功能文件未创建前保留空目录。
  - 价值：避免目录被版本控制忽略，确保协作者拉取后结构一致。

- `backend/app/api/.gitkeep`
  - 作用：保留 API 路由层目录。
  - 价值：后续集中放置 HTTP 接口定义，避免业务代码直接写在入口文件。

- `backend/app/core/.gitkeep`
  - 作用：保留核心配置与基础组件目录。
  - 价值：后续承载配置加载、鉴权基础、通用异常处理等跨模块能力。

- `backend/app/models/.gitkeep`
  - 作用：保留数据模型目录。
  - 价值：后续集中管理 Trip/Footprint/MovieJob 等 ORM 模型。

- `backend/app/schemas/.gitkeep`
  - 作用：保留输入输出数据结构目录。
  - 价值：将接口入参/出参与数据库模型解耦。

- `backend/app/services/.gitkeep`
  - 作用：保留业务服务层目录。
  - 价值：封装业务逻辑，降低 API 层与数据层耦合。

- `backend/app/tasks/.gitkeep`
  - 作用：保留异步任务目录（V1.1）。
  - 价值：为 MovieJob 的队列任务预留稳定落点。

- `backend/alembic/.gitkeep`
  - 作用：保留数据库迁移目录。
  - 价值：后续迁移版本可持续演进，保障环境一致性。

- `infra/docker/.gitkeep`、`infra/scripts/.gitkeep`
  - 作用：保留部署和脚本目录。
  - 价值：为容器化与自动化流程预留标准位置。

## 4. memory-bank 文档职责分工

- `memory-bank/design-document.md`
  - 作用：产品与交互设计主文档（做什么、为什么做）。

- `memory-bank/tech-stack.md`
  - 作用：技术选型与分阶段落地策略（用什么实现）。

- `memory-bank/implementation-plan.md`
  - 作用：可执行步骤与验证标准（按什么顺序做、如何验收）。

- `memory-bank/progress.md`
  - 作用：真实执行轨迹与风险跟踪（做到了哪里、下一步是什么）。

- `memory-bank/architecture.md`
  - 作用：沉淀结构认知与文件职责（每个目录/文件为什么存在）。

## 5. 步骤 2 新增配置层洞察

- `backend/.env.example`
  - 作用：开发环境变量模板。
  - 价值：统一本地配置基线，减少“我这边能跑/你那边不能跑”的环境差异。

- `backend/.env.production.example`
  - 作用：生产环境变量模板。
  - 价值：明确生产所需关键变量，降低上线漏配风险。

- `frontend/.env.example`
  - 作用：前端环境变量模板。
  - 价值：统一前端 API 基地址等关键配置入口。

- `backend/requirements.txt`
  - 作用：步骤 2 所需最小后端依赖清单。
  - 价值：确保配置加载与最小服务启动可复现。

- `backend/app/core/settings.py`
  - 作用：集中管理后端配置加载与校验逻辑。
  - 价值：把“配置读取”和“业务逻辑”解耦；在缺失配置时快速失败并返回可读错误。

- `backend/app/main.py`
  - 作用：最小 FastAPI 入口与健康检查接口。
  - 价值：提供步骤 2 的验证锚点（配置完整时服务可启动）。

- `backend/app/__init__.py`、`backend/app/core/__init__.py`
  - 作用：包初始化文件。
  - 价值：确保模块导入路径稳定，便于后续分层扩展。

## 6. 当前架构结论

- 现有结构已满足步骤 1 和步骤 2 的目标：目录齐备、命名统一、配置分层已建立。
- 架构上已形成“文档驱动 + 分层预留 + 配置先行”的基础盘，可进入步骤 3 实施统一日志与错误追踪。

## 7. 步骤 3 新增日志与错误层洞察

- `backend/app/core/logging.py`
  - 作用：提供结构化（JSON）日志格式和请求日志中间件。
  - 价值：把“请求观测”标准化，后续可直接对接日志平台并追踪接口耗时。

- `backend/app/core/errors.py`
  - 作用：提供统一异常类型、错误码分类与全局异常处理器注册。
  - 价值：让前端和后端对错误语义达成一致，避免同类错误返回格式不一致。

- `backend/app/main.py`（步骤 3 增量）
  - 作用：把配置、日志、错误处理在应用入口统一装配。
  - 价值：保证所有请求天然经过同一套观测和错误处理链路。

- `backend/README.md`（步骤 3 增量）
  - 作用：沉淀日志字段与错误响应规范，作为协作约定。
  - 价值：新开发者可快速理解“该如何判定日志和错误行为是否正确”。

## 8. 当前架构结论（更新）

- 步骤 1-3 已形成稳定“启动 -> 观测 -> 失败可读”的后端基线。
- 当前状态适合进入步骤 4（用户模型与迁移），且具备最小可诊断能力。

## 9. 步骤 4 新增数据与迁移层洞察

- `backend/app/db/base.py`
  - 作用：定义 ORM 基类（Declarative Base）。
  - 价值：为所有模型提供统一元数据入口，支持 Alembic 自动识别模型变化。

- `backend/app/db/session.py`
  - 作用：集中创建数据库引擎与会话工厂。
  - 价值：统一数据库连接配置来源，避免各模块重复创建连接。

- `backend/app/models/user.py`
  - 作用：定义 `User` 实体（`id`、`email`、`password_hash`、`created_at`）。
  - 价值：建立用户域的最小可用数据基线，并在数据库层约束 `email` 唯一性。

- `backend/app/models/__init__.py`
  - 作用：统一导出模型集合。
  - 价值：在迁移和模块导入时提供稳定入口。

- `backend/alembic.ini`
  - 作用：Alembic 主配置文件。
  - 价值：统一迁移运行参数和脚本入口位置。

- `backend/alembic/env.py`
  - 作用：迁移运行时环境配置，接入项目 `Settings` 和模型元数据。
  - 价值：让迁移与实际应用配置保持一致，降低环境漂移风险。

- `backend/alembic/script.py.mako`
  - 作用：迁移脚本模板。
  - 价值：保证后续迁移文件结构一致。

- `backend/alembic/versions/20260425_0001_create_users.py`
  - 作用：首个迁移版本，创建 `users` 表和索引。
  - 价值：提供可回放的数据库起点，为注册流程打下稳定基础。

## 10. 当前架构结论（更新）

- 步骤 1-4 已构成“可启动、可观测、可迁移”的后端基础架构。
- 当前状态可安全进入步骤 5（注册能力实现），且具备数据库约束保障。

