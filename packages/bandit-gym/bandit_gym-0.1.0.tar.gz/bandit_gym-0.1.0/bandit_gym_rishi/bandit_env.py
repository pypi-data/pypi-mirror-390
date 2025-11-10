import gym
from gym import spaces
import numpy as np

class MultiArmedBanditEnv(gym.Env):
    """
    A simple Gym-style Multi-Armed Bandit environment.

    The agent selects one of N arms, and receives a stochastic reward
    drawn from a fixed Gaussian distribution per arm.

    Observation: None (stateless)
    Action: Discrete(N)
    Reward: float
    Done: Always False (continuous task)
    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, n_arms=5, mean_range=(0, 1), std=1.0, seed=None):
        super(MultiArmedBanditEnv, self).__init__()

        self.n_arms = n_arms
        self.mean_range = mean_range
        self.std = std
        self.seed(seed)

        # Action space = choose arm
        self.action_space = spaces.Discrete(self.n_arms)
        # Observation space = empty vector (stateless)
        self.observation_space = spaces.Discrete(1)

        self._generate_bandits()
        self.last_action = None
        self.last_reward = None

    def _generate_bandits(self):
        self.means = np.random.uniform(self.mean_range[0], self.mean_range[1], self.n_arms)

    def seed(self, seed=None):
        np.random.seed(seed)

    def reset(self, *, seed=None, options=None):
        """Resets the environment (no state)."""
        super().reset(seed=seed)
        self.last_action = None
        self.last_reward = None
        return 0, {}

    def step(self, action):
        """Pull the selected arm and return reward."""
        assert self.action_space.contains(action), "Invalid arm index."
        reward = np.random.normal(self.means[action], self.std)
        self.last_action = action
        self.last_reward = reward
        done = False  # Bandit is stateless
        info = {"means": self.means}
        return 0, reward, done, info

    def render(self, mode="human"):
        if self.last_action is not None:
            print(f"Pulled arm {self.last_action}, got reward {self.last_reward:.3f}")

    def close(self):
        pass
