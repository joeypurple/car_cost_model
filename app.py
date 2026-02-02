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
oil_price = st.sidebar.number_input("油车新车价", value=cm.inputs['油车新车价'], step=1000)
ev_price = st.sidebar.number_input("电车新车价", value=cm.inputs['电车新车价'], step=1000)

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

override_mileage = st.sidebar.number_input("覆盖年里程（留空使用默认）", value=0)

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
    oil_cf = cm.calc_cashflow(cm.inputs['油车品牌'], cm.inputs['油车新车价'], cm.inputs['油车起始年'], cm.inputs['油车结束年'], False, override_annual_mileage=override_mileage if override_mileage>0 else None)
    ev_cf = cm.calc_cashflow(cm.inputs['电车品牌'], cm.inputs['电车新车价'], cm.inputs['电车起始年'], cm.inputs['电车结束年'], True, override_annual_mileage=override_mileage if override_mileage>0 else None)

    st.subheader('油车现金流')
    st.dataframe(oil_cf)
    st.download_button('下载油车 CSV', oil_cf.to_csv(index=False).encode('utf-8'), file_name='oil_cashflow.csv')

    st.subheader('电车现金流')
    st.dataframe(ev_cf)
    st.download_button('下载电车 CSV', ev_cf.to_csv(index=False).encode('utf-8'), file_name='ev_cashflow.csv')

    # 绘图：净现金流、累计现金流、NPV 比较
    fig1, ax1 = plt.subplots()
    ax1.plot(oil_cf['年'], oil_cf['净现金流'], marker='o', label='油车')
    ax1.plot(ev_cf['年'], ev_cf['净现金流'], marker='o', label='电车')
    ax1.set_xlabel('年')
    ax1.set_ylabel('净现金流 (元)')
    ax1.legend()
    st.subheader('净现金流比较')
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(oil_cf['年'], oil_cf['累计现金流'], marker='o', label='油车')
    ax2.plot(ev_cf['年'], ev_cf['累计现金流'], marker='o', label='电车')
    ax2.set_xlabel('年')
    ax2.set_ylabel('累计现金流 (元)')
    ax2.legend()
    st.subheader('累计现金流比较')
    st.pyplot(fig2)

    # NPV 对比
    oil_npv = oil_cf['折现现金流'].sum()
    ev_npv = ev_cf['折现现金流'].sum()
    fig3, ax3 = plt.subplots()
    ax3.bar(['油车', '电车'], [oil_npv, ev_npv], color=['#1f77b4', '#ff7f0e'])
    ax3.set_ylabel('NPV (元)')
    st.subheader('NPV 对比（折现现金流之和）')
    st.pyplot(fig3)

    st.write(f"油车 NPV: {oil_npv:,.0f} 元")
    st.write(f"电车 NPV: {ev_npv:,.0f} 元")
