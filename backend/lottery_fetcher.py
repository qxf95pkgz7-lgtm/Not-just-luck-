"""
Auto-fetch lottery results from external sources
- Swiss Lotto: Scrapes from lottolyzer.com (primary, structured tables), lotteryextreme.com (fallback)
- EuroMillions: Uses free API from pedromealha.dev (Tue & Fri draws)

PERMANENT FIX: Old scrapers (6richtige.ch, lottoland, swisslos.ch) all broke due to
JS rendering / recaptcha / structure changes. Replaced with lottolyzer.com which returns
clean HTML tables with date, numbers, and lucky number columns.
"""

import httpx
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import uuid

logger = logging.getLogger(__name__)

# EuroMillions API (free, reliable)
EUROMILLIONS_API = "https://euromillions.api.pedromealha.dev"

# Swiss Lotto sources (ordered by reliability)
LOTTOLYZER_URL = "https://en.lottolyzer.com/history/switzerland/swiss-lotto/page/1/per-page/50/summary-view"
LOTTERYEXTREME_URL = "https://www.lotteryextreme.com/swiss-lotto/"


async def fetch_euromillions_latest(limit: int = 10) -> List[Dict]:
    """
    Fetch latest EuroMillions results from the free API
    Returns list of draws with date, numbers, stars
    """
    results = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{EUROMILLIONS_API}/draws",
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            draws = data if isinstance(data, list) else data.get("draws", [])
            draws = list(reversed(draws))
            
            for draw in draws[:limit]:
                date_str = draw.get("date", "")
                numbers = draw.get("numbers", [])
                stars = draw.get("stars", [])
                
                if date_str and numbers:
                    try:
                        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                        formatted_date = dt.strftime("%d.%m.%Y")
                    except Exception:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            formatted_date = dt.strftime("%d.%m.%Y")
                        except Exception:
                            formatted_date = date_str
                    
                    nums = sorted([int(n) for n in numbers])
                    star_nums = sorted([int(s) for s in stars]) if stars else []
                    
                    results.append({
                        "date": formatted_date,
                        "numbers": nums,
                        "stars": star_nums
                    })
            
            logger.info(f"Fetched {len(results)} EuroMillions draws from API")
            
    except Exception as e:
        logger.error(f"Error fetching EuroMillions: {e}")
    
    return results


async def fetch_swisslotto_from_lottolyzer(limit: int = 50) -> List[Dict]:
    """
    PRIMARY SOURCE: Scrape Swiss Lotto results from lottolyzer.com
    Returns clean structured data: date (DD.MM.YYYY), 6 numbers, lucky number.
    Table format: Draw | Date | Winning No. | Lucky No. | ...
    """
    results = []
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                LOTTOLYZER_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                logger.warning("Lottolyzer: No table found on page")
                return results
            
            rows = table.find_all('tr')
            
            for row in rows[2:]:  # Skip 2 header rows
                cells = row.find_all('td')
                if len(cells) < 4:
                    continue
                
                try:
                    texts = [c.get_text(strip=True) for c in cells]
                    date_str = texts[0]      # DD.MM.YYYY
                    numbers_str = texts[2]    # "1,6,8,14,22,34"
                    lucky_str = texts[3]      # "1"
                    
                    if not re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
                        continue
                    if ',' not in numbers_str:
                        continue
                    
                    nums = sorted([int(n.strip()) for n in numbers_str.split(',')])
                    if len(nums) != 6:
                        continue
                    if not all(1 <= n <= 42 for n in nums):
                        continue
                    
                    lucky = int(lucky_str) if lucky_str.isdigit() else 1
                    
                    results.append({
                        "date": date_str,
                        "numbers": nums,
                        "lucky_number": lucky,
                        "replay_number": 1
                    })
                    
                    if len(results) >= limit:
                        break
                except Exception as e:
                    logger.debug(f"Lottolyzer: Error parsing row: {e}")
                    continue
            
            logger.info(f"Fetched {len(results)} Swiss Lotto draws from lottolyzer.com")
            
    except Exception as e:
        logger.error(f"Error fetching from lottolyzer.com: {e}")
    
    return results


async def fetch_swisslotto_from_lotteryextreme() -> List[Dict]:
    """
    FALLBACK SOURCE: Parse latest Swiss Lotto from lotteryextreme.com
    The page has displayball UL elements and embedded text with draw data.
    """
    results = []
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                LOTTERYEXTREME_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first displayball UL (latest Swiss Lotto draw)
            ball_lists = soup.find_all('ul', class_='displayball')
            
            if ball_lists:
                # First displayball has the main 6 numbers + lucky
                first_ball = ball_lists[0]
                lis = first_ball.find_all('li')
                all_nums = []
                for li in lis:
                    txt = li.get_text(strip=True)
                    if txt.isdigit():
                        all_nums.append(int(txt))
                
                if len(all_nums) >= 6:
                    main_nums = sorted(all_nums[:6])
                    lucky = all_nums[6] if len(all_nums) > 6 else 1
                    
                    # Extract date from page text
                    page_text = soup.get_text()
                    date_match = re.search(
                        r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(?:st|nd|rd|th)\s+'
                        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
                        page_text
                    )
                    
                    if date_match:
                        day = int(date_match.group(1))
                        month_name = date_match.group(2)
                        year = int(date_match.group(3))
                        month_num = {
                            'January': 1, 'February': 2, 'March': 3, 'April': 4,
                            'May': 5, 'June': 6, 'July': 7, 'August': 8,
                            'September': 9, 'October': 10, 'November': 11, 'December': 12
                        }.get(month_name, 1)
                        date_str = f"{day:02d}.{month_num:02d}.{year}"
                    else:
                        # Try DD.MM.YYYY pattern directly
                        dm = re.search(r'(\d{2}\.\d{2}\.\d{4})', page_text)
                        date_str = dm.group(1) if dm else datetime.now().strftime("%d.%m.%Y")
                    
                    results.append({
                        "date": date_str,
                        "numbers": main_nums,
                        "lucky_number": lucky,
                        "replay_number": 1
                    })
            
            logger.info(f"Fetched {len(results)} Swiss Lotto draws from lotteryextreme.com")
            
    except Exception as e:
        logger.error(f"Error fetching from lotteryextreme.com: {e}")
    
    return results


async def sync_euromillions_to_db(db, limit: int = 20) -> Dict:
    """
    Fetch latest EuroMillions and add new draws to database
    Returns stats about what was added
    """
    stats = {"fetched": 0, "new": 0, "existing": 0, "errors": 0}
    
    try:
        draws = await fetch_euromillions_latest(limit)
        stats["fetched"] = len(draws)
        
        for draw in draws:
            # Check if this draw already exists
            existing = await db.euromillions_draws.find_one({"date": draw["date"]})
            
            if existing:
                stats["existing"] += 1
            else:
                # Add new draw
                doc = {
                    "id": str(uuid.uuid4()),
                    "date": draw["date"],
                    "numbers": draw["numbers"],
                    "stars": draw["stars"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "auto_fetch"
                }
                await db.euromillions_draws.insert_one(doc)
                stats["new"] += 1
                logger.info(f"Added new EuroMillions draw: {draw['date']} - {draw['numbers']}")
                
    except Exception as e:
        logger.error(f"Error syncing EuroMillions: {e}")
        stats["errors"] += 1
    
    return stats


async def sync_swisslotto_to_db(db, limit: int = 50) -> Dict:
    """
    Fetch latest Swiss Lotto and add new draws to database.
    Uses lottolyzer.com as primary (50 draws, clean tables).
    Falls back to lotteryextreme.com (latest draw only).
    """
    stats = {"fetched": 0, "new": 0, "existing": 0, "errors": 0, "source": "none"}
    
    try:
        # PRIMARY: lottolyzer.com (structured table, up to 50 draws)
        draws = await fetch_swisslotto_from_lottolyzer(limit)
        if draws:
            stats["source"] = "lottolyzer.com"
        
        if not draws:
            # FALLBACK: lotteryextreme.com (latest draw)
            draws = await fetch_swisslotto_from_lotteryextreme()
            if draws:
                stats["source"] = "lotteryextreme.com"
        
        stats["fetched"] = len(draws)
        
        for draw in draws:
            existing = await db.draws.find_one({"date": draw["date"]})
            
            if existing:
                stats["existing"] += 1
            else:
                doc = {
                    "id": str(uuid.uuid4()),
                    "date": draw["date"],
                    "numbers": draw["numbers"],
                    "lucky_number": draw.get("lucky_number", 1),
                    "replay_number": draw.get("replay_number", 1),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": stats["source"]
                }
                await db.draws.insert_one(doc)
                stats["new"] += 1
                logger.info(f"Added new Swiss Lotto draw: {draw['date']} - {draw['numbers']} (from {stats['source']})")
                
    except Exception as e:
        logger.error(f"Error syncing Swiss Lotto: {e}")
        stats["errors"] += 1
    
    return stats


async def auto_sync_all(db) -> Dict:
    """
    Sync both lotteries and return combined stats
    """
    logger.info("Starting auto-sync of lottery results...")
    
    euro_stats = await sync_euromillions_to_db(db)
    swiss_stats = await sync_swisslotto_to_db(db)
    
    total_new = euro_stats["new"] + swiss_stats["new"]
    
    if total_new > 0:
        logger.info(f"Auto-sync complete: {total_new} new draws added")
    else:
        logger.info("Auto-sync complete: No new draws found")
    
    return {
        "euromillions": euro_stats,
        "swisslotto": swiss_stats,
        "total_new": total_new,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
