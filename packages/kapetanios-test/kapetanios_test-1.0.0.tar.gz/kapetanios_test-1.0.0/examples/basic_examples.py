"""
Example: Basic usage of Kapetanios unit root test
Author: Dr. Merwan Roudane
"""

import numpy as np
import matplotlib.pyplot as plt
from kapetanios_test import kapetanios_test


def example_1_random_walk_with_break():
    """
    Example 1: Test random walk with structural break
    """
    print("=" * 70)
    print("Example 1: Random Walk with Structural Break")
    print("=" * 70)
    
    # Generate data
    np.random.seed(42)
    T = 200
    y = np.cumsum(np.random.randn(T))
    y[100:] += 10  # Add level break at t=100
    
    # Run test
    result = kapetanios_test(
        y,
        max_breaks=3,
        model='A',  # Intercept breaks only
        trimming=0.15,
        lag_selection='aic'
    )
    
    print(result)
    print("\n")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(y, label='Series')
    for break_date in result.break_dates:
        plt.axvline(x=break_date, color='r', linestyle='--', 
                   label=f'Break at t={break_date}')
    plt.title('Random Walk with Structural Break')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('example1_random_walk.png', dpi=300)
    print("Plot saved as 'example1_random_walk.png'\n")


def example_2_stationary_ar_process():
    """
    Example 2: Test stationary AR(1) process with trend break
    """
    print("=" * 70)
    print("Example 2: Stationary AR(1) with Trend Break")
    print("=" * 70)
    
    # Generate AR(1) with break
    np.random.seed(123)
    T = 250
    y = np.zeros(T)
    y[0] = np.random.randn()
    
    for t in range(1, T):
        if t < 125:
            # Low trend
            y[t] = 0.5 + 0.02 * t + 0.7 * y[t-1] + np.random.randn()
        else:
            # High trend
            y[t] = 0.5 + 0.10 * t + 0.7 * y[t-1] + np.random.randn()
    
    # Run test
    result = kapetanios_test(
        y,
        max_breaks=2,
        model='B',  # Trend breaks only
        trimming=0.15
    )
    
    print(result)
    print("\n")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(y, label='Series', linewidth=1.5)
    for break_date in result.break_dates:
        plt.axvline(x=break_date, color='r', linestyle='--', 
                   label=f'Break at t={break_date}')
    plt.title('Stationary AR(1) with Trend Break')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('example2_stationary_ar.png', dpi=300)
    print("Plot saved as 'example2_stationary_ar.png'\n")


def example_3_multiple_breaks():
    """
    Example 3: Test series with multiple structural breaks
    """
    print("=" * 70)
    print("Example 3: Multiple Structural Breaks")
    print("=" * 70)
    
    # Generate series with 3 breaks
    np.random.seed(456)
    T = 400
    y = np.zeros(T)
    y[0] = 0
    
    for t in range(1, T):
        if t < 100:
            y[t] = 1.0 + 0.05 * t + 0.6 * y[t-1] + np.random.randn()
        elif t < 200:
            y[t] = 5.0 + 0.05 * t + 0.6 * y[t-1] + np.random.randn()
        elif t < 300:
            y[t] = 2.0 + 0.10 * t + 0.6 * y[t-1] + np.random.randn()
        else:
            y[t] = 8.0 + 0.05 * t + 0.6 * y[t-1] + np.random.randn()
    
    # Run test
    result = kapetanios_test(
        y,
        max_breaks=5,
        model='C',  # Both intercept and trend breaks
        trimming=0.10
    )
    
    print(result)
    print("\n")
    
    # Plot
    plt.figure(figsize=(14, 6))
    plt.plot(y, label='Series', linewidth=1.5)
    colors = ['r', 'g', 'b', 'm', 'c']
    for i, break_date in enumerate(result.break_dates):
        color = colors[i % len(colors)]
        plt.axvline(x=break_date, color=color, linestyle='--', 
                   label=f'Break {i+1} at t={break_date}')
    plt.title('Series with Multiple Structural Breaks')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('example3_multiple_breaks.png', dpi=300)
    print("Plot saved as 'example3_multiple_breaks.png'\n")


def example_4_model_comparison():
    """
    Example 4: Compare results across different models
    """
    print("=" * 70)
    print("Example 4: Model Comparison")
    print("=" * 70)
    
    # Generate data
    np.random.seed(789)
    T = 200
    y = np.cumsum(np.random.randn(T))
    y[100:] += 5
    
    # Test all three models
    models = ['A', 'B', 'C']
    results = {}
    
    print("\nComparing Models A, B, and C:\n")
    for model in models:
        result = kapetanios_test(y, max_breaks=2, model=model)
        results[model] = result
        
        print(f"Model {model} ({['Intercept', 'Trend', 'Both'][ord(model)-ord('A')]}):")
        print(f"  Statistic: {result.statistic:.4f}")
        print(f"  Breaks: {result.break_dates}")
        print(f"  Reject H0: {result.reject_null}")
        print()


def example_5_power_simulation():
    """
    Example 5: Power simulation
    """
    print("=" * 70)
    print("Example 5: Power Simulation")
    print("=" * 70)
    
    n_simulations = 100
    T = 150
    rejections = 0
    
    print(f"Running {n_simulations} simulations...")
    print("Testing stationary AR(1) with break vs. unit root null\n")
    
    for i in range(n_simulations):
        # Generate stationary AR(1) with break
        np.random.seed(i)
        y = np.zeros(T)
        y[0] = 0
        for t in range(1, T):
            if t < 75:
                y[t] = 0.5 + 0.7 * y[t-1] + np.random.randn()
            else:
                y[t] = 2.0 + 0.7 * y[t-1] + np.random.randn()
        
        result = kapetanios_test(y, max_breaks=2, model='A')
        if result.reject_null:
            rejections += 1
    
    power = rejections / n_simulations
    print(f"Rejection rate (power): {power:.2%}")
    print(f"({rejections} out of {n_simulations} simulations)\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("Kapetanios Unit Root Test - Examples")
    print("Author: Dr. Merwan Roudane")
    print("=" * 70 + "\n")
    
    # Run examples
    example_1_random_walk_with_break()
    example_2_stationary_ar_process()
    example_3_multiple_breaks()
    example_4_model_comparison()
    example_5_power_simulation()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
