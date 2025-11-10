"""
H16Trader - 一个高度自由化的量化交易框架库

提供完整的量化交易回测框架，支持股票、期货等多种金融工具，
具有高度自由化的策略定制能力。

作者: Aphatar
版本: 0.1.0
"""

__version__ = '0.1.0'
__author__ = 'Aphatar'

from .core import (
    EData,
    Engine,
    Indicators,
    OrderType,
    OrderDirection,
    Trade,
    Position,
    CommissionModel,
    FixedCommissionModel,
    SlippageModel,
    FixedSlippageModel,
    Analyzer,
    PerformanceAnalyzer,
    InstrumentType
)

__all__ = [
    'EData',
    'Engine',
    'Indicators',
    'OrderType',
    'OrderDirection',
    'Trade',
    'Position',
    'CommissionModel',
    'FixedCommissionModel',
    'SlippageModel',
    'FixedSlippageModel',
    'Analyzer',
    'PerformanceAnalyzer',
    'InstrumentType'
]