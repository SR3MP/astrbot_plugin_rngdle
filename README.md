# RNGdle 抽数字插件

一个 AstrBot 插件，通过真实浏览器（Playwright + Chromium）打开 [rngdle.com](https://www.rngdle.com/)，抽取每日随机数字，并返回官方的分享结果。

## 功能

- 群内发送 `rngdle`（大小写不敏感）即可触发
- 真实打开 rngdle.com 页面 → 点击 **GENERATE** 抽取数字
- 等待 badge 逐个弹出（约 20~30 秒）
- 点击 **SHARE** 按钮，捕获官方分享文本并回复
- 返回内容包含：数字、稀有度、百分位、徽章列表、得分 EP、官网链接

## 触发方式

| 指令 | 说明 |
|------|------|
| `rngdle` | 抽取并返回分享结果（大小写不敏感） |
| `RNGDLE` | 同上 |
| `抽数字` | 中文别名，效果相同 |

## 输出示例

```
RNGdle 🎲 571795

🟩 UNCOMMON • Top 33%

🟩 🎨 Flush
🟩 🧹 Semi-Clean
🟩 🧘 Equilibrium
+12 more

7,779 EP
https://rngdle.com
```

## 安装依赖

插件运行需要 **Playwright** 和 **Chromium** 浏览器，首次安装：

```bash
# 1. 安装 Playwright
pip install playwright

# 2. 下载 Chromium 浏览器内核
python3 -m playwright install chromium

# 3.（可选）若启动报缺少系统库，安装依赖：
apt-get install -y libnspr4 libnss3 libatk1.0-0 libcups2 libxcomposite1 libxdamage1
```

> 国内网络建议使用镜像加速：`pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 安装插件

将本插件目录（`astrbot_plugin_rngdle`）放入 AstrBot 的 `data/plugins/` 目录，然后重启 AstrBot 即可加载。

```bash
# 重启 AstrBot 容器（示例，按你的实际部署调整）
docker restart <你的容器名或ID>
```

## 使用说明

- 触发后机器人会先回复「正在抽取，需要约30秒」，抽取完成后返回分享结果
- **每台机器/账号 rngdle 每天限抽 1 次**（页面有 `NEXT ROLL IN` 倒计时），当日已抽过会提示等待或返回重复结果
- **多群共享一个 bot 时，同一天只有第一次触发会真实启动浏览器抽取，后续请求直接复用当日缓存结果**（见常见问题）
- 抽取过程为真实浏览器操作，耗时约 20~30 秒，属正常现象

## 插件结构

```
astrbot_plugin_rngdle/
├── metadata.yaml    # 插件元数据（名称、版本、作者等）
├── main.py          # 主逻辑：注册 rngdle 命令、调用抽取引擎
└── rngdle_roll.py   # 抽取引擎：Playwright 真实打开页面并捕获分享文本
```

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)。

## 常见问题

**Q: 触发后报「抽取失败」？**
A: 请确认 Playwright 已安装、Chromium 已下载，且系统库齐全（见上方"安装依赖"）。

**Q: 为什么抽取要等 20~30 秒？**
A: rngdle 的 badge 动画需要逐个播放，SHARE 按钮在动画结束后才出现，脚本会等待其出现后再点击。

**Q: 群内多个群同时触发会冲突吗？**
A: 不会。插件内部加了互斥锁，多个请求会串行执行，避免浏览器并发冲突。

**Q: 多群/多人同一天触发，会抽到不同数字吗？**
A: 不会，这是有意为之。rngdle 每天限抽一次，插件按 UTC 日期缓存当日结果，同一天内后续触发直接返回缓存，不会重复启动浏览器。想要新数字请等次日 UTC 0 点后。

**Q: 截图保存在哪里？**
A: 不再写死路径，默认保存在系统临时目录（`tempfile.gettempdir()`）下的 `rngdle/` 文件夹，不会因宿主机缺少 `/AstrBot/data/temp` 而报错。
