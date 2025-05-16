import numpy as np

# Parameters
mu = np.array([1, 2])
cov = np.array([[3, 3], [3, 5]])
N = 1000000  # number of simulations

# Simulate bivariate normal samples
samples = np.random.multivariate_normal(mu, cov, size=N)

# Compute conditions
cond_mask = (samples[:, 0] - samples[:, 1]) < 0
numerator_mask = (samples[:, 0] + samples[:, 1]) > 0

# Estimate conditional probability
estimated_prob = np.sum(cond_mask & numerator_mask) / np.sum(cond_mask)

print(f"Estimated P(X1+X2>0 | X1-X2<0): {estimated_prob:.5f}")
