import numpy as np
from scipy import stats


class MonteCarloSimulator:
    """Monte Carlo simulation for stock price predictions"""
    
    def __init__(self, current_price, mean_return, std_return, risk_free_rate=0.02):
        """Initialize Monte Carlo Simulator"""
        self.current_price = current_price
        self.mean_return = mean_return
        self.std_return = std_return
        self.risk_free_rate = risk_free_rate
    
    def run_simulation(self, days=252, num_simulations=1000, seed=None):
        """Run Monte Carlo simulation using geometric Brownian motion"""
        if seed is not None:
            np.random.seed(seed)
        
        dt = 1
        price_paths = np.zeros((num_simulations, days + 1))
        price_paths[:, 0] = self.current_price
        
        for day in range(1, days + 1):
            random_returns = np.random.normal(self.mean_return, self.std_return, num_simulations)
            price_paths[:, day] = price_paths[:, day - 1] * (1 + random_returns)
        
        return price_paths
    
    def get_statistics(self, price_paths):
        """Calculate statistics from simulated price paths"""
        final_prices = price_paths[:, -1]
        
        stats_dict = {
            'mean_final_price': np.mean(final_prices),
            'median_final_price': np.median(final_prices),
            'std_final_price': np.std(final_prices),
            'min_final_price': np.min(final_prices),
            'max_final_price': np.max(final_prices),
            'percentile_5': np.percentile(final_prices, 5),
            'percentile_25': np.percentile(final_prices, 25),
            'percentile_75': np.percentile(final_prices, 75),
            'percentile_95': np.percentile(final_prices, 95),
            'prob_profit': np.sum(final_prices > self.current_price) / len(final_prices),
            'expected_return': (np.mean(final_prices) - self.current_price) / self.current_price,
            'value_at_risk_95': np.percentile(final_prices, 5),
            'all_final_prices': final_prices
        }
        
        return stats_dict
    
    def get_confidence_interval(self, price_paths, confidence=0.95):
        """Calculate confidence intervals for final prices"""
        final_prices = price_paths[:, -1]
        alpha = (1 - confidence) / 2
        lower = np.percentile(final_prices, alpha * 100)
        upper = np.percentile(final_prices, (1 - alpha) * 100)
        return lower, upper
