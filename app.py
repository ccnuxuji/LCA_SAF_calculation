import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from LCA_calculation import SAF_LCA_Model

# 设置页面配置
st.set_page_config(
    page_title="SAF排放分析工具",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stExpander {
        border: 1px solid #e6e6e6;
        border-radius: 0.5rem;
    }
    .fixed-config {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="main-header">🛩️ SAF排放分析工具</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">可持续航空燃料(SAF)温室气体排放分析平台</p>', unsafe_allow_html=True)

# 显示固定配置信息
st.markdown("""
<div class="fixed-config">
<h4>🔧 固定模型配置</h4>
<ul>
<li><strong>生产路径:</strong> Fischer-Tropsch (FT)</li>
<li><strong>功能单位:</strong> MJ</li>
<li><strong>CO2来源:</strong> 直接空气捕获 (DAC)</li>
<li><strong>工艺路线:</strong> DAC → 电解 → Fischer-Tropsch合成</li>
</ul>
</div>
""", unsafe_allow_html=True)

# 侧边栏参数设置
st.sidebar.markdown("## 📊 参数设置")

# 创建模型实例（移除固定参数）
@st.cache_resource
def create_model():
    return SAF_LCA_Model()

model = create_model()

# 参数设置区域
with st.sidebar.expander("🏭 直接空气捕集(DAC)参数", expanded=True):
    dac_efficiency = st.slider("捕集效率 (%)", 50, 95, 80, 5)
    dac_energy = st.slider("能耗 (MJ/kg CO2)", 10, 50, 20, 5)
    dac_emissions = st.slider("排放 (kg CO2e/kg CO2)", 0.0, 0.3, 0.08, 0.01)
    dac_water = st.slider("用水量 (L/kg CO2)", 1, 20, 5, 1)
    dac_co2_rate = st.slider("CO2需求 (kg CO2/kg fuel)", 2.0, 4.0, 3.1, 0.1)

with st.sidebar.expander("⚡ 电解参数", expanded=True):
    co2_elec_eff = st.slider("CO2电解效率 (%)", 40, 80, 65, 5)
    h2o_elec_eff = st.slider("水电解效率 (%)", 60, 90, 75, 5)
    
    electricity_source = st.selectbox(
        "电力来源",
        ["renewable_mix", "wind", "solar", "grid_global", "grid_eu", "grid_us", 
         "grid_china", "natural_gas", "coal", "hydro", "nuclear"],
        index=1
    )
    
    co_energy = st.slider("CO生产能耗 (MJ/kg CO)", 15, 40, 28, 1)
    h2_energy = st.slider("H2生产能耗 (MJ/kg H2)", 40, 70, 55, 1)
    elec_water = st.slider("电解用水量 (L/kg syngas)", 10, 40, 20, 2)

with st.sidebar.expander("🔬 费托合成参数", expanded=True):
    ft_efficiency = st.slider("转化效率", 0.5, 0.8, 0.65, 0.05)
    ft_emissions = st.slider("排放 (kg CO2e/kg fuel)", 0.1, 0.5, 0.2, 0.05)
    ft_energy = st.slider("能耗 (MJ/kg fuel)", 15, 40, 25, 1)
    ft_water = st.slider("用水量 (L/kg fuel)", 2, 15, 5, 1)
    syngas_req = st.slider("合成气需求 (kg/kg fuel)", 1.5, 3.0, 2.13, 0.05)
    co_h2_ratio = st.slider("CO:H2比例", 0.5, 1.5, 0.923, 0.05)

with st.sidebar.expander("🚛 分配运输参数", expanded=False):
    transport_mode = st.selectbox(
        "运输方式",
        ["truck", "rail", "ship", "barge", "pipeline"],
        index=0,
        help="不同运输方式具有不同的排放因子和能耗"
    )
    transport_distance = st.slider("运输距离 (km)", 100, 2000, 500, 50)
    fuel_density = st.slider("SAF密度 (kg/L)", 0.7, 0.9, 0.8, 0.01)

with st.sidebar.expander("✈️ 使用阶段参数", expanded=False):
    combustion_emissions = st.slider("燃烧排放 (kg CO2e/kg fuel)", 0.0, 1.0, 0.0, 0.1)
    energy_density = st.slider("能量密度 (MJ/kg)", 35, 50, 43, 1)

# 设置模型参数（使用静默模式避免控制台输出）
model.set_use_phase_data(
    combustion_emissions=combustion_emissions,
    energy_density=energy_density
)

model.set_carbon_capture_data(
    capture_efficiency=dac_efficiency,
    energy_requirement=dac_energy,
    ghg_emissions=dac_emissions,
    water_usage=dac_water,
    co2_capture_rate=dac_co2_rate
)

model.set_electrolysis_data(
    co2_electrolysis_efficiency=co2_elec_eff,
    water_electrolysis_efficiency=h2o_elec_eff,
    electricity_source=electricity_source,
    energy_input_co=co_energy,
    energy_input_h2=h2_energy,
    water_usage=elec_water,
    silent=True  # 静默模式
)

model.set_conversion_data(
    technology="Fischer-Tropsch",
    efficiency=ft_efficiency,
    ghg_emissions=ft_emissions,
    energy_input=ft_energy,
    water_usage=ft_water,
    syngas_requirement=syngas_req,
    co_h2_ratio=co_h2_ratio
)

model.set_distribution_data(
    transport_distance=transport_distance,
    transport_mode=transport_mode,
    fuel_density=fuel_density,
    silent=True  # 静默模式
)

# 计算LCA（使用静默模式）
results = model.calculate_lca(silent=True)
emission_reduction = model.calculate_emission_reduction(silent=True)

# LCA计算公式展示（可折叠）
with st.expander("📐 查看详细LCA计算公式与参数解释", expanded=False):
    # 基础参数说明
    st.markdown("""
    #### 🔧 基础参数与标准化
    """)
    
    # 标准化因子详解
    normalization = 1/energy_density
    st.markdown(f"""
    **标准化因子计算**：将所有排放统一转换为每MJ燃料的排放量
    ```
    标准化因子 = 1 / 能量密度 = 1 / {energy_density} MJ/kg = {normalization:.4f} kg/MJ
    ```
    - 能量密度 {energy_density} MJ/kg 是C₁₂H₂₆的高热值
    - 标准化因子用于将每kg燃料的排放转换为每MJ的排放
    """)
    
    st.markdown("---")
    
    # 第一阶段：碳捕获 (DAC)
    st.markdown("#### 🏭 阶段1：直接空气捕获 (DAC)")
    actual_co2_needed = dac_co2_rate / (dac_efficiency / 100)
    dac_emission_result = dac_emissions * actual_co2_needed * normalization
    
    st.markdown(f"""
    **步骤1：计算实际CO₂捕获需求**
    ```
    理论CO₂需求 = {dac_co2_rate} kg CO₂/kg fuel  (基于C₁₂H₂₆化学计量比)
    DAC捕获效率 = {dac_efficiency}%  (DAC系统从大气中捕获CO₂的效率)
    实际CO₂需求 = {dac_co2_rate} / ({dac_efficiency}/100) = {actual_co2_needed:.3f} kg CO₂/kg fuel
    ```
    
    **步骤2：计算DAC阶段排放**
    ```
    DAC排放系数 = {dac_emissions} kg CO₂e/kg CO₂ (DAC过程本身的排放)
    E_DAC = {dac_emissions} × {actual_co2_needed:.3f} × {normalization:.4f} = {dac_emission_result:.5f} kg CO₂e/MJ
    E_DAC = {dac_emission_result*1000:.2f} g CO₂e/MJ
    ```
    
    **参数解释**：
    - DAC排放系数包括压缩机、加热器、冷却系统等设备的间接排放
    - 使用可再生电力时此值较低，使用电网电力时会更高
    """)
    
    st.markdown("---")
    
    # 第二阶段：电解
    st.markdown("#### ⚡ 阶段2：电解制取合成气")
    elec_intensity_mj = model.electrolysis_data['electricity_carbon_intensity'] / 3.6
    total_syngas_needed = syngas_req * normalization
    co_h2_ratio_val = co_h2_ratio
    co_needed = total_syngas_needed * (co_h2_ratio_val / (1 + co_h2_ratio_val))
    h2_needed = total_syngas_needed * (1 / (1 + co_h2_ratio_val))
    actual_co_needed = co_needed / (co2_elec_eff / 100)
    actual_h2_needed = h2_needed / (h2o_elec_eff / 100)
    co_emissions = actual_co_needed * co_energy * elec_intensity_mj
    h2_emissions = actual_h2_needed * h2_energy * elec_intensity_mj
    total_elec_emissions = co_emissions + h2_emissions
    
    st.markdown(f"""
    **步骤1：电力碳强度转换**
    ```
    电力碳强度 = {model.electrolysis_data['electricity_carbon_intensity']:.3f} kg CO₂e/kWh ({electricity_source})
    电力碳强度(MJ) = {model.electrolysis_data['electricity_carbon_intensity']:.3f} / 3.6 = {elec_intensity_mj:.4f} kg CO₂e/MJ
    ```
    
    **步骤2：合成气需求分配**
    ```
    合成气总需求 = {syngas_req} kg/kg × {normalization:.4f} = {total_syngas_needed:.4f} kg syngas/MJ fuel
    CO:H₂摩尔比 = {co_h2_ratio_val:.3f} (优化的费托合成比例)
    CO需求 = {total_syngas_needed:.4f} × ({co_h2_ratio_val:.3f}/(1+{co_h2_ratio_val:.3f})) = {co_needed:.4f} kg CO/MJ
    H₂需求 = {total_syngas_needed:.4f} × (1/(1+{co_h2_ratio_val:.3f})) = {h2_needed:.4f} kg H₂/MJ
    ```
    
    **步骤3：考虑电解效率的实际需求**
    ```
    CO₂电解效率 = {co2_elec_eff}% (CO₂→CO转换效率)
    水电解效率 = {h2o_elec_eff}% (H₂O→H₂转换效率)
    实际CO需求 = {co_needed:.4f} / ({co2_elec_eff}/100) = {actual_co_needed:.4f} kg CO/MJ
    实际H₂需求 = {h2_needed:.4f} / ({h2o_elec_eff}/100) = {actual_h2_needed:.4f} kg H₂/MJ
    ```
    
    **步骤4：电解阶段排放计算**
    ```
    CO生产能耗 = {co_energy} MJ/kg CO (CO₂电解所需电力)
    H₂生产能耗 = {h2_energy} MJ/kg H₂ (水电解所需电力)
    CO生产排放 = {actual_co_needed:.4f} × {co_energy} × {elec_intensity_mj:.4f} = {co_emissions:.5f} kg CO₂e/MJ
    H₂生产排放 = {actual_h2_needed:.4f} × {h2_energy} × {elec_intensity_mj:.4f} = {h2_emissions:.5f} kg CO₂e/MJ
    E_电解 = {co_emissions:.5f} + {h2_emissions:.5f} = {total_elec_emissions:.5f} kg CO₂e/MJ
    E_电解 = {total_elec_emissions*1000:.2f} g CO₂e/MJ
    ```
    
    **参数解释**：
    - 电解是整个过程的高能耗环节，电力来源直接影响总排放
    - AEM技术效率高于传统电解，但仍需大量电力
    """)
    
    # 能量需求和水需求计算
    st.markdown("#### ⚡ 电解阶段能量与水需求详细计算")
    
    # 电力需求计算
    co_electricity_needed = actual_co_needed * co_energy  # MJ electricity for CO
    h2_electricity_needed = actual_h2_needed * h2_energy  # MJ electricity for H2
    total_electricity_needed = co_electricity_needed + h2_electricity_needed  # Total MJ electricity per MJ fuel
    
    # 水需求计算
    dac_water_needed = actual_co2_needed * dac_water * normalization  # L water for DAC per MJ fuel
    elec_water_needed = total_syngas_needed * elec_water  # L water for electrolysis per MJ fuel
    ft_water_needed = ft_water * normalization  # L water for FT per MJ fuel
    total_water_needed = dac_water_needed + elec_water_needed + ft_water_needed
    
    st.markdown(f"""
    **电力需求计算**
    ```
    CO生产电力需求 = {actual_co_needed:.4f} kg CO/MJ × {co_energy} MJ/kg = {co_electricity_needed:.3f} MJ电力/MJ燃料
    H₂生产电力需求 = {actual_h2_needed:.4f} kg H₂/MJ × {h2_energy} MJ/kg = {h2_electricity_needed:.3f} MJ电力/MJ燃料
    总电力需求 = {co_electricity_needed:.3f} + {h2_electricity_needed:.3f} = {total_electricity_needed:.3f} MJ电力/MJ燃料
    ```
    
    **电力转换为kWh**
    ```
    总电力需求 = {total_electricity_needed:.3f} MJ ÷ 3.6 = {total_electricity_needed/3.6:.4f} kWh电力/MJ燃料
    按1L燃料计算 = {total_electricity_needed/3.6:.4f} × {energy_density} × {fuel_density} = {(total_electricity_needed/3.6) * energy_density * fuel_density:.2f} kWh/L燃料
    ```
    
    **水需求计算**
    ```
    DAC用水需求 = {actual_co2_needed:.3f} kg CO₂/kg × {dac_water} L/kg CO₂ × {normalization:.4f} = {dac_water_needed:.3f} L水/MJ燃料
    电解用水需求 = {total_syngas_needed:.4f} kg syngas/MJ × {elec_water} L/kg = {elec_water_needed:.3f} L水/MJ燃料
    FT用水需求 = {ft_water} L/kg × {normalization:.4f} = {ft_water_needed:.3f} L水/MJ燃料
    总用水需求 = {dac_water_needed:.3f} + {elec_water_needed:.3f} + {ft_water_needed:.3f} = {total_water_needed:.3f} L水/MJ燃料
    ```
    
    **按1L燃料计算用水量**
    ```
    总用水量 = {total_water_needed:.3f} L水/MJ × {energy_density} MJ/kg × {fuel_density} kg/L = {total_water_needed * energy_density * fuel_density:.2f} L水/L燃料
    ```
    
    **能源效率分析**
    ```
    能源比率 = 产出能量/投入电力 = 1.0 MJ燃料 / {total_electricity_needed:.3f} MJ电力 = {1/total_electricity_needed:.3f}
    电力-燃料转换效率 = {(1/total_electricity_needed)*100:.1f}%
    ```
    """)
    
    st.markdown("---")
    
    # 第三阶段：费托合成
    st.markdown("#### 🔬 阶段3：Fischer-Tropsch合成")
    ft_emission_result = ft_emissions * normalization
    
    st.markdown(f"""
    **Fischer-Tropsch合成过程计算**
    ```
    FT工艺排放系数 = {ft_emissions} kg CO₂e/kg fuel
    FT转换效率 = {ft_efficiency:.2f} (合成气→液体燃料的能量转换效率)
    合成气需求 = {syngas_req} kg syngas/kg fuel (化学计量需求)
    CO:H₂比例 = {co_h2_ratio:.3f} (优化的反应比例)
    ```
    
    **FT合成排放计算**
    ```
    E_FT = {ft_emissions} × {normalization:.4f} = {ft_emission_result:.5f} kg CO₂e/MJ
    E_FT = {ft_emission_result*1000:.2f} g CO₂e/MJ
    ```
    
    **参数解释**：
    - FT合成排放包括：反应热能需求、催化剂再生、产品分离纯化
    - 工艺温度约200-350°C，压力20-40 bar
    - 副产品包括轻烃、蜡等，需要进一步加工
    - 催化剂通常为铁基或钴基，定期需要再生或更换
    """)
    
    st.markdown("---")
    
    # 第四阶段：运输
    st.markdown("#### 🚛 阶段4：分配运输")
    transport_emission_result = model.distribution_data['ghg_emissions'] * normalization
    
    st.markdown(f"""
    **运输排放计算**
    ```
    运输方式 = {transport_mode}
    运输距离 = {transport_distance} km
    排放因子 = {model.distribution_data['emission_factor']} kg CO₂e/tonne-km
    燃料重量 = 0.001 tonne/kg (单位转换)
    燃料密度 = {fuel_density} kg/L (SAF密度)
    ```
    
    **运输阶段排放**
    ```
    单位运输排放 = {model.distribution_data['emission_factor']} × 0.001 × {transport_distance} = {model.distribution_data['ghg_emissions']:.5f} kg CO₂e/kg fuel
    E_运输 = {model.distribution_data['ghg_emissions']:.5f} × {normalization:.4f} = {transport_emission_result:.5f} kg CO₂e/MJ
    E_运输 = {transport_emission_result*1000:.2f} g CO₂e/MJ
    ```
    
    **运输方式对比** (kg CO₂e/tonne-km)：
    - 管道 (pipeline): 0.002 (最低排放，但基础设施要求高)
    - 海运 (ship): 0.015 (长距离运输最优选择)
    - 铁路 (rail): 0.022 (陆地长距离运输较好选择)
    - 驳船 (barge): 0.031 (内河运输)
    - 卡车 (truck): 0.062 (灵活但排放较高)
    """)
    
    st.markdown("---")
    
    # 第五阶段：使用
    st.markdown("#### ✈️ 阶段5：使用阶段")
    use_emission_result = combustion_emissions * normalization
    
    st.markdown(f"""
    **使用阶段排放**
    ```
    燃烧排放系数 = {combustion_emissions} kg CO₂e/kg fuel
    E_使用 = {combustion_emissions} × {normalization:.4f} = {use_emission_result:.5f} kg CO₂e/MJ
    E_使用 = {use_emission_result*1000:.2f} g CO₂e/MJ
    ```
    
    **碳中性说明**：
    - DAC从大气中捕获CO₂，燃烧时释放相同量的CO₂回到大气
    - 实现了碳循环闭环，使用阶段理论排放为0
    - 这是SAF相对于化石燃料的主要减排优势
    """)
    
    st.markdown("---")
    
    # 总排放与减排率
    st.markdown("#### 📊 总排放汇总与减排率")
    total_calc_emissions = results['ghg_emissions']['total']
    
    st.markdown(f"""
    **各阶段排放汇总**
    ```
    E_总排放 = E_DAC + E_电解 + E_FT + E_运输 + E_使用
    E_总排放 = {results['ghg_emissions']['carbon_capture']*1000:.2f} + {results['ghg_emissions']['electrolysis']*1000:.2f} + {results['ghg_emissions']['conversion']*1000:.2f} + {results['ghg_emissions']['distribution']*1000:.2f} + {results['ghg_emissions']['use_phase']*1000:.2f}
    E_总排放 = {total_calc_emissions*1000:.2f} g CO₂e/MJ
    ```
    
    **减排率计算**
    ```
    传统航空燃料基准 = 89.0 g CO₂e/MJ (EU RED II标准)
    减排率 = (89.0 - {total_calc_emissions*1000:.2f}) / 89.0 × 100% = {emission_reduction:.1f}%
    ```
    
    **政策合规性评估**：
    - CORSIA (≥10%): {'✅ 合规' if emission_reduction >= 10 else '❌ 不合规'}
    - EU RED II (≥65%): {'✅ 合规' if emission_reduction >= 65 else '❌ 不合规'}  
    - CA LCFS (≥20%): {'✅ 合规' if emission_reduction >= 20 else '❌ 不合规'}
    """)

# 快速公式参考
st.info(f"""
💡 **LCA核心公式**: 总排放 = DAC({results['ghg_emissions']['carbon_capture']*1000:.1f}) + 电解({results['ghg_emissions']['electrolysis']*1000:.1f}) + FT({results['ghg_emissions']['conversion']*1000:.1f}) + 运输({results['ghg_emissions']['distribution']*1000:.1f}) + 使用({results['ghg_emissions']['use_phase']*1000:.1f}) = **{results['ghg_emissions']['total']*1000:.1f} g CO₂e/MJ** | 减排率: **{emission_reduction:.1f}%**
""")

# 主界面显示结果
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="sub-header">📈 排放分析结果</h2>', unsafe_allow_html=True)
    
    # 关键排放指标
    col1_1, col1_2, col1_3 = st.columns(3)
    
    with col1_1:
        total_emissions = results["ghg_emissions"]["total"] * 1000  # 转换为g CO2e/MJ
        st.metric(
            label="总排放量",
            value=f"{total_emissions:.1f} g CO₂e/MJ",
            help="每兆焦耳燃料的温室气体排放量"
        )
    
    with col1_2:
        st.metric(
            label="减排率",
            value=f"{emission_reduction:.1f}%",
            delta=f"{emission_reduction-65:.1f}%" if emission_reduction >= 65 else f"{emission_reduction-65:.1f}%",
            help="相对于传统航空燃料(89.0 g CO₂e/MJ)的减排率"
        )
    
    with col1_3:
        # 电力来源信息
        elec_intensity = model.electrolysis_data["electricity_carbon_intensity"]
        st.metric(
            label="电力碳强度",
            value=f"{elec_intensity:.3f} kg CO₂e/kWh",
            help="电力生产的碳排放强度"
        )

with col2:
    st.markdown('<h2 class="sub-header">🎯 合规性检查</h2>', unsafe_allow_html=True)
    
    if emission_reduction >= 65:
        st.success("✅ 符合EU RED II标准 (≥65%)")
    elif emission_reduction >= 10:
        st.warning("⚠️ 符合CORSIA标准 (≥10%)")
    else:
        st.error("❌ 不符合减排要求")
    
    # 显示当前配置信息
    st.info(f"🔌 电力来源: {electricity_source}")
    st.info(f"🚛 运输方式: {transport_mode}")
    st.info(f"📏 运输距离: {transport_distance} km")

# 排放分解可视化
st.markdown('<h2 class="sub-header">📊 排放分解分析</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # 排放分解饼图
    emissions_data = results["ghg_emissions"]
    stages = [k for k in emissions_data.keys() if k != "total"]
    values = [emissions_data[k] * 1000 for k in stages]  # 转换为g CO2e/MJ
    
    # 阶段名称映射
    stage_names = {
        "carbon_capture": "直接空气捕集",
        "electrolysis": "电解过程", 
        "conversion": "费托合成",
        "distribution": "分配运输",
        "use_phase": "使用阶段"
    }
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=[stage_names.get(stage, stage) for stage in stages],
        values=values,
        hole=0.3,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:.1f} g',
        textposition='auto'
    )])
    fig_pie.update_layout(
        title="各阶段排放占比",
        font=dict(size=12),
        height=450
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # 排放对比柱状图
    comparison_data = {
        "传统航空燃料": 89.0,
        "FT SAF": total_emissions
    }
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=list(comparison_data.keys()),
            y=list(comparison_data.values()),
            marker_color=['#FF6B6B', '#4ECDC4'],
            text=[f"{v:.1f}" for v in comparison_data.values()],
            textposition='auto',
            textfont=dict(size=14, color='white')
        )
    ])
    fig_bar.update_layout(
        title=f"排放对比 (减排{emission_reduction:.1f}%)",
        yaxis_title="排放量 (g CO2e/MJ)",
        height=450,
        showlegend=False
    )
    
    # 添加目标线
    fig_bar.add_hline(y=89.0*0.35, line_dash="dash", line_color="orange", 
                     annotation_text="EU RED II目标 (≤31.2 g CO2e/MJ)")
    fig_bar.add_hline(y=89.0*0.9, line_dash="dash", line_color="red",
                     annotation_text="CORSIA最低要求 (≤80.1 g CO2e/MJ)")
    
    st.plotly_chart(fig_bar, use_container_width=True)

# 能量消耗与水消耗分析
st.markdown('<h2 class="sub-header">⚡ 能量消耗与水消耗分析</h2>', unsafe_allow_html=True)

# 计算详细的能量和水消耗数据
energy_data = results["energy_consumption"]
water_data = results["water_usage"]

# 从LCA公式计算部分获取详细参数
normalization = 1/energy_density
actual_co2_needed = dac_co2_rate / (dac_efficiency / 100)
co_h2_ratio_val = co_h2_ratio
total_syngas_needed = syngas_req * normalization
co_needed = total_syngas_needed * (co_h2_ratio_val / (1 + co_h2_ratio_val))
h2_needed = total_syngas_needed * (1 / (1 + co_h2_ratio_val))
actual_co_needed = co_needed / (co2_elec_eff / 100)
actual_h2_needed = h2_needed / (h2o_elec_eff / 100)

# 电力需求计算
co_electricity_needed = actual_co_needed * co_energy
h2_electricity_needed = actual_h2_needed * h2_energy
total_electricity_needed = co_electricity_needed + h2_electricity_needed

# 水需求计算
dac_water_needed = actual_co2_needed * dac_water * normalization
elec_water_needed = total_syngas_needed * elec_water
ft_water_needed = ft_water * normalization
total_water_needed = dac_water_needed + elec_water_needed + ft_water_needed

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔋 能量消耗分析")
    
    # 能量消耗饼图
    energy_stages = [k for k in energy_data.keys() if k != "total"]
    energy_values = [energy_data[k] for k in energy_stages]
    
    fig_energy = go.Figure(data=[go.Pie(
        labels=[stage_names.get(stage, stage) for stage in energy_stages],
        values=energy_values,
        hole=0.3,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:.2f} MJ',
        textposition='auto'
    )])
    fig_energy.update_layout(
        title="各阶段能量消耗占比",
        font=dict(size=10),
        height=400
    )
    st.plotly_chart(fig_energy, use_container_width=True)
    
    # 关键能量指标
    st.markdown("#### 🔍 关键能量指标")
    col1_1, col1_2 = st.columns(2)
    
    with col1_1:
        st.metric(
            label="总能量输入",
            value=f"{energy_data['total']:.2f} MJ/MJ",
            help="每MJ燃料产出需要投入的总能量"
        )
    
    with col1_2:
        energy_efficiency = (1/energy_data['total'])*100 if energy_data['total'] > 0 else 0
        st.metric(
            label="能量转换效率",
            value=f"{energy_efficiency:.1f}%",
            help="产出能量/投入能量的比率"
        )

with col2:
    st.markdown("### 💧 水消耗分析")
    
    # 水消耗饼图
    water_stages = ["carbon_capture", "electrolysis", "conversion"]
    water_values = [water_data[stage] for stage in water_stages if stage in water_data]
    water_labels = [stage_names.get(stage, stage) for stage in water_stages if stage in water_data]
    
    fig_water = go.Figure(data=[go.Pie(
        labels=water_labels,
        values=water_values,
        hole=0.3,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:.3f} L',
        textposition='auto'
    )])
    fig_water.update_layout(
        title="各阶段水消耗占比",
        font=dict(size=10),
        height=400
    )
    st.plotly_chart(fig_water, use_container_width=True)
    
    # 关键水消耗指标
    st.markdown("#### 🔍 关键水消耗指标")
    col2_1, col2_2 = st.columns(2)
    
    with col2_1:
        st.metric(
            label="总水消耗",
            value=f"{water_data['total']:.3f} L/MJ",
            help="每MJ燃料生产所需的总用水量"
        )
    
    with col2_2:
        water_per_liter = water_data['total'] * energy_density * fuel_density
        st.metric(
            label="每升燃料用水",
            value=f"{water_per_liter:.2f} L/L",
            help="每升SAF燃料生产所需的水量"
        )

# 详细能量和水消耗表格
st.markdown("### 📊 详细能量与水消耗分解")

# 创建综合数据表
detailed_consumption = []
for stage in stages:
    if stage in energy_data and stage in water_data:
        detailed_consumption.append({
            "生产阶段": stage_names.get(stage, stage),
            "能量消耗 (MJ/MJ)": f"{energy_data[stage]:.3f}",
            "水消耗 (L/MJ)": f"{water_data[stage]:.3f}",
            "能量占比 (%)": f"{(energy_data[stage]/energy_data['total'])*100:.1f}%" if energy_data['total'] > 0 else "0.0%",
            "水消耗占比 (%)": f"{(water_data[stage]/water_data['total'])*100:.1f}%" if water_data['total'] > 0 else "0.0%"
        })

# 添加总计行
detailed_consumption.append({
    "生产阶段": "总计",
    "能量消耗 (MJ/MJ)": f"{energy_data['total']:.3f}",
    "水消耗 (L/MJ)": f"{water_data['total']:.3f}",
    "能量占比 (%)": "100.0%",
    "水消耗占比 (%)": "100.0%"
})

consumption_df = pd.DataFrame(detailed_consumption)
st.dataframe(consumption_df, use_container_width=True, hide_index=True)

# 能量和水消耗洞察
col1, col2, col3 = st.columns(3)

with col1:
    # 找出最大能量消耗阶段
    max_energy_stage = max(energy_data.items(), key=lambda x: x[1] if x[0] != "total" else 0)
    max_energy_name = stage_names.get(max_energy_stage[0], max_energy_stage[0])
    max_energy_percentage = (max_energy_stage[1] / energy_data['total']) * 100
    st.success(f"""
    **🔋 最大能耗环节**
    - 阶段: {max_energy_name}
    - 消耗: {max_energy_stage[1]:.3f} MJ/MJ
    - 占比: {max_energy_percentage:.1f}%
    """)

with col2:
    # 找出最大水消耗阶段
    water_stages_only = {k: v for k, v in water_data.items() if k != "total"}
    if water_stages_only:
        max_water_stage = max(water_stages_only.items(), key=lambda x: x[1])
        max_water_name = stage_names.get(max_water_stage[0], max_water_stage[0])
        max_water_percentage = (max_water_stage[1] / water_data['total']) * 100 if water_data['total'] > 0 else 0
        st.info(f"""
        **💧 最大水耗环节**
        - 阶段: {max_water_name}
        - 消耗: {max_water_stage[1]:.3f} L/MJ
        - 占比: {max_water_percentage:.1f}%
        """)

with col3:
    # 电力需求分析
    electricity_kwh_per_mj = total_electricity_needed / 3.6
    electricity_kwh_per_liter = electricity_kwh_per_mj * energy_density * fuel_density
    st.warning(f"""
    **⚡ 电力需求**
    - 每MJ燃料: {electricity_kwh_per_mj:.4f} kWh
    - 每升燃料: {electricity_kwh_per_liter:.2f} kWh
    - 能量比率: {1/total_electricity_needed:.3f}
    """)

# 电力来源敏感性分析
st.markdown('<h2 class="sub-header">⚡ 电力来源敏感性分析</h2>', unsafe_allow_html=True)

# 运行电力来源敏感性分析
with st.spinner('正在分析不同电力来源的影响...'):
    electricity_analysis = model.analyze_electricity_sources()

# 电力来源影响可视化
col1, col2 = st.columns(2)

with col1:
    # 总排放对比
    fig_elec = go.Figure()
    
    elec_sources = electricity_analysis['electricity_source'].tolist()
    elec_emissions = electricity_analysis['saf_emissions_mjbasis'].tolist()
    
    # 高亮当前选择的电力来源
    colors = ['#FF6B6B' if source == electricity_source else '#4ECDC4' for source in elec_sources]
    
    fig_elec.add_trace(go.Bar(
        x=elec_sources,
        y=elec_emissions,
        marker_color=colors,
        text=[f"{e:.1f}" for e in elec_emissions],
        textposition='auto',
        name='总排放量'
    ))
    
    fig_elec.update_layout(
        title="不同电力来源的总排放对比",
        xaxis_title="电力来源",
        yaxis_title="总排放量 (g CO2e/MJ)",
        height=400,
        showlegend=False
    )
    fig_elec.update_xaxes(tickangle=45)
    
    # 添加政策目标线
    fig_elec.add_hline(y=89.0*0.35, line_dash="dash", line_color="orange", 
                      annotation_text="EU RED II目标 (≤31.2 g CO2e/MJ)")
    fig_elec.add_hline(y=89.0*0.9, line_dash="dash", line_color="red",
                      annotation_text="CORSIA最低要求 (≤80.1 g CO2e/MJ)")
    
    st.plotly_chart(fig_elec, use_container_width=True)

with col2:
    # 减排率对比
    fig_reduction = go.Figure()
    
    reduction_rates = electricity_analysis['emission_reduction'].tolist()
    colors_reduction = ['#28a745' if rate >= 65 else '#ffc107' if rate >= 10 else '#dc3545' for rate in reduction_rates]
    
    fig_reduction.add_trace(go.Bar(
        x=elec_sources,
        y=reduction_rates,
        marker_color=colors_reduction,
        text=[f"{r:.1f}%" for r in reduction_rates],
        textposition='auto',
        name='减排率'
    ))
    
    fig_reduction.update_layout(
        title="不同电力来源的减排率对比",
        xaxis_title="电力来源",
        yaxis_title="减排率 (%)",
        height=400,
        showlegend=False
    )
    fig_reduction.update_xaxes(tickangle=45)
    
    # 添加政策要求线
    fig_reduction.add_hline(y=65, line_dash="dash", line_color="green", 
                           annotation_text="EU RED II要求 (≥65%)")
    fig_reduction.add_hline(y=10, line_dash="dash", line_color="orange",
                           annotation_text="CORSIA要求 (≥10%)")
    
    st.plotly_chart(fig_reduction, use_container_width=True)

# 电力来源详细对比表
st.markdown("### 📊 电力来源详细分析")

# 创建展示表格
elec_display = electricity_analysis.copy()
elec_display = elec_display.rename(columns={
    'electricity_source': '电力来源',
    'carbon_intensity': '碳强度 (kg CO2e/kWh)',
    'saf_emissions_mjbasis': '总排放量 (g CO2e/MJ)',
    'emission_reduction': '减排率 (%)',
    'electrolysis_emissions': '电解排放 (g CO2e/MJ)',
    'electrolysis_contribution': '电解贡献 (%)'
})

# 添加政策合规性列
def check_compliance(reduction):
    if reduction >= 65:
        return "✅ EU RED II"
    elif reduction >= 20:
        return "⚠️ CA LCFS"
    elif reduction >= 10:
        return "⚠️ CORSIA"
    else:
        return "❌ 不合规"

elec_display['政策合规'] = elec_display['减排率 (%)'].apply(check_compliance)

# 电力来源分类
def categorize_source(source):
    renewables = ['wind', 'solar', 'hydro', 'renewable_mix', 'renewable']
    nuclear = ['nuclear']
    fossil = ['coal', 'natural_gas']
    grid = ['grid_global', 'grid_eu', 'grid_us', 'grid_china']
    
    if source in renewables:
        return "🌱 可再生"
    elif source in nuclear:
        return "⚛️ 核能"
    elif source in fossil:
        return "🔥 化石"
    elif source in grid:
        return "🏭 电网"
    else:
        return "❓ 其他"

elec_display['电力类型'] = elec_display['电力来源'].apply(categorize_source)

# 格式化数值
for col in ['碳强度 (kg CO2e/kWh)', '总排放量 (g CO2e/MJ)', '减排率 (%)', '电解排放 (g CO2e/MJ)', '电解贡献 (%)']:
    if col in elec_display.columns:
        elec_display[col] = elec_display[col].round(3)

# 显示表格
st.dataframe(
    elec_display[['电力来源', '电力类型', '碳强度 (kg CO2e/kWh)', '总排放量 (g CO2e/MJ)', '减排率 (%)', '政策合规']].round(3), 
    use_container_width=True, 
    hide_index=True
)

# 关键洞察
st.markdown("### 🔍 关键洞察")
best_source = electricity_analysis.loc[electricity_analysis['saf_emissions_mjbasis'].idxmin()]
worst_source = electricity_analysis.loc[electricity_analysis['saf_emissions_mjbasis'].idxmax()]
current_source_data = electricity_analysis[electricity_analysis['electricity_source'] == electricity_source].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.success(f"""
    **🏆 最佳电力来源**
    - 来源: {best_source['electricity_source']}
    - 排放: {best_source['saf_emissions_mjbasis']:.1f} g CO₂e/MJ
    - 减排: {best_source['emission_reduction']:.1f}%
    """)

with col2:
    st.error(f"""
    **⚠️ 最差电力来源**
    - 来源: {worst_source['electricity_source']}
    - 排放: {worst_source['saf_emissions_mjbasis']:.1f} g CO₂e/MJ
    - 减排: {worst_source['emission_reduction']:.1f}%
    """)

with col3:
    st.info(f"""
    **📊 当前电力来源**
    - 来源: {electricity_source}
    - 排放: {current_source_data['saf_emissions_mjbasis']:.1f} g CO₂e/MJ
    - 减排: {current_source_data['emission_reduction']:.1f}%
    """)

# 电力优化建议
st.markdown(f"""
### 💡 电力优化建议

- **短期策略**: 优先使用风能、太阳能等可再生电力
- **中期策略**: 投资电网清洁化，减少对化石电力依赖  
- **长期策略**: 发展储能技术，提高可再生电力利用率

**电解阶段关键性**: 电解排放通常占总排放的 **{current_source_data['electrolysis_contribution']:.1f}%**，是减排的关键环节
""")

# 运输方式影响分析
st.markdown('<h2 class="sub-header">🚛 运输方式影响分析</h2>', unsafe_allow_html=True)

# 运行运输敏感性分析
transport_analysis = model.analyze_transport_modes(base_distance=transport_distance)

# 显示运输方式比较
fig_transport = go.Figure()

transport_modes = transport_analysis['transport_mode'].tolist()
transport_emissions = transport_analysis['saf_emissions_mjbasis'].tolist()

# 高亮当前选择的运输方式
colors = ['#FF6B6B' if mode == transport_mode else '#4ECDC4' for mode in transport_modes]

fig_transport.add_trace(go.Bar(
    x=transport_modes,
    y=transport_emissions,
    marker_color=colors,
    text=[f"{e:.1f}" for e in transport_emissions],
    textposition='auto',
    name='总排放量'
))

fig_transport.update_layout(
    title=f"不同运输方式的排放比较 (距离: {transport_distance} km)",
    xaxis_title="运输方式",
    yaxis_title="总排放量 (g CO2e/MJ)",
    height=400,
    showlegend=False
)

st.plotly_chart(fig_transport, use_container_width=True)

# 显示运输方式详细数据
st.markdown("### 📊 运输方式详细对比")
transport_display = transport_analysis.copy()
transport_display = transport_display.rename(columns={
    'transport_mode': '运输方式',
    'emission_factor': '排放因子 (kg CO2e/tonne-km)',
    'energy_factor': '能耗因子 (MJ/tonne-km)',
    'saf_emissions_mjbasis': '总排放量 (g CO2e/MJ)',
    'transport_emissions': '运输排放 (g CO2e/MJ)',
    'transport_contribution': '运输贡献 (%)'
})

# 格式化数值显示
for col in ['排放因子 (kg CO2e/tonne-km)', '能耗因子 (MJ/tonne-km)', '总排放量 (g CO2e/MJ)', '运输排放 (g CO2e/MJ)', '运输贡献 (%)']:
    if col in transport_display.columns:
        transport_display[col] = transport_display[col].round(3)

st.dataframe(transport_display[['运输方式', '排放因子 (kg CO2e/tonne-km)', '总排放量 (g CO2e/MJ)', '运输贡献 (%)']].round(3), use_container_width=True, hide_index=True)

# 详细排放数据表
st.markdown('<h3 class="sub-header">📋 详细排放数据</h3>', unsafe_allow_html=True)

# 定义阶段描述函数
def get_stage_description(stage, value, total):
    percentage = (value / total) * 100
    if stage == "carbon_capture":
        return f"DAC过程贡献{percentage:.1f}%，主要来自设备能耗"
    elif stage == "electrolysis":
        return f"电解过程贡献{percentage:.1f}%，电力来源是关键因素"
    elif stage == "conversion":
        return f"FT合成贡献{percentage:.1f}%，包括反应热和设备运行"
    elif stage == "distribution":
        return f"运输分配贡献{percentage:.1f}%，距离和运输方式影响"
    elif stage == "use_phase":
        return f"使用阶段贡献{percentage:.1f}%，理论上为碳中性"
    else:
        return f"该阶段贡献{percentage:.1f}%"

# 创建详细数据表
detailed_data = []
for stage in stages:
    stage_value = emissions_data[stage] * 1000
    percentage = (stage_value / total_emissions) * 100
    detailed_data.append({
        "生产阶段": stage_names.get(stage, stage),
        "排放量 (g CO2e/MJ)": f"{stage_value:.2f}",
        "占比 (%)": f"{percentage:.1f}%",
        "贡献描述": get_stage_description(stage, stage_value, total_emissions)
    })

detailed_df = pd.DataFrame(detailed_data)
st.dataframe(detailed_df, use_container_width=True, hide_index=True)

# 排放结果摘要
st.markdown('<h3 class="sub-header">📋 排放结果摘要</h3>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔍 主要排放源")
    # 找出最大的排放源
    max_stage = max(emissions_data.items(), key=lambda x: x[1] if x[0] != "total" else 0)
    max_stage_name = stage_names.get(max_stage[0], max_stage[0])
    max_percentage = (max_stage[1] * 1000 / total_emissions) * 100
    st.info(f"**{max_stage_name}**是最大排放源，占总排放的**{max_percentage:.1f}%**")

with col2:
    st.markdown("#### 🎯 减排潜力")
    if emission_reduction < 65:
        gap = 65 - emission_reduction
        st.warning(f"需要进一步减排**{gap:.1f}%**才能达到EU RED II标准")
    else:
        excess = emission_reduction - 65
        st.success(f"超出EU RED II标准**{excess:.1f}%**")

with col3:
    st.markdown("#### ⚡ 电力影响")
    elec_emissions = emissions_data["electrolysis"] * 1000
    elec_percentage = (elec_emissions / total_emissions) * 100
    st.info(f"电解过程占总排放的**{elec_percentage:.1f}%**，优化电力来源可显著降低排放")

# 导出简化结果
st.markdown('<h3 class="sub-header">💾 导出排放数据</h3>', unsafe_allow_html=True)

if st.button("📊 导出排放分析结果", type="primary"):
    export_df = pd.DataFrame({
        '生产阶段': [stage_names.get(stage, stage) for stage in stages] + ['总计'],
        '排放量(g CO2e/MJ)': [emissions_data[stage] * 1000 for stage in stages] + [total_emissions],
        '占比(%)': [(emissions_data[stage] * 1000 / total_emissions) * 100 for stage in stages] + [100.0]
    })
    
    csv = export_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="下载排放数据CSV",
        data=csv,
        file_name="SAF_emissions_analysis.csv",
        mime="text/csv"
    )

# 页脚
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666; font-size: 0.9rem;">© 2024 SAF排放分析工具 | 专注于温室气体排放评估 | DAC → 电解 → Fischer-Tropsch工艺路线</p>',
    unsafe_allow_html=True
) 