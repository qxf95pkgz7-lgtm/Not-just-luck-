"""
Auto-fetch lottery results from external sources
- Swiss Lotto: Scrapes from swisslos.ch (Wed & Sat draws)
- EuroMillions: Uses free API from pedromealha.dev (Tue & Fri draws)
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

# Swiss Lotto - we'll scrape from swisslos.ch
SWISSLOS_URL = "https://www.swisslos.ch/en/swisslotto/information/winning-numbers/winning-numbers.html"


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
            
            # Get the most recent draws (API returns oldest first, so reverse)
            draws = data if isinstance(data, list) else data.get("draws", [])
            draws = list(reversed(draws))  # Most recent first
            
            for draw in draws[:limit]:
                # API format: {"date": "Fri, 13 Feb 2004 00:00:00 GMT", "numbers": ["16","29",...], "stars": ["7","9"]}
                date_str = draw.get("date", "")
                numbers = draw.get("numbers", [])
                stars = draw.get("stars", [])
                
                if date_str and numbers:
                    # Convert date from "Fri, 13 Feb 2004 00:00:00 GMT" to DD.MM.YYYY
                    try:
                        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                        formatted_date = dt.strftime("%d.%m.%Y")
                    except:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            formatted_date = dt.strftime("%d.%m.%Y")
                        except:
                            formatted_date = date_str
                    
                    # Convert string numbers to int
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


async def fetch_swisslotto_latest(limit: int = 10) -> List[Dict]:
    """
    Scrape latest Swiss Lotto results from swisslos.ch
    Returns list of draws with date, numbers, lucky_number, replay_number
    """
    results = []
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                SWISSLOS_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find draw containers - swisslos uses specific class patterns
            # Look for the winning numbers sections
            draw_sections = soup.find_all('div', class_=re.compile(r'winning-numbers|draw-result|result-item'))
            
            if not draw_sections:
                # Try alternative parsing - look for number balls
                ball_containers = soup.find_all('div', class_=re.compile(r'ball|number'))
                logger.info(f"Found {len(ball_containers)} ball containers")
            
            # Also try to find via JavaScript data or JSON embedded in page
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'winningNumbers' in str(script.string):
                    # Try to extract JSON data
                    text = script.string
                    # Look for patterns like numbers: [1,2,3,4,5,6]
                    number_match = re.search(r'numbers["\s:]+\[([0-9,\s]+)\]', text)
                    if number_match:
                        nums = [int(n.strip()) for n in number_match.group(1).split(',')]
                        logger.info(f"Found numbers in script: {nums}")
            
            # If direct scraping fails, try the API endpoint that the page uses
            api_url = "https://www.swisslos.ch/api/lotto/winning-numbers"
            try:
                api_response = await client.get(api_url)
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    logger.info(f"Got data from swisslos API: {api_data}")
            except:
                pass
                
            logger.info(f"Scraped {len(results)} Swiss Lotto draws")
            
    except Exception as e:
        logger.error(f"Error fetching Swiss Lotto: {e}")
    
    return results


async def fetch_swisslotto_from_lottoland() -> List[Dict]:
    """
    Alternative: Fetch Swiss Lotto from lottoland.com which has cleaner structure
    """
    results = []
    try:
        url = "https://www.lottoland.com/en/swisslotto/results-winning-numbers"
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Lottoland typically shows results in structured divs
            # Look for result rows
            result_rows = soup.find_all('div', class_=re.compile(r'result|draw|winning'))
            
            for row in result_rows[:10]:
                # Try to extract date and numbers
                date_elem = row.find(class_=re.compile(r'date'))
                number_elems = row.find_all(class_=re.compile(r'ball|number'))
                
                if date_elem and number_elems:
                    date_text = date_elem.get_text(strip=True)
                    numbers = []
                    for elem in number_elems:
                        try:
                            num = int(elem.get_text(strip=True))
                            if 1 <= num <= 42:
                                numbers.append(num)
                        except:
                            pass
                    
                    if len(numbers) >= 6:
                        results.append({
                            "date": date_text,
                            "numbers": sorted(numbers[:6]),
                            "lucky_number": numbers[6] if len(numbers) > 6 else 1,
                            "replay_number": numbers[7] if len(numbers) > 7 else 1
                        })
            
            logger.info(f"Fetched {len(results)} Swiss Lotto draws from lottoland")
            
    except Exception as e:
        logger.error(f"Error fetching from lottoland: {e}")
    
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


async def sync_swisslotto_to_db(db, limit: int = 20) -> Dict:
    """
    Fetch latest Swiss Lotto and add new draws to database
    Returns stats about what was added
    """
    stats = {"fetched": 0, "new": 0, "existing": 0, "errors": 0}
    
    try:
        # Try lottoland first (usually more reliable scraping)
        draws = await fetch_swisslotto_from_lottoland()
        
        if not draws:
            # Fallback to swisslos.ch
            draws = await fetch_swisslotto_latest(limit)
        
        stats["fetched"] = len(draws)
        
        for draw in draws:
            # Check if this draw already exists
            existing = await db.draws.find_one({"date": draw["date"]})
            
            if existing:
                stats["existing"] += 1
            else:
                # Add new draw
                doc = {
                    "id": str(uuid.uuid4()),
                    "date": draw["date"],
                    "numbers": draw["numbers"],
                    "lucky_number": draw.get("lucky_number", 1),
                    "replay_number": draw.get("replay_number", 1),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "auto_fetch"
                }
                await db.draws.insert_one(doc)
                stats["new"] += 1
                logger.info(f"Added new Swiss Lotto draw: {draw['date']} - {draw['numbers']}")
                
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
