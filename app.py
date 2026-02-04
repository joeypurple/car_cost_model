import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import cost_model as cm

try:
    st.set_option('deprecation.showPyplotGlobalUse', False)
except Exception:
    # 兼容不同版本的 Streamlit：如果配置项不存在则忽略
    pass

st.title("油电车成本比较模型")

st.sidebar.header("参数设置")

# 品牌选择
oil_brands = cm.brands[cm.brands['动力'] == '油'].index.tolist()
ev_brands = cm.brands[cm.brands['动力'] == '电'].index.tolist()

oil_brand = st.sidebar.selectbox("油车品牌", oil_brands, index=oil_brands.index(cm.inputs['油车品牌']) if cm.inputs['油车品牌'] in oil_brands else 0)
ev_brand = st.sidebar.selectbox("电车品牌", ev_brands, index=ev_brands.index(cm.inputs['电车品牌']) if cm.inputs['电车品牌'] in ev_brands else 0)

# 价格与里程等基本参数
oil_price = st.sidebar.number_input("油车新车价", value=float(cm.inputs['油车新车价']), step=1000.0)
ev_price = st.sidebar.number_input("电车新车价", value=float(cm.inputs['电车新车价']), step=1000.0)

油价 = st.sidebar.number_input("油价 (元/L)", value=cm.inputs['油价'])
家充价 = st.sidebar.number_input("家充电价 (元/kWh)", value=cm.inputs['家充电价'])
公共充电价 = st.sidebar.number_input("公共充电价 (元/kWh)", value=cm.inputs['公共充电价'])
家充比例 = st.sidebar.slider("家充比例", 0.0, 1.0, float(cm.inputs['家充比例']))

工作日通勤天数 = st.sidebar.number_input("工作日通勤天数", value=cm.inputs['工作日通勤天数'], min_value=0)
工作日单日里程 = st.sidebar.number_input("工作日单日里程 (km)", value=cm.inputs['工作日单日里程'], min_value=0)
周末单日里程 = st.sidebar.number_input("周末单日里程 (km)", value=cm.inputs['周末单日里程'], min_value=0)

工作日高速比例 = st.sidebar.slider("工作日高速比例", 0.0, 1.0, float(cm.inputs['工作日高速比例']))
周末高速比例 = st.sidebar.slider("周末高速比例", 0.0, 1.0, float(cm.inputs['周末高速比例']))

电车膨胀系数 = st.sidebar.number_input("电车膨胀系数", value=cm.inputs['电车膨胀系数'])
电车膨胀开关 = st.sidebar.selectbox("电车膨胀开关", (0,1), index=0 if cm.inputs.get('电车膨胀开关',1)==0 else 1)

油车起始年 = st.sidebar.number_input("油车起始年", value=cm.inputs['油车起始年'], min_value=1)
油车结束年 = st.sidebar.number_input("油车结束年", value=cm.inputs['油车结束年'], min_value=1)
电车起始年 = st.sidebar.number_input("电车起始年", value=cm.inputs['电车起始年'], min_value=1)
电车结束年 = st.sidebar.number_input("电车结束年", value=cm.inputs['电车结束年'], min_value=1)

过路费单价 = st.sidebar.number_input("过路费单价 (元/km)", value=cm.inputs['过路费单价'])
停车费 = st.sidebar.number_input("停车费 (元/年)", value=cm.inputs['停车费'])
上海油牌通胀 = st.sidebar.number_input("上海油牌通胀 (元/年)", value=cm.inputs['上海油牌通胀'])
罚款 = st.sidebar.number_input("罚款 (元/年)", value=cm.inputs['罚款'])

折现率 = st.sidebar.number_input("折现率", value=cm.inputs['折现率'])

if st.sidebar.button("运行模型"):
    # 更新 cost_model 中的 inputs
    new_inputs = {
        '油车品牌': oil_brand,
        '电车品牌': ev_brand,
        '油价': float(油价),
        '家充电价': float(家充价),
        '公共充电价': float(公共充电价),
        '家充比例': float(家充比例),
        '工作日通勤天数': int(工作日通勤天数),
        '工作日单日里程': int(工作日单日里程),
        '周末单日里程': int(周末单日里程),
        '工作日高速比例': float(工作日高速比例),
        '周末高速比例': float(周末高速比例),
        '电车膨胀系数': float(电车膨胀系数),
        '电车膨胀开关': int(电车膨胀开关),
        '油车新车价': float(oil_price),
        '电车新车价': float(ev_price),
        '油车起始年': int(油车起始年),
        '油车结束年': int(油车结束年),
        '电车起始年': int(电车起始年),
        '电车结束年': int(电车结束年),
        '过路费单价': float(过路费单价),
        '停车费': float(停车费),
        '上海油牌通胀': float(上海油牌通胀),
        '罚款': float(罚款),
        '折现率': float(折现率)
    }

    cm.inputs.update(new_inputs)

    # 调用计算函数
    oil_cf = cm.calc_cashflow(cm.inputs['油车品牌'], cm.inputs['油车新车价'], cm.inputs['油车起始年'], cm.inputs['油车结束年'], False)
    ev_cf = cm.calc_cashflow(cm.inputs['电车品牌'], cm.inputs['电车新车价'], cm.inputs['电车起始年'], cm.inputs['电车结束年'], True)

    st.subheader('油车现金流')
    st.dataframe(oil_cf)
    st.download_button('下载油车 CSV', oil_cf.to_csv(index=False).encode('utf-8'), file_name='oil_cashflow.csv')

    st.subheader('电车现金流')
    st.dataframe(ev_cf)
    st.download_button('下载电车 CSV', ev_cf.to_csv(index=False).encode('utf-8'), file_name='ev_cashflow.csv')

    # 绘图：累计现金流（已修复显示）
    fig2, ax2 = plt.subplots()
    ax2.plot(oil_cf['年'], oil_cf['累计现金流'].fillna(0), marker='o', label='油车')
    ax2.plot(ev_cf['年'], ev_cf['累计现金流'].fillna(0), marker='o', label='电车')
    ax2.set_xlabel('年')
    ax2.set_ylabel('累计现金流 (元)')
    ax2.legend()
    ax2.grid(True)
    # 设置合理的 y 轴范围以确保曲线可见（留 10% 边距）
    ymin = min(oil_cf['累计现金流'].min(), ev_cf['累计现金流'].min())
    ymax = max(oil_cf['累计现金流'].max(), ev_cf['累计现金流'].max())
    if pd.notna(ymin) and pd.notna(ymax) and ymax > ymin:
        margin = (ymax - ymin) * 0.1
        ax2.set_ylim(ymin - margin, ymax + margin)
    fig2.tight_layout()
    st.subheader('累计现金流比较')
    st.pyplot(fig2)

    # 比较新电车与不同起购年份的二手油车（使用 app 中的电车持有年限）
    ev_hold_years = cm.inputs['电车结束年'] - cm.inputs['电车起始年'] + 1
    oil_start_years = list(range(1, 9))
    diffs = []
    for sy in oil_start_years:
        # 电车按 app 中的持有年限（从 1 年开始计算）
        ev_cf_comp = cm.calc_cashflow(cm.inputs['电车品牌'], cm.inputs['电车新车价'], 1, ev_hold_years, True)
        ev_cost = -ev_cf_comp['折现现金流'].sum()

        oil_cf_comp = cm.calc_cashflow(cm.inputs['油车品牌'], cm.inputs['油车新车价'], sy, sy + ev_hold_years - 1, False)
        oil_cost = -oil_cf_comp['折现现金流'].sum()

        diffs.append(oil_cost - ev_cost)

    fig_compare, axc = plt.subplots()
    axc.plot(oil_start_years, diffs, marker='o')
    axc.axhline(0, linestyle='--')
    axc.set_xlabel('油车购入年份')
    axc.set_ylabel('油车成本 - 电车成本（元）')
    axc.set_title(f'新电车 vs 不同年限油车（电车持有 {ev_hold_years} 年）')
    axc.grid(True)
    fig_compare.tight_layout()
    st.subheader('新电车 vs 不同年限油车（同持有年限）')
    st.pyplot(fig_compare)

    # 年里程对比（给出数值与条形图）
    weekday_km = cm.inputs['工作日通勤天数'] * cm.inputs['工作日单日里程'] * 52
    weekend_km = 2 * cm.inputs['周末单日里程'] * 52
    annual_mileage = weekday_km + weekend_km
    if cm.inputs.get('电车膨胀开关', 1) == 1:
        ev_annual_mileage = annual_mileage * cm.inputs.get('电车膨胀系数', 1.0)
    else:
        ev_annual_mileage = annual_mileage

    st.subheader('年总里程（按输入计算）')
    st.write(f"油车年总里程: {annual_mileage:,.0f} km")
    st.write(f"电车年总里程: {ev_annual_mileage:,.0f} km")

    fig_miles, axm = plt.subplots()
    axm.bar(['油车', '电车'], [annual_mileage, ev_annual_mileage], color=['#1f77b4', '#ff7f0e'])
    axm.set_ylabel('年里程 (km)')
    axm.set_ylim(0, max(annual_mileage, ev_annual_mileage) * 1.2 if max(annual_mileage, ev_annual_mileage) > 0 else 1)
    fig_miles.tight_layout()
    st.pyplot(fig_miles)

    # 简短说明
    st.caption('注：电车年里程已考虑电车膨胀系数（如果已打开）。')
