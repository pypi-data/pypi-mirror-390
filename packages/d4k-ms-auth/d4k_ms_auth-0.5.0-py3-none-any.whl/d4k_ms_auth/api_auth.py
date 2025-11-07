from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from d4k_ms_base import ServiceEnvironment

api_key_header = APIKeyHeader(name="X-API-Key")


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == ServiceEnvironment().get("API_KEY"):
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
