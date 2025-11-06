"""HTTP wrapper for the MCP server to be deployed on Railway."""
import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from .client import PennylaneClient
from .tools import invoices, customers, suppliers, transactions, accounting, quotes

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pennylane MCP HTTP Server")

# Ajouter CORS pour Dust
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
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Pennylane MCP HTTP Server",
        "version": "1.0.0",
        "tools_count": 38
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/tools")
async def list_tools():
    """Liste tous les outils disponibles."""
    return {
        "tools": [
            {"name": "pennylane_list_customers", "description": "Liste tous les clients"},
            {"name": "pennylane_get_customer", "description": "Récupère un client"},
            {"name": "pennylane_list_customer_invoices", "description": "Liste toutes les factures clients"},
            {"name": "pennylane_get_customer_invoice", "description": "Récupère une facture client"},
            {"name": "pennylane_create_customer_invoice", "description": "Crée une facture client"},
            {"name": "pennylane_list_quotes", "description": "Liste tous les devis"},
            {"name": "pennylane_get_quote", "description": "Récupère un devis"},
            {"name": "pennylane_create_quote", "description": "Crée un devis"},
            {"name": "pennylane_update_quote", "description": "Met à jour un devis"},
            {"name": "pennylane_update_quote_status", "description": "Met à jour le statut d'un devis"},
            {"name": "pennylane_list_transactions", "description": "Liste toutes les transactions"},
            {"name": "pennylane_list_bank_accounts", "description": "Liste tous les comptes bancaires"},
        ]
    }


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    """Execute a Pennylane MCP tool."""
    try:
        body = await request.json()
        arguments = body.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        # Router vers le bon outil
        result = await route_tool(tool_name, arguments)
        
        return JSONResponse(content={
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def route_tool(name: str, arguments: dict):
    """Route tool calls to the appropriate handler."""
    
    # FACTURES CLIENTS
    if name == "pennylane_list_customer_invoices":
        return await invoices.list_customer_invoices(
            pennylane_client,
            limit=arguments.get("limit", 20),
            cursor=arguments.get("cursor"),
            filter_query=arguments.get("filter"),
            sort=arguments.get("sort", "-id")
        )
    
    elif name == "pennylane_get_customer_invoice":
        return await invoices.get_customer_invoice(
            pennylane_client,
            arguments["invoice_id"]
        )
    
    elif name == "pennylane_create_customer_invoice":
        return await invoices.create_customer_invoice(
            pennylane_client,
            **arguments
        )
    
    # CLIENTS
    elif name == "pennylane_list_customers":
        return await customers.list_customers(
            pennylane_client,
            limit=arguments.get("limit", 20),
            cursor=arguments.get("cursor"),
            filter_query=arguments.get("filter"),
            sort=arguments.get("sort", "-id")
        )
    
    elif name == "pennylane_get_customer":
        return await customers.get_customer(
            pennylane_client,
            arguments["customer_id"]
        )
    
    # DEVIS
    elif name == "pennylane_list_quotes":
        return await quotes.list_quotes(
            pennylane_client,
            limit=arguments.get("limit", 30),
            cursor=arguments.get("cursor"),
            filter_query=arguments.get("filter"),
            sort=arguments.get("sort", "-id")
        )
    
    elif name == "pennylane_get_quote":
        return await quotes.get_quote(
            pennylane_client,
            arguments["quote_id"]
        )
    
    elif name == "pennylane_create_quote":
        return await quotes.create_quote(
            pennylane_client,
            **arguments
        )
    
    # TRANSACTIONS
    elif name == "pennylane_list_transactions":
        return await transactions.list_transactions(
            pennylane_client,
            limit=arguments.get("limit", 20),
            cursor=arguments.get("cursor"),
            filter_query=arguments.get("filter"),
            sort=arguments.get("sort", "-id")
        )
    
    # COMPTABILITÉ
    elif name == "pennylane_list_bank_accounts":
        return await accounting.list_bank_accounts(pennylane_client)
    
    else:
        raise ValueError(f"Unknown tool: {name}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await pennylane_client.close()
