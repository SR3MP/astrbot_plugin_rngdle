"""
RNGdle 抽数字插件
=================
通过真实浏览器(Playwright + Chromium)打开 rngdle.com，
点击 GENERATE 抽取每日随机数字，等待 badge 弹出后点击 SHARE，
返回官方分享文本。

触发方式：
    群内发送 `rngdle`（大小写不敏感）

依赖（需预先安装）：
    pip install playwright
    python3 -m playwright install chromium
    # 若缺系统库: apt-get install -y libnspr4 libnss3 libatk1.0-0 libcups2 libxcomposite1 libxdamage1
"""
import asyncio
import datetime
import sys
import tempfile
import threading
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

# 插件目录下已放置 rngdle_roll.py，加载时一次性导入
PLUGIN_DIR = Path(__file__).resolve().parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))
from rngdle_roll import roll_rngdle


@register("astrbot_plugin_rngdle", "mcxxiu", "RNGdle 抽数字", "1.0.1")
class RngdlePlugin(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config
        self._lock = threading.Lock()  # 防止浏览器并发冲突
        self._daily_cache = {}  # {"YYYY-MM-DD": share_text}，同一日期只真抽一次

    @filter.command("rngdle", alias={"抽数字", "rngdle抽数", "RNGDLE"})
    async def on_rngdle(self, event: AstrMessageEvent):
        """RNGdle 抽数字并返回分享结果"""
        # 立刻给个提示，说明正在抽取（可能需要30秒左右）
        yield event.plain_result("🎲 正在为你抽取 RNGdle 数字，需要约30秒，请稍候...")

        # 按 UTC 日期分桶缓存：rngdle 每天限抽一次，同一天内多群/多人触发直接复用结果
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        cached = self._daily_cache.get(today)
        if cached:
            yield event.plain_result(cached + "\n（今日已抽取，直接返回今日结果）")
            return

        loop = asyncio.get_running_loop()
        try:
            share_text = await loop.run_in_executor(None, self._do_roll)
        except Exception as e:
            logger.error(f"RNGdle 抽取失败: {e}")
            yield event.plain_result(f"❌ 抽取失败: {e}\n请确认 Playwright/Chromium 已安装。")
            return

        self._daily_cache[today] = share_text
        yield event.plain_result(share_text)

    def _do_roll(self) -> str:
        """在线程池中执行真实浏览器抽取（阻塞操作）"""
        screenshot_dir = str(Path(tempfile.gettempdir()) / "rngdle")
        with self._lock:  # 全局串行，避免多群并发启动浏览器冲突
            try:
                return roll_rngdle(headless=True, wait_max=90, screenshot_dir=screenshot_dir)
            except Exception as e:
                return f"❌ 抽取异常: {e}"
