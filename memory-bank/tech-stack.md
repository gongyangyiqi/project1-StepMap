# 迹录 StepMap 技术栈建议

## 1. 选择原则

- 先确保 `V1.0` 快速上线，再平滑扩展到 `V1.1`。
- 组件尽量选主流方案，方便面试讲清楚“为什么这样选”。
- 优先选择文档完善、社区活跃、部署成本低的技术。

## 2. 推荐技术栈（主方案）

### 2.1 前端

- 框架：`React + TypeScript + Vite`
- 路由：`React Router`
- UI：`Tailwind CSS` + `shadcn/ui`（或 `Radix UI`）
- 地图：`Leaflet` + `react-leaflet` + `OpenStreetMap`
- 状态管理：`TanStack Query`（服务端状态）+ `Zustand`（少量本地状态）
- 表单与校验：`React Hook Form` + `Zod`
- HTTP 客户端：`Axios`（可统一拦截 token 和错误）

为什么适合你：
- 学习曲线相对平滑，开发速度快。
- 面试中能体现工程能力（类型安全、接口管理、请求状态管理）。
- 与地图和移动端适配兼容性好。

### 2.2 后端

- 框架：`FastAPI`（Python）
- ORM：`SQLAlchemy 2.0` + `Alembic`
- 数据校验：`Pydantic v2`
- 鉴权：`JWT`（`python-jose`）+ 密码哈希（`passlib[bcrypt]`）
- 异步任务（V1.1）：`Celery` + `Redis`
- 对象存储：`S3 兼容`（开发可用 `MinIO`，生产用 `AWS S3` / `阿里云 OSS`）
- 视频生成（V1.1）：`ffmpeg`（可配合 `moviepy`）

为什么适合你：
- 与当前设计主文档一致，减少重构成本。
- FastAPI 对新手非常友好，自动生成 OpenAPI 文档。
- 后续加异步任务和媒体处理路径清晰。

### 2.3 数据库与缓存

- 主数据库：`PostgreSQL`
- 缓存/队列中间件：`Redis`（V1.1 强烈建议）

为什么适合你：
- PostgreSQL 是实习和生产中非常常见的能力项。
- Redis 可同时支持队列、缓存、限流等后续扩展。

### 2.4 文件与媒体处理

- 图片处理：`Pillow`（压缩、尺寸限制、去 EXIF）
- 上传方式：后端签名上传（后续可升级前端直传）
- 视频处理（V1.1）：`ffmpeg` 命令行优先，`moviepy` 作为封装层

### 2.5 部署与运维

- 前端部署：`Vercel`
- 后端部署：`Render` / `Railway`（新手更友好）或 `Fly.io`
- 数据库托管：`Neon` / `Supabase Postgres`
- 对象存储：`S3/OSS`
- 反向代理（可选）：`Nginx`
- CI/CD：`GitHub Actions`（lint/test/build）
- 监控与日志：`Sentry` + 结构化日志（`loguru` 或标准 logging JSON）

## 3. 项目分阶段技术落地

### V1.0（必须）

- 前端：React + TS + Vite + Tailwind + Leaflet
- 后端：FastAPI + PostgreSQL + SQLAlchemy + JWT
- 存储：本地文件（开发）/ MinIO（联调）
- 部署：前端 Vercel，后端 Render，数据库 Neon

目标：完成“注册登录 -> 创建旅行 -> 添加足迹 -> 时间线 -> 地图总览”的全链路上线。

### V1.1（增强）

- 引入 Redis + Celery
- 上线电影生成任务队列与状态查询
- 接入 ffmpeg 生成视频并保存到对象存储

目标：支持异步生成旅行电影、失败重试和下载链接。

## 4. 目录结构建议（单仓库）

```text
stepmap/
  frontend/
    src/
    public/
  backend/
    app/
      api/
      core/
      models/
      schemas/
      services/
      tasks/        # V1.1 Celery 任务
    alembic/
  infra/
    docker/
    scripts/
  memory-bank/
    design-document.md
    tech-stack.md
    implementation-plan.md
    progress.md
    architecture.md
```

## 5. 核心依赖清单（建议）

### 前端依赖

- `react`, `react-dom`, `typescript`, `vite`
- `react-router-dom`
- `tailwindcss`, `postcss`, `autoprefixer`
- `leaflet`, `react-leaflet`
- `@tanstack/react-query`
- `react-hook-form`, `zod`, `@hookform/resolvers`
- `axios`
- `zustand`

### 后端依赖

- `fastapi`, `uvicorn[standard]`
- `sqlalchemy`, `alembic`, `psycopg[binary]`
- `pydantic`, `pydantic-settings`
- `python-jose[cryptography]`, `passlib[bcrypt]`
- `python-multipart`（文件上传）
- `pillow`
- `boto3`（S3/OSS）
- `celery`, `redis`（V1.1）

## 6. 为什么不推荐的一些选择（当前阶段）

- 不建议一开始上微服务：会显著增加部署和排障复杂度。
- 不建议前端先上 Next.js SSR：你的场景更偏交互应用，Vite 更快更轻。
- 不建议自建复杂权限系统：当前 JWT + 资源归属校验足够。
- 不建议第一版就引入过多 DevOps 工具：先把功能链路和稳定性做扎实。

## 7. 作品集加分点（面试导向）

- 在 README 中写清技术选型理由（不仅写“用了什么”，还要写“为什么”）。
- 给出 2-3 个关键 trade-off：
  - 为什么 V1.0 不做电影生成
  - 为什么选 PostgreSQL 而不是 SQLite
  - 为什么先后端代传文件，再升级前端直传
- 补一页“性能与稳定性”：
  - 足迹保存耗时
  - 上传成功率
  - 地图加载失败降级策略

## 8. 一句话结论

对你当前阶段最合适的组合是：  
`React + TypeScript + Vite + Tailwind + Leaflet`（前端）  
`FastAPI + PostgreSQL + SQLAlchemy + JWT + S3`（后端）  
`Redis + Celery + ffmpeg`（V1.1 电影生成）。
