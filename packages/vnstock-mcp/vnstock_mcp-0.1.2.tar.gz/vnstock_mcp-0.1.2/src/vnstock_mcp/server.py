"""
Vietnamese Stock Market Data MCP Server
Provides tools to fetch stock, forex, crypto, and index historical data from vnstock
"""

import asyncio

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("vnstock")

# NOTE: All vnstock imports are done lazily (inside functions) to avoid circular dependency
# Importing from vnstock.* at module level triggers vnstock/__init__.py which imports vnai,
# causing a circular import error. Lazy imports solve this by deferring import until needed.


@mcp.tool()
async def get_stock_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical stock price data for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        start_date: Start date in YYYY-MM-DD format (e.g., '2024-01-01')
        end_date: End date in YYYY-MM-DD format (e.g., '2024-12-31')
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical price data including time, open, high, low, close, volume
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.vci import Quote

        loop = asyncio.get_event_loop()

        # Initialize VCI Quote object
        quote = Quote(symbol=symbol)

        # Fetch historical data in executor to avoid blocking
        df = await loop.run_in_executor(
            None,
            lambda: quote.history(start=start_date, end=end_date, interval=interval),
        )

        if df is None or df.empty:
            return f"No data found for {symbol} between {start_date} and {end_date}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"


@mcp.tool()
async def get_forex_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical forex exchange rate data.

    Args:
        symbol: Forex pair symbol (e.g., 'USDVND', 'JPYVND', 'EURVND')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical forex rate data (time, open, high, low, close)
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.msn import Quote as MSNQuote

        loop = asyncio.get_event_loop()

        # Initialize MSN Quote for forex data
        quote = MSNQuote(symbol=symbol)

        # Fetch historical data in executor to avoid blocking
        df = await loop.run_in_executor(
            None,
            lambda: quote.history(start=start_date, end=end_date, interval=interval),
        )

        if df is None or df.empty:
            return (
                f"No forex data found for {symbol} between {start_date} and {end_date}"
            )

        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching forex data: {str(e)}"


@mcp.tool()
async def get_crypto_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical cryptocurrency price data.

    Args:
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical crypto price data (time, open, high, low, close, volume)
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.msn import Quote as MSNQuote

        loop = asyncio.get_event_loop()

        # Initialize MSN Quote for crypto data
        quote = MSNQuote(symbol=symbol)

        # Fetch historical data in executor to avoid blocking
        df = await loop.run_in_executor(
            None,
            lambda: quote.history(start=start_date, end=end_date, interval=interval),
        )

        if df is None or df.empty:
            return (
                f"No crypto data found for {symbol} between {start_date} and {end_date}"
            )

        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching crypto data: {str(e)}"


@mcp.tool()
async def get_index_history(
    symbol: str, start_date: str, end_date: str, interval: str = "1D"
) -> str:
    """
    Get historical market index data (Vietnamese and international indices).

    Args:
        symbol: Index symbol
               Vietnamese: 'VNINDEX', 'HNXINDEX', 'UPCOMINDEX'
               International: 'DJI' (Dow Jones)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval - '1D' (daily), '1W' (weekly), '1M' (monthly)

    Returns:
        JSON string with historical index data (time, open, high, low, close, volume)
    """
    try:
        # Lazy imports to avoid circular dependency
        from vnstock.explorer.vci import Quote
        from vnstock.explorer.msn import Quote as MSNQuote

        loop = asyncio.get_event_loop()

        # Check if it's a Vietnamese index
        vietnam_indices = ["VNINDEX", "HNXINDEX", "UPCOMINDEX"]

        if symbol.upper() in vietnam_indices:
            # Use VCI Quote for Vietnamese indices
            quote = Quote(symbol=symbol)
            df = await loop.run_in_executor(
                None,
                lambda: quote.history(
                    start=start_date, end=end_date, interval=interval
                ),
            )
        else:
            # Use MSN Quote for international indices
            quote = MSNQuote(symbol=symbol)
            df = await loop.run_in_executor(
                None,
                lambda: quote.history(
                    start=start_date, end=end_date, interval=interval
                ),
            )

        if df is None or df.empty:
            return (
                f"No index data found for {symbol} between {start_date} and {end_date}"
            )

        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching index data: {str(e)}"


@mcp.tool()
async def get_income_statement(symbol: str, lang: str = "en") -> str:
    """
    Get annual income statement (profit & loss) for Vietnamese stocks with chronological year ordering.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese')

    Returns:
        JSON string with annual income statement data including revenue, expenses,
        profit metrics, and earnings per share (EPS) for multiple years, sorted chronologically
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.vci import Finance

        loop = asyncio.get_event_loop()

        # Initialize Finance with VCI source
        finance = Finance(symbol=symbol.upper(), source="VCI")

        # Fetch annual income statement in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: finance.income_statement(period="year", lang=lang)
        )

        if df is None or df.empty:
            return f"No income statement data found for {symbol}"

        # Sort by yearReport for chronological analysis
        df = df.sort_values("yearReport").reset_index(drop=True)

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching income statement for {symbol}: {str(e)}"


@mcp.tool()
async def get_balance_sheet(symbol: str, lang: str = "en") -> str:
    """
    Get annual balance sheet for Vietnamese stocks with chronological year ordering.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual balance sheet data including assets, liabilities,
        equity, and detailed financial position metrics for multiple years, sorted chronologically
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.vci import Finance

        loop = asyncio.get_event_loop()

        # Initialize Finance with VCI source
        finance = Finance(symbol=symbol.upper(), source="VCI")

        # Fetch annual balance sheet in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: finance.balance_sheet(period="year", lang=lang)
        )

        if df is None or df.empty:
            return f"No balance sheet data found for {symbol}"

        # Sort by yearReport for chronological analysis
        df = df.sort_values("yearReport").reset_index(drop=True)

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching balance sheet for {symbol}: {str(e)}"


@mcp.tool()
async def get_cash_flow(symbol: str, lang: str = "en") -> str:
    """
    Get annual cash flow statement for Vietnamese stocks with chronological year ordering.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual cash flow data including operating, investing,
        and financing activities for multiple years, sorted chronologically
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.vci import Finance

        loop = asyncio.get_event_loop()

        # Initialize Finance with VCI source
        finance = Finance(symbol=symbol.upper(), source="VCI")

        # Fetch annual cash flow statement in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: finance.cash_flow(period="year", lang=lang)
        )

        if df is None or df.empty:
            return f"No cash flow data found for {symbol}"

        # Sort by yearReport for chronological analysis
        df = df.sort_values("yearReport").reset_index(drop=True)

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching cash flow for {symbol}: {str(e)}"


@mcp.tool()
async def get_financial_ratios(symbol: str, lang: str = "en") -> str:
    """
    Get annual financial ratios and metrics for Vietnamese stocks with chronological year ordering.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'VNM', 'HPG')
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with annual financial ratios including P/B (Price-to-Book),
        ROE (Return on Equity), and other key financial health indicators, sorted chronologically
    """
    try:
        # Lazy imports to avoid circular dependency
        from vnstock.explorer.vci import Finance
        from vnstock.core.utils.transform import flatten_hierarchical_index

        loop = asyncio.get_event_loop()

        # Initialize Finance with VCI source
        finance = Finance(symbol=symbol.upper(), source="VCI")

        # Fetch annual financial ratios in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: finance.ratio(period="year", lang=lang)
        )

        if df is None or df.empty:
            return f"No financial ratio data found for {symbol}"

        # Flatten MultiIndex DataFrame first, then sort chronologically
        flattened_df = await loop.run_in_executor(
            None,
            lambda: flatten_hierarchical_index(
                df, separator="_", handle_duplicates=True, drop_levels=0
            ),
        )

        # Sort flattened DataFrame by yearReport for chronological analysis
        if "yearReport" in flattened_df.columns:
            flattened_df = flattened_df.sort_values("yearReport").reset_index(drop=True)

        # Convert to JSON
        return flattened_df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching financial ratios for {symbol}: {str(e)}"


@mcp.tool()
async def get_dividend_history(symbol: str) -> str:
    """
    Get complete dividend history for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'ACB', 'HPG')

    Returns:
        JSON string with complete dividend history including exercise date,
        cash year, dividend percentage, and issue method for all historical records
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.tcbs import Company as TCBSCompany

        loop = asyncio.get_event_loop()

        # Initialize TCBS Company (dividends only available from TCBS)
        company = TCBSCompany(symbol=symbol.upper())

        # Fetch dividend history in executor to avoid blocking
        df = await loop.run_in_executor(None, lambda: company.dividends())

        if df is None or df.empty:
            return f"No dividend data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching dividend history for {symbol}: {str(e)}"


@mcp.tool()
async def get_sjc_gold_price(date: str = None) -> str:
    """
    Get SJC gold prices (current or historical).

    Args:
        date: Date in YYYY-MM-DD format (e.g., '2024-01-15').
              If None, returns current prices. Historical data available from 2016-01-02.

    Returns:
        JSON string with gold price data including name, branch, buy_price, sell_price, date
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.misc.gold_price import sjc_gold_price

        loop = asyncio.get_event_loop()

        # Fetch SJC gold prices in executor to avoid blocking
        df = await loop.run_in_executor(None, lambda: sjc_gold_price(date=date))

        if df is None or df.empty:
            date_str = date if date else "current date"
            return f"No SJC gold price data found for {date_str}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching SJC gold prices: {str(e)}"


@mcp.tool()
async def get_btmc_gold_price() -> str:
    """
    Get current BTMC (Bảo Tín Minh Châu) gold prices.

    Returns:
        JSON string with gold price data including name, karat, gold_content,
        buy_price, sell_price, world_price, time
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.misc.gold_price import btmc_goldprice

        loop = asyncio.get_event_loop()

        # Fetch BTMC gold prices in executor to avoid blocking
        df = await loop.run_in_executor(None, lambda: btmc_goldprice())

        if df is None or df.empty:
            return "No BTMC gold price data found"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching BTMC gold prices: {str(e)}"


@mcp.tool()
async def get_vcb_exchange_rate(date: str) -> str:
    """
    Get VCB (Vietcombank) exchange rates for a specific date.

    Args:
        date: Date in YYYY-MM-DD format (e.g., '2024-01-15')

    Returns:
        JSON string with exchange rate data including currency_code, currency_name,
        buy_cash, buy_transfer, sell, date for 20 major currencies
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.misc.exchange_rate import vcb_exchange_rate

        loop = asyncio.get_event_loop()

        # Fetch VCB exchange rates in executor to avoid blocking
        df = await loop.run_in_executor(None, lambda: vcb_exchange_rate(date=date))

        if df is None or df.empty:
            return f"No VCB exchange rate data found for {date}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching VCB exchange rates: {str(e)}"


@mcp.tool()
async def get_company_info(
    symbol: str, info_type: str = "overview", lang: str = "en"
) -> str:
    """
    Get company information for Vietnamese stocks.

    Args:
        symbol: Stock ticker symbol (e.g., 'VCI', 'ACB', 'HPG')
        info_type: Type of company information to fetch:
                  'overview' - Company overview and basic information
                  'shareholders' - Major shareholders information
                  'officers' - Company officers and management (filter: 'working', 'resigned', 'all')
                  'subsidiaries' - Subsidiaries and associated companies (filter: 'all', 'subsidiary')
                  'events' - Corporate events and announcements
                  'news' - Company news and updates
                  'reports' - Analysis reports
                  'ratio_summary' - Financial ratios summary
                  'trading_stats' - Trading statistics and market data
        lang: Language - 'en' (English) or 'vi' (Vietnamese)

    Returns:
        JSON string with company information based on the requested type
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.vci import Company

        loop = asyncio.get_event_loop()

        # Initialize Company with VCI source
        company = Company(symbol=symbol.upper(), source="VCI")

        # Fetch the requested company information in executor to avoid blocking
        if info_type == "overview":
            df = await loop.run_in_executor(None, lambda: company.overview())
        elif info_type == "shareholders":
            df = await loop.run_in_executor(None, lambda: company.shareholders())
        elif info_type == "officers":
            # Default to working officers, can be extended to accept filter parameter
            df = await loop.run_in_executor(
                None, lambda: company.officers(filter_by="working")
            )
        elif info_type == "subsidiaries":
            # Default to all subsidiaries and associated companies
            df = await loop.run_in_executor(
                None, lambda: company.subsidiaries(filter_by="all")
            )
        elif info_type == "events":
            df = await loop.run_in_executor(None, lambda: company.events())
        elif info_type == "news":
            df = await loop.run_in_executor(None, lambda: company.news())
        elif info_type == "reports":
            df = await loop.run_in_executor(None, lambda: company.reports())
        elif info_type == "ratio_summary":
            df = await loop.run_in_executor(None, lambda: company.ratio_summary())
        elif info_type == "trading_stats":
            df = await loop.run_in_executor(None, lambda: company.trading_stats())
        else:
            return f"Invalid info_type '{info_type}'. Valid types: overview, shareholders, officers, subsidiaries, events, news, reports, ratio_summary, trading_stats"

        if df is None or df.empty:
            return f"No {info_type} data found for {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching {info_type} for {symbol}: {str(e)}"


# ========== Fund Management Tools ==========


@mcp.tool()
async def get_fund_listing(fund_type: str = "") -> str:
    """
    Get list of all available mutual funds.

    Args:
        fund_type: Filter by fund type - '' (all), 'BALANCED', 'BOND', 'STOCK'

    Returns:
        JSON string with complete fund listing including fund codes, names, NAV,
        fund types, owners, inception dates, and performance metrics
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.fmarket.fund import Fund

        loop = asyncio.get_event_loop()

        # Initialize Fund with lazy loading
        fund = Fund()

        # Fetch fund listing in executor to avoid blocking
        df = await loop.run_in_executor(None, lambda: fund.listing(fund_type=fund_type))

        if df is None or df.empty:
            return f"No funds found for type: {fund_type}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching fund listing: {str(e)}"


@mcp.tool()
async def search_funds(symbol: str) -> str:
    """
    Search for mutual funds by symbol or partial name.

    Args:
        symbol: Fund short name or ticker (case-insensitive, partial match allowed)

    Returns:
        JSON string with matching funds including their IDs and short names
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.fmarket.fund import Fund

        loop = asyncio.get_event_loop()

        # Initialize Fund with lazy loading
        fund = Fund()

        # Search for funds in executor to avoid blocking
        df = await loop.run_in_executor(None, lambda: fund.filter(symbol=symbol))

        if df is None or df.empty:
            return f"No funds found matching: {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error searching funds: {str(e)}"


@mcp.tool()
async def get_fund_nav_report(symbol: str) -> str:
    """
    Get historical NAV report for a specific mutual fund.

    Args:
        symbol: Fund short name/ticker (e.g., 'SSISCA', 'VESAF')

    Returns:
        JSON string with historical NAV data including dates and NAV per unit
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.fmarket.fund import Fund

        loop = asyncio.get_event_loop()

        # Initialize Fund with lazy loading
        fund = Fund()

        # Fetch NAV report in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: fund.details.nav_report(symbol=symbol.upper())
        )

        if df is None or df.empty:
            return f"No NAV data found for fund: {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching NAV report for {symbol}: {str(e)}"


@mcp.tool()
async def get_fund_top_holdings(symbol: str) -> str:
    """
    Get top 10 holdings for a specific mutual fund.

    Args:
        symbol: Fund short name/ticker (e.g., 'SSISCA', 'VESAF')

    Returns:
        JSON string with top holdings including stock codes, industries,
        net asset percentages, asset types, and last update date
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.fmarket.fund import Fund

        loop = asyncio.get_event_loop()

        # Initialize Fund with lazy loading
        fund = Fund()

        # Fetch top holdings in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: fund.details.top_holding(symbol=symbol.upper())
        )

        if df is None or df.empty:
            return f"No top holdings data found for fund: {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching top holdings for {symbol}: {str(e)}"


@mcp.tool()
async def get_fund_industry_allocation(symbol: str) -> str:
    """
    Get industry allocation breakdown for a specific mutual fund.

    Args:
        symbol: Fund short name/ticker (e.g., 'SSISCA', 'VESAF')

    Returns:
        JSON string with industry allocation including industry names
        and net asset percentages
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.fmarket.fund import Fund

        loop = asyncio.get_event_loop()

        # Initialize Fund with lazy loading
        fund = Fund()

        # Fetch industry allocation in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: fund.details.industry_holding(symbol=symbol.upper())
        )

        if df is None or df.empty:
            return f"No industry allocation data found for fund: {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching industry allocation for {symbol}: {str(e)}"


@mcp.tool()
async def get_fund_asset_allocation(symbol: str) -> str:
    """
    Get asset allocation breakdown for a specific mutual fund.

    Args:
        symbol: Fund short name/ticker (e.g., 'SSISCA', 'VESAF')

    Returns:
        JSON string with asset allocation including asset types
        and asset percentages
    """
    try:
        # Lazy import to avoid circular dependency
        from vnstock.explorer.fmarket.fund import Fund

        loop = asyncio.get_event_loop()

        # Initialize Fund with lazy loading
        fund = Fund()

        # Fetch asset allocation in executor to avoid blocking
        df = await loop.run_in_executor(
            None, lambda: fund.details.asset_holding(symbol=symbol.upper())
        )

        if df is None or df.empty:
            return f"No asset allocation data found for fund: {symbol}"

        # Convert to JSON
        return df.to_json(orient="records", date_format="iso", indent=2)

    except Exception as e:
        return f"Error fetching asset allocation for {symbol}: {str(e)}"


def main():
    """Main entry point for the MCP server."""
    # Run server with stdio transport (default)
    mcp.run()


if __name__ == "__main__":
    main()
