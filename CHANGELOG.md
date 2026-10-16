# 更新日志

## v1.0.3（2026-10-16）

变更：

- **抽取缓存从"全局按日期"改为"按用户+日期"分桶**：此前所有用户共用一个当日结果，第一个用户抽完后其余人直接返回同一缓存。现改为 `(uid, 日期)` 作为缓存键，每个用户当天第一次触发各自真实抽取一次，互不影响。同一用户当天重复触发仍复用自己的结果。

## v1.0.2（2026-10-16）

修复：

- **Playwright Chromium 不走系统代理导致页面加载超时**：Chromium 不会自动读取 `http_proxy`/`https_proxy` 环境变量，在有代理的服务器上会裸连外网超时。新增从环境变量自动解析代理 URL（含用户名密码认证），传入 Playwright `launch(proxy=...)` 参数。
- **`roll_rngdle()` 函数签名缺少 `screenshot_dir` 参数导致调用报错**：旧版函数定义没有该参数，但调用方传了，引发 `unexpected keyword argument` 异常。函数签名已补齐 `screenshot_dir: str = None`。
- **`sys.modules` 拄留旧版 `rngdle_roll` 模块导致热重载后仍用旧代码**：`main.py` 改用 `importlib.util.spec_from_file_location` 以绝对路径强制加载插件目录内的版本，避免同名旧模块缓存干扰。
- 依赖新增 `urllib.parse`（用于解析代理 URL）。

## v1.0.1（2026-10-10）

修复：

- 剪贴板捕获在 headless Chromium 下失效的问题：`navigator.clipboard` 可能不存在或 `writeText` 被沙箱拒绝，现同时覆盖 `writeText`/`write`，并监听 `copy`/`paste` 事件兜底。
- 截图路径硬编码 `/AstrBot/data/temp/`，宿主机无此目录会报错；改为默认保存到系统临时目录 `rngdle/` 子目录，可通过参数指定。
- `wait_until="networkidle"` 在 SPA 页面上永远无法达成导致超时；改为 `domcontentloaded`。
- `sys.path.insert` 每次调用都重复插入；改为插件加载时一次性导入。
- 多群/多人同一天触发会各自启动浏览器、可能互相挤掉每日限抽名额；新增按 UTC 日期分桶缓存，同一日期只真实抽取一次，后续直接复用当日结果。

## v1.0.0（2026-08-27）

- 首个版本：通过 Playwright 真实打开 rngdle.com 抽取每日随机数字并返回官方分享文本。
