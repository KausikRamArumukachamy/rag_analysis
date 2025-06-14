import asyncio
import httpx
import logging

BACKEND_URL = "https://rag-analysis.onrender.com/health" 

async def keep_server_alive():
    """Pings the server every 10 minutes to prevent Render from sleeping."""
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(BACKEND_URL)
                logging.info(f"Keep-alive ping sent: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in keep-alive ping: {e}")
        
        await asyncio.sleep(15)  # Wait 15 seconds before the next ping
