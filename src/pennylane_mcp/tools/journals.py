"""Outils pour gérer les journaux comptables Pennylane."""
from typing import Any
from ..client import PennylaneClient


async def list_journals(
    client: PennylaneClient,
    limit: int = 25,
    cursor: str | None = None,
    filter_query: str | None = None,
    sort: str = "-id"
) -> dict[str, Any]:
    """Liste tous les journaux comptables."""
    params = {
        "per_page": limit,
        "sort": sort,
    }
    
    if cursor:
        params["cursor"] = cursor
    if filter_query:
        params["filter"] = filter_query
    
    return await client.get("/journals", params=params)


async def get_journal(client: PennylaneClient, journal_id: int) -> dict[str, Any]:
    """Récupère un journal comptable par son ID."""
    return await client.get(f"/journals/{journal_id}")


async def create_journal(
    client: PennylaneClient,
    code: str,
    label: str
) -> dict[str, Any]:
    """Crée un nouveau journal comptable.
    
    Args:
        code: Code du journal (2 à 5 lettres)
        label: Libellé du journal
    """
    data = {
        "code": code,
        "label": label
    }
    
    return await client.post("/journals", json=data)
