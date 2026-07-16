"""
Focused Playwright verification script for the Kombo UI restoration bug.

This file mirrors the script executed through the browser automation tool.
It validates the preview flow only: VIP unlock, Kombo panel visibility,
mode switching, wheel interaction, backend request URLs/results, virgin badge,
clear reset, and Euro wheel count.
"""

async def run(page):
    import re

    try:
        print("STEP 1: open preview with a clean visitor session")
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("https://rolling-lottery-math.preview.emergentagent.com", wait_until="domcontentloaded", timeout=60000)
        await page.evaluate("localStorage.clear()")
        await page.reload(wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector('[data-testid="promo-code-toggle"]', timeout=30000)
        print("PASS: app loaded and promo-code gate is visible")

        requests = []
        page.on("request", lambda request: requests.append(request.url))

        print("STEP 2: unlock VIP with promo code 93928")
        await page.locator('[data-testid="promo-code-toggle"]').click()
        await page.locator('[data-testid="promo-code-input"]').fill("93928")
        await page.locator('[data-testid="promo-code-submit"]').click()
        await page.wait_for_selector('text=VIP unlocked', timeout=30000)
        print("PASS: VIP unlocked banner is visible")

        initial_kombo_count = await page.locator('[data-testid="kombo-position-panel"]').count()
        print(f"INFO: Kombo panel count immediately after VIP unlock before opening Multiple Tickets: {initial_kombo_count}")

        print("STEP 3: open Multiple Tickets section and verify Kombo panel/toggle")
        await page.locator('[data-testid="multi-tickets-toggle"]').scroll_into_view_if_needed()
        await page.locator('[data-testid="multi-tickets-toggle"]').click()
        await page.wait_for_selector('[data-testid="kombo-position-panel"]', timeout=15000)
        await page.locator('[data-testid="kombo-position-panel"]').scroll_into_view_if_needed()
        assert await page.locator('[data-testid="kombo-position-toggle"]').is_visible(), "Kombo toggle not visible"
        print("PASS: Kombo panel and collapsed toggle are visible inside Multiple Tickets")

        await page.locator('[data-testid="kombo-position-toggle"]').click()
        await page.wait_for_selector('[data-testid="kombo-mode-toggle"]', timeout=10000)
        for idx in range(1, 7):
            assert await page.locator(f'[data-testid="kombo-position-p{idx}"]').is_visible(), f"Swiss P{idx} wheel missing"
        assert await page.locator('[data-testid="kombo-position-run-btn"]').is_visible(), "Check history button missing"
        print("PASS: expanded Kombo panel shows mode toggle, six Swiss wheels, and Check history button")

        print("STEP 4: verify mode toggle descriptions update")
        locked_desc = await page.locator('[data-testid="kombo-position-panel"]').inner_text()
        assert "exact positions" in locked_desc, "Locked mode description missing exact-position wording"
        await page.locator('[data-testid="kombo-mode-free"]').click()
        await page.wait_for_timeout(300)
        free_desc = await page.locator('[data-testid="kombo-position-panel"]').inner_text()
        assert "position doesn't matter" in free_desc or "anywhere" in free_desc, "Free mode description did not update"
        await page.locator('[data-testid="kombo-mode-locked"]').click()
        await page.wait_for_timeout(300)
        print("PASS: Position-Locked and Position-Free toggles update the visible description")

        async def wheel_to(test_id, target):
            """Drive the custom wheel like a user and verify its center value."""
            outer = page.locator(f'[data-testid="{test_id}"]')
            wheel = page.locator(f'[data-testid="{test_id}-wheel"]')
            await wheel.scroll_into_view_if_needed()

            def parse_selected(txt):
                vals = [line.strip() for line in txt.splitlines() if line.strip()]
                if len(vals) >= 3:
                    center = vals[2]
                elif vals:
                    center = vals[0]
                else:
                    return None
                return 0 if center == '—' else int(center)

            current = parse_selected(await outer.inner_text())
            attempts = 0
            while current != target and attempts < 80:
                # The component wraps 0..max. Move forward for this focused test.
                await wheel.dispatch_event("wheel", {"deltaY": 100, "bubbles": True, "cancelable": True})
                await page.wait_for_timeout(120)
                current = parse_selected(await outer.inner_text())
                attempts += 1
            txt = await outer.inner_text()
            print(f"INFO: {test_id} selected after wheel events: {current}; text: {txt}")
            assert current == target, f"{test_id} did not reach {target}; current={current}"

        print("STEP 5: Position-Locked check: set P1=13 and run history search")
        await wheel_to("kombo-position-p1-wheel", 13)
        await page.locator('[data-testid="kombo-position-run-btn"]').click()
        await page.wait_for_selector('[data-testid="kombo-position-results"]', timeout=30000)
        locked_results = await page.locator('[data-testid="kombo-position-results"]').inner_text()
        locked_match = re.search(r"Found\s+(\d+)\s+historical", locked_results)
        assert locked_match and int(locked_match.group(1)) > 0, f"Locked results did not show match_count > 0: {locked_results[:200]}"
        assert any('/api/kombo/position/swiss?p1=13' in u for u in requests), "Expected /api/kombo/position/swiss?p1=13 request not captured"
        print(f"PASS: locked search called /api/kombo/position/swiss?p1=13 and returned {locked_match.group(1)} matches")

        print("STEP 6: Position-Free check: clear, set one wheel to 14 and run history search")
        await page.locator('[data-testid="kombo-position-clear-btn"]').click()
        await page.wait_for_timeout(500)
        assert await page.locator('[data-testid="kombo-position-results"]').count() == 0, "Results did not clear"
        await page.locator('[data-testid="kombo-mode-free"]').click()
        await page.wait_for_timeout(300)
        await wheel_to("kombo-position-p1-wheel", 14)
        await page.locator('[data-testid="kombo-position-run-btn"]').click()
        await page.wait_for_selector('[data-testid="kombo-position-results"]', timeout=30000)
        free_results = await page.locator('[data-testid="kombo-position-results"]').inner_text()
        free_match = re.search(r"Found\s+(\d+)\s+historical", free_results)
        assert free_match and int(free_match.group(1)) > 0, f"Free results did not show match_count > 0: {free_results[:200]}"
        assert any('/api/history-echo/swiss?nums=14' in u for u in requests), "Expected /api/history-echo/swiss?nums=14 request not captured"
        print(f"PASS: free search called /api/history-echo/swiss?nums=14 and returned {free_match.group(1)} matches")

        print("STEP 7: clear button resets results/wheel display")
        await page.locator('[data-testid="kombo-position-clear-btn"]').click()
        await page.wait_for_timeout(800)
        assert await page.locator('[data-testid="kombo-position-results"]').count() == 0, "Results still visible after clear"
        p1_text_after_clear = await page.locator('[data-testid="kombo-position-p1-wheel"]').inner_text()
        assert "—" in p1_text_after_clear, "P1 wheel did not reset to dash/zero state"
        print("PASS: Clear resets the Kombo results and P1 wheel to empty")

        print("STEP 8: generate tickets and verify virgin badge auto-appears")
        await page.locator('[data-testid="generate-tickets-btn"]').scroll_into_view_if_needed()
        await page.locator('[data-testid="generate-tickets-btn"]').click()
        await page.wait_for_selector('[data-testid="kombo-virgin-panel"]', timeout=45000)
        virgin_text = await page.locator('[data-testid="kombo-virgin-panel"]').inner_text()
        assert ("VIRGIN" in virgin_text) or ("PLAYED" in virgin_text) or ("checking history" in virgin_text), f"Virgin panel text unexpected: {virgin_text}"
        if "checking history" in virgin_text:
            await page.wait_for_timeout(3000)
            virgin_text = await page.locator('[data-testid="kombo-virgin-panel"]').inner_text()
            assert ("VIRGIN" in virgin_text) or ("PLAYED" in virgin_text), f"Virgin badge did not resolve: {virgin_text}"
        assert any('/api/kombo/virgin/swiss?nums=' in u for u in requests), "Expected kombo virgin API request not captured"
        print(f"PASS: Generate triggered Kombo virgin badge: {virgin_text.replace(chr(10), ' | ')}")

        print("STEP 9: switch to EuroMillions and verify only five Kombo wheels render")
        await page.locator('[data-testid="euromillions-toggle"]').scroll_into_view_if_needed()
        await page.locator('[data-testid="euromillions-toggle"]').click()
        await page.wait_for_timeout(1500)
        await page.locator('[data-testid="multi-tickets-toggle"]').scroll_into_view_if_needed()
        # Multi section remains open in this app state; if not, open it.
        if await page.locator('[data-testid="kombo-position-panel"]').count() == 0:
            await page.locator('[data-testid="multi-tickets-toggle"]').click()
            await page.wait_for_selector('[data-testid="kombo-position-panel"]', timeout=10000)
        if await page.locator('[data-testid="kombo-mode-toggle"]').count() == 0:
            await page.locator('[data-testid="kombo-position-toggle"]').click()
            await page.wait_for_selector('[data-testid="kombo-mode-toggle"]', timeout=10000)
        euro_wheel_count = await page.locator('[data-testid^="kombo-position-p"]').evaluate_all("els => els.filter(el => /^kombo-position-p[1-6]$/.test(el.dataset.testid)).length")
        assert euro_wheel_count == 5, f"Expected 5 Euro Kombo position containers, found {euro_wheel_count}"
        assert await page.locator('[data-testid="kombo-position-p6"]').count() == 0, "P6 wheel should not render for Euro"
        print("PASS: EuroMillions mode renders five Kombo wheels and hides P6")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
        print("OVERALL RESULT: PASS")
    except Exception as e:
        print(f"OVERALL RESULT: FAIL - {type(e).__name__}: {e}")
        await page.screenshot(path="/tmp/kombo_failure.jpg", quality=40, full_page=False)
        raise