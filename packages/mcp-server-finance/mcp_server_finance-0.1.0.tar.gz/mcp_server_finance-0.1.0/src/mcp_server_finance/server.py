import os
import base64
import json
from typing import Annotated, Optional, List
import yfinance as yf

import httpx
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP(
    name="Finance MCP Server",
    instructions="A Model Context Protocol server that provides tools to fetch and manage finance data.",
)



def _format_response(data: object) -> str:
    """Pretty-print JSON for MCP textual output."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def _is_valid_iso_datetime(value: str) -> bool:
    # Basic validation: ISO 8601 with 'T' separator and parseable by fromisoformat (after trimming Z)
    if "T" not in value:
        return False
    # Allow trailing Z by replacing with +00:00 for Python parsing
    try:
        from datetime import datetime

        candidate = value.replace("Z", "+00:00")
        datetime.fromisoformat(candidate)
        return True
    except Exception:
        return False

@mcp.tool(
    description="Get stock metadata and company information for a given stock symbol",
)
async def get_stock_metadata(
    stockSymbol: Annotated[
        str,
        Field(description="The stock symbol to get data for"),
    ],
) -> str:
    symbol = yf.Ticker(stockSymbol)
    info = symbol.info
    
    data = {
        "companySector": info['sector'],
        "peRatio": info['trailingPE'],
        "companyBeta": info['beta'],
    }
    for key, value in info.items():
        data[key] = value

    return _format_response(data)




@mcp.tool(
    description="Get stock time series data for a given stock symbol",
)
async def get_stock_time_series(
    stockSymbol: Annotated[
        str,
        Field(description="The stock symbol to get data for"),
    ],
    startDate: Annotated[
        str,
        Field(description="Start date (e.g., 2024-04-08)"),
    ],
    endDate: Annotated[
        str,
        Field(description="End date (e.g., 2024-04-14)"),
    ],
    interval: Annotated[
        str,
        Field(description="Interval (e.g. 1m, 5m, 1h, 1d, ,1wk, 1mo)"),
    ] = "1d",
) -> str:
    symbol = yf.Ticker(stockSymbol)
    hist = symbol.history(start=startDate, end=endDate, interval=interval)

    return hist.to_json(orient="records")




@mcp.tool(
    description="Get options expiration dates for a given stock symbol",
)
async def get_options_expiration_dates(
    tickerSymbol: Annotated[
        str,
        Field(description="The ticker symbol to get data for"),
    ],
) -> str:
    symbol = yf.Ticker(tickerSymbol)
    expirations = symbol.options
    return _format_response(expirations)



@mcp.tool(
    description="Get options time series data for a given stock symbol",
)
async def get_options_time_series(
    tickerSymbol: Annotated[
        str,
        Field(description="The ticker symbol to get data for"),
    ],
    expirationDate: Annotated[
        str,
        Field(description="Expiration date (e.g., 2024-04-08)"),
    ],
    optionType: Annotated[
        str,
        Field(description="Option type (e.g., call, put)"),
    ] = "call",
) -> str:
    symbol = yf.Ticker(tickerSymbol)
    chain = symbol.option_chain(expirationDate)  
    if optionType == "call":
        data = chain.calls
    elif optionType == "put":
        data = chain.puts
    else:
        raise ValueError(f"Invalid option type: {optionType}")

    return data.to_json(orient="records")


def main() -> None:
    """Run the Finance MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
