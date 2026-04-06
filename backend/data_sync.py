"""
Data Sync Module - Keeps EuroMillions and Swiss Lotto data files updated
This runs on startup and can be triggered manually via API

The static Python files are the source of truth for the prediction engine.
This module fetches latest draws from APIs and updates those files.
"""

import httpx
import asyncio
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

EUROMILLIONS_API = "https://euromillions.api.pedromealha.dev"
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


async def fetch_euromillions_from_api() -> list:
    """Fetch all EuroMillions draws from the free API"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{EUROMILLIONS_API}/draws",
                headers={
                    "accept": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            if response.status_code == 200:
                data = response.json()
                draws = data if isinstance(data, list) else data.get("draws", [])
                logger.info(f"Fetched {len(draws)} draws from EuroMillions API")
                return draws
            else:
                logger.error(f"API returned status {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching from EuroMillions API: {e}")
    return []


def parse_api_draw(draw: dict) -> dict:
    """Convert API draw format to our format"""
    date_str = draw.get("date", "")
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        formatted_date = dt.strftime("%d.%m.%Y")
        nums = sorted([int(n) for n in draw.get("numbers", [])])
        stars = sorted([int(s) for s in draw.get("stars", [])])
        return {
            "date": formatted_date,
            "numbers": nums,
            "stars": stars
        }
    except:
        return None


async def sync_euromillions_data() -> dict:
    """
    Sync EuroMillions data file with latest from API
    Returns stats about what was synced
    """
    stats = {"status": "started", "existing": 0, "new": 0, "errors": []}
    
    try:
        # Import current data
        from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
        existing = {d['date']: d for d in EUROMILLIONS_DRAWS_2024_2026}
        stats["existing"] = len(existing)
        
        # Fetch from API
        api_draws = await fetch_euromillions_from_api()
        if not api_draws:
            stats["status"] = "api_error"
            stats["errors"].append("Could not fetch from API")
            return stats
        
        # Find new draws for 2024-2026
        new_draws = []
        for draw in api_draws:
            parsed = parse_api_draw(draw)
            if parsed:
                try:
                    year = int(parsed['date'].split('.')[-1])
                    if year >= 2024 and parsed['date'] not in existing:
                        new_draws.append(parsed)
                        existing[parsed['date']] = parsed
                except:
                    pass
        
        stats["new"] = len(new_draws)
        
        if new_draws:
            # Sort all draws by date
            def parse_date(d):
                parts = d['date'].split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            
            all_draws = sorted(existing.values(), key=parse_date)
            
            # Generate updated file
            file_content = f'''"""
EuroMillions historical draws 2024-2026
Auto-updated from euromillions.api.pedromealha.dev
Last update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total draws: {len(all_draws)}
"""

EUROMILLIONS_DRAWS_2024_2026 = [
'''
            for draw in all_draws:
                file_content += f'    {{"date": "{draw["date"]}", "numbers": {draw["numbers"]}, "stars": {draw["stars"]}}},\n'
            
            file_content += ''']

print(f"Total EuroMillions draws (2024-2026): {len(EUROMILLIONS_DRAWS_2024_2026)}")
'''
            
            # Write the file
            file_path = os.path.join(DATA_DIR, 'euromillions_data_2024_2026.py')
            with open(file_path, 'w') as f:
                f.write(file_content)
            
            logger.info(f"Updated euromillions_data_2024_2026.py with {len(new_draws)} new draws")
            for draw in new_draws:
                logger.info(f"  Added: {draw['date']} | {draw['numbers']} | Stars: {draw['stars']}")
            
            stats["status"] = "updated"
            stats["new_draws"] = new_draws
        else:
            stats["status"] = "up_to_date"
            logger.info("EuroMillions data is already up to date")
        
    except Exception as e:
        stats["status"] = "error"
        stats["errors"].append(str(e))
        logger.error(f"Error syncing EuroMillions data: {e}")
    
    return stats


async def startup_sync():
    """Run sync on application startup"""
    logger.info("Running startup data sync...")
    
    # Wait a moment for services to stabilize
    await asyncio.sleep(2)
    
    try:
        euro_stats = await sync_euromillions_data()
        logger.info(f"EuroMillions sync: {euro_stats['status']} - {euro_stats['new']} new draws")
        return {"euromillions": euro_stats}
    except Exception as e:
        logger.error(f"Startup sync error: {e}")
        return {"error": str(e)}


# Allow running directly for manual sync
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    print("Running manual data sync...")
    result = asyncio.run(startup_sync())
    print(f"Result: {result}")
