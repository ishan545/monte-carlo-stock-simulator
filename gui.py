import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from data_fetcher import DataFetcher
from simulator import MonteCarloSimulator


class MonteCarloGUI:
    """GUI for Monte Carlo Stock Simulator"""
    
    STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    
    def __init__(self, root):
        """Initialize GUI"""
        self.root = root
        self.root.title("Monte Carlo Stock Simulator")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        self.data_fetcher = DataFetcher(period="1y")
        self.current_simulation = None
        self.current_stock = None
        self.stock_stats = {}
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
        self.load_stock_statistics()
    
    def create_widgets(self):
        """Create GUI widgets"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Stock:").pack(side=tk.LEFT, padx=5)
        self.stock_var = tk.StringVar(value="AAPL")
        stock_combo = ttk.Combobox(control_frame, textvariable=self.stock_var, 
                                   values=self.STOCKS, state="readonly", width=10)
        stock_combo.pack(side=tk.LEFT, padx=5)
        stock_combo.bind("<<ComboboxSelected>>", self.on_stock_changed)
        
        ttk.Label(control_frame, text="Days:").pack(side=tk.LEFT, padx=5)
        self.days_var = tk.StringVar(value="252")
        days_spin = ttk.Spinbox(control_frame, from_=1, to=1000, textvariable=self.days_var, width=10)
        days_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Simulations:").pack(side=tk.LEFT, padx=5)
        self.sims_var = tk.StringVar(value="1000")
        sims_spin = ttk.Spinbox(control_frame, from_=100, to=10000, textvariable=self.sims_var, width=10)
        sims_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT, padx=20)
        
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        ttk.Label(left_panel, text="Stock Statistics", font=("Arial", 12, "bold")).pack()
        
        self.stats_frame = ttk.Frame(left_panel)
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chart_frame = ttk.Frame(content_frame)
        self.chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        ttk.Label(right_panel, text="Simulation Results", font=("Arial", 12, "bold")).pack()
        
        self.results_frame = ttk.Frame(right_panel)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_stock_statistics(self):
        """Load statistics for all stocks"""
        for stock in self.STOCKS:
            stats = self.data_fetcher.get_statistics(stock)
            if stats:
                self.stock_stats[stock] = stats
        
        self.display_stock_stats()
    
    def display_stock_stats(self):
        """Display statistics for current stock"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stock = self.stock_var.get()
        if stock not in self.stock_stats:
            ttk.Label(self.stats_frame, text="Loading...").pack()
            return
        
        stats = self.stock_stats[stock]
        
        info_text = f"""
Stock: {stats['ticker']}
Current Price: ${stats['current_price']:.2f}

Annual Metrics:
Return: {stats['annual_return']*100:.2f}%
Volatility: {stats['annual_volatility']*100:.2f}%

Historical Range:
Min: ${stats['min_price']:.2f}
Max: ${stats['max_price']:.2f}
        """
        
        ttk.Label(self.stats_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=5, pady=5)
    
    def on_stock_changed(self, event):
        """Handle stock selection change"""
        self.display_stock_stats()
        self.clear_charts()
        self.clear_results()
    
    def clear_charts(self):
        """Clear chart area"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
    
    def clear_results(self):
        """Clear results area"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def run_simulation(self):
        """Run Monte Carlo simulation"""
        try:
            stock = self.stock_var.get()
            days = int(self.days_var.get())
            num_sims = int(self.sims_var.get())
            
            if stock not in self.stock_stats:
                messagebox.showerror("Error", f"Statistics not loaded for {stock}")
                return
            
            stats = self.stock_stats[stock]
            
            simulator = MonteCarloSimulator(
                current_price=stats['current_price'],
                mean_return=stats['mean_return'],
                std_return=stats['std_return']
            )
            
            price_paths = simulator.run_simulation(days=days, num_simulations=num_sims)
            sim_stats = simulator.get_statistics(price_paths)
            ci_lower, ci_upper = simulator.get_confidence_interval(price_paths)
            
            self.current_simulation = {
                'price_paths': price_paths,
                'stats': sim_stats,
                'simulator': simulator,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper
            }
            
            self.display_charts(price_paths, sim_stats)
            self.display_results(sim_stats, ci_lower, ci_upper)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def display_charts(self, price_paths, stats):
        """Display simulation charts"""
        self.clear_charts()
        
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # Chart 1: Sample paths
        ax1 = fig.add_subplot(2, 2, 1)
        for i in range(min(100, len(price_paths))):
            ax1.plot(price_paths[i], alpha=0.1, color='blue')
        ax1.axhline(y=stats['mean_final_price'], color='red', linestyle='--', label='Mean')
        ax1.set_title('Simulated Price Paths (Sample of 100)')
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Distribution of final prices
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.hist(stats['all_final_prices'], bins=50, color='green', alpha=0.7, edgecolor='black')
        ax2.axvline(x=stats['mean_final_price'], color='red', linestyle='--', label='Mean')
        ax2.axvline(x=self.current_simulation['ci_lower'], color='orange', linestyle='--', label='95% CI')
        ax2.axvline(x=self.current_simulation['ci_upper'], color='orange', linestyle='--')
        ax2.set_title('Distribution of Final Prices')
        ax2.set_xlabel('Price ($)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Chart 3: Percentiles
        ax3 = fig.add_subplot(2, 2, 3)
        percentiles = ['5%', '25%', '50%', '75%', '95%']
        values = [
            stats['percentile_5'],
            stats['percentile_25'],
            stats['median_final_price'],
            stats['percentile_75'],
            stats['percentile_95']
        ]
        colors = ['red' if v < self.current_simulation['simulator'].current_price else 'green' for v in values]
        ax3.bar(percentiles, values, color=colors, alpha=0.7, edgecolor='black')
        ax3.axhline(y=self.current_simulation['simulator'].current_price, color='blue', linestyle='--', label='Current Price')
        ax3.set_title('Price Percentiles')
        ax3.set_ylabel('Price ($)')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Chart 4: Mean path with confidence interval
        ax4 = fig.add_subplot(2, 2, 4)
        mean_path = np.mean(price_paths, axis=0)
        std_path = np.std(price_paths, axis=0)
        days = len(mean_path)
        x = np.arange(days)
        
        ax4.plot(x, mean_path, color='blue', label='Mean Path', linewidth=2)
        ax4.fill_between(x, mean_path - std_path, mean_path + std_path, alpha=0.3, color='blue', label='±1 Std Dev')
        ax4.set_title('Mean Price Path with Confidence Band')
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Price ($)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def display_results(self, stats, ci_lower, ci_upper):
        """Display simulation results"""
        self.clear_results()
        
        results_text = f"""
SIMULATION RESULTS

Final Price Statistics:
  Mean: ${stats['mean_final_price']:.2f}
  Median: ${stats['median_final_price']:.2f}
  Std Dev: ${stats['std_final_price']:.2f}
  Min: ${stats['min_final_price']:.2f}
  Max: ${stats['max_final_price']:.2f}

Confidence Interval (95%):
  Lower: ${ci_lower:.2f}
  Upper: ${ci_upper:.2f}

Risk Metrics:
  Prob. of Profit: {stats['prob_profit']*100:.2f}%
  Expected Return: {stats['expected_return']*100:.2f}%
  Value at Risk (95%): ${stats['value_at_risk_95']:.2f}

Percentiles:
  5th: ${stats['percentile_5']:.2f}
  25th: ${stats['percentile_25']:.2f}
  75th: ${stats['percentile_75']:.2f}
  95th: ${stats['percentile_95']:.2f}
        """
        
        text_widget = tk.Text(self.results_frame, width=35, height=30, font=("Courier", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, results_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)


def main():
    """Main entry point"""
    root = tk.Tk()
    gui = MonteCarloGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
