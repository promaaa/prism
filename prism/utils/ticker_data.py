"""
Ticker data for autocomplete suggestions.
Includes CAC 40 stocks and top 100 market cap cryptocurrencies.
"""

from typing import Dict, List, Tuple


# CAC 40 Companies (French Stock Market Index)
# Format: Ticker -> (Company Name, Sector)
CAC40_STOCKS = {
    "AC.PA": ("Accor", "Hotels"),
    "AI.PA": ("Air Liquide", "Chemicals"),
    "AIR.PA": ("Airbus SE", "Aerospace & Defense"),
    "ALO.PA": ("Alstom", "Industrial Machinery"),
    "MT.PA": ("ArcelorMittal", "Steel"),
    "CS.PA": ("AXA", "Insurance"),
    "BNP.PA": ("BNP Paribas", "Banking"),
    "EN.PA": ("Bouygues", "Construction"),
    "CAP.PA": ("Capgemini", "IT Services"),
    "CA.PA": ("Carrefour", "Retail"),
    "ACA.PA": ("Crédit Agricole", "Banking"),
    "BN.PA": ("Danone", "Food & Beverages"),
    "DSY.PA": ("Dassault Systèmes", "Software"),
    "EDEN.PA": ("Edenred", "Business Services"),
    "ENGI.PA": ("ENGIE", "Utilities"),
    "EL.PA": ("EssilorLuxottica", "Healthcare"),
    "ERF.PA": ("Eurofins Scientific", "Healthcare"),
    "RMS.PA": ("Hermès", "Luxury Goods"),
    "KER.PA": ("Kering", "Luxury Goods"),
    "OR.PA": ("L'Oréal", "Cosmetics"),
    "LR.PA": ("Legrand", "Electrical Equipment"),
    "MC.PA": ("LVMH", "Luxury Goods"),
    "ML.PA": ("Michelin", "Auto Parts"),
    "ORA.PA": ("Orange", "Telecommunications"),
    "RI.PA": ("Pernod Ricard", "Beverages"),
    "PUB.PA": ("Publicis Groupe", "Advertising"),
    "RNO.PA": ("Renault", "Automotive"),
    "SAF.PA": ("Safran", "Aerospace & Defense"),
    "SGO.PA": ("Saint-Gobain", "Building Materials"),
    "SAN.PA": ("Sanofi", "Pharmaceuticals"),
    "SU.PA": ("Schneider Electric", "Electrical Equipment"),
    "GLE.PA": ("Société Générale", "Banking"),
    "STLAP.PA": ("Stellantis", "Automotive"),
    "STMPA.PA": ("STMicroelectronics", "Semiconductors"),
    "TEP.PA": ("Teleperformance", "Business Services"),
    "HO.PA": ("Thales", "Aerospace & Defense"),
    "TTE.PA": ("TotalEnergies", "Oil & Gas"),
    "URW.PA": ("Unibail-Rodamco-Westfield", "Real Estate"),
    "VIE.PA": ("Veolia Environnement", "Utilities"),
    "DG.PA": ("Vinci", "Construction"),
    "VIV.PA": ("Vivendi", "Media"),
    "WLN.PA": ("Worldline", "Payment Services"),
}


# Top 100 Cryptocurrencies by Market Cap
# Format: Ticker -> (Full Name, Category)
TOP_CRYPTO = {
    "BTC": ("Bitcoin", "Currency"),
    "ETH": ("Ethereum", "Smart Contract Platform"),
    "USDT": ("Tether", "Stablecoin"),
    "BNB": ("Binance Coin", "Exchange Token"),
    "SOL": ("Solana", "Smart Contract Platform"),
    "USDC": ("USD Coin", "Stablecoin"),
    "XRP": ("Ripple", "Payment Network"),
    "STETH": ("Lido Staked Ether", "Liquid Staking"),
    "ADA": ("Cardano", "Smart Contract Platform"),
    "DOGE": ("Dogecoin", "Meme Coin"),
    "AVAX": ("Avalanche", "Smart Contract Platform"),
    "TRX": ("TRON", "Smart Contract Platform"),
    "DOT": ("Polkadot", "Interoperability"),
    "MATIC": ("Polygon", "Scaling Solution"),
    "LINK": ("Chainlink", "Oracle Network"),
    "TON": ("Toncoin", "Smart Contract Platform"),
    "SHIB": ("Shiba Inu", "Meme Coin"),
    "WBTC": ("Wrapped Bitcoin", "Wrapped Token"),
    "DAI": ("Dai", "Stablecoin"),
    "LTC": ("Litecoin", "Currency"),
    "BCH": ("Bitcoin Cash", "Currency"),
    "UNI": ("Uniswap", "DEX"),
    "ATOM": ("Cosmos", "Interoperability"),
    "LEO": ("UNUS SED LEO", "Exchange Token"),
    "XLM": ("Stellar", "Payment Network"),
    "OKB": ("OKB", "Exchange Token"),
    "ICP": ("Internet Computer", "Cloud Computing"),
    "ETC": ("Ethereum Classic", "Smart Contract Platform"),
    "FIL": ("Filecoin", "Storage"),
    "HBAR": ("Hedera", "Smart Contract Platform"),
    "CRO": ("Cronos", "Exchange Token"),
    "MKR": ("Maker", "DeFi"),
    "APT": ("Aptos", "Smart Contract Platform"),
    "LDO": ("Lido DAO", "Liquid Staking"),
    "NEAR": ("NEAR Protocol", "Smart Contract Platform"),
    "VET": ("VeChain", "Supply Chain"),
    "ARB": ("Arbitrum", "Scaling Solution"),
    "QNT": ("Quant", "Interoperability"),
    "TAO": ("Bittensor", "AI/Machine Learning"),
    "OP": ("Optimism", "Scaling Solution"),
    "ALGO": ("Algorand", "Smart Contract Platform"),
    "IMX": ("Immutable X", "NFT Scaling"),
    "GRT": ("The Graph", "Indexing Protocol"),
    "INJ": ("Injective", "DeFi"),
    "RUNE": ("THORChain", "Cross-Chain DEX"),
    "STX": ("Stacks", "Bitcoin Layer"),
    "AAVE": ("Aave", "DeFi Lending"),
    "FTM": ("Fantom", "Smart Contract Platform"),
    "SNX": ("Synthetix", "Synthetic Assets"),
    "MNT": ("Mantle", "Scaling Solution"),
    "XMR": ("Monero", "Privacy Coin"),
    "TIA": ("Celestia", "Modular Blockchain"),
    "FLR": ("Flare", "Smart Contract Platform"),
    "SUI": ("Sui", "Smart Contract Platform"),
    "SEI": ("Sei", "DeFi Infrastructure"),
    "SAND": ("The Sandbox", "Metaverse"),
    "MANA": ("Decentraland", "Metaverse"),
    "XTZ": ("Tezos", "Smart Contract Platform"),
    "EOS": ("EOS", "Smart Contract Platform"),
    "EGLD": ("MultiversX", "Smart Contract Platform"),
    "THETA": ("Theta Network", "Video Streaming"),
    "AXS": ("Axie Infinity", "Gaming"),
    "KCS": ("KuCoin Token", "Exchange Token"),
    "XDC": ("XDC Network", "Enterprise Blockchain"),
    "FLOW": ("Flow", "NFT Platform"),
    "KAVA": ("Kava", "DeFi"),
    "ZEC": ("Zcash", "Privacy Coin"),
    "GALA": ("Gala", "Gaming"),
    "MINA": ("Mina Protocol", "Zero-Knowledge"),
    "NEO": ("Neo", "Smart Contract Platform"),
    "CHZ": ("Chiliz", "Fan Tokens"),
    "CFX": ("Conflux", "Smart Contract Platform"),
    "CAKE": ("PancakeSwap", "DEX"),
    "1INCH": ("1inch", "DEX Aggregator"),
    "ENJ": ("Enjin Coin", "Gaming NFTs"),
    "ZIL": ("Zilliqa", "Smart Contract Platform"),
    "LRC": ("Loopring", "Scaling Solution"),
    "BAT": ("Basic Attention Token", "Digital Advertising"),
    "COMP": ("Compound", "DeFi Lending"),
    "CRV": ("Curve DAO", "DeFi"),
    "DASH": ("Dash", "Currency"),
    "WAVES": ("Waves", "Smart Contract Platform"),
    "ZRX": ("0x", "DEX Protocol"),
    "ENS": ("Ethereum Name Service", "Domain Names"),
    "YFI": ("yearn.finance", "DeFi Aggregator"),
    "SUSHI": ("SushiSwap", "DEX"),
    "BAL": ("Balancer", "DeFi"),
    "RVN": ("Ravencoin", "Asset Transfer"),
    "ICX": ("ICON", "Interoperability"),
    "QTUM": ("Qtum", "Smart Contract Platform"),
    "OMG": ("OMG Network", "Scaling Solution"),
    "ANKR": ("Ankr", "Web3 Infrastructure"),
    "SC": ("Siacoin", "Storage"),
    "ONT": ("Ontology", "Enterprise Blockchain"),
    "DGB": ("DigiByte", "Currency"),
    "HOT": ("Holo", "Distributed Computing"),
    "BNT": ("Bancor", "DEX"),
    "FET": ("Fetch.ai", "AI/Machine Learning"),
    "AGIX": ("SingularityNET", "AI/Machine Learning"),
    "OCEAN": ("Ocean Protocol", "Data Marketplace"),
    "RNDR": ("Render Token", "GPU Rendering"),
}


class TickerSuggestions:
    """Provides ticker suggestions for autocomplete."""

    def __init__(self):
        """Initialize ticker suggestions."""
        self._all_tickers: Dict[str, Tuple[str, str]] = {}
        self._load_data()

    def _load_data(self):
        """Load all ticker data."""
        # Combine stocks and crypto
        self._all_tickers.update(CAC40_STOCKS)
        self._all_tickers.update(TOP_CRYPTO)

    def get_all_tickers(self) -> List[str]:
        """
        Get list of all ticker symbols.

        Returns:
            List of ticker symbols
        """
        return sorted(self._all_tickers.keys())

    def get_ticker_info(self, ticker: str) -> Tuple[str, str, str]:
        """
        Get information about a ticker.

        Args:
            ticker: Ticker symbol

        Returns:
            Tuple of (ticker, name, category/sector)
        """
        ticker_upper = ticker.upper()

        # Direct match
        if ticker_upper in self._all_tickers:
            name, category = self._all_tickers[ticker_upper]
            return (ticker_upper, name, category)

        # Try adding .PA suffix for French stocks
        if not ticker_upper.endswith(".PA"):
            ticker_with_pa = f"{ticker_upper}.PA"
            if ticker_with_pa in self._all_tickers:
                name, category = self._all_tickers[ticker_with_pa]
                return (ticker_with_pa, name, category)

        # Try removing .PA suffix
        if ticker_upper.endswith(".PA"):
            ticker_without_pa = ticker_upper[:-3]
            if ticker_without_pa in self._all_tickers:
                name, category = self._all_tickers[ticker_without_pa]
                return (ticker_without_pa, name, category)

        return (ticker_upper, "Unknown", "Unknown")

    def get_suggestions(self, query: str) -> List[Tuple[str, str, str]]:
        """
        Get ticker suggestions based on query.

        Args:
            query: Search query (ticker or company name)

        Returns:
            List of (ticker, name, category) tuples
        """
        if not query:
            return []

        query_lower = query.lower()
        suggestions = []

        for ticker, (name, category) in self._all_tickers.items():
            # Match ticker or company name
            if (
                query_lower in ticker.lower()
                or query_lower in name.lower()
                or query_lower in category.lower()
            ):
                suggestions.append((ticker, name, category))

        # Sort by relevance (exact ticker match first, then by name)
        suggestions.sort(
            key=lambda x: (
                not x[0].lower().startswith(query_lower),  # Ticker starts with query
                not x[1].lower().startswith(query_lower),  # Name starts with query
                x[1],  # Alphabetical by name
            )
        )

        return suggestions

    def format_suggestion(self, ticker: str, name: str, category: str) -> str:
        """
        Format a suggestion for display.

        Args:
            ticker: Ticker symbol
            name: Company/crypto name
            category: Sector/category

        Returns:
            Formatted string
        """
        return f"{ticker} - {name} ({category})"

    def get_formatted_suggestions(self, query: str) -> List[str]:
        """
        Get formatted ticker suggestions.

        Args:
            query: Search query

        Returns:
            List of formatted suggestion strings
        """
        suggestions = self.get_suggestions(query)
        return [self.format_suggestion(t, n, c) for t, n, c in suggestions]

    def extract_ticker_from_suggestion(self, suggestion: str) -> str:
        """
        Extract ticker from formatted suggestion string.

        Args:
            suggestion: Formatted suggestion string

        Returns:
            Ticker symbol
        """
        # Format is "TICKER - Name (Category)"
        if " - " in suggestion:
            return suggestion.split(" - ")[0].strip()
        return suggestion.strip()

    def is_stock(self, ticker: str) -> bool:
        """
        Check if ticker is a stock (vs crypto).

        Args:
            ticker: Ticker symbol

        Returns:
            True if stock, False if crypto
        """
        return ticker.upper() in CAC40_STOCKS

    def is_crypto(self, ticker: str) -> bool:
        """
        Check if ticker is a cryptocurrency.

        Args:
            ticker: Ticker symbol

        Returns:
            True if crypto, False otherwise
        """
        return ticker.upper() in TOP_CRYPTO

    def get_asset_type(self, ticker: str) -> str:
        """
        Get asset type for ticker.

        Args:
            ticker: Ticker symbol

        Returns:
            "stock", "crypto", or "unknown"
        """
        ticker_upper = ticker.upper()
        if ticker_upper in CAC40_STOCKS:
            return "stock"
        elif ticker_upper in TOP_CRYPTO:
            return "crypto"
        else:
            return "unknown"

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about available tickers.

        Returns:
            Dictionary with counts
        """
        return {
            "total": len(self._all_tickers),
            "stocks": len(CAC40_STOCKS),
            "crypto": len(TOP_CRYPTO),
        }


# Global instance
_suggestions_instance = TickerSuggestions()


def get_ticker_suggestions() -> TickerSuggestions:
    """
    Get the global ticker suggestions instance.

    Returns:
        TickerSuggestions instance
    """
    return _suggestions_instance


# Convenience functions
def get_all_tickers() -> List[str]:
    """Get all available tickers."""
    return _suggestions_instance.get_all_tickers()


def get_suggestions(query: str) -> List[Tuple[str, str, str]]:
    """Get ticker suggestions for query."""
    return _suggestions_instance.get_suggestions(query)


def get_formatted_suggestions(query: str) -> List[str]:
    """Get formatted suggestions for query."""
    return _suggestions_instance.get_formatted_suggestions(query)


def get_ticker_info(ticker: str) -> Tuple[str, str, str]:
    """Get info about a ticker."""
    return _suggestions_instance.get_ticker_info(ticker)


def extract_ticker(suggestion: str) -> str:
    """Extract ticker from formatted suggestion."""
    return _suggestions_instance.extract_ticker_from_suggestion(suggestion)


def get_asset_type(ticker: str) -> str:
    """Get asset type for ticker."""
    return _suggestions_instance.get_asset_type(ticker)


# Example usage
if __name__ == "__main__":
    suggestions = get_ticker_suggestions()

    print(f"Total tickers: {suggestions.get_stats()}")
    print("\nSearching for 'LVMH':")
    for result in suggestions.get_suggestions("LVMH"):
        print(f"  {suggestions.format_suggestion(*result)}")

    print("\nSearching for 'bitcoin':")
    for result in suggestions.get_suggestions("bitcoin"):
        print(f"  {suggestions.format_suggestion(*result)}")

    print("\nSearching for 'ban':")
    for result in suggestions.get_suggestions("ban")[:5]:
        print(f"  {suggestions.format_suggestion(*result)}")
