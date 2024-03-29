import gym
from gym import spaces
import numpy as np
import random

MAX_ACCOUNT_BALANCE = 2147483647
MAX_NUM_SHARES = 2147483647
MAX_SHARE_PRICE = 5000
MAX_OPEN_POSITIONS = 5
MAX_STEPS = 20000

INITIAL_ACCOUNT_BALANCE = 10000

class StockTradingEnv(gym.Env):

    metadata = { 'render.modes': [ 'human' ] }

    def __init__(self, df):

        super(StockTradingEnv, self).__init__()

        self.df = df
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)

        self.action_space = spaces.Box(low=np.array([0, 0]), high=np.array([3, 1]), dtype=np.float16)
        self.observation_space = spaces.Box(low=0, high=1, shape=(6, 6), dtype=np.float16)

    def step(self, action):

        self._take_action(action)

        self.current_step += 1

        if self.current_step > len(self.df.loc[:, 'Open'].values) - 6:
            self.current_step = 0
        
        delay_modifier = (self.current_step / MAX_STEPS)

        reward = self.balance * delay_modifier
        done = (self.net_worth <= 0)

        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self):
    
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_worth = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0

        self.current_step = random.randint(0, len(self.df.loc[:, 'Open'].values) - 6)

        return self._next_observation()

    def render(self, mode='human'):

        profit = self.net_worth - INITIAL_ACCOUNT_BALANCE

        print(f"Step: {self.current_step}")
        print(f"Balance: {self.balance}")
        print(f"Shares held: {self.shares_held} (Total sold: {self.total_shares_sold})")
        print(f"Average cost for held shares: {self.cost_basis} (Total sales value: {self.total_sales_value})")
        print(f"Net worth: {self.net_worth} (Max net worth: {self.max_net_worth})")
        print(f"Profit: {profit}")
    
    def _next_observation(self):

        frame = np.array([
            self.df.loc[self.current_step : self.current_step + 5, 'Open'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step : self.current_step + 5, 'High'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step : self.current_step + 5, 'Low'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step : self.current_step + 5, 'Close'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step : self.current_step + 5, 'Volume'].values / MAX_NUM_SHARES,
        ])

        obs = np.append(frame, [[
            self.balance / MAX_ACCOUNT_BALANCE,
            self.max_net_worth / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
            self.total_shares_sold / MAX_NUM_SHARES,
            self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE)
        ]], axis=0)

        return obs

    def _take_action(self, action):

        current_price = random.uniform(self.df.loc[self.current_step, 'Low'], 
                                       self.df.loc[self.current_step, 'High'])

        action_type = action[0]
        amount = action[1]

        if action_type < 1:

            total_possible = self.balance / current_price
            shares_bought = total_possible / current_price
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price

            self.balance -= additional_cost
            self.cost_basis = (prev_cost + additional_cost) / (self.shares_held + shares_bought)
            self.shares_held += shares_bought

        elif action_type < 2:

            shares_sold = self.shares_held * amount
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price

        self.net_worth = self.balance + self.shares_held * current_price

        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth

        if self.shares_held == 0:
            self.cost_basis = 0
