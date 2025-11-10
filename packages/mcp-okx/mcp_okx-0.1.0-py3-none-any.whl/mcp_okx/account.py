from fastmcp import FastMCP
from pydantic import Field
from okx.Account import AccountAPI

from .config import *

ACCOUNT = AccountAPI(
    api_key=OKX_API_KEY,
    api_secret_key=OKX_API_SECRET,
    passphrase=OKX_PASSPHRASE,
    flag=OKX_TRADE_FLAG,
    domain=OKX_BASE_URL,
)


def add_tools(mcp: FastMCP):

    @mcp.tool(
        title="Get account configuration",
        description="Retrieve current OKX account configuration. "
                    "It is recommended to use this tool to obtain account configuration information before using all other tools",
    )
    def account_config():
        resp = ACCOUNT.get_account_config() or {}
        if int(resp.get("code", 0)):
            return resp
        resp["_response_schema"] = """
        uid	String	Account ID of current request
        mainUid	String	Main Account ID of current request.
            The current request account is main account if uid = mainUid.
            The current request account is sub-account if uid != mainUid.
        acctLv	String	Account mode
            1: Spot mode
            2: Futures mode
            3: Multi-currency margin
            4: Portfolio margin
        acctStpMode	String	Account self-trade prevention mode: cancel_maker/cancel_taker/cancel_both
            The default value is cancel_maker. Users can log in to the webpage through the master account to modify this configuration
        posMode	String	Position mode. long_short_mode: long/short, only applicable to FUTURES/SWAP; net_mode: net
        autoLoan	Boolean	Whether to borrow coins automatically
            true: borrow coins automatically
            false: not borrow coins automatically
        feeType	String	Fee type
            0: fee is charged in the currency you receive from the trade
            1: fee is always charged in the quote currency of the trading pair
        level	String	The user level of the current real trading volume on the platform, e.g Lv1, which means regular user level
        levelTmp	String	Temporary experience user level of special users, e.g Lv1
        ctIsoMode	String	Contract isolated margin trading settings. automatic: Auto transfers; autonomy: Manual transfers
        mgnIsoMode	String	Margin isolated margin trading settings
            auto_transfers_ccy: New auto transfers, enabling both base and quote currency as the margin for isolated margin trading
            automatic: Auto transfers
            quick_margin: Quick Margin Mode (For new accounts, including subaccounts, some defaults will be automatic, and others will be quick_margin)
        roleType	String	Role type
            0: General user
            1: Leading trader
            2: Copy trader
        traderInsts	Array of strings	Leading trade instruments, only applicable to Leading trader
        spotRoleType	String	SPOT copy trading role type. 0: General user; 1: Leading trader; 2: Copy trader
        spotTraderInsts	Array of strings	Spot lead trading instruments, only applicable to lead trader
        opAuth	String	Whether the optional trading was activated. 0: not activate; 1: activated
        kycLv	String	Main account KYC level
            0: No verification
            1: level 1 completed
            2: level 2 completed
            3: level 3 completed
            If the request originates from a subaccount, kycLv is the KYC level of the main account.
            If the request originates from the main account, kycLv is the KYC level of the current account.
        label	String	API key note of current request API key. No more than 50 letters (case sensitive) or numbers, which can be pure letters or pure numbers
        ip	String	IP addresses that linked with current API key, separate with commas if more than one. It is an empty string "" if there is no IP bonded.
        perm	String	The permission of the current requesting API key or Access token. read_only: Read; trade: Trade; withdraw: Withdraw
        liquidationGear	String	The maintenance margin ratio level of liquidation alert
            3 and -1 means that you will get hourly liquidation alerts on app and channel "Position risk warning" when your margin level drops to or below 300%. -1 is the initial value which has the same effect as -3
            0 means that there is not alert
        enableSpotBorrow	Boolean	Whether borrow is allowed or not in Spot mode. true: Enabled; false: Disabled
        spotBorrowAutoRepay	Boolean	Whether auto-repay is allowed or not in Spot mode. true: Enabled; false: Disabled
        type	String	Account type
            0: Main account
            1: Standard sub-account
            2: Managed trading sub-account
            5: Custody trading sub-account - Copper
            9: Managed trading sub-account - Copper
            12: Custody trading sub-account - Komainu
        settleCcy	String	Current account's USD-margined contract settle currency
        settleCcyList	String	Current account's USD-margined contract settle currency list, like ["USD", "USDC", "USDG"]
        """
        return resp

    @mcp.tool(
        title="Get account balance",
        description="Retrieve a list of assets (with non-zero balance), remaining balance, and available amount in the OKX trading account",
    )
    def account_balance(
        ccy: str = Field("", description="Single currency or multiple currencies (no more than 20) separated with comma, e.g. BTC or BTC,ETH."
                                         "Optional, all by default if not passed"),
    ):
        resp = ACCOUNT.get_account_balance(ccy) or {}
        if int(resp.get("code", 0)):
            return resp
        resp["_response_schema"] = """
        totalEq: The total amount of equity in USD
        isoEq: Isolated margin equity in USD. Applicable to Futures mode/Multi-currency margin/Portfolio margin
        adjEq: Adjusted / Effective equity in USD.
            The net fiat value of the assets in the account that can provide margins for spot, expiry futures, perpetual futures and options under the cross-margin mode.
            In multi-ccy or PM mode, the asset and margin requirement will all be converted to USD value to process the order check or liquidation.
            Due to the volatility of each currency market, our platform calculates the actual USD value of each currency based on discount rates to balance market risks.
            Applicable to Spot mode/Multi-currency margin and Portfolio margin
        availEq: Account level available equity, excluding currencies that are restricted due to the collateralized borrowing limit.
            Applicable to Multi-currency margin/Portfolio margin
        ordFroz: Cross margin frozen for pending orders in USD. Only applicable to Spot mode/Multi-currency margin/Portfolio margin
        imr: Initial margin requirement in USD.
            The sum of initial margins of all open positions and pending orders under cross-margin mode in USD.
            Applicable to Spot mode/Multi-currency margin/Portfolio margin
        mmr: Maintenance margin requirement in USD.
            The sum of maintenance margins of all open positions and pending orders under cross-margin mode in USD.
            Applicable to Spot mode/Multi-currency margin/Portfolio margin
        borrowFroz: Potential borrowing IMR of the account in USD.
            Only applicable to Spot mode/Multi-currency margin/Portfolio margin. It is "" for other margin modes.
        mgnRatio: Maintenance margin ratio in USD. Applicable to Spot mode/Multi-currency margin/Portfolio margin
        notionalUsd: Notional value of positions in USD. Applicable to Spot mode/Multi-currency margin/Portfolio margin
        notionalUsdForBorrow: Notional value for Borrow in USD. Applicable to Spot mode/Multi-currency margin/Portfolio margin
        notionalUsdForSwap: Notional value of positions for Perpetual Futures in USD. Applicable to Multi-currency margin/Portfolio margin
        notionalUsdForFutures: Notional value of positions for Expiry Futures in USD. Applicable to Multi-currency margin/Portfolio margin
        notionalUsdForOption: Notional value of positions for Option in USD. Applicable to Spot mode/Multi-currency margin/Portfolio margin
        upl: Cross-margin info of unrealized profit and loss at the account level in USD. Applicable to Multi-currency margin/Portfolio margin
        details: Detailed asset information in all currencies
        details.ccy: Currency
        details.eq: Equity of currency
        details.cashBal: Cash balance
        details.disEq: Discount equity of currency in USD. Applicable to Spot mode(enabled spot borrow)/Multi-currency margin/Portfolio margin
        details.fixedBal: Frozen balance for Dip Sniper and Peak Sniper
        details.availBal: Available balance of currency
        details.frozenBal: Frozen balance of currency
        details.ordFrozen: Margin frozen for open orders. Applicable to Spot mode/Futures mode/Multi-currency margin
        details.liab: Liabilities of currency. It is a positive value, e.g. 21625.64; Applicable to Spot mode/Multi-currency margin/Portfolio margin
        details.uplLiab: Liabilities due to Unrealized loss of currency. Applicable to Multi-currency margin/Portfolio margin
        details.crossLiab: Cross liabilities of currency. Applicable to Spot mode/Multi-currency margin/Portfolio margin
        details.rewardBal: Trial fund balance
        details.isoLiab: Isolated liabilities of currency. Applicable to Multi-currency margin/Portfolio margin
        details.interest: Accrued interest of currency. It is a positive value, e.g. 9.01; Applicable to Spot mode/Multi-currency margin/Portfolio margin
        details.twap: Risk indicator of forced repayment. Divided into multiple levels from 0 to 5, the larger the number, 
            the more likely the forced repayment will be triggered. Applicable to Spot mode/Multi-currency margin/Portfolio margin
        details.frpType: Forced repayment (FRP) type. 0: no FRP; 1: user based FRP; 2: platform based FRP; 
            Return 1/2 when twap is >= 1, applicable to Spot mode/Multi-currency margin/Portfolio margin
        details.maxLoan: Max loan of currency. Applicable to cross of Spot mode/Multi-currency margin/Portfolio margin
        details.eqUsd: Equity in USD of currency
        details.borrowFroz: Potential borrowing IMR of currency in USD. Applicable to Multi-currency margin/Portfolio margin. It is "" for other margin modes.
        details.notionalLever: Leverage of currency. Applicable to Futures mode
        details.stgyEq: Strategy equity
        details.isoUpl: Isolated unrealized profit and loss of currency. Applicable to Futures mode/Multi-currency margin/Portfolio margin
        details.spotInUseAmt: Spot in use amount. Applicable to Portfolio margin
        details.clSpotInUseAmt: User-defined spot risk offset amount. Applicable to Portfolio margin
        details.maxSpotInUse: Max possible spot risk offset amount. Applicable to Portfolio margin
        details.spotIsoBal: Spot isolated balance. Applicable to copy trading. Applicable to Spot mode/Futures mode.
        details.smtSyncEq: Smart sync equity. The default is "0", only applicable to copy trader
        details.spotCopyTradingEq: Spot smart sync equity. The default is "0", only applicable to copy trader.
        details.spotBal: Spot balance. The unit is currency, e.g. BTC
        details.openAvgPx: Spot average cost price. The unit is USD
        details.accAvgPx: Spot accumulated cost price. The unit is USD
        details.spotUpl: Spot unrealized profit and loss. The unit is USD
        details.spotUplRatio: Spot unrealized profit and loss ratio
        details.totalPnl: Spot accumulated profit and loss. The unit is USD
        details.totalPnlRatio: Spot accumulated profit and loss ratio
        details.colRes: Platform level collateral restriction status.
            0: The restriction is not enabled.
            1: The restriction is not enabled. But the crypto is close to the platform's collateral limit.
            2: The restriction is enabled. This crypto can't be used as margin for your new orders. This may result in failed orders.
            But it will still be included in the account's adjusted equity and doesn't impact margin ratio.
        details.colBorrAutoConversion: Risk indicator of auto conversion. Divided into multiple levels from 1-5, the larger the number, the more likely the repayment will be triggered. The default will be 0, indicating there is no risk currently. 5 means this user is undergoing auto conversion now, 4 means this user will undergo auto conversion soon whereas 1/2/3 indicates there is a risk for auto conversion.
            Applicable to Spot mode/Futures mode/Multi-currency margin/Portfolio margin.
            When the total liability for each crypto set as collateral exceeds a certain percentage of the platform's total limit, the auto-conversion mechanism may be triggered.
            This may result in the automatic sale of excess collateral crypto if you've set this crypto as collateral and have large borrowings.
            To lower this risk, consider reducing your use of the crypto as collateral or reducing your liabilities.
        details.collateralEnabled: true: Collateral enabled; false: Collateral disabled. Applicable to Multi-currency margin
        details.autoLendStatus: Auto lend status
            unsupported: auto lend is not supported by this currency
            off: auto lend is supported but turned off
            pending: auto lend is turned on but pending matching
            active: auto lend is turned on and matched
        details.autoLendMtAmt: Auto lend currency matched amount.
            Return "0" when autoLendStatus is unsupported/off/pending. Return matched amount when autoLendStatus is active
        """
        return resp

    @mcp.tool(
        title="Get account positions",
        description="Retrieve information on your OKX positions. When the account is in net mode, net positions will be displayed, "
                    "and when the account is in long/short mode, long or short positions will be displayed. "
                    "Return in reverse chronological order using ctime.",
    )
    def account_positions(
        instType: str = Field("", description="Instrument type: "
                                              "`SPOT`: 币币现货/"
                                              "`MARGIN`: 币币杠杆/"
                                              "`SWAP`: 永续合约/"
                                              "`FUTURES`: 交割合约/"
                                              "`OPTION`: 期权."
                                              "`instId` will be checked against `instType` when both parameters are passed. "
                                              "Optional, all by default if not passed"),
        instId: str = Field("", description="Instrument ID, e.g. `BTC-USDT-SWAP`. Single instrument ID or multiple instrument IDs (no more than 10) separated with comma. "
                                            "Optional, all by default if not passed"),
        posId: str = Field("", description="Single position ID or multiple position IDs (no more than 20) separated with comma. "
                                           "There is attribute expiration, the posId and position information will be cleared if it is more than 30 days after the last full close position. "
                                           "Optional, all by default if not passed"),
    ):
        if str(instType).upper() in ["SPOT"]:
            instType = ""
        resp = ACCOUNT.get_positions(instType, instId=instId, posId=posId) or {}
        if int(resp.get("code", 0)):
            return resp
        resp["_response_schema"] = """
        mgnMode: Margin mode
        posSide: Position side. long, pos is positive; short, pos is positive;
                 net (FUTURES/SWAP/OPTION: positive pos means long position and negative pos means short position. For MARGIN, 
                 pos is always positive, posCcy being base currency means long position, posCcy being quote currency means short position.)
        pos: Quantity of positions. In the isolated margin mode, when doing manual transfers, a position with pos of 0 will be generated after the deposit is transferred
        posCcy: Position currency, only applicable to MARGIN positions.
        availPos: Position that can be closed. Only applicable to MARGIN and OPTION. 
                  For MARGIN position, the rest of sz will be SPOT trading after the liability is repaid while closing the position. 
                  Please get the available reduce-only amount from `Get maximum available tradable amount` if you want to reduce the amount of SPOT trading as much as possible
        avgPx: Average open price. Under cross-margin mode, the entry price of expiry futures will update at settlement to the last settlement price, and when the position is opened or increased
        nonSettleAvgPx: Non-settlement entry price. The non-settlement entry price only reflects the average price at which the position is opened or increased. Applicable to cross FUTURES positions
        markPx: Latest Mark price
        upl: Unrealized profit and loss calculated by mark price
        uplRatio: Unrealized profit and loss ratio calculated by mark price
        uplLastPx: Unrealized profit and loss calculated by last price. Main usage is showing, actual value is upl
        uplRatioLastPx: Unrealized profit and loss ratio calculated by last price
        lever: Leverage. Not applicable to OPTION and positions of cross margin mode under Portfolio margin
        liqPx: Estimated liquidation price. Not applicable to OPTION
        imr: Initial margin requirement
        margin: Margin, can be added or reduced
        mgnRatio: Maintenance margin ratio
        mmr: Maintenance margin requirement
        liab: Liabilities, only applicable to MARGIN
        liabCcy: Liabilities currency
        optVal: Option Value, only applicable to OPTION
        pendingCloseOrdLiabVal: The amount of close orders of isolated margin liability
        notionalUsd: Notional value of positions in USD
        adl: Auto-deleveraging (ADL) indicator. Divided into 6 levels, from 0 to 5, the smaller the number, 
             the weaker the adl intensity. Only applicable to FUTURES/SWAP/OPTION
        ccy: Currency used for margin
        last: Latest traded price
        idxPx: Latest underlying index price
        usdPx: Latest USD price of the ccy on the market, only applicable to FUTURES/SWAP/OPTION
        bePx: Breakeven price
        deltaBS: delta: Black-Scholes Greeks in dollars, only applicable to OPTION
        deltaPA: delta: Greeks in coins, only applicable to OPTION
        gammaBS: gamma: Black-Scholes Greeks in dollars, only applicable to OPTION
        gammaPA: gamma: Greeks in coins, only applicable to OPTION
        thetaBS: theta：Black-Scholes Greeks in dollars, only applicable to OPTION
        thetaPA: theta：Greeks in coins, only applicable to OPTION
        vegaBS: vega：Black-Scholes Greeks in dollars, only applicable to OPTION
        vegaPA: vega：Greeks in coins, only applicable to OPTION
        spotInUseAmt: Spot in use amount. Applicable to Portfolio margin
        spotInUseCcy: Spot in use unit, e.g. BTC. Applicable to Portfolio margin
        clSpotInUseAmt: User-defined spot risk offset amount. Applicable to Portfolio margin
        maxSpotInUseAmt: Max possible spot risk offset amount. Applicable to Portfolio margin
        bizRefId: External business id, e.g. experience coupon id
        bizRefType: External business type
        realizedPnl: Realized profit and loss. Only applicable to FUTURES/SWAP/OPTION. 
                     realizedPnl=pnl+fee+fundingFee+liqPenalty+settledPnl
        settledPnl: Accumulated settled profit and loss (calculated by settlement price). Only applicable to cross FUTURES
        pnl: Accumulated pnl of closing order(s) (excluding the fee)
        fee: Accumulated fee. Negative number represents the user transaction fee charged by the platform.Positive number represents rebate.
        fundingFee: Accumulated funding fee
        liqPenalty: Accumulated liquidation penalty. It is negative when there is a value
        closeOrderAlgo: Close position algo orders attached to the position. 
                        This array will have values only after you request 'Place algo order' with closeFraction=1
        closeOrderAlgo.slTriggerPx: Stop-loss trigger price
        closeOrderAlgo.tpTriggerPx: Take-profit trigger price
        closeOrderAlgo.slTriggerPxType: Stop-loss trigger price type.
            last: last price
            index: index price
            mark: mark price
        closeOrderAlgo.tpTriggerPxType: Take-profit trigger price type.
            last: last price
            index: index price
            mark: mark price
        closeOrderAlgo.closeFraction: Fraction of position to be closed when the algo order is triggered
        """
        return resp

    @mcp.tool(
        title="Get account position risk",
        description="Obtain the overall holding risk of the OKX account",
    )
    def account_position_risk(
        instType: str = Field("", description="Instrument type: "
                                              "`MARGIN`: 币币杠杆/"
                                              "`SWAP`: 永续合约/"
                                              "`FUTURES`: 交割合约/"
                                              "`OPTION`: 期权. "
                                              "Optional, all by default if not passed"),
    ):
        resp = ACCOUNT.get_position_risk(instType) or {}
        if int(resp.get("code", 0)):
            return resp
        resp["_response_schema"] = """
        adjEq: Adjusted / Effective equity in USD. Applicable to Multi-currency margin and Portfolio margin
        balData: Detailed asset information in all currencies
        balData.ccy: Currency
        balData.eq: Equity of currency
        balData.disEq: Discount equity of currency in USD
        posData: Detailed position information in all currencies
        posData.mgnMode: Margin mode: cross/isolated
        posData.instId: Instrument ID, e.g. BTC-USDT-SWAP
        posData.pos: Quantity of positions contract. In the isolated margin mode, when doing manual transfers,
            a position with pos of 0 will be generated after the deposit is transferred
        posData.posSide: Position side: long/short
            net (FUTURES/SWAP/OPTION: positive pos means long position and negative pos means short position. MARGIN: posCcy being base currency means long position, posCcy being quote currency means short position.)
        posData.posCcy: Position currency, only applicable to MARGIN positions
        posData.ccy: Currency used for margin
        posData.notionalCcy: Notional value of positions in coin
        posData.notionalUsd: Notional value of positions in USD
        """
        return resp
