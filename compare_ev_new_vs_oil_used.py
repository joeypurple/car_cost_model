import matplotlib.pyplot as plt
import numpy as np

from cost_model import calc_cashflow, inputs

hold_years = [2, 3, 4, 5, 6]
oil_start_years = range(1, 9)

results = {h: [] for h in hold_years}

for h in hold_years:
    ev_cf = calc_cashflow(
        inputs['电车品牌'],
        inputs['电车新车价'],
        1,
        h,
        True
    )
    ev_cost = -ev_cf['折现现金流'].sum()

    for sy in oil_start_years:
        oil_cf = calc_cashflow(
            inputs['油车品牌'],
            inputs['油车新车价'],
            sy,
            sy + h - 1,
            False
        )
        oil_cost = -oil_cf['折现现金流'].sum()
        results[h].append(oil_cost - ev_cost)

plt.figure(figsize=(10, 6))
for h, diff in results.items():
    plt.plot(oil_start_years, diff, marker='o', label=f'持有 {h} 年')

plt.axhline(0, linestyle='--')
plt.xlabel('油车购入年份')
plt.ylabel('油车成本 - 电车成本（元）')
plt.title('新电车 vs 不同年限油车（同持有年限）')
plt.legend()
plt.grid(True)
plt.show()
