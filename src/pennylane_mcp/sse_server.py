"""SSE MCP Server for Dust integration."""
import os
import json
import asyncio
from typing import Any
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from mcp.server import Server
from mcp.types import Tool, TextContent
from .client import PennylaneClient
from .tools import invoices, customers, suppliers, transactions, accounting, quotes

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

# Créer le serveur MCP
mcp_server = Server("pennylane-mcp")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Liste tous les outils disponibles."""
    return [
        Tool(
            name="pennylane_list_customers",
            description="Liste tous les clients Pennylane",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nombre de résultats", "default": 20},
                },
            },
        ),
        Tool(
            name="pennylane_list_quotes",
            description="Liste tous les devis Pennylane",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nombre de résultats", "default": 30},
                },
            },
        ),
        Tool(
            name="pennylane_create_quote",
            description="Crée un nouveau devis Pennylane",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "ID du client"},
                    "date": {"type": "string", "description": "Date du devis (YYYY-MM-DD)"},
                    "deadline": {"type": "string", "description": "Date limite (YYYY-MM-DD)"},
                    "invoice_lines": {"type": "array", "description": "Lignes du devis"},
                },
                "required": ["customer_id", "date", "deadline", "invoice_lines"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Exécute un outil."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    try:
        if name == "pennylane_list_customers":
            result = await customers.list_customers(
                pennylane_client,
                limit=arguments.get("limit", 20),
            )
        elif name == "pennylane_list_quotes":
            result = await quotes.list_quotes(
                pennylane_client,
                limit=arguments.get("limit", 30),
            )
        elif name == "pennylane_create_quote":
            result = await quotes.create_quote(
                pennylane_client,
                **arguments
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "Pennylane MCP SSE Server"}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol."""
    
    async def event_generator():
        """Generate SSE events."""
        try:
            # Envoyer l'initialisation
            yield {
                "event": "message",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "method": "initialized",
                    "params": {}
                })
            }
            
            # Garder la connexion ouverte
            while True:
                if await request.is_disconnected():
                    break
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
    
    return EventSourceResponse(event_generator())


@app.post("/message")
async def handle_message(request: Request):
    """Handle MCP JSON-RPC messages."""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        msg_id = body.get("id")
        
        logger.info(f"Received message: {method}")
        
        if method == "tools/list":
            tools = await list_tools()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": r.text} for r in result]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if body else None,
            "error": {"code": -32603, "message": str(e)}
        }


@app.on_event("shutdown")
async def shutdown():
    """Cleanup."""
    await pennylane_client.close()
