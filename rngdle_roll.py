#!/usr/bin/env python3
"""
RNGdle 自动抽数字工具
======================
真实打开 rngdle.com -> 点击 GENERATE -> 等待 badge 逐个弹出(约20-30秒)
-> 点击 SHARE 按钮 -> 捕获复制到剪贴板的官方分享文本 -> 输出。

用法:
    python3 rngdle_roll.py

依赖:
    pip install playwright
    python3 -m playwright install chromium   # 首次需下载浏览器
    （如缺系统库: apt-get install -y libnspr4 libnss3 libatk1.0-0 libcups2
                  libxcomposite1 libxdamage1）

说明:
    - 需要在点击 GENERATE 后耐心等待 badge 动画播放完，SHARE 按钮才会出现。
    - 通过拦截 navigator.clipboard.writeText 捕获分享文本（headless 无法直接读剪贴板）。
"""
import sys
import time


def roll_rngdle(headless: bool = True, wait_max: int = 90) -> str:
    """真实抽取一个 RNGdle 数字并返回官方分享文本。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1280, "height": 1200},
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = context.new_page()

        # 拦截 navigator.clipboard.writeText，捕获分享文本
        page.add_init_script("""
            window.__copiedShare = null;
            try {
                const origWrite = navigator.clipboard.writeText.bind(navigator.clipboard);
                navigator.clipboard.writeText = async function (text) {
                    window.__copiedShare = text;
                    return origWrite(text);
                };
            } catch (e) {}
            document.addEventListener('copy', function (e) {
                try { window.__copiedShare = e.clipboardData.getData('text/plain'); }
                catch (err) {}
            });
        """)

        page.goto("https://www.rngdle.com/", wait_until="networkidle", timeout=60000)
        page.get_by_role("button", name="GENERATE").click()
        print("[*] 已点击 GENERATE，等待 badge 逐个弹出...", flush=True)

        # 等待 SHARE 按钮出现
        share_btn = None
        for i in range(wait_max):
            time.sleep(1)
            try:
                share_btn = page.locator('[aria-label="Copy to clipboard"]')
                if share_btn.count() > 0:
                    print(f"[+] 第 {i+1} 秒找到 SHARE 按钮", flush=True)
                    break
            except Exception:
                pass
        else:
            page.screenshot(path="/AstrBot/data/temp/rngdle_fail.png", full_page=True)
            browser.close()
            return "[错误] 等待超时，未找到 SHARE 按钮（badge 可能未加载完）。"

        # 点击 SHARE
        share_btn.click()
        time.sleep(3)

        # 读取捕获的分享文本
        captured = page.evaluate("window.__copiedShare || '(未捕获到)'")

        # 兜底：若未捕获，尝试读取页面显示的数字/评分信息
        if captured == "(未捕获到)":
            text = page.inner_text("body")
            captured = f"(剪贴板捕获失败，页面信息如下)\n{text[:1200]}"

        page.screenshot(path="/AstrBot/data/temp/rngdle_result.png", full_page=True)
        browser.close()
        return captured


if __name__ == "__main__":
    print("=" * 45)
    print("  🎲 RNGDLE 自动抽数字")
    print("=" * 45)
    share = roll_rngdle()
    print("\n📤 分享结果：")
    print(share)
    print("=" * 45)
