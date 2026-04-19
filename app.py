import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import cost_model as cm

try:
    st.set_option('deprecation.showPyplotGlobalUse', False)
except Exception:
    # 兼容不同版本的 Streamlit：如果配置项不存在则忽略
    pass

st.title("车辆成本比较模型")

st.sidebar.header("参数设置")

vehicle_types = ['油', '电']

vehicle1_type = st.sidebar.selectbox("车辆1类型", vehicle_types, index=0)
vehicle1_brands = cm.brands[cm.brands['动力'] == vehicle1_type].index.tolist()
vehicle1_brand_default = cm.inputs['油车品牌'] if vehicle1_type == '油' else cm.inputs['电车品牌']
vehicle1_brand = st.sidebar.selectbox(
    "车辆1品牌",
    vehicle1_brands,
    index=vehicle1_brands.index(vehicle1_brand_default) if vehicle1_brand_default in vehicle1_brands else 0
)

vehicle2_type = st.sidebar.selectbox("车辆2类型", vehicle_types, index=1)
vehicle2_brands = cm.brands[cm.brands['动力'] == vehicle2_type].index.tolist()
vehicle2_brand_default = cm.inputs['电车品牌'] if vehicle2_type == '电' else cm.inputs['油车品牌']
vehicle2_brand = st.sidebar.selectbox(
    "车辆2品牌",
    vehicle2_brands,
    index=vehicle2_brands.index(vehicle2_brand_default) if vehicle2_brand_default in vehicle2_brands else 0
)

vehicle1_price = st.sidebar.number_input(
    "车辆1新车价",
    value=float(cm.inputs['油车新车价']) if vehicle1_type == '油' else float(cm.inputs['电车新车价']),
    step=1000.0
)
vehicle2_price = st.sidebar.number_input(
    "车辆2新车价",
    value=float(cm.inputs['电车新车价']) if vehicle2_type == '电' else float(cm.inputs['油车新车价']),
    step=1000.0
)

vehicle1_start_year = st.sidebar.number_input(
    "车辆1起始年",
    value=int(cm.inputs['油车起始年'] if vehicle1_type == '油' else cm.inputs['电车起始年']),
    min_value=1
)
vehicle1_end_year = st.sidebar.number_input(
    "车辆1结束年",
    value=int(cm.inputs['油车结束年'] if vehicle1_type == '油' else cm.inputs['电车结束年']),
    min_value=vehicle1_start_year
)

# 油车购入里程（仅对油车显示）
vehicle1_purchase_mileage = None
if vehicle1_type == '油':
    vehicle1_purchase_mileage = st.sidebar.number_input(
        "车辆1购入里程 (km)",
        value=50000 if vehicle1_start_year > 1 else 0,
        min_value=0,
        help="油车购入时的里程数，用于估算购入价及后续折旧价"
    )

vehicle2_start_year = st.sidebar.number_input(
    "车辆2起始年",
    value=int(cm.inputs['电车起始年'] if vehicle2_type == '电' else cm.inputs['油车起始年']),
    min_value=1
)
vehicle2_end_year = st.sidebar.number_input(
    "车辆2结束年",
    value=int(cm.inputs['电车结束年'] if vehicle2_type == '电' else cm.inputs['油车结束年']),
    min_value=vehicle2_start_year
)

# 油车购入里程（仅对油车显示）
vehicle2_purchase_mileage = None
if vehicle2_type == '油':
    vehicle2_purchase_mileage = st.sidebar.number_input(
        "车辆2购入里程 (km)",
        value=50000 if vehicle2_start_year > 1 else 0,
        min_value=0,
        help="油车购入时的里程数，用于估算购入价及后续折旧价"
    )

# 价格与里程等基本参数
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

过路费单价 = st.sidebar.number_input("过路费单价 (元/km)", value=cm.inputs['过路费单价'])
停车费 = st.sidebar.number_input("停车费 (元/年)", value=cm.inputs['停车费'])
上海油牌通胀 = st.sidebar.number_input("上海油牌通胀 (元/年)", value=cm.inputs['上海油牌通胀'])
罚款 = st.sidebar.number_input("罚款 (元/年)", value=cm.inputs['罚款'])

折现率 = st.sidebar.number_input("折现率", value=cm.inputs['折现率'])

if st.sidebar.button("运行模型"):
    # 更新 cost_model 中的通用参数
    new_inputs = {
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
        '过路费单价': float(过路费单价),
        '停车费': float(停车费),
        '上海油牌通胀': float(上海油牌通胀),
        '罚款': float(罚款),
        '折现率': float(折现率)
    }
    cm.inputs.update(new_inputs)

    vehicle1_cf = cm.calc_cashflow(
        vehicle1_brand,
        float(vehicle1_price),
        int(vehicle1_start_year),
        int(vehicle1_end_year),
        vehicle1_type == '电',
        oil_purchase_mileage=vehicle1_purchase_mileage
    )

    vehicle2_cf = cm.calc_cashflow(
        vehicle2_brand,
        float(vehicle2_price),
        int(vehicle2_start_year),
        int(vehicle2_end_year),
        vehicle2_type == '电',
        oil_purchase_mileage=vehicle2_purchase_mileage
    )

    st.subheader('车辆1 现金流')
    st.write(f"类型: {vehicle1_type}，品牌: {vehicle1_brand}，起始年: {vehicle1_start_year}，结束年: {vehicle1_end_year}")
    st.dataframe(vehicle1_cf)
    st.download_button('下载车辆1 CSV', vehicle1_cf.to_csv(index=False).encode('utf-8'), file_name='vehicle1_cashflow.csv')

    st.subheader('车辆2 现金流')
    st.write(f"类型: {vehicle2_type}，品牌: {vehicle2_brand}，起始年: {vehicle2_start_year}，结束年: {vehicle2_end_year}")
    st.dataframe(vehicle2_cf)
    st.download_button('下载车辆2 CSV', vehicle2_cf.to_csv(index=False).encode('utf-8'), file_name='vehicle2_cashflow.csv')

    # 比较累计现金流
    fig2, ax2 = plt.subplots()
    ax2.plot(vehicle1_cf['年'], vehicle1_cf['累计现金流'].fillna(0), marker='o', label='车辆1')
    ax2.plot(vehicle2_cf['年'], vehicle2_cf['累计现金流'].fillna(0), marker='o', label='车辆2')
    ax2.set_xlabel('年')
    ax2.set_ylabel('累计现金流 (元)')
    ax2.legend()
    ax2.grid(True)
    ymin = min(vehicle1_cf['累计现金流'].min(), vehicle2_cf['累计现金流'].min())
    ymax = max(vehicle1_cf['累计现金流'].max(), vehicle2_cf['累计现金流'].max())
    if pd.notna(ymin) and pd.notna(ymax) and ymax > ymin:
        margin = (ymax - ymin) * 0.1
        ax2.set_ylim(ymin - margin, ymax + margin)
    fig2.tight_layout()
    st.subheader('累计现金流比较')
    st.pyplot(fig2)

    st.subheader('NPV 汇总')
    npv1 = vehicle1_cf['折现现金流'].sum()
    npv2 = vehicle2_cf['折现现金流'].sum()
    st.write(f"车辆1 NPV: {npv1:,.0f} 元")
    st.write(f"车辆2 NPV: {npv2:,.0f} 元")
    st.write(f"NPV 差值 (车辆1 - 车辆2): {npv1 - npv2:,.0f} 元")

    # 年里程对比
    weekday_km = cm.inputs['工作日通勤天数'] * cm.inputs['工作日单日里程'] * 52
    weekend_km = 2 * cm.inputs['周末单日里程'] * 52
    annual_mileage = weekday_km + weekend_km
    if cm.inputs.get('电车膨胀开关', 1) == 1:
        ev_annual_mileage = annual_mileage * cm.inputs.get('电车膨胀系数', 1.0)
    else:
        ev_annual_mileage = annual_mileage

    st.subheader('年总里程（按输入计算）')
    st.write(f"常规年总里程: {annual_mileage:,.0f} km")
    st.write(f"电车年总里程: {ev_annual_mileage:,.0f} km")

    fig_miles, axm = plt.subplots()
    axm.bar(['常规年里程', '电车年里程'], [annual_mileage, ev_annual_mileage], color=['#1f77b4', '#ff7f0e'])
    axm.set_ylabel('年里程 (km)')
    axm.set_ylim(0, max(annual_mileage, ev_annual_mileage) * 1.2 if max(annual_mileage, ev_annual_mileage) > 0 else 1)
    fig_miles.tight_layout()
    st.pyplot(fig_miles)

    st.caption('注：电车年里程已考虑电车膨胀系数（如果已打开）。')
