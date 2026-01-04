"""
VNCSSDetector Web Service - Seed Demo Nodes
Run this script to add 100 demo nodes along Nguyễn Tri Phương street
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker, init_db
from app.models.node import Node, DeviceType, NodeStatus

# Nguyễn Tri Phương street coordinates (HCM - from District 5 to District 10)
# Approximate lat/lng range
NTP_LAT_START = 10.7580  # Near Đại học Y
NTP_LAT_END = 10.7720    # Near Lê Hồng Phong
NTP_LNG_START = 106.6620
NTP_LNG_END = 106.6680

DEVICE_TYPES = [
    DeviceType.ORBIC,
    DeviceType.TPLINK, 
    DeviceType.TMOBILE,
    DeviceType.WINGTECH,
    DeviceType.PINEPHONE,
    DeviceType.MSM8916,
]

STATUSES = [NodeStatus.ONLINE, NodeStatus.OFFLINE, NodeStatus.WARNING, NodeStatus.ERROR]
STATUS_WEIGHTS = [0.7, 0.15, 0.1, 0.05]  # 70% online


async def create_demo_nodes():
    """Create 100 demo nodes along Nguyễn Tri Phương street."""
    await init_db()
    
    async with async_session_maker() as session:
        try:
            print("Creating 100 demo nodes...")
            
            for i in range(1, 101):
                # Calculate position along the street
                progress = i / 100
                lat = NTP_LAT_START + (NTP_LAT_END - NTP_LAT_START) * progress
                lng = NTP_LNG_START + (NTP_LNG_END - NTP_LNG_START) * progress
                
                # Add some randomness
                lat += random.uniform(-0.0005, 0.0005)
                lng += random.uniform(-0.0005, 0.0005)
                
                # Random status based on weights
                status = random.choices(STATUSES, STATUS_WEIGHTS)[0]
                
                # Random last seen
                if status == NodeStatus.ONLINE:
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
                
                if i % 10 == 0:
                    print(f"  Created {i} nodes...")
            
            await session.commit()
            print("✅ Successfully created 100 demo nodes!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(create_demo_nodes())
