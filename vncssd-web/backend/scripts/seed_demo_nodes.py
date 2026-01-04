"""
VNCSSDetector Web Service - Seed Demo Nodes
Run this script to delete old nodes and add 100 demo nodes around specified coordinates
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete
from app.database import async_session_maker, init_db
from app.models.node import Node

# Center coordinates (user specified)
CENTER_LAT = 10.76950491413405
CENTER_LNG = 106.66356222364968

# Spread radius (~500m in each direction)
SPREAD_LAT = 0.005  # ~555m
SPREAD_LNG = 0.005  # ~500m

DEVICE_TYPES = [
    "orbic",
    "tplink", 
    "tmobile",
    "wingtech",
    "pinephone",
    "msm8916",
]

STATUSES = ["online", "offline", "warning", "error"]
STATUS_WEIGHTS = [0.7, 0.15, 0.1, 0.05]  # 70% online


async def create_demo_nodes():
    """Delete old nodes and create 100 demo nodes around center coordinates."""
    await init_db()
    
    async with async_session_maker() as session:
        try:
            # Delete old demo nodes
            print("Deleting old NTP nodes...")
            await session.execute(delete(Node).where(Node.name.like("NTP-%")))
            await session.commit()
            print("✅ Deleted old nodes")
            
            print("Creating 100 demo nodes...")
            
            for i in range(1, 101):
                # Random position around center
                lat = CENTER_LAT + random.uniform(-SPREAD_LAT, SPREAD_LAT)
                lng = CENTER_LNG + random.uniform(-SPREAD_LNG, SPREAD_LNG)
                
                # Random status based on weights
                status = random.choices(STATUSES, STATUS_WEIGHTS)[0]
                
                # Random last seen
                if status == "online":
                    last_seen = datetime.utcnow() - timedelta(minutes=random.randint(0, 5))
                else:
                    last_seen = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                
                node = Node(
                    uuid=str(uuid.uuid4()),
                    name=f"NTP-{i:03d}",
                    device_type=random.choice(DEVICE_TYPES),
                    location_name=f"Số {random.randint(1, 500)} Nguyễn Tri Phương, Q.{random.choice([5, 10])}, TP.HCM",
                    location_lat=Decimal(str(round(lat, 8))),
                    location_lng=Decimal(str(round(lng, 8))),
                    status=status,
                    last_seen_at=last_seen
                )
                session.add(node)
                
                if i % 20 == 0:
                    print(f"  Created {i} nodes...")
            
            await session.commit()
            print("✅ Successfully created 100 demo nodes!")
            print(f"📍 Center: {CENTER_LAT}, {CENTER_LNG}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(create_demo_nodes())
