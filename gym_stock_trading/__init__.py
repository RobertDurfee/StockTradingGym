from gym.envs.registration import register

register(
    id='stock-trading-v0',
    entry_point='gym_stock_trading.envs:StockTradingEnv'
)
