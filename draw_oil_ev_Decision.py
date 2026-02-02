"""
油电车选择决策热力图绘制模块
需要从 cost_model.py 导入必要的数据
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 从 cost_model 导入必要的数据
from cost_model import oil_cf, ev_cf, inputs


def calc_total_cost(
    car_type: str,        # "ICE" 或 "EV"
    buy_year: int,        # 第 x 年买
    hold_years: int       # 持有 y 年
) -> float:
    """
    返回：从 buy_year 开始，持有 hold_years 年的总成本（现金流折现或不折现，按你现有逻辑）
    注意：
    - buy_year != 1 时，购车价必须是【折旧后的价格】（你已经修过这一点）
    - 不要重复计算第 0 / 第 1 年
    """
    if car_type == "ICE":
        cf_data = oil_cf
        start_year_input = inputs['油车起始年']
        end_year_input = inputs['油车结束年']
    else:  # EV
        cf_data = ev_cf
        start_year_input = inputs['电车起始年']
        end_year_input = inputs['电车结束年']
    
    # 计算在指定年份范围内的成本
    total_cost = 0
    for year in range(buy_year, buy_year + hold_years):
        if year <= len(cf_data):
            total_cost += cf_data['折现现金流'].iloc[year - 1]
    
    return abs(total_cost)


if __name__ == "__main__":
    START_YEARS = range(1, 11)   # x ∈ [1,10]
    HOLD_YEARS  = range(1, 11)   # y ∈ [1,10]

    # 结果矩阵
    # -1: 选油车
    #  0: 两者接近（差值在阈值内）
    # +1: 选电车
    choice_matrix = np.zeros((len(START_YEARS), len(HOLD_YEARS)))

    # 记录差值，方便你之后 debug / 标注
    diff_matrix = np.zeros_like(choice_matrix, dtype=float)

    THRESHOLD = 2000  # 成本差 < 2000 认为"差不多"

    for i, buy_year in enumerate(START_YEARS):
        for j, hold_year in enumerate(HOLD_YEARS):
            cost_ice = calc_total_cost(
                car_type="ICE",
                buy_year=buy_year,
                hold_years=hold_year
            )

            cost_ev = calc_total_cost(
                car_type="EV",
                buy_year=buy_year,
                hold_years=hold_year
            )

            diff = cost_ice - cost_ev
            diff_matrix[i, j] = diff

            if abs(diff) < THRESHOLD:
                choice_matrix[i, j] = 0
            elif diff > 0:
                choice_matrix[i, j] = 1   # 电车更便宜
            else:
                choice_matrix[i, j] = -1  # 油车更便宜

    # ===================== 绘制热力图 =====================
    plt.figure(figsize=(10, 8))

    im = plt.imshow(
        choice_matrix,
        origin="lower",
        aspect="auto"
    )

    plt.colorbar(
        im,
        ticks=[-1, 0, 1],
        label="决策结果"
    )

    plt.clim(-1, 1)

    plt.xticks(
        ticks=range(len(HOLD_YEARS)),
        labels=HOLD_YEARS
    )
    plt.yticks(
        ticks=range(len(START_YEARS)),
        labels=START_YEARS
    )

    plt.xlabel("持有年限 y（年）")
    plt.ylabel("购车起始年 x（第几年）")
    plt.title("起始年 × 持有年：油车 vs 电车 选择热力图")

    # 可选：在格子里标注差值（电车便宜为正）
    for i in range(len(START_YEARS)):
        for j in range(len(HOLD_YEARS)):
            plt.text(
                j, i,
                f"{int(diff_matrix[i, j])}",
                ha="center",
                va="center",
                fontsize=8
            )

    plt.tight_layout()
    plt.show()
