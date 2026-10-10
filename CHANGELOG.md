# 更新日志

## v1.0.1（2026-10-10）

修复：

- 剪贴板捕获在 headless Chromium 下失效的问题：`navigator.clipboard` 可能不存在或 `writeText` 被沙箱拒绝，现同时覆盖 `writeText`/`write`，并监听 `copy`/`paste` 事件兜底。
- 截图路径硬编码 `/AstrBot/data/temp/`，宿主机无此目录会报错；改为默认保存到系统临时目录 `rngdle/` 子目录，可通过参数指定。
- `wait_until="networkidle"` 在 SPA 页面上永远无法达成导致超时；改为 `domcontentloaded`。
- `sys.path.insert` 每次调用都重复插入；改为插件加载时一次性导入。
- 多群/多人同一天触发会各自启动浏览器、可能互相挤掉每日限抽名额；新增按 UTC 日期分桶缓存，同一日期只真实抽取一次，后续直接复用当日结果。

## v1.0.0（2026-08-27）

- 首个版本：通过 Playwright 真实打开 rngdle.com 抽取每日随机数字并返回官方分享文本。
