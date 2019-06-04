import gym
import pandas as pd
import numpy as np

df = pd.read_csv('./data/AAPL.csv')
df = df.sort_values('Date')

# Be sure to run `pip3 install -e .` first...
env = gym.make('gym_stock_trading:stock-trading-v0', df=df)

env.reset()

# Buy with all money available...
obs, rewards, done, info = env.step(np.array([0, 1]))
print(f"obs: {obs}")
print(f"rewards: {rewards}")
print(f"done: {done}")
env.render()

# Sell everything...
obs, rewards, done, info = env.step(np.array([1, 1]))
print(f"obs: {obs}")
print(f"rewards: {rewards}")
print(f"done: {done}")
env.render()
