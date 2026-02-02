import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cost_model import calc_cashflow, inputs
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 年里程范围：5k ~ 40k
mileages = np.arange(5000, 40001, 2500)

oil_costs = []
ev_costs = []
cost_diff = []  # 油车成本 - 电车成本（正数表示电车更便宜）

for m in mileages:
    # 无需修改 inputs，直接传入年里程参数
    oil_cf = calc_cashflow(
        inputs['油车品牌'],
        inputs['油车新车价'],
        1, 5, False,
        override_annual_mileage=m
    )
    ev_cf = calc_cashflow(
        inputs['电车品牌'],
        inputs['电车新车价'],
        1, 5, True,
        override_annual_mileage=m
    )

    oil_total = -oil_cf['折现现金流'].sum()
    ev_total = -ev_cf['折现现金流'].sum()
    
    oil_costs.append(oil_total)
    ev_costs.append(ev_total)
    cost_diff.append(oil_total - ev_total)  # 正数 = 电车更便宜

# ===================== 创建可视化 =====================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# ===== 图1：成本对比曲线 =====
ax1.plot(mileages, oil_costs, marker='o', linewidth=2.5, markersize=8, 
         label='油车', color='#FF6B6B')
ax1.plot(mileages, ev_costs, marker='s', linewidth=2.5, markersize=8, 
         label='电车', color='#4ECDC4')

ax1.set_xlabel('年行驶里程（km）', fontsize=12, fontweight='bold')
ax1.set_ylabel('5 年总使用成本（元，NPV）', fontsize=12, fontweight='bold')
ax1.set_title('年里程对油 / 电车使用成本的影响', fontsize=13, fontweight='bold')
ax1.legend(fontsize=11, loc='upper left')
ax1.grid(True, alpha=0.3)

# 在点上标注成本值
for i, (m, oil, ev) in enumerate(zip(mileages, oil_costs, ev_costs)):
    ax1.text(m, oil - 5000, f'{int(oil/10000)}w', ha='center', fontsize=9, color='#FF6B6B')
    ax1.text(m, ev + 5000, f'{int(ev/10000)}w', ha='center', fontsize=9, color='#4ECDC4')

# ===== 图2：成本差异（电车优势） =====
colors = ['#4ECDC4' if d > 0 else '#FF6B6B' for d in cost_diff]
ax2.bar(range(len(mileages)), cost_diff, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax2.set_xticks(range(len(mileages)))
ax2.set_xticklabels([f'{m//1000}k' for m in mileages], fontsize=10)
ax2.set_xlabel('年行驶里程（km）', fontsize=12, fontweight='bold')
ax2.set_ylabel('成本差异（元）', fontsize=12, fontweight='bold')
ax2.set_title('油车成本 - 电车成本（正数 = 电车更便宜）', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 标注数值
for i, (m, diff) in enumerate(zip(mileages, cost_diff)):
    offset = 10000 if diff > 0 else -10000
    ax2.text(i, diff + offset, f'{int(diff/1000)}k', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.show()

# ===================== 打印数据汇总 =====================
print("\n========== 公里数敏感性分析结果 ==========")
print(f"分析周期：5 年（起始年=1，结束年=5）\n")

result_df = pd.DataFrame({
    '年里程(km)': mileages,
    '油车成本(元)': [int(x) for x in oil_costs],
    '电车成本(元)': [int(x) for x in ev_costs],
    '成本差(元)': [int(x) for x in cost_diff],
    '电车优势': ['电车更便宜' if d > 0 else '油车更便宜' for d in cost_diff]
})

print(result_df.to_string(index=False))

# 找出盈亏平衡点
breakeven_idx = np.argmin(np.abs(cost_diff))
print(f"\n盈亏平衡点（近似）：年里程约 {int(mileages[breakeven_idx])} km，差异为 {int(cost_diff[breakeven_idx])} 元")
print(f"里程越高，电车优势越明显（能源成本占比高）")
