import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_reservation(client):
    dto = {
        "slot_start": (datetime.now() + timedelta(hours=1)).isoformat(),
        "duration_min": 60,
        "party_size": 2
    }

    response = await client.post("/reservations", json=dto)

    assert response.status_code == 200
    data = response.json()
    assert "reservation_id" in data
    assert isinstance(data["reservation_id"], str)
    assert len(data["reservation_id"]) > 0