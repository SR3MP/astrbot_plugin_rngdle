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
import os
import threading
import time
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

# 插件目录下已放置 rngdle_roll.py
PLUGIN_DIR = Path(__file__).resolve().parent


@register("astrbot_plugin_rngdle", "mcxxiu", "RNGdle 抽数字", "1.0.0")
class RngdlePlugin(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config
        self._lock = threading.Lock()  # 防止并发冲突

    @filter.command("rngdle", alias={"抽数字", "rngdle抽数", "RNGDLE"})
    async def on_rngdle(self, event: AstrMessageEvent):
        """RNGdle 抽数字并返回分享结果"""
        # 立刻给个提示，说明正在抽取（可能需要30秒左右）
        yield event.plain_result("🎲 正在为你抽取 RNGdle 数字，需要约30秒，请稍候...")

        loop = asyncio.get_running_loop()
        try:
            share_text = await loop.run_in_executor(None, self._do_roll)
        except Exception as e:
            logger.error(f"RNGdle 抽取失败: {e}")
            yield event.plain_result(f"❌ 抽取失败: {e}\n请确认 Playwright/Chromium 已安装。")
            return

        yield event.plain_result(share_text)

    def _do_roll(self) -> str:
        """在线程池中执行真实浏览器抽取（阻塞操作）"""
        import sys
        sys.path.insert(0, str(PLUGIN_DIR))
        try:
            from rngdle_roll import roll_rngdle
        except ImportError as e:
            return f"❌ 无法加载 rngdle_roll: {e}"

        with self._lock:  # 全局串行，避免多群并发冲突
            try:
                return roll_rngdle(headless=True, wait_max=90)
            except Exception as e:
                return f"❌ 抽取异常: {e}"
