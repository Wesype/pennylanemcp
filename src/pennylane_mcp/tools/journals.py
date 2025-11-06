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


async def list_ledger_entries(
    client: PennylaneClient,
    limit: int = 20,
    page: int = 1,
    filter_query: str | None = None,
    sort: str = "-updated_at"
) -> dict[str, Any]:
    """Liste toutes les écritures comptables.
    
    Filtres disponibles:
    - updated_at, created_at, date: lt, lteq, gt, gteq, eq, not_eq
    - journal_id: lt, lteq, gt, gteq, eq, not_eq, in, not_in
    """
    params = {
        "per_page": limit,
        "page": page,
        "sort": sort,
    }
    
    if filter_query:
        params["filter"] = filter_query
    
    return await client.get("/ledger_entries", params=params)


async def list_ledger_entry_lines(
    client: PennylaneClient,
    ledger_entry_id: int,
    limit: int = 20,
    page: int = 1
) -> dict[str, Any]:
    """Liste les lignes d'écriture d'une écriture comptable."""
    params = {
        "per_page": limit,
        "page": page,
    }
    
    return await client.get(f"/ledger_entries/{ledger_entry_id}/ledger_entry_lines", params=params)


async def create_ledger_entry(
    client: PennylaneClient,
    date: str,
    label: str,
    journal_id: int,
    ledger_entry_lines: list[dict[str, Any]],
    ledger_attachment_id: int | None = None,
    currency: str = "EUR"
) -> dict[str, Any]:
    """Crée une nouvelle écriture comptable.
    
    Args:
        date: Date de l'écriture (YYYY-MM-DD)
        label: Libellé de l'écriture
        journal_id: ID du journal
        ledger_entry_lines: Lignes d'écriture avec debit, credit, ledger_account_id, label
        ledger_attachment_id: ID de la pièce jointe
        currency: Devise (ex: EUR)
    """
    data = {
        "date": date,
        "label": label,
        "journal_id": journal_id,
        "ledger_entry_lines": ledger_entry_lines,
        "currency": currency
    }
    
    if ledger_attachment_id:
        data["ledger_attachment_id"] = ledger_attachment_id
    
    return await client.post("/ledger_entries", json=data)


async def update_ledger_entry(
    client: PennylaneClient,
    ledger_entry_id: int,
    date: str | None = None,
    label: str | None = None,
    journal_id: int | None = None,
    ledger_entry_lines: dict[str, Any] | None = None,
    ledger_attachment_id: int | None = None,
    currency: str | None = None
) -> dict[str, Any]:
    """Met à jour une écriture comptable.
    
    Args:
        ledger_entry_id: ID de l'écriture
        date: Date de l'écriture (YYYY-MM-DD)
        label: Libellé de l'écriture
        journal_id: ID du journal
        ledger_entry_lines: Dict avec "create" et "update" pour les lignes
        ledger_attachment_id: ID de la pièce jointe
        currency: Devise
    """
    data = {}
    
    if date:
        data["date"] = date
    if label:
        data["label"] = label
    if journal_id:
        data["journal_id"] = journal_id
    if ledger_entry_lines:
        data["ledger_entry_lines"] = ledger_entry_lines
    if ledger_attachment_id:
        data["ledger_attachment_id"] = ledger_attachment_id
    if currency:
        data["currency"] = currency
    
    return await client.put(f"/ledger_entries/{ledger_entry_id}", json=data)


async def list_all_ledger_entry_lines(
    client: PennylaneClient,
    limit: int = 20,
    cursor: str | None = None,
    filter_query: str | None = None,
    sort: str = "id"
) -> dict[str, Any]:
    """Liste toutes les lignes d'écriture."""
    params = {
        "limit": limit,
        "sort": sort,
    }
    
    if cursor:
        params["cursor"] = cursor
    if filter_query:
        params["filter"] = filter_query
    
    return await client.get("/ledger_entry_lines", params=params)


async def get_ledger_entry_line(client: PennylaneClient, line_id: int) -> dict[str, Any]:
    """Récupère une ligne d'écriture par son ID."""
    return await client.get(f"/ledger_entry_lines/{line_id}")


async def list_lettered_ledger_entry_lines(
    client: PennylaneClient,
    line_id: int,
    limit: int = 20,
    page: int = 1
) -> dict[str, Any]:
    """Liste les lignes d'écriture lettrées avec une ligne donnée."""
    params = {
        "per_page": limit,
        "page": page,
    }
    
    return await client.get(f"/ledger_entry_lines/{line_id}/lettered_ledger_entry_lines", params=params)


async def list_ledger_entry_line_categories(
    client: PennylaneClient,
    line_id: int,
    limit: int = 20,
    page: int = 1
) -> dict[str, Any]:
    """Liste les catégories analytiques d'une ligne d'écriture."""
    params = {
        "per_page": limit,
        "page": page,
    }
    
    return await client.get(f"/ledger_entry_lines/{line_id}/categories", params=params)


async def link_categories_to_ledger_entry_line(
    client: PennylaneClient,
    line_id: int,
    categories: list[dict[str, Any]]
) -> dict[str, Any]:
    """Lie des catégories analytiques à une ligne d'écriture."""
    data = {"categories": categories}
    return await client.put(f"/ledger_entry_lines/{line_id}/categories", json=data)


async def letter_ledger_entry_lines(
    client: PennylaneClient,
    ledger_entry_lines: list[dict[str, int]],
    unbalanced_lettering_strategy: str = "none"
) -> dict[str, Any]:
    """Lettre des lignes d'écriture ensemble.
    
    Args:
        ledger_entry_lines: Liste de lignes avec leur ID (min 2)
        unbalanced_lettering_strategy: "none" ou "partial"
    """
    data = {
        "unbalanced_lettering_strategy": unbalanced_lettering_strategy,
        "ledger_entry_lines": ledger_entry_lines
    }
    
    return await client.post("/ledger_entry_lines/lettering", json=data)


async def unletter_ledger_entry_lines(
    client: PennylaneClient,
    ledger_entry_lines: list[dict[str, int]],
    unbalanced_lettering_strategy: str = "none"
) -> dict[str, Any]:
    """Délettre des lignes d'écriture.
    
    Args:
        ledger_entry_lines: Liste de lignes avec leur ID (min 1)
        unbalanced_lettering_strategy: "none" ou "partial"
    """
    data = {
        "unbalanced_lettering_strategy": unbalanced_lettering_strategy,
        "ledger_entry_lines": ledger_entry_lines
    }
    
    return await client.delete("/ledger_entry_lines/lettering", json=data)
