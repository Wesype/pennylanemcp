"""Définition de tous les outils MCP Pennylane pour le serveur SSE."""

ALL_TOOLS = [
    # FACTURES CLIENTS
    {
        "name": "pennylane_list_customer_invoices",
        "description": "Liste les factures clients avec pagination et filtres",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de résultats", "default": 20},
                "cursor": {"type": "string", "description": "Curseur de pagination"},
                "filter": {"type": "string", "description": "Filtres"},
                "sort": {"type": "string", "description": "Tri", "default": "-id"}
            }
        }
    },
    {
        "name": "pennylane_get_customer_invoice",
        "description": "Récupère une facture client par son ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "ID de la facture"}
            },
            "required": ["invoice_id"]
        }
    },
    {
        "name": "pennylane_create_customer_invoice",
        "description": "Crée une nouvelle facture client",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "ID du client"},
                "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                "deadline": {"type": "string", "description": "Date limite (YYYY-MM-DD)"},
                "invoice_lines": {"type": "array", "description": "Lignes de facture"},
                "draft": {"type": "boolean", "description": "Brouillon ou finalisée", "default": True}
            },
            "required": ["customer_id", "date", "deadline", "invoice_lines", "draft"]
        }
    },
    # CLIENTS
    {
        "name": "pennylane_list_customers",
        "description": "Liste tous les clients",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de résultats", "default": 20}
            }
        }
    },
    {
        "name": "pennylane_get_customer",
        "description": "Récupère un client par son ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "ID du client"}
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "pennylane_create_customer",
        "description": "Crée un nouveau client",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom du client"},
                "email": {"type": "string", "description": "Email"},
                "customer_type": {"type": "string", "description": "Type: company ou individual"}
            },
            "required": ["name", "customer_type"]
        }
    },
    # DEVIS
    {
        "name": "pennylane_list_quotes",
        "description": "Liste tous les devis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de résultats", "default": 30}
            }
        }
    },
    {
        "name": "pennylane_get_quote",
        "description": "Récupère un devis par son ID",
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
                "customer_id": {"type": "integer", "description": "ID du client"},
                "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                "deadline": {"type": "string", "description": "Date limite (YYYY-MM-DD)"},
                "invoice_lines": {"type": "array", "description": "Lignes du devis"}
            },
            "required": ["customer_id", "date", "deadline", "invoice_lines"]
        }
    },
    {
        "name": "pennylane_update_quote",
        "description": "Met à jour un devis existant",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quote_id": {"type": "integer", "description": "ID du devis"},
                "deadline": {"type": "string", "description": "Nouvelle date limite"}
            },
            "required": ["quote_id"]
        }
    },
    {
        "name": "pennylane_update_quote_status",
        "description": "Met à jour le statut d'un devis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quote_id": {"type": "integer", "description": "ID du devis"},
                "status": {"type": "string", "description": "Statut: pending, accepted, denied, invoiced, expired"}
            },
            "required": ["quote_id", "status"]
        }
    },
    # TRANSACTIONS
    {
        "name": "pennylane_list_transactions",
        "description": "Liste toutes les transactions bancaires",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de résultats", "default": 20}
            }
        }
    },
    {
        "name": "pennylane_create_transaction",
        "description": "Crée une nouvelle transaction bancaire",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bank_account_id": {"type": "integer", "description": "ID du compte bancaire"},
                "label": {"type": "string", "description": "Libellé"},
                "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                "amount": {"type": "string", "description": "Montant"},
                "fee": {"type": "string", "description": "Frais", "default": "0"}
            },
            "required": ["bank_account_id", "label", "date", "amount", "fee"]
        }
    },
    # COMPTABILITÉ
    {
        "name": "pennylane_list_bank_accounts",
        "description": "Liste tous les comptes bancaires",
        "inputSchema": {"type": "object", "properties": {}}
    },
    # FOURNISSEURS
    {
        "name": "pennylane_list_suppliers",
        "description": "Liste tous les fournisseurs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de résultats", "default": 20}
            }
        }
    },
    {
        "name": "pennylane_create_supplier",
        "description": "Crée un nouveau fournisseur",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom du fournisseur"},
                "email": {"type": "string", "description": "Email"}
            },
            "required": ["name"]
        }
    },
    # JOURNAUX COMPTABLES
    {
        "name": "pennylane_list_journals",
        "description": "Liste tous les journaux comptables",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de résultats", "default": 25},
                "cursor": {"type": "string", "description": "Curseur de pagination"},
                "filter": {"type": "string", "description": "Filtres (type: eq, not_eq, in, not_in)"},
                "sort": {"type": "string", "description": "Tri", "default": "-id"}
            }
        }
    },
    {
        "name": "pennylane_get_journal",
        "description": "Récupère un journal comptable par son ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "journal_id": {"type": "integer", "description": "ID du journal"}
            },
            "required": ["journal_id"]
        }
    },
    {
        "name": "pennylane_create_journal",
        "description": "Crée un nouveau journal comptable",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code du journal (2 à 5 lettres)"},
                "label": {"type": "string", "description": "Libellé du journal"}
            },
            "required": ["code", "label"]
        }
    }
]
