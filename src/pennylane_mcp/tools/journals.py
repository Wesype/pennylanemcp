"""Outils pour gérer les journaux comptables et comptes généraux Pennylane."""
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


async def list_ledger_accounts(
    client: PennylaneClient,
    limit: int = 20,
    page: int = 1,
    filter_query: str | None = None
) -> dict[str, Any]:
    """Liste tous les comptes généraux (ledger accounts).
    
    Filtres disponibles:
    - id: lt, lteq, gt, gteq, eq, not_eq, in, not_in
    - number: start_with, eq, in
    - enabled: eq
    """
    params = {
        "per_page": limit,
        "page": page,
    }
    
    if filter_query:
        params["filter"] = filter_query
    
    return await client.get("/ledger_accounts", params=params)


async def get_ledger_account(client: PennylaneClient, account_id: int) -> dict[str, Any]:
    """Récupère un compte général par son ID."""
    return await client.get(f"/ledger_accounts/{account_id}")


async def create_ledger_account(
    client: PennylaneClient,
    number: str,
    label: str,
    vat_rate: str | None = None,
    country_alpha2: str | None = None
) -> dict[str, Any]:
    """Crée un nouveau compte général.
    
    Args:
        number: Numéro du compte. Si commence par 401 (fournisseur) ou 411 (client),
                un fournisseur/client correspondant sera aussi créé
        label: Libellé du compte
        vat_rate: Taux de TVA (ex: FR_200, FR_1_75)
        country_alpha2: Code pays (ex: FR)
    """
    data = {
        "number": number,
        "label": label
    }
    
    if vat_rate:
        data["vat_rate"] = vat_rate
    if country_alpha2:
        data["country_alpha2"] = country_alpha2
    
    return await client.post("/ledger_accounts", json=data)
