import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ===================== 品牌库 =====================
brands = pd.DataFrame([
    ['丰田 凯美瑞', '油', 8.2, 6.4, None, None, 0.025, 2000,
     [0.92, 0.87, 0.82, 0.78, 0.74, 0.70, 0.66, 0.63, 0.60, 0.57]],
    ['特斯拉 Model 3', '电', None, None, 14, 17, 0.032, 300,
     [0.85, 0.75, 0.65, 0.58, 0.52, 0.47, 0.42, 0.38, 0.34, 0.31]],
    ['本田 雅阁', '油', 8.0, 6.2, None, None, 0.025, 2000,
     [0.91, 0.86, 0.81, 0.77, 0.73, 0.69, 0.65, 0.62, 0.59, 0.56]],

    ['大众 帕萨特', '油', 8.5, 6.6, None, None, 0.026, 2200,
     [0.90, 0.85, 0.80, 0.76, 0.72, 0.68, 0.64, 0.61, 0.58, 0.55]],

    ['比亚迪 秦PLUS DM-i', '油', 4.5, 4.0, None, None, 0.024, 1800,
     [0.85, 0.78, 0.72, 0.66, 0.62, 0.58, 0.55, 0.52, 0.49, 0.46]],

    ['丰田 RAV4', '油', 9.0, 7.0, None, None, 0.027, 2300,
     [0.91, 0.86, 0.81, 0.77, 0.73, 0.69, 0.66, 0.63, 0.60, 0.57]],

    ['比亚迪 海豹', '电', None, None, 13.5, 16.5, 0.030, 300,
     [0.82, 0.72, 0.62, 0.55, 0.49, 0.44, 0.39, 0.35, 0.32, 0.29]],

    ['小鹏 P7', '电', None, None, 14.5, 18.0, 0.033, 350,
     [0.81, 0.71, 0.61, 0.53, 0.47, 0.42, 0.37, 0.33, 0.30, 0.27]],

    ['蔚来 ET5', '电', None, None, 15.5, 19.0, 0.035, 400,
     [0.79, 0.69, 0.59, 0.51, 0.45, 0.40, 0.35, 0.31, 0.28, 0.25]],

    ['理想 L7', '电', None, None, 18.0, 21.0, 0.034, 450,
     [0.82, 0.72, 0.62, 0.55, 0.49, 0.44, 0.39, 0.35, 0.32, 0.29]],

    # 新增车型：奥迪、宝马、奔驰、极氪（数据来源于懂车帝及行业公开参数）
    ['奥迪 A4L', '油', 8.5, 6.3, None, None, 0.025, 2300,
     [0.88, 0.82, 0.77, 0.73, 0.69, 0.65, 0.61, 0.58, 0.55, 0.52]],
    ['奥迪 A4 Avant', '油', 8.8, 6.6, None, None, 0.025, 2300,
     [0.92, 0.86, 0.82, 0.78, 0.75, 0.71, 0.69, 0.67, 0.65, 0.63]],
    ['宝马 330i', '油', 8.2, 6.0, None, None, 0.025, 2400,
     [0.88, 0.82, 0.77, 0.72, 0.68, 0.64, 0.60, 0.57, 0.54, 0.51]],
    ['奔驰 C260L', '油', 9.0, 6.8, None, None, 0.026, 2400,
     [0.87, 0.80, 0.75, 0.71, 0.67, 0.63, 0.60, 0.57, 0.54, 0.51]],
    ['极氪 007 GT', '电', None, None, 17.5, 20.5, 0.033, 450,
     [0.82, 0.72, 0.62, 0.55, 0.49, 0.44, 0.39, 0.35, 0.32, 0.29]]
], columns=[
    "品牌", "动力", "城区油耗", "高速油耗",
    "城区电耗", "高速电耗",
    "首年保险率", "年保养费", "残值率"
])
brands.set_index('品牌', inplace=True)

# ===================== 输入参数 =====================
inputs = {
    '油车品牌': '丰田 凯美瑞',
    '电车品牌': '特斯拉 Model 3',

    '油价': 6.5,
    '家充电价': 0.7,
    '公共充电价': 1.5,
    '家充比例': 0,

    '工作日通勤天数': 5,
    '工作日单日里程': 60,
    '周末单日里程': 100,

    '工作日高速比例': 0.5,
    '周末高速比例': 0.5,

    '电车膨胀系数': 1.2,
    '电车膨胀开关': 1,

    '油车新车价': 200000,
    '电车新车价': 240000,

    '油车起始年': 4,
    '油车结束年': 8,
    '电车起始年': 4,
    '电车结束年': 8,

    '过路费单价': 0.33,      # 元 / km
    '停车费': 6000,            # 元 / 年
    '上海油牌通胀': 2500,      # 元 / 年
    '罚款': 400,               # 元 / 年

    '折现率': 0.06
}

YEARS = 10


def get_residual_rate(brand_info, age_years, is_ev, annual_mileage):
    """返回残值率：电车按年份，油车按每万公里数修正。"""
    if age_years <= 0:
        return 1.0

    rates = brand_info['残值率']
    if is_ev:
        idx = min(age_years, len(rates) - 1)
    else:
        mileage_units = int(age_years * annual_mileage / 10000)
        idx = min(mileage_units, len(rates) - 1)
    return rates[idx]


def get_a4avant_market_price(mileage):
    """按里程插值得到 A4 Avant 的实际二手成交价。"""
    points = [
        (40000, 170000),
        (46000, 168000),
        (50000, 150000),
        (60000, 138000),
        (73000, 134000)
    ]
    if mileage <= points[0][0]:
        return points[0][1]
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if mileage <= x1:
            return y0 + (y1 - y0) * (mileage - x0) / (x1 - x0)
    x0, y0 = points[-2]
    x1, y1 = points[-1]
    slope = (y1 - y0) / (x1 - x0)
    return y1 + slope * (mileage - x1)

# ===================== 现金流计算函数 =====================
def calc_cashflow(brand, new_price, start_year, end_year, is_ev, override_annual_mileage=None, oil_purchase_mileage=None):
    """
    计算现金流
    override_annual_mileage: 如果提供，将覆盖默认的年里程（用于敏感性分析）
    oil_purchase_mileage: 油车购入时的里程数（公里），用于估算购入价及后续折旧价
    """
    brand_info = brands.loc[brand]
    brand_info = brands.loc[brand]

    # ===== 每次调用时根据当前 inputs 重新计算年里程与城市/高速拆分 =====
    weekday_km = inputs['工作日通勤天数'] * inputs['工作日单日里程'] * 52
    weekend_km = 2 * inputs['周末单日里程'] * 52
    annual_mileage = weekday_km + weekend_km

    if inputs['电车膨胀开关'] == 1:
        ev_annual_mileage = annual_mileage * inputs['电车膨胀系数']
    else:
        ev_annual_mileage = annual_mileage

    highway_km = (
        weekday_km * inputs['工作日高速比例'] +
        weekend_km * inputs['周末高速比例']
    )
    city_km = annual_mileage - highway_km

    # 计算年里程（支持动态覆盖）
    if override_annual_mileage is not None:
        # 使用覆盖的总年里程，并按原有比例分配城市/高速
        actual_annual_mileage = override_annual_mileage
        original_annual_mileage = weekday_km + weekend_km

        if original_annual_mileage > 0:
            scale = actual_annual_mileage / original_annual_mileage
        else:
            scale = 1.0

        actual_city_km = (original_annual_mileage - highway_km) * scale
        actual_highway_km = highway_km * scale
        actual_ev_annual_mileage = actual_annual_mileage * inputs['电车膨胀系数'] if inputs['电车膨胀开关'] == 1 else actual_annual_mileage
    else:
        # 使用刚计算得到的里程变量
        actual_annual_mileage = annual_mileage
        actual_city_km = city_km
        actual_highway_km = highway_km
        actual_ev_annual_mileage = ev_annual_mileage

    # ===== 实际购入价格 =====
    if start_year == 1:
        purchase_price = new_price
    else:
        if not is_ev and oil_purchase_mileage is not None and brand == '奥迪 A4 Avant':
            # A4 Avant：使用实际二手成交里程-价格曲线估算购入价，独立于新车价
            purchase_price = get_a4avant_market_price(oil_purchase_mileage)
        elif not is_ev and oil_purchase_mileage is not None:
            # 油车：根据购入时的实际里程数计算残值率
            mileage_units = int(oil_purchase_mileage / 10000)
            purchase_price = new_price * brand_info['残值率'][min(mileage_units, len(brand_info['残值率']) - 1)]
        else:
            # 电车或其他情况：沿用之前的年份估算
            purchase_price = new_price * get_residual_rate(
                brand_info,
                start_year - 1,
                is_ev,
                actual_annual_mileage
            )

    rows = []

    for year in range(1, YEARS + 1):
        in_use = start_year <= year <= end_year

        # ---- 购车 ----
        buy = -purchase_price if year == start_year else 0

        # ---- 能源 ----
        if in_use:
            if is_ev:
                unit_price = (
                    inputs['家充电价'] * inputs['家充比例'] +
                    inputs['公共充电价'] * (1 - inputs['家充比例'])
                )
                energy = -(
                    actual_city_km / 100 * brand_info['城区电耗'] +
                    actual_highway_km / 100 * brand_info['高速电耗']
                ) * unit_price * (actual_ev_annual_mileage / actual_annual_mileage) if actual_annual_mileage > 0 else 0
            else:
                energy = -(
                    actual_city_km / 100 * brand_info['城区油耗'] +
                    actual_highway_km / 100 * brand_info['高速油耗']
                ) * inputs['油价']
        else:
            energy = 0

        # ---- 保险（每年出险一次，第三年后稳定）----
        if in_use:
            if not is_ev and oil_purchase_mileage is not None and brand == '奥迪 A4 Avant':
                # A4 Avant：按累计里程的市场成交价估算当年车辆价值
                cumulative_mileage = oil_purchase_mileage + (year - start_year) * actual_annual_mileage
                car_value = get_a4avant_market_price(cumulative_mileage)
            elif not is_ev and oil_purchase_mileage is not None:
                # 其他油车：根据累积里程计算残值率
                cumulative_mileage = oil_purchase_mileage + (year - start_year) * actual_annual_mileage
                mileage_units = int(cumulative_mileage / 10000)
                car_value = new_price * brand_info['残值率'][min(mileage_units, len(brand_info['残值率']) - 1)]
            else:
                # 电车或其他情况：沿用年份估算
                age_years = year - 1
                car_value = new_price * get_residual_rate(
                    brand_info,
                    age_years,
                    is_ev,
                    actual_annual_mileage
                )

            if year == 1:
                factor = 1.0
            elif year == 2:
                factor = 0.90
            else:
                factor = 0.85

            insurance = -car_value * brand_info['首年保险率'] * factor
        else:
            insurance = 0

        # ---- 保养 ----
        maintenance = -brand_info['年保养费'] if in_use else 0

        # ---- 过路费 ----
        toll = -actual_highway_km * inputs['过路费单价'] if in_use else 0

        # ---- 其他固定成本 ----
        parking = -inputs['停车费'] if in_use else 0
        plate = -inputs['上海油牌通胀'] if (in_use and not is_ev) else 0
        fine = -inputs['罚款'] if in_use else 0

        # ---- 卖车 ----
        if year == end_year and in_use:
            sell = car_value
        else:
            sell = 0

        net_cf = (
            buy + energy + insurance + maintenance +
            toll + parking + plate + fine + sell
        )

        rows.append([
            year, buy, energy, insurance, maintenance,
            toll, parking, plate, fine, sell, net_cf
        ])

    df = pd.DataFrame(rows, columns=[
        '年', '购车', '能源', '保险', '保养',
        '过路费', '停车费', '油牌通胀', '罚款',
        '卖车', '净现金流'
    ])

    df['累计现金流'] = df['净现金流'].cumsum()
    df['折现现金流'] = df['净现金流'] / ((1 + inputs['折现率']) ** (df['年'] - 1))
    return df


if __name__ == '__main__':
    # ===================== 计算（仅在作为脚本运行时） =====================
    oil_cf = calc_cashflow(
        inputs['油车品牌'],
        inputs['油车新车价'],
        inputs['油车起始年'],
        inputs['油车结束年'],
        False
    )

    ev_cf = calc_cashflow(
        inputs['电车品牌'],
        inputs['电车新车价'],
        inputs['电车起始年'],
        inputs['电车结束年'],
        True
    )

    # ===================== 对齐打印 =====================
    pd.set_option('display.float_format', '{:,.0f}'.format)

    print("\n======== 油车现金流（元） ========")
    print(oil_cf.to_string(index=False))

    print("\n======== 电车现金流（元） ========")
    print(ev_cf.to_string(index=False))

    print("\n======== NPV 汇总 ========")
    print(f"{'油车 NPV':<12}: {oil_cf['折现现金流'].sum():,.0f}")
    print(f"{'电车 NPV':<12}: {ev_cf['折现现金流'].sum():,.0f}")
