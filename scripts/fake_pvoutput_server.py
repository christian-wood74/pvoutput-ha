from aiohttp import web
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_LOGGER = logging.getLogger(__name__)

async def handle_add_status(request):
    """Handle the addstatus.jsp POST request."""
    # Log headers
    headers = request.headers
    api_key = headers.get('X-Pvoutput-Apikey')
    system_id = headers.get('X-Pvoutput-SystemId')
    
    _LOGGER.info("Received request from System ID: %s", system_id)
    _LOGGER.info("API Key (provided): %s", api_key)
    
    # Log body
    try:
        data = await request.post()
        _LOGGER.info("Payload: %s", dict(data))
    except Exception as e:
        _LOGGER.error("Could not parse payload: %s", e)
        # Fallback to reading raw body if post() fails (e.g., if not form-encoded)
        body = await request.text()
        _LOGGER.info("Raw Body: %s", body)

    # Return success response as expected by PVOutput
    # PVOutput usually returns 200 OK for success
    return web.Response(text="OK 200", status=200)

async def start_server(host, port):
    """Start the mock server."""
    app = web.Application()
    # PVOutput endpoint for adding status
    app.router.add_post('/service/r2/addstatus.jsp', handle_add_status)
    # Also handle root or any other path for generic logging if needed
    app.router.add_post('/', handle_add_status)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    
    _LOGGER.info("Starting fake PVOutput server on http://%s:%s", host, port)
    _LOGGER.info("Configure your integration with API URL: http://%s:%s/service/r2/addstatus.jsp", host, port)
    
    await site.start()
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    import asyncio
    
    parser = argparse.ArgumentParser(description="Fake PVOutput Server for Testing")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(start_server(args.host, args.port))
    except KeyboardInterrupt:
        _LOGGER.info("Server stopped by user")
