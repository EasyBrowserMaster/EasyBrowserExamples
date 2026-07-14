# -*- coding: utf-8 -*-
"""Minimal Cloudflare Turnstile test example."""

import asyncio
import time

from loguru import logger

from easybrowser_sdk import EasyBrowserAPI, HumanBehavior, connect_browser_with_retry, find_page_by_target, wait_for_page_ready

DEFAULT_URL = "https://nopecha.com/captcha/turnstile"
ENV_NAME = "CFTest"
EXIT_DELAY_SECONDS = 15


async def find_visible_element(page, selectors):
    # Search visible elements across all frames.
    for frame in page.frames:
        for selector in selectors:
            try:
                element = await frame.query_selector(selector)
                if element and await element.is_visible():
                    return selector, element
            except Exception:
                continue
    return None, None


async def click_checkbox(page, human, checkbox):
    # Try a human-like click first.
    try:
        box = await checkbox.bounding_box()
    except Exception:
        box = None

    if box:
        try:
            await human.move_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            await page.wait_for_timeout(80)
            await page.mouse.down()
            await page.wait_for_timeout(70)
            await page.mouse.up()
            return True
        except Exception:
            pass

    try:
        await human.click(checkbox)
        return True
    except Exception:
        return False


async def main():
    # Fixed test site.
    api = EasyBrowserAPI()
    api.ensure_local_api_available()

    # Create one environment and open the page.
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

        # Try the checkbox, then wait for the token.
        human = HumanBehavior(page)
        token_selectors = (
            "input[name='cf-turnstile-response']",
            "textarea[name='cf-turnstile-response']",
            "input[name='g-recaptcha-response']",
        )
        checkbox_selectors = (
            "input[type=checkbox]",
            "label.cb-lb input",
            ".cb-c input[type=checkbox]",
            ".ctp-checkbox-label input",
            "#challenge-stage input[type=checkbox]",
        )
        deadline = time.monotonic() + 150
        token = ""
        click_result = False
        hold_until = None
        while time.monotonic() < deadline:
            token_selector, token_element = await find_visible_element(page, token_selectors)
            if token_element is not None:
                logger.info("Found element: {}", token_selector)
                try:
                    token = (await token_element.input_value()).strip()
                except Exception:
                    token = ""
            if token and hold_until is None:
                break
            if hold_until is None:
                checkbox_selector, checkbox = await find_visible_element(page, checkbox_selectors)
                if checkbox is not None:
                    logger.info("Found element: {}", checkbox_selector)
                    logger.info("Clicking element: {}", checkbox_selector)
                    click_result = await click_checkbox(page, human, checkbox)
                    if click_result:
                        logger.success("Click success: {}", checkbox_selector)
                        hold_until = time.monotonic() + EXIT_DELAY_SECONDS
                        logger.info("Exiting in {} seconds", EXIT_DELAY_SECONDS)
            if hold_until is not None and time.monotonic() >= hold_until:
                break
            await page.wait_for_timeout(2000)

        if not token:
            token_selector, token_element = await find_visible_element(page, token_selectors)
            if token_element is not None:
                logger.info("Found element: {}", token_selector)
                try:
                    token = (await token_element.input_value()).strip()
                except Exception:
                    token = ""

        print(f"click result: {click_result}")
        if token:
            print("\n=== Turnstile Token ===")
            print(token)
            print("=======================\n")

        logger.success("Finished: url={}", page.url)
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


if __name__ == "__main__":
    asyncio.run(main())
