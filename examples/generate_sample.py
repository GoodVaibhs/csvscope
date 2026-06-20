"""Generate a realistic but synthetic sample CSV to demo csvscope."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 500

df = pd.DataFrame(
    {
        "customer_id": range(1, n + 1),
        "age": rng.normal(40, 12, n).clip(18, 90).round().astype(int),
        "city": rng.choice(["New York", "San Francisco", "Austin", "Chicago", "Seattle"], n),
        "plan": rng.choice(["free", "pro", "enterprise"], n, p=[0.6, 0.3, 0.1]),
        "monthly_spend": rng.gamma(2.0, 30, n).round(2),
        "signup_channel": rng.choice(["organic", "ads", "referral", None], n, p=[0.4, 0.3, 0.2, 0.1]),
        "is_active": rng.choice([True, False], n, p=[0.7, 0.3]),
    }
)
# Inject a few outliers and duplicates to make the quality report interesting.
df.loc[rng.choice(n, 5, replace=False), "monthly_spend"] = rng.uniform(5000, 9000, 5)
df = pd.concat([df, df.iloc[:8]], ignore_index=True)

if __name__ == "__main__":
    df.to_csv("examples/customers.csv", index=False)
    print(f"Wrote examples/customers.csv ({len(df)} rows)")
