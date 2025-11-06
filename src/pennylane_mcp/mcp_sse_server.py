"""MCP SSE Server for remote access (Dust compatible)."""
import os
import json
import asyncio
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from .client import PennylaneClient
from .tools import invoices, customers, quotes, transactions, accounting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le client Pennylane
api_key = os.getenv("PENNYLANE_API_KEY")
base_url = os.getenv("PENNYLANE_BASE_URL", "https://app.pennylane.com/api/external/v2")

if not api_key:
    raise ValueError("PENNYLANE_API_KEY environment variable is required")

pennylane_client = PennylaneClient(api_key=api_key, base_url=base_url)


@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "ok",
        "service": "Pennylane MCP SSE Server",
        "protocol": "mcp/sse",
        "version": "1.0.0"
    }


@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol."""
    
    async def event_stream():
        """Generate SSE events for MCP protocol."""
        try:
            # Get the base URL from request (use https for Railway)
            base_url = str(request.base_url).rstrip('/').replace('http://', 'https://')
            endpoint_url = f"{base_url}/message"
            
            # Send endpoint event - just the URL string
            yield f"event: endpoint\n"
            yield f"data: {endpoint_url}\n\n"
            
            logger.info(f"SSE connection established, endpoint: {endpoint_url}")
            
            # Keep connection alive with heartbeat
            while True:
                if await request.is_disconnected():
                    logger.info("Client disconnected from SSE")
                    break
                await asyncio.sleep(30)
                yield f": heartbeat\n\n"
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/message")
async def handle_message(request: Request):
    """Handle MCP JSON-RPC messages."""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        msg_id = body.get("id")
        
        logger.info(f"Received MCP message: {method}")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "pennylane-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "pennylane_list_customers",
                            "description": "Liste tous les clients Pennylane",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "limit": {"type": "integer", "description": "Nombre de résultats", "default": 20}
                                }
                            }
                        },
                        {
                            "name": "pennylane_list_quotes",
                            "description": "Liste tous les devis Pennylane",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "limit": {"type": "integer", "description": "Nombre de résultats", "default": 30}
                                }
                            }
                        },
                        {
                            "name": "pennylane_get_quote",
                            "description": "Récupère un devis spécifique",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "quote_id": {"type": "integer", "description": "ID du devis"}
                                },
                                "required": ["quote_id"]
                            }
                        },
                        {
                            "name": "pennylane_create_quote",
                            "description": "Crée un nouveau devis",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "customer_id": {"type": "integer"},
                                    "date": {"type": "string"},
                                    "deadline": {"type": "string"},
                                    "invoice_lines": {"type": "array"}
                                },
                                "required": ["customer_id", "date", "deadline", "invoice_lines"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result_text = await call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }


async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool and return result as JSON string."""
    try:
        if name == "pennylane_list_customers":
            result = await customers.list_customers(
                pennylane_client,
                limit=arguments.get("limit", 20)
            )
        elif name == "pennylane_list_quotes":
            result = await quotes.list_quotes(
                pennylane_client,
                limit=arguments.get("limit", 30)
            )
        elif name == "pennylane_get_quote":
            result = await quotes.get_quote(
                pennylane_client,
                arguments["quote_id"]
            )
        elif name == "pennylane_create_quote":
            result = await quotes.create_quote(
                pennylane_client,
                **arguments
            )
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return json.dumps({"error": str(e)})


@app.on_event("shutdown")
async def shutdown():
    """Cleanup."""
    await pennylane_client.close()
