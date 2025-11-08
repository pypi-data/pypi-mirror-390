

"""
x402 Wallet Utilities for Solana

Simple wallet creation and management.
"""

import json
import os
import base58
from pathlib import Path
from typing import Optional

from solders.keypair import Keypair


def create_wallet() -> Keypair:
    """
    Create a new Solana wallet
    
    Returns:
        New Keypair
    
    Example:
        >>> wallet = create_wallet()
        >>> print(f"Address: {wallet.pubkey()}")
    """
    return Keypair()


def save_wallet(keypair: Keypair, filepath: str) -> None:
    """
    Save wallet to JSON file
    
    Args:
        keypair: Wallet to save
        filepath: Path to save file
    
    Example:
        >>> wallet = create_wallet()
        >>> save_wallet(wallet, "wallet.json")
    """
    # Create directory if needed
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Save as byte array (Phantom format)
    wallet_bytes = bytes(keypair)
    wallet_list = list(wallet_bytes)
    
    with open(filepath, 'w') as f:
        json.dump(wallet_list, f)
    
    print(f"Wallet saved to {filepath}")
    print(f"Address: {keypair.pubkey()}")


def load_wallet(filepath: str) -> Keypair:
    """
    Load wallet from JSON file
    
    Args:
        filepath: Path to wallet file
    
    Returns:
        Loaded Keypair
    
    Example:
        >>> wallet = load_wallet("wallet.json")
        >>> print(f"Loaded: {wallet.pubkey()}")
    """
    with open(filepath, 'r') as f:
        wallet_list = json.load(f)
    
    wallet_bytes = bytes(wallet_list)
    return Keypair.from_bytes(wallet_bytes)


def load_wallet_from_env(env_var: str = "SOLANA_PRIVATE_KEY") -> Optional[Keypair]:
    """
    Load wallet from environment variable
    
    Args:
        env_var: Environment variable name
    
    Returns:
        Keypair if found, None otherwise
    
    Example:
        >>> # Set env: export SOLANA_PRIVATE_KEY="base58_private_key"
        >>> wallet = load_wallet_from_env()
        >>> if wallet:
        ...     print(f"Loaded: {wallet.pubkey()}")
    """
    private_key = os.getenv(env_var)
    if not private_key:
        return None
    
    try:
        # Try base58 decode
        decoded = base58.b58decode(private_key)
        return Keypair.from_bytes(decoded[:32])  # Use first 32 bytes
    except:
        # Try as raw hex
        try:
            decoded = bytes.fromhex(private_key)
            return Keypair.from_bytes(decoded[:32])
        except:
            return None


def get_wallet_balance_url(address: str, network: str = "devnet") -> str:
    """
    Get Solana Explorer URL for wallet
    
    Args:
        address: Wallet address
        network: Network name
    
    Returns:
        Explorer URL
    """
    if network == "mainnet":
        return f"https://explorer.solana.com/address/{address}"
    else:
        return f"https://explorer.solana.com/address/{address}?cluster={network}"