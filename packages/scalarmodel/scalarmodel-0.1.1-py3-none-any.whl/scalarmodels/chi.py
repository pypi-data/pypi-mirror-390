import numpy as np
from scipy.stats import chi2_contingency, chi2
import matplotlib.pyplot as plt

def chi():
    np.random.seed(42) 

    observed = np.random.poisson(lam=20, size=(4, 20))


    row_sums = np.sum(observed, axis=1)
    col_sums = np.sum(observed, axis=0)
    total_sum = np.sum(observed)

    expected = np.outer(row_sums, col_sums) / total_sum
    chi_square_stat = np.sum((observed - expected) ** 2 / expected)
    dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)

    chi2_stat, p_val, dof_scipy, expected_scipy = chi2_contingency(observed)

    alpha = 0.05

    if p_val <= alpha:
        hypothesis_result = "Reject the null hypothesis."
    else:
        hypothesis_result = "Fail to reject the null hypothesis"

    # Print results
    print("\nResults from scipy.stats.chi2_contingency:")
    print(f"Chi-Square Statistic (scipy): {chi2_stat}")
    print(f"\nDecision based on alpha = {alpha}:")
    print(hypothesis_result)


    x = np.linspace(0, chi2.ppf(0.999, dof), 1000)  # 0 to 99.9 percentile chi2

    y = chi2.pdf(x, dof)

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, label=f'Chi-square distribution df={dof}', color='blue')

    plt.axvline(chi_square_stat, color='red', linestyle='--', label=f'Observed chi-square = {chi_square_stat:.2f}')

    critical_value = chi2.ppf(1 - alpha, dof)
    plt.axvspan(critical_value, max(x), color='orange', alpha=0.3, label=f'Critical region (alpha={alpha})')

    plt.title('Chi-square Distribution with Observed Statistic')
    plt.xlabel('Chi-square value')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)
    plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

def ks():
    observed = [8, 12, 10, 88, 7, 18]
    expected = [10] * 6

    statistic, p_value = ks_2samp(observed, expected)

    print("KS statistic:", statistic)
    print("p-value:", p_value)
    if p_value < 0.05:
        print("The distributions are significantly different.")
    else:
        print("The distributions are not significantly different.")


    def ecdf(data):
        """Compute x,y values for an empirical CDF"""
        x = np.sort(data)
        y = np.arange(1, len(data) + 1) / len(data)
        return x, y

    x_obs, y_obs = ecdf(observed)
    x_exp, y_exp = ecdf(expected)

    plt.step(x_obs, y_obs, label='Observed', where='post')
    plt.step(x_exp, y_exp, label='Expected', where='post')

    # Highlight the KS statistic (max vertical distance)
    # Find x locations where ECDF difference is maximum
    all_points = np.sort(np.concatenate([x_obs, x_exp]))
    cdf_obs_at_points = np.searchsorted(x_obs, all_points, side='right') / len(observed)
    cdf_exp_at_points = np.searchsorted(x_exp, all_points, side='right') / len(expected)
    diffs = np.abs(cdf_obs_at_points - cdf_exp_at_points)
    max_diff_index = np.argmax(diffs)
    x_diff = all_points[max_diff_index]
    y_obs_diff = cdf_obs_at_points[max_diff_index]
    y_exp_diff = cdf_exp_at_points[max_diff_index]

    plt.vlines(x_diff, y_exp_diff, y_obs_diff, colors='red', linestyles='dashed',
               label=f'KS Statistic = {statistic:.2f}')

    plt.xlabel('Value')
    plt.ylabel('ECDF')
    plt.title('Empirical CDFs of Observed and Expected Samples')
    plt.legend()
    plt.grid(True)
    plt.show()


from scipy.stats import shapiro

def sha():
    observed = [8, 12,10,88,7,18]
    expected =[10]*6
    
    stat1, p1 = shapiro(observed)
    print("observed - Shapiro-Wilk statistic:", stat1, "p-value:", p1)
    
    stat2, p2 = shapiro(expected)
    print("expected - Shapiro-Wilk statistic:", stat2, "p-value:", p2)
