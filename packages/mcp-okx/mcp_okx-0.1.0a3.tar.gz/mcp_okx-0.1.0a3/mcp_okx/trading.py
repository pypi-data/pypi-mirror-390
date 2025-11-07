from fastmcp import FastMCP
from pydantic import Field
from typing import Any
from okx.Trade import TradeAPI

from .config import *

ACCOUNT = TradeAPI(
    api_key=OKX_API_KEY,
    api_secret_key=OKX_API_SECRET,
    passphrase=OKX_PASSPHRASE,
    flag=OKX_TRADE_FLAG,
    domain=OKX_BASE_URL,
)


def add_tools(mcp: FastMCP):

    @mcp.tool(
        title="Place a new order",
        description="Place a new order on OKX for trading",
    )
    def place_order(
        instId: str = Field(description="Instrument ID, e.g. BTC-USDT"),
        tdMode: str = Field(description="Trade Mode, when placing an order, you need to specify the trade mode."
                                        "\nSpot mode: `cash`(SPOT and OPTION buyer; 币币和期权买方)"
                                        "\nFutures mode:"
                                        "\n- `cash`(SPOT; 币币)"
                                        "\n- `cross`(Cross MARGIN/FUTURES/SWAP/OPTION; 全仓杠杆/交割/永续/期权)"
                                        "\n- `isolated`(Isolated MARGIN/FUTURES/SWAP/OPTION; 逐仓杠杆/交割/永续/期权)"
                                        "\nMulti-currency margin mode: `cross`(Cross SPOT/FUTURES/SWAP/OPTION; 全仓币币/交割/永续/期权)"
                                        "\nPortfolio margin: `cross`(Cross SPOT/FUTURES/SWAP/OPTION; 全仓币币/交割/永续/期权)"
        ),
        side: str = Field(description="Order side, `buy`/`sell`"),
        ordType: str = Field(description="Order type. When creating a new order, you must specify the order type. "
                                         "The order type you specify will affect: 1) what order parameters are required, and 2) how the matching system executes your order."
                                         "\nThe following are valid order types:"
                                         "\n`limit`: Limit order, which requires specified sz and px."
                                         "\n`market`: Market order. For SPOT and MARGIN, market order will be filled with market price (by swiping opposite order book). For Expiry Futures and Perpetual Futures, market order will be placed to order book with most aggressive price allowed by Price Limit Mechanism. For OPTION, market order is not supported yet. As the filled price for market orders cannot be determined in advance, OKX reserves/freezes your quote currency by an additional 5% for risk check."
                                         "\n`post_only`: Post-only order, which the order can only provide liquidity to the market and be a maker. If the order would have executed on placement, it will be canceled instead."
                                         "\n`fok`: Fill or kill order. If the order cannot be fully filled, the order will be canceled. The order would not be partially filled."
                                         "\n`ioc`: Immediate or cancel order. Immediately execute the transaction at the order price, cancel the remaining unfilled quantity of the order, and the order quantity will not be displayed in the order book."
                                         "\n`optimal_limit_ioc`: Market order with ioc (immediate or cancel). Immediately execute the transaction of this market order, cancel the remaining unfilled quantity of the order, and the order quantity will not be displayed in the order book. Only applicable to Expiry Futures and Perpetual Futures."),
        sz: str = Field(description="Quantity to buy or sell."
                                    "\nFor SPOT/MARGIN Buy and Sell Limit Orders, it refers to the quantity in base currency."
                                    "\nFor MARGIN Buy Market Orders, it refers to the quantity in quote currency."
                                    "\nFor MARGIN Sell Market Orders, it refers to the quantity in base currency."
                                    "\nFor SPOT Market Orders, it is set by tgtCcy."
                                    "\nFor FUTURES/SWAP/OPTION orders, it refers to the number of contracts."
        ),
        ccy: str = Field("", description="Margin currency. Applicable to all `isolated` `MARGIN` orders and `cross` `MARGIN` orders in `Futures mode`"),
        clOrdId: str = Field("", description="Client Order ID as assigned by the client."
                                             "A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters."
                                             "Only applicable to general order. It will not be posted to algoId when placing TP/SL order after the general order is filled completely."),
        tag: str = Field("", description="Order tag. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters"),
        posSide: str = Field("", description="Position side. The default is `net` in the net mode. "
                                             "It is required in the `long/short` mode, and can only be `long` or `short`. "
                                             "Only applicable to `FUTURES`/`SWAP`."
                                             "\nPosition side, this parameter is not mandatory in net mode. If you pass it through, the only valid value is net."
                                             "\nIn long/short mode, it is mandatory. Valid values are long or short."
                                             "\nIn long/short mode, side and posSide need to be specified in the combinations below:"
                                             "\nOpen long: buy and open long (side: fill in buy; posSide: fill in long)"
                                             "\nOpen short: sell and open short (side: fill in sell; posSide: fill in short)"
                                             "\nClose long: sell and close long (side: fill in sell; posSide: fill in long)"
                                             "\nClose short: buy and close short (side: fill in buy; posSide: fill in short)"
                                             "\nPortfolio margin mode: Expiry Futures and Perpetual Futures only support net mode"
        ),
        px: str = Field("", description="Order price. Only applicable to `limit`,`post_only`,`fok`,`ioc`,`mmp`,`mmp_and_post_only` order. "
                                        "When placing an option order, one of px/pxUsd/pxVol must be filled in, and only one can be filled in."
                                        "\nThe value for px must be a multiple of tickSz for OPTION orders."
                                        "\nIf not, the system will apply the rounding rules below. Using tickSz 0.0005 as an example:"
                                        "\nThe px will be rounded up to the nearest 0.0005 when the remainder of px to 0.0005 is more than 0.00025 or `px` is less than 0.0005."
                                        "\nThe px will be rounded down to the nearest 0.0005 when the remainder of px to 0.0005 is less than 0.00025 and `px` is more than 0.0005."
        ),
        tgtCcy: str = Field("", description="Whether the target currency uses the quote or base currency. "
                                            "\nThis parameter is used to specify the order quantity in the order request is denominated in the quantity of base or quote currency. This is applicable to SPOT Market Orders only."
                                            "\nBase currency: `base_ccy`; Quote currency: `quote_ccy`"
                                            "\nIf you use the Base Currency quantity for buy market orders or the Quote Currency for sell market orders, please note:"
                                            "\n1. If the quantity you enter is greater than what you can buy or sell, the system will execute the order according to your maximum buyable or sellable quantity. "
                                            "If you want to trade according to the specified quantity, you should use Limit orders."
                                            "\n2. When the market price is too volatile, the locked balance may not be sufficient to buy the Base Currency quantity or sell to receive the Quote Currency that you specified. "
                                            "We will change the quantity of the order to execute the order based on best effort principle based on your account balance. "
                                            "In addition, we will try to over lock a fraction of your balance to avoid changing the order quantity."
                                            "\n2.1 Example of base currency buy market order: "
                                            "Taking the market order to buy 10 LTCs as an example, and the user can buy 11 LTC. At this time, if 10 < 11, the order is accepted. "
                                            "When the LTC-USDT market price is 200, and the locked balance of the user is 3,000 USDT, as 200*10 < 3,000, the market order of 10 LTC is fully executed; "
                                            "If the market is too volatile and the LTC-USDT market price becomes 400, 400*10 > 3,000, "
                                            "the user's locked balance is not sufficient to buy using the specified amount of base currency, the user's maximum locked balance of 3,000 USDT will be used to settle the trade. "
                                            "Final transaction quantity becomes 3,000/400 = 7.5 LTC."
                                            "\n2.2 Example of quote currency sell market order: "
                                            "Taking the market order to sell 1,000 USDT as an example, and the user can sell 1,200 USDT, 1,000 < 1,200, the order is accepted. "
                                            "When the LTC-USDT market price is 200, and the locked balance of the user is 6 LTC, as 1,000/200 < 6, the market order of 1,000 USDT is fully executed; "
                                            "If the market is too volatile and the LTC-USDT market price becomes 100, 100*6 < 1,000, "
                                            "the user's locked balance is not sufficient to sell using the specified amount of quote currency, the user's maximum locked balance of 6 LTC will be used to settle the trade. "
                                            "Final transaction quantity becomes 6 * 100 = 600 USDT."
        ),
        reduceOnly: str | bool = Field("", description="Whether orders can only reduce in position size. "
                                                       "Valid options: `true` or `false`. The default value is `false`. "
                                                       "Only applicable to `MARGIN` orders, and `FUTURES`/`SWAP` orders in net mode. "
                                                       "Only applicable to `Futures mode` and `Multi-currency margin`."),
        stpMode: str = Field("", description="Self trade prevention mode: `cancel_maker`,`cancel_taker`,`cancel_both`. Cancel both does not support FOK. "
                                             "The account-level acctStpMode will be used to place orders by default. The default value of this field is `cancel_maker`. "
                                             "Users can log in to the webpage through the master account to modify this configuration. "
                                             "Users can also utilize the stpMode request parameter of the placing order endpoint to determine the stpMode of a certain order."),
        pxUsd: str = Field("", description="Place options orders in `USD`. Only applicable to options. "
                                           "When placing an option order, one of px/pxUsd/pxVol must be filled in, and only one can be filled in"),
        pxVol: str = Field("", description="Place options orders based on implied volatility, where 1 represents 100%. Only applicable to options. "
                                           "When placing an option order, one of px/pxUsd/pxVol must be filled in, and only one can be filled in"),
        banAmend: str | bool = Field("", description="Whether to disallow the system from amending the size of the SPOT Market Order. "
                                                     "Valid options: `true` or `false`. The default value is `false`. "
                                                     "If `true`, system will not amend and reject the market order if user does not have sufficient funds. "
                                                     "Only applicable to SPOT Market Orders"),
        attachAlgoOrds: list | None = Field(None, description="TP/SL information attached when placing order."
                                                              "1. TP/SL algo order will be generated only when this order is filled fully, or there is no TP/SL algo order generated."
                                                              "2. Attaching TP/SL is neither supported for market buy with `tgtCcy` is `base_ccy` or market sell with `tgtCcy` is `quote_ccy`"
                                                              "3. If `tpOrdKind` is `limit`, and there is only one conditional TP order, `attachAlgoClOrdId` can be used as `clOrdId` for retrieving on `get_trade_order` tool."
                                                              "4. For 'split TPs', including condition TP order and limit TP order."
                                                              "* TP/SL orders in Split TPs only support one-way TP/SL. You can't use slTriggerPx&slOrdPx and tpTriggerPx&tpOrdPx at the same time, or error code 51076 will be thrown."
                                                              "* Take-profit trigger price types (tpTriggerPxType) must be the same in an order with Split TPs attached, or error code 51080 will be thrown."
                                                              "* Take-profit trigger prices (tpTriggerPx) cannot be the same in an order with Split TPs attached, or error code 51081 will be thrown."
                                                              "* The size of the TP order among split TPs attached cannot be empty, or error code 51089 will be thrown."
                                                              "* The total size of TP orders with Split TPs attached in a same order should equal the size of this order, or error code 51083 will be thrown."
                                                              "* The number of TP orders with Split TPs attached in a same order cannot exceed 10, or error code 51079 will be thrown."
                                                              "* Setting multiple TP and cost-price SL orders isn’t supported for spot and margin trading, or error code 51077 will be thrown."
                                                              "* The number of SL orders with Split TPs attached in a same order cannot exceed 1, or error code 51084 will be thrown."
                                                              "* The number of TP orders cannot be less than 2 when cost-price SL is enabled (amendPxOnTriggerType set as 1) for Split TPs, or error code 51085 will be thrown."
                                                              "* All TP orders in one order must be of the same type, or error code 51091 will be thrown."
                                                              "* TP order prices (tpOrdPx) in one order must be different, or error code 51092 will be thrown."
                                                              "* TP limit order prices (tpOrdPx) in one order can't be –1 (market price), or error code 51093 will be thrown."
                                                              "* You can't place TP limit orders in spot, margin, or options trading. Otherwise, error code 51094 will be thrown."
        ),
    ):
        params = {
            'instId': instId, 'tdMode': tdMode, 'side': side, 'ordType': ordType, 'sz': sz, 'ccy': ccy,
            'clOrdId': clOrdId, 'tag': tag, 'posSide': posSide, 'px': px, 'reduceOnly': reduceOnly,
            'tgtCcy': tgtCcy, 'stpMode': stpMode, 'pxUsd': pxUsd, 'pxVol': pxVol, 'banAmend': banAmend,
        }
        if isinstance(reduceOnly, bool):
            params['reduceOnly'] = 'true' if reduceOnly else 'false'
        if isinstance(banAmend, bool):
            params['banAmend'] = 'true' if banAmend else 'false'
        if attachAlgoOrds:
            params['attachAlgoOrds'] = attachAlgoOrds
        return ACCOUNT.place_order(**params)

    @mcp.tool(
        title="Cancel an incomplete order",
        description="Cancel an incomplete order on OKX",
    )
    def cancel_order(
        instId: str = Field(description="Instrument ID, e.g. BTC-USDT"),
        ordId: str = Field("", description="Order ID. Either ordId or clOrdId is required. If both are passed, ordId will be used"),
        clOrdId: str = Field("", description="Client Order ID as assigned by the client"),
    ):
        return ACCOUNT.cancel_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    @mcp.tool(
        title="Get order details",
        description="Retrieve order details on OKX. "
                    "For a detailed schema of the output object, please read the resource at: `schema://trade/order`",
    )
    def get_trade_order(
        instId: str = Field(description="Instrument ID, e.g. BTC-USDT"),
        ordId: str = Field("", description="Order ID. Either ordId or clOrdId is required. If both are passed, ordId will be used"),
        clOrdId: str = Field("", description="Client Order ID as assigned by the client"),
    ):
        return ACCOUNT.get_order(instId=instId, ordId=ordId, clOrdId=clOrdId)

    @mcp.tool(
        title="Get incomplete order list",
        description="Retrieve all incomplete orders under the current OKX account. "
                    "For a detailed schema of the output object, please read the resource at: `schema://trade/order`",
    )
    def get_order_list(
        instType: str = Field("", description="Instrument type: `SPOT/MARGIN/SWAP/FUTURES/OPTION`"),
        instFamily: str = Field("", description="Instrument family. Applicable to `FUTURES/SWAP/OPTION`"),
        instId: str = Field("", description="Instrument ID, e.g. BTC-USD-200927"),
        state: str = Field("", description="State: `live`/`partially_filled`"),
        ordType: str = Field("", description="Order type. "
                                             "\n`market`: Market order"
                                             "\n`limit`: Limit order"
                                             "\n`post_only`: Post-only order"
                                             "\n`fok`: Fill-or-kill order"
                                             "\n`ioc`: Immediate-or-cancel order"
                                             "\n`optimal_limit_ioc`: Market order with immediate-or-cancel order"
                                             "\n`mmp`: Market Maker Protection (only applicable to Option in Portfolio Margin mode)"
                                             "\n`mmp_and_post_only`: Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode)"
                                             "\n`op_fok`: Simple options (fok)"),
    ):
        return ACCOUNT.get_order_list(
            instType=instType,
            instFamily=instFamily,
            instId=instId,
            state=state,
            ordType=ordType,
            limit=100,
        )

    @mcp.tool(
        title="Get Order History",
        description="Get completed orders on OKX which are placed in the last 7 days, including those placed 7 days ago but completed in the last 7 days."
                    "The incomplete orders that have been canceled are only reserved for 2 hours. "
                    "For a detailed schema of the output object, please read the resource at: `schema://trade/order`",
    )
    def get_orders_history(
        instType: str = Field(description="Instrument type: `SPOT/MARGIN/SWAP/FUTURES/OPTION`"),
        instFamily: str = Field("", description="Instrument family. Applicable to `FUTURES/SWAP/OPTION`"),
        instId: str = Field("", description="Instrument ID, e.g. BTC-USDT"),
        state: str = Field("", description="State: `canceled`/`filled`/`mmp_canceled`: Order canceled automatically due to Market Maker Protection"),
        category: str = Field("", description="Category: `twap/adl/full_liquidation/partial_liquidation/delivery`/`ddh`: Delta dynamic hedge"),
        ordType: str = Field("", description="Order type. "
                                             "\n`market`: Market order"
                                             "\n`limit`: Limit order"
                                             "\n`post_only`: Post-only order"
                                             "\n`fok`: Fill-or-kill order"
                                             "\n`ioc`: Immediate-or-cancel order"
                                             "\n`optimal_limit_ioc`: Market order with immediate-or-cancel order"
                                             "\n`mmp`: Market Maker Protection (only applicable to Option in Portfolio Margin mode)"
                                             "\n`mmp_and_post_only`: Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode)"
                                             "\n`op_fok`: Simple options (fok)"),
        limit: str | int = Field(20, description="Number of results per request. [1-100]. Default: 20"),
    ):
        return ACCOUNT.get_orders_history(
            instType=instType,
            instFamily=instFamily,
            instId=instId,
            state=state,
            ordType=ordType,
            limit=str(limit),
        )

    @mcp.tool(
        title="Close positions",
        description="Liquidate all positions in the designated trading product at market price on OKX",
    )
    def close_positions(
        instId: str = Field(description="Instrument ID, e.g. BTC-USDT"),
        mgnMode: str = Field(description="Margin mode: `cross`/`isolated`"),
        posSide: str = Field("", description="Position side. "
                                             "This parameter can be omitted in `net` mode, and the default value is `net`. You can only fill with `net`. "
                                             "This parameter must be filled in under the `long/short` mode. Fill in `long` for close-long and `short` for close-short."),
        ccy: str = Field("", description="Margin currency, required in the case of closing `cross` `MARGIN` position for `Futures mode`"),
        autoCxl: Any = Field("", description="Whether any pending orders for closing out needs to be automatically canceled when close position via a market order."
                                             "`false` or `true`, the default is `false`"),
        clOrdId: str = Field("", description="Client-supplied ID. A combination of case-sensitive alphanumerics, "
                                             "all numbers, or all letters of up to 32 characters."),
        tag: str = Field("", description="Order tag. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters"),
    ):
        return ACCOUNT.close_positions(
            instId=instId,
            mgnMode=mgnMode,
            posSide=posSide,
            ccy=ccy,
            autoCxl=autoCxl in [True, "true", "yes", 1],
            clOrdId=clOrdId,
            tag=tag,
        )


    @mcp.resource(
        uri="schema://trade/order",
        description="This resource is used to describe the schema of the trade order on OKX",
    )
    def schema_trade_order():
        return """
        instType	String	Instrument type `MARGIN/SWAP/FUTURES/OPTION`
        instId	String	Instrument ID
        tgtCcy	String	Order quantity unit setting for sz
            base_ccy: Base currency ,quote_ccy: Quote currency
            Only applicable to SPOT Market Orders
            Default is quote_ccy for buy, base_ccy for sell
        ccy	String	Margin currency
            Applicable to all isolated MARGIN orders and cross MARGIN orders in Futures mode, FUTURES and SWAP contracts.
        ordId	String	Order ID
        clOrdId	String	Client Order ID as assigned by the client
        tag	String	Order tag
        px	String	Price. For options, use coin as unit (e.g. BTC, ETH)
        pxUsd	String	Options price in USDOnly applicable to options; return "" for other instrument types
        pxVol	String	Implied volatility of the options orderOnly applicable to options; return "" for other instrument types
        pxType	String	Price type of options
            px: Place an order based on price, in the unit of coin (the unit for the request parameter px is BTC or ETH)
            pxVol: Place an order based on pxVol
            pxUsd: Place an order based on pxUsd, in the unit of USD (the unit for the request parameter px is USD)
        sz	String	Quantity to buy or sell
        pnl	String	Profit and loss (excluding the fee). Applicable to orders which have a trade and aim to close position. It always is 0 in other conditions
        ordType	String	Order type
            market: Market order
            limit: Limit order
            post_only: Post-only order
            fok: Fill-or-kill order
            ioc: Immediate-or-cancel order
            optimal_limit_ioc: Market order with immediate-or-cancel order
            mmp: Market Maker Protection (only applicable to Option in Portfolio Margin mode)
            mmp_and_post_only: Market Maker Protection and Post-only order(only applicable to Option in Portfolio Margin mode)
            op_fok: Simple options (fok)
        side	String	Order side
        posSide	String	Position side
        tdMode	String	Trade mode
        accFillSz	String	Accumulated fill quantity
            The unit is base_ccy for SPOT and MARGIN, e.g. BTC-USDT, the unit is BTC; For market orders, the unit both is base_ccy when the tgtCcy is base_ccy or quote_ccy;
            The unit is contract for FUTURES/SWAP/OPTION
        fillPx	String	Last filled price. If none is filled, it will return "".
        tradeId	String	Last traded ID
        fillSz	String	Last filled quantity
            The unit is base_ccy for SPOT and MARGIN, e.g. BTC-USDT, the unit is BTC; For market orders, the unit both is base_ccy when the tgtCcy is base_ccy or quote_ccy;
            The unit is contract for FUTURES/SWAP/OPTION
        fillTime	String	Last filled time
        avgPx	String	Average filled price. If none is filled, it will return "".
        state	String	State. canceled/live/partially_filled/filled/mmp_canceled
        lever	String	Leverage, from 0.01 to 125. Only applicable to MARGIN/FUTURES/SWAP
        stpMode	String	Self trade prevention mode
        attachAlgoClOrdId	String	Client-supplied Algo ID when placing order attaching TP/SL.
        tpTriggerPx	String	Take-profit trigger price.
        tpTriggerPxType	String	Take-profit trigger price type.
            last: last price
            index: index price
            mark: mark price
        tpOrdPx	String	Take-profit order price.
        slTriggerPx	String	Stop-loss trigger price.
        slTriggerPxType	String	Stop-loss trigger price type.
            last: last price
            index: index price
            mark: mark price
        slOrdPx	String	Stop-loss order price.
        attachAlgoOrds	Array of objects	TP/SL information attached when placing order
        > attachAlgoId	String	The order ID of attached TP/SL order. It can be used to identity the TP/SL order when amending. It will not be posted to algoId when placing TP/SL order after the general order is filled completely.
        > attachAlgoClOrdId	String	Client-supplied Algo ID when placing order attaching TP/SL
            A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.
            It will be posted to algoClOrdId when placing TP/SL order once the general order is filled completely.
        > tpOrdKind	String	TP order kind. condition/limit
        > tpTriggerPx	String	Take-profit trigger price.
        > tpTriggerPxType	String	Take-profit trigger price type.
            last: last price
            index: index price
            mark: mark price
        > tpOrdPx	String	Take-profit order price.
        > slTriggerPx	String	Stop-loss trigger price.
        > slTriggerPxType	String	Stop-loss trigger price type.
            last: last price
            index: index price
            mark: mark price
        > slOrdPx	String	Stop-loss order price.
        > sz	String	Size. Only applicable to TP order of split TPs
        > amendPxOnTriggerType	String	Whether to enable Cost-price SL. Only applicable to SL order of split TPs.
            0: disable, the default value
            1: Enable
        > amendPxOnTriggerType	String	Whether to enable Cost-price SL. Only applicable to SL order of split TPs.
            0: disable, the default value
            1: Enable
        > failCode	String	The error code when failing to place TP/SL order, e.g. 51020. The default is ""
        > failReason	String	The error reason when failing to place TP/SL order. The default is ""
        linkedAlgoOrd	Object	Linked SL order detail, only applicable to the order that is placed by one-cancels-the-other (OCO) order that contains the TP limit order.
        > algoId	String	Algo ID
        feeCcy	String	Fee currency
            For maker sell orders of Spot and Margin, this represents the quote currency. For all other cases, it represents the currency in which fees are charged.
        fee	String	Fee amount
            For Spot and Margin (excluding maker sell orders): accumulated fee charged by the platform, always negative
            For maker sell orders in Spot and Margin, Expiry Futures, Perpetual Futures and Options: accumulated fee and rebate (always in quote currency for maker sell orders in Spot and Margin)
        rebateCcy	String	Rebate currency
            For maker sell orders of Spot and Margin, this represents the base currency. For all other cases, it represents the currency in which rebates are paid.
        rebate	String	Rebate amount, only applicable to Spot and Margin
            For maker sell orders: Accumulated fee and rebate amount in base currency.
            For all other cases, it represents the maker rebate amount, always positive, return "" if no rebate.
        source	String	Order source
            6: The normal order triggered by the trigger order
            7: The normal order triggered by the TP/SL order
            13: The normal order triggered by the algo order
            25: The normal order triggered by the trailing stop order
            34: The normal order triggered by the chase order
        category	String	Category. normal/twap/adl/full_liquidation/partial_liquidation/delivery/ddh(Delta dynamic hedge)/auto_conversion
        reduceOnly	String	Whether the order can only reduce the position size. Valid options: true or false.
        isTpLimit	String	Whether it is TP limit order. true or false
        cancelSource	String	Code of the cancellation source.
        cancelSourceReason	String	Reason for the cancellation.
        quickMgnType	String	Quick Margin type, Only applicable to Quick Margin Mode of isolated margin. manual/auto_borrow/auto_repay
        algoClOrdId	String	Client-supplied Algo ID. There will be a value when algo order attaching algoClOrdId is triggered, or it will be "".
        algoId	String	Algo ID. There will be a value when algo order is triggered, or it will be "".
        tradeQuoteCcy	String	The quote currency used for trading.
        """
