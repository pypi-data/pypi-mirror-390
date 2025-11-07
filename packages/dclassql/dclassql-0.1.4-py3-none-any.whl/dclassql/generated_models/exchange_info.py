from dataclasses import dataclass
from pathlib import Path
import random
from typing import Literal, Protocol, TypeVar, cast
import re

__datasource__ = {
    'provider': 'sqlite', 
    'url': 'sqlite:///data/exchange_info.db',
}

def try_parse_float(s: str) -> float | int | str | None:
    # print('try_parse_float', s, type(s))
    if isinstance(s, float | int):
        return s

    if isinstance(s, str):
        if re.match(r'^\d+\.\d+$', s):
            return float(s)
        elif re.match(r'^\d+$', s):
            return int(s)

    return s

# def find_latest_exchange_records(table: HasQuery[T]) -> dict[str, T]:
#     sql_query = f"""
#         SELECT r.*
#         FROM {table} r
#         JOIN (
#             SELECT symbol, MAX(run_id) AS max_run_id
#             FROM {table}
#             GROUP BY symbol
#         ) latest
#         ON r.symbol = latest.symbol AND r.run_id = latest.max_run_id
#         JOIN run
#         ON r.run_id = run.id;
#     """

#     return {
#         r.symbol: r
#         for r in table.q(sql_query)
#     }



@dataclass
class FuturesExchangeRecord:
    '''
        {'symbol': 'BTCUSDT',
        'pair': 'BTCUSDT',
        'contractType': 'PERPETUAL',
        'deliveryDate': 4133404800000,
        'onboardDate': 1569398400000,
        'status': 'TRADING',
        'maintMarginPercent': '2.5000',
        'requiredMarginPercent': '5.0000',
        'baseAsset': 'BTC',
        'quoteAsset': 'USDT',
        'marginAsset': 'USDT',
        'pricePrecision': 2,
        'quantityPrecision': 3,
        'baseAssetPrecision': 8,
        'quotePrecision': 8,
        'underlyingType': 'COIN',
        'underlyingSubType': ['PoW'],
        'triggerProtect': '0.0500',
        'liquidationFee': '0.012500',
        'marketTakeBound': '0.05',
        'maxMoveOrderLimit': 10000,
        }
    '''
    id: int
    run_id: int
    run: 'Run'

    symbol: str
    pair: str
    contractType: str
    deliveryDate: int
    onboardDate: int
    status: str
    maintMarginPercent: float
    requiredMarginPercent: float
    baseAsset: str
    quoteAsset: str
    marginAsset: str
    pricePrecision: int
    quantityPrecision: int
    baseAssetPrecision: int
    quotePrecision: int
    underlyingType: str
    underlyingSubType: str | None
    '''虽然币安返回的是列表, 但是实际上只有最多一个元素. '''
    triggerProtect: float
    liquidationFee: float
    marketTakeBound: float
    maxMoveOrderLimit: int

    #    [{'filterType': 'PRICE_FILTER',
    #    'maxPrice': '4529764',
    #    'minPrice': '556.80',
    #    'tickSize': '0.10'},
    #   {'filterType': 'LOT_SIZE',
    #    'minQty': '0.001',
    #    'maxQty': '1000',
    #    'stepSize': '0.001'},
    #   {'stepSize': '0.001',
    #    'maxQty': '120',
    #    'filterType': 'MARKET_LOT_SIZE',
    #    'minQty': '0.001'},
    #   {'filterType': 'MAX_NUM_ORDERS', 'limit': 200},
    #   {'filterType': 'MAX_NUM_ALGO_ORDERS', 'limit': 10},
    #   {'filterType': 'MIN_NOTIONAL', 'notional': '100'},
    #   {'multiplierDecimal': '4',
    #    'multiplierUp': '1.0500',
    #    'multiplierDown': '0.9500',
    #    'filterType': 'PERCENT_PRICE'}]

    PRICE_FILTER_maxPrice: float
    PRICE_FILTER_minPrice: float
    PRICE_FILTER_tickSize: float

    LOT_SIZE_minQty: float
    LOT_SIZE_maxQty: float
    LOT_SIZE_stepSize: float

    MARKET_LOT_SIZE_minQty: float
    MARKET_LOT_SIZE_maxQty: float
    MARKET_LOT_SIZE_stepSize: float

    MAX_NUM_ORDERS_limit: int
    MAX_NUM_ALGO_ORDERS_limit: int
    MIN_NOTIONAL_notional: float
    PERCENT_PRICE_multiplierDecimal: float
    PERCENT_PRICE_multiplierUp: float
    PERCENT_PRICE_multiplierDown: float


    @classmethod
    def from_dict(cls, run_id: int, d: dict) -> dict:
        new_dic = {}
        d = d.copy()
        filters = d.pop('filters')
        d.pop('orderTypes')
        d.pop('timeInForce')
        if 'permissionSets' in d:
            d.pop('permissionSets')

        for filter in filters:
            filter_type = filter['filterType']
            if filter_type == 'POSITION_RISK_CONTROL':
                continue

            for k, v in filter.items():
                if k == 'filterType':
                    continue
                new_dic[f'{filter_type}_{k}'] = try_parse_float(v)

        new_dic.update(d)
        new_dic['underlyingSubType'] = new_dic['underlyingSubType'][0] if new_dic['underlyingSubType'] else None

        for k, v in new_dic.items():
            new_dic[k] = try_parse_float(v)
        new_dic['run_id'] = run_id
        # print(new_dic)
        return new_dic

    def index(self):
        yield self.symbol
    def foreign_key(self):
        yield self.run_id == self.run.id, Run.futures

@dataclass
class SpotExchangeRecord:
    '''
    {'symbol': 'ETHBTC',
    'status': 'TRADING',
    'baseAsset': 'ETH',
    'baseAssetPrecision': 8,
    'quoteAsset': 'BTC',
    'quotePrecision': 8,
    'quoteAssetPrecision': 8,
    'baseCommissionPrecision': 8,
    'quoteCommissionPrecision': 8,
    'orderTypes': ['LIMIT',
    'LIMIT_MAKER',
    'MARKET',
    'STOP_LOSS',
    'STOP_LOSS_LIMIT',
    'TAKE_PROFIT',
    'TAKE_PROFIT_LIMIT'],
    'icebergAllowed': True,
    'ocoAllowed': True,
    'otoAllowed': True,
    'quoteOrderQtyMarketAllowed': True,
    'allowTrailingStop': True,
    'cancelReplaceAllowed': True,
    'isSpotTradingAllowed': True,
    'isMarginTradingAllowed': True,

    '''
    id: int
    run_id: int
    run: 'Run'

    symbol: str
    status: str
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    quoteAssetPrecision: int
    baseCommissionPrecision: int
    quoteCommissionPrecision: int

    icebergAllowed: bool
    ocoAllowed: bool
    otoAllowed: bool
    quoteOrderQtyMarketAllowed: bool
    allowTrailingStop: bool
    cancelReplaceAllowed: bool
    isSpotTradingAllowed: bool
    isMarginTradingAllowed: bool
    pegInstructionsAllowed: bool
    '''是否允许挂钩订单, 20250920 新增'''

    #  'filters': [{'filterType': 'PRICE_FILTER',
    #    'minPrice': '0.00001000',
    #    'maxPrice': '922327.00000000',
    #    'tickSize': '0.00001000'},
    #   {'filterType': 'LOT_SIZE',
    #    'minQty': '0.00010000',
    #    'maxQty': '100000.00000000',
    #    'stepSize': '0.00010000'},
    #   {'filterType': 'ICEBERG_PARTS', 'limit': 10},
    #   {'filterType': 'MARKET_LOT_SIZE',
    #    'minQty': '0.00000000',
    #    'maxQty': '1525.22087824',
    #    'stepSize': '0.00000000'},
    #   {'filterType': 'TRAILING_DELTA',
    #    'minTrailingAboveDelta': 10,
    #    'maxTrailingAboveDelta': 2000,
    #    'minTrailingBelowDelta': 10,
    #    'maxTrailingBelowDelta': 2000},
    #   {'filterType': 'PERCENT_PRICE_BY_SIDE',
    #    'bidMultiplierUp': '5',
    #    'bidMultiplierDown': '0.2',
    #    'askMultiplierUp': '5',
    #    'askMultiplierDown': '0.2',
    #    'avgPriceMins': 5},
    #   {'filterType': 'NOTIONAL',
    #    'minNotional': '0.00010000',
    #    'applyMinToMarket': True,
    #    'maxNotional': '9000000.00000000',
    #    'applyMaxToMarket': False,
    #    'avgPriceMins': 5},
    #   {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200},
    #   {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}],

    PRICE_FILTER_minPrice: float
    PRICE_FILTER_maxPrice: float
    PRICE_FILTER_tickSize: float

    LOT_SIZE_minQty: float
    LOT_SIZE_maxQty: float
    LOT_SIZE_stepSize: float

    ICEBERG_PARTS_limit: int
    MARKET_LOT_SIZE_minQty: float | None
    MARKET_LOT_SIZE_maxQty: float | None
    MARKET_LOT_SIZE_stepSize: float | None

    TRAILING_DELTA_minTrailingAboveDelta: float
    TRAILING_DELTA_maxTrailingAboveDelta: float
    TRAILING_DELTA_minTrailingBelowDelta: float
    TRAILING_DELTA_maxTrailingBelowDelta: float

    PERCENT_PRICE_BY_SIDE_bidMultiplierUp: float
    PERCENT_PRICE_BY_SIDE_bidMultiplierDown: float
    PERCENT_PRICE_BY_SIDE_askMultiplierUp: float
    PERCENT_PRICE_BY_SIDE_askMultiplierDown: float
    PERCENT_PRICE_BY_SIDE_avgPriceMins: int

    NOTIONAL_minNotional: float
    NOTIONAL_maxNotional: float
    NOTIONAL_applyMinToMarket: bool
    NOTIONAL_applyMaxToMarket: bool
    NOTIONAL_avgPriceMins: int

    MAX_NUM_ORDERS_maxNumOrders: int
    MAX_NUM_ALGO_ORDERS_maxNumAlgoOrders: int
    MAX_NUM_ORDER_LISTS_maxNumOrderLists: int | None
    '''20250920 新增'''
    MAX_NUM_ORDER_AMENDS_maxNumOrderAmends: int | None
    '''20250920 新增'''

    MAX_POSITION_maxPosition: float | None

    amendAllowed: bool | None = None
    '''自2025年4月24日 07:00 UTC起，amendAllowed 字段将在交易所信息请求中可见，但该功能尚未启用。
    
    https://developers.binance.com/docs/zh-CN/binance-spot-api-docs#2025-04-21
    '''

    @classmethod
    def from_dict(cls, run_id: int, d: dict) -> dict:
        new_dic = {}
        d = d.copy()
        filters = d.pop('filters')
        for pop in ['orderTypes', 'permissions', 'permissionSets', 'defaultSelfTradePreventionMode', 'allowedSelfTradePreventionModes']:
            if pop in d:
                d.pop(pop)
            else:
                import warnings
                warnings.warn(f'{pop} not in {d}')

        for filter in filters:
            filter_type = filter['filterType']
            if filter_type == 'POSITION_RISK_CONTROL':
                continue

            for k, v in filter.items():
                if k == 'filterType':
                    continue
                new_dic[f'{filter_type}_{k}'] = try_parse_float(v)

        new_dic.update(d)
        new_dic['run_id'] = run_id
        # print(new_dic)
        return new_dic

    def index(self):
        yield self.symbol

    def foreign_key(self):
        yield self.run_id == self.run.id, Run.spots

@dataclass
class Run:
    id: int
    dt: str
    '''请求时间, isoformat'''

    spots: list[SpotExchangeRecord]
    futures: list[FuturesExchangeRecord]
