from typing import Annotated

from fastapi import FastAPI, Query

from schemas.activation import ActivationIn

app = FastAPI()


@app.get("/assets")
async def get_assets(filters: Annotated[ActivationIn, Query()]) -> dict[str, str | int]:
    """Get assets."""
    return {"date": filters.date.isoformat(), "volume": filters.volume}
