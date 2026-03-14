🚀 AIOps-Bridge | AI Agent System Context
1. 项目定位 (System Role)
本项目是一个 ChatOps 中继器。它将飞书 (Feishu) 的 Webhook 事件转化为受控的 Linux Shell 指令。核心目标：在保证系统安全的前提下，通过聊天窗口完成自动化运维。技术栈：Python 3.10+, FastAPI (Asynchronous), Asyncio Subprocess, Feishu Open API.
2. 目录架构 (Component Map)
AI 在阅读代码前应理解各模块职责：
文件名 职责 (Responsibility) 关键逻辑
main.py事件网关 (Gateway)处理飞书 Challenge 校验；将耗时任务分发至 BackgroundTasks 以避免 Webhook 超时重试。
security.py安全防火墙 (Firewall)用户 UserID 白名单检查；正则过滤危险指令（黑名单）；sudo 权限范围审计。
executor.py执行引擎 (Runtime)基于 asyncio.create_subprocess_shell 的非阻塞命令执行；处理超时 (Timeout) 与标准流捕获。
feishu_bot.py交互适配器 (Adapter)封装飞书 API 交互；处理长文本输出的截断逻辑。
config.yaml静态配置 (Env)存储 AppID、AppSecret、管理员白名单及提权指令清单。
3. 核心工作流 (Execution Pipeline)
Ingress: main.py 接收飞书 POST 请求 -> 校验签名。Auth: security.py 检查 sender.open_id 是否在允许名单。Sanitize: security.py 对用户输入的 text 进行正则匹配，拦截 rm, mkfs 等危险模式。Async Exec: executor.py 开启子进程执行，设置 timeout=60s 并在执行期间保持网关 200 OK 响应。Egress: feishu_bot.py 格式化 stdout/stderr 并回传给用户（支持大结果截断）。
4. 安全约束 (Strict Constraints)
AI 在修改项目时必须遵守：Forbidden: 禁止删除或绕过 SecuritySandbox 逻辑。Forbidden: 禁止在 main.py 的主路由中直接 await 命令执行（必须异步后台化）。Required: 所有提权操作必须通过系统的 /etc/sudoers 最小化授权，而非在 Python 中传递明文密码。
5. 待办扩展 (Future Extensions)实现基于 im/v1/files 的超长日志文件上传功能。接入分布式锁，防止同一时刻对同一资源进行冲突的运维操作。