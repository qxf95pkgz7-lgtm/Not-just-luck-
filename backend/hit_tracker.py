"""
HIT TRACKER - Track Generated Tickets vs Actual Draws
=====================================================
Save generations, compare to real results, mark the hits!
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from bson import ObjectId


class HitTracker:
    """Track story generator predictions vs actual draws"""
    
    def __init__(self, db):
        self.db = db
        self.generations_collection = db.generations
        self.draws_collection = db.draws
    
    async def save_generation(
        self,
        target_date: str,
        tickets: List[Dict],
        generation_type: str = "story"
    ) -> str:
        """Save a generation for later hit tracking"""
        
        generation = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target_date": target_date,
            "generation_type": generation_type,
            "tickets": tickets,
            "hits_calculated": False,
            "hit_results": None,
            "total_hits": 0,
            "lucky_hits": 0,
            "best_ticket_hits": 0
        }
        
        result = await self.generations_collection.insert_one(generation)
        return str(result.inserted_id)
    
    async def get_draw_by_date(self, date_str: str) -> Optional[Dict]:
        """Get actual draw result for a date"""
        draw = await self.draws_collection.find_one(
            {"date": date_str},
            {"_id": 0}
        )
        return draw
    
    async def calculate_hits(self, generation_id: str) -> Dict:
        """Calculate hits for a saved generation"""
        
        try:
            gen = await self.generations_collection.find_one(
                {"_id": ObjectId(generation_id)}
            )
        except:
            return {"error": "Invalid generation ID"}
        
        if not gen:
            return {"error": "Generation not found"}
        
        target_date = gen["target_date"]
        actual_draw = await self.get_draw_by_date(target_date)
        
        if not actual_draw:
            return {
                "error": f"Draw for {target_date} not yet available",
                "generation_id": generation_id,
                "target_date": target_date,
                "status": "PENDING"
            }
        
        actual_numbers = set(actual_draw.get("numbers", []))
        actual_lucky = actual_draw.get("lucky_number", actual_draw.get("lucky"))
        
        hit_results = []
        total_number_hits = 0
        total_lucky_hits = 0
        best_ticket_hits = 0
        
        for i, ticket in enumerate(gen["tickets"]):
            ticket_numbers = set(ticket.get("numbers", []))
            ticket_lucky = ticket.get("lucky")
            
            # Find matching numbers
            number_hits = ticket_numbers & actual_numbers
            lucky_hit = ticket_lucky == actual_lucky
            
            hit_count = len(number_hits)
            total_number_hits += hit_count
            if lucky_hit:
                total_lucky_hits += 1
            
            if hit_count > best_ticket_hits:
                best_ticket_hits = hit_count
            
            hit_results.append({
                "ticket_num": i + 1,
                "predicted_numbers": sorted(ticket_numbers),
                "predicted_lucky": ticket_lucky,
                "story": ticket.get("story", ""),
                "number_hits": sorted(number_hits),
                "hit_count": hit_count,
                "lucky_hit": lucky_hit,
                "total_matches": hit_count + (1 if lucky_hit else 0)
            })
        
        # Update the generation record
        await self.generations_collection.update_one(
            {"_id": ObjectId(generation_id)},
            {"$set": {
                "hits_calculated": True,
                "hit_results": hit_results,
                "total_hits": total_number_hits,
                "lucky_hits": total_lucky_hits,
                "best_ticket_hits": best_ticket_hits,
                "actual_draw": {
                    "numbers": sorted(actual_numbers),
                    "lucky": actual_lucky
                }
            }}
        )
        
        return {
            "generation_id": generation_id,
            "target_date": target_date,
            "actual_draw": {
                "numbers": sorted(actual_numbers),
                "lucky": actual_lucky
            },
            "hit_results": hit_results,
            "summary": {
                "total_number_hits": total_number_hits,
                "total_lucky_hits": total_lucky_hits,
                "best_ticket_hits": best_ticket_hits,
                "tickets_with_hits": sum(1 for r in hit_results if r["hit_count"] > 0),
                "tickets_with_3plus": sum(1 for r in hit_results if r["hit_count"] >= 3),
                "tickets_with_lucky": sum(1 for r in hit_results if r["lucky_hit"])
            }
        }
    
    async def get_generation_history(
        self,
        limit: int = 50,
        include_hits: bool = True
    ) -> List[Dict]:
        """Get saved generations sorted by target_date.
        
        RULES:
        - Sorted by target_date descending (newest draw first)
        - Show last 10 generations for recent dates
        - Older dates: only show if best_ticket_hits >= 2
        """
        
        all_gens = await self.generations_collection.find(
            {},
            {"_id": 1, "generated_at": 1, "target_date": 1, "generation_type": 1,
             "tickets": 1, "hits_calculated": 1, "hit_results": 1,
             "total_hits": 1, "lucky_hits": 1, "best_ticket_hits": 1, "actual_draw": 1}
        ).to_list(length=500)
        
        for gen in all_gens:
            gen["_id"] = str(gen["_id"])
        
        # Sort by target_date descending
        def parse_target_date(g):
            try:
                return datetime.strptime(g.get('target_date', '01.01.2000'), '%d.%m.%Y')
            except:
                return datetime.min
        
        all_gens.sort(key=parse_target_date, reverse=True)
        
        # Group by target_date
        from collections import OrderedDict
        by_date = OrderedDict()
        for gen in all_gens:
            td = gen.get('target_date', 'unknown')
            if td not in by_date:
                by_date[td] = []
            by_date[td].append(gen)
        
        # Build result: last 10 for recent, 2+ hits for older
        result = []
        dates_seen = 0
        
        for target_date, gens_for_date in by_date.items():
            dates_seen += 1
            
            if dates_seen <= 3:
                for g in gens_for_date:
                    if len(result) < 10:
                        result.append(g)
            else:
                for g in gens_for_date:
                    if g.get('hits_calculated') and g.get('best_ticket_hits', 0) >= 2:
                        result.append(g)
        
        return result
    
    async def get_last_draw(self) -> Optional[Dict]:
        """Get the most recent draw"""
        
        draws = await self.draws_collection.find(
            {},
            {"_id": 0}
        ).to_list(3000)
        
        if not draws:
            return None
        
        # Sort by date
        def parse_date(d):
            try:
                return datetime.strptime(d["date"], "%d.%m.%Y")
            except:
                return datetime.min
        
        draws.sort(key=parse_date, reverse=True)
        return draws[0] if draws else None
    
    async def get_overall_stats(self) -> Dict:
        """Get overall hit statistics across all generations"""
        
        generations = await self.generations_collection.find(
            {"hits_calculated": True}
        ).to_list(1000)
        
        if not generations:
            return {
                "total_generations": 0,
                "total_tickets": 0,
                "total_number_hits": 0,
                "total_lucky_hits": 0,
                "best_ever_hits": 0,
                "avg_hits_per_ticket": 0,
                "tickets_with_3plus": 0,
                "tickets_with_4plus": 0,
                "tickets_with_5plus": 0
            }
        
        total_generations = len(generations)
        total_tickets = sum(len(g.get("tickets", [])) for g in generations)
        total_number_hits = sum(g.get("total_hits", 0) for g in generations)
        total_lucky_hits = sum(g.get("lucky_hits", 0) for g in generations)
        best_ever_hits = max(g.get("best_ticket_hits", 0) for g in generations)
        
        tickets_with_3plus = 0
        tickets_with_4plus = 0
        tickets_with_5plus = 0
        
        for gen in generations:
            for result in gen.get("hit_results", []):
                hits = result.get("hit_count", 0)
                if hits >= 3:
                    tickets_with_3plus += 1
                if hits >= 4:
                    tickets_with_4plus += 1
                if hits >= 5:
                    tickets_with_5plus += 1
        
        return {
            "total_generations": total_generations,
            "total_tickets": total_tickets,
            "total_number_hits": total_number_hits,
            "total_lucky_hits": total_lucky_hits,
            "best_ever_hits": best_ever_hits,
            "avg_hits_per_ticket": round(total_number_hits / total_tickets, 2) if total_tickets > 0 else 0,
            "tickets_with_3plus": tickets_with_3plus,
            "tickets_with_4plus": tickets_with_4plus,
            "tickets_with_5plus": tickets_with_5plus
        }
    
    async def recalculate_all_hits(self) -> Dict:
        """Recalculate hits for all generations that haven't been calculated yet"""
        
        pending = await self.generations_collection.find(
            {"hits_calculated": False}
        ).to_list(1000)
        
        calculated = 0
        still_pending = 0
        
        for gen in pending:
            gen_id = str(gen["_id"])
            result = await self.calculate_hits(gen_id)
            
            if "error" not in result or result.get("status") == "PENDING":
                if result.get("status") == "PENDING":
                    still_pending += 1
                else:
                    calculated += 1
        
        return {
            "calculated": calculated,
            "still_pending": still_pending,
            "message": f"Calculated hits for {calculated} generations, {still_pending} awaiting draws"
        }
