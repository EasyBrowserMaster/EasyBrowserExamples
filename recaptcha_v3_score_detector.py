# -*- coding: utf-8 -*-
"""Minimal reCAPTCHA v3 test example."""

import asyncio
import re
import time

from loguru import logger

from easybrowser_sdk import EasyBrowserAPI, connect_browser_with_retry, find_page_by_target, wait_for_page_ready

DEFAULT_URL = "https://antcpt.com/score_detector"
ENV_NAME = "RecaptV3Test"
TIMEOUT_SECONDS = 60
EXIT_DELAY_SECONDS = 15


async def main():
    # Fixed test site.
    api = EasyBrowserAPI()
    api.ensure_local_api_available()

    # Create one environment and hold it open.
    logger.info("Target URL: {}", DEFAULT_URL)
    logger.info("Environment name: {}", ENV_NAME)

    env_id = api.ensure_container(name=ENV_NAME, defaultUrl=DEFAULT_URL)["id"]
    playwright = None
    browser = None

    try:
        debug_port = api.browser_start()["debug_port"]
        tab = api.new_tab(env_id, url=DEFAULT_URL)
        target_id = tab["target_id"]

        playwright, browser = await connect_browser_with_retry(debug_port)
        page = await find_page_by_target(browser, target_id)
        if page is None:
            raise RuntimeError(f"page not found for target_id={target_id}")

        await wait_for_page_ready(page)
        logger.info("Page ready: {}", page.url)

        deadline = time.monotonic() + TIMEOUT_SECONDS
        score = None
        while time.monotonic() < deadline:
            body_text = await page.inner_text("body")
            match = re.search(r"Your score is:\s*([0-9.]+)", body_text)
            if match:
                score = match.group(1)
                logger.success("Score detected: {}", score)
                logger.info("Exiting in {} seconds", EXIT_DELAY_SECONDS)
                await asyncio.sleep(EXIT_DELAY_SECONDS)
                break
            await page.wait_for_timeout(1000)

        if score is None:
            logger.warning("Score not found within timeout")
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        if playwright:
            try:
                await playwright.stop()
            except Exception:
                pass
        try:
            api.browser_stop()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
