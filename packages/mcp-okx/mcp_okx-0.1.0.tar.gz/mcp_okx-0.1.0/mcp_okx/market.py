from fastmcp import FastMCP
from pydantic import Field
from okx.MarketData import MarketAPI

from .config import *

ACCOUNT = MarketAPI(
    api_key=OKX_API_KEY,
    api_secret_key=OKX_API_SECRET,
    passphrase=OKX_PASSPHRASE,
    flag=OKX_TRADE_FLAG,
    domain=OKX_BASE_URL,
)


def add_tools(mcp: FastMCP):

    @mcp.tool(
        title="Get market tickers",
        description="Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours."
                    "Get the ranking of coins with the highest increase or the largest trading volume.",
    )
    def market_tickers(
        instType: str = Field("SPOT", description="Instrument type: [SPOT/SWAP/FUTURES/OPTION]"),
        instFamily: str = Field("", description="Instrument family。 Applicable to FUTURES/SWAP/OPTION"),
        sortBy: str = Field("change24h", description="Sorting method: [change24h/changeMax/last/vol24h/...]"),
        limit: int | str = Field(30, description="Number of results. Default: 30"),
    ):
        resp = ACCOUNT.get_tickers(instType=instType, instFamily=instFamily) or {}
        if int(resp.get("code", 0)):
            return resp
        data = resp.get("data", [])
        for item in data:
            try:
                item["change24h"] = round((float(item["last"]) - float(item["open24h"])) / float(item["open24h"]) * 100, 2)
                item["changeMax"] = round((float(item["high24h"]) - float(item["low24h"])) / float(item["low24h"]) * 100, 2)
            except Exception:
                continue
        data.sort(key=lambda x: float(x.get(sortBy) or 0), reverse=True)
        resp["data"] = data[:int(limit)]
        resp["_response_schema"] = """
        instType	String	Instrument type
        instId	String	Instrument ID
        last	String	Last traded price
        lastSz	String	Last traded size. 0 represents there is no trading volume
        askPx	String	Best ask price
        askSz	String	Best ask size
        bidPx	String	Best bid price
        bidSz	String	Best bid size
        open24h	String	Open price in the past 24 hours
        high24h	String	Highest price in the past 24 hours
        low24h	String	Lowest price in the past 24 hours
        volCcy24h	String	24h trading volume, with a unit of currency.
            If it is a derivatives contract, the value is the number of base currency. e.g. the unit is BTC for BTC-USD-SWAP and BTC-USDT-SWAP
            If it is SPOT/MARGIN, the value is the quantity in quote currency.
        vol24h	String	24h trading volume, with a unit of contract.
            If it is a derivatives contract, the value is the number of contracts.
            If it is SPOT/MARGIN, the value is the quantity in base currency.
        sodUtc0	String	Open price in the UTC 0
        sodUtc8	String	Open price in the UTC 8
        change24h   float   Percentage change over 24 hours
        changeMax   float   24-hour high and low percentage range
        """
        return resp
