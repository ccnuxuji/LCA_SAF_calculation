# SAF生命周期评估(LCA)模型使用说明

## 1. 模型概述

本模型用于计算基于直接空气捕获CO₂(DAC)→电解→费托合成路线的可持续航空燃料(SAF)全生命周期环境影响。模型以C₁₂H₂₆作为SAF的代表性组分，评估包括温室气体排放、能源消耗和水资源使用等环境指标。

## 2. 模型初始化参数

```python
from LCA_calculation import SAF_LCA_Model

model = SAF_LCA_Model(
    pathway="FT",           # 生产路线
                           # - "FT": 费托合成路线
  
    functional_unit="MJ",   # 功能单位，决定了所有计算结果的基准单位
                           # - "MJ": 以能量为基准
                           # - "kg": 以质量为基准
                           # - "L": 以体积为基准
  
    co2_source="DAC"       # CO₂来源
                           # - "DAC": 直接空气捕获
)
```

### 参数详解

* **pathway**: 确定使用哪种技术路线生产SAF。目前只支持"FT"（费托合成），这种方法通过将合成气（CO和H₂）通过催化反应转化为烃类。
* **functional_unit**: 定义报告结果的基准单位，影响所有计算的标准化处理。

  - "MJ"：以每兆焦能量为基准，便于与不同能源载体比较
  - "kg"：以每千克燃料为基准，便于工艺设计和物料平衡分析
  - "L"：以每升燃料为基准，便于燃料销售和使用场景分析
* **co2_source**: 指定CO₂的来源，影响碳平衡计算和减排评估。

  - "DAC"：直接空气捕获，从大气中捕获CO₂，使燃料燃烧排放基本碳中和

## 3. 输入参数详解

### 3.1 使用阶段参数

```python
model.set_use_phase_data(
    combustion_emissions=0.0,  # 燃烧排放 (kg CO₂e/kg fuel)
                              # - 使用DAC时通常设为0（碳中和）
                              # - 与燃料碳含量相关
  
    energy_density=43.0       # 能量密度 (MJ/kg fuel)
                              # - C₁₂H₂₆的低位热值
                              # - 影响功能单位转换
                              # - 典型值：43.0 MJ/kg
)
```

#### 参数详解

* **combustion_emissions**: 使用阶段的温室气体排放量，单位为kg CO₂e/kg fuel。

  - 当CO₂来源为DAC时，该值设为0是基于"碳中和"原理：燃料燃烧释放的CO₂正是之前从大气中捕获的
  - 如果使用生物质或工业捕获的CO₂，此值应根据碳循环分析进行调整
  - 此参数影响整个生命周期评估的最终碳足迹
* **energy_density**: 燃料的能量密度（低位热值），单位为MJ/kg fuel。

  - C₁₂H₂₆的能量密度为43 MJ/kg，略低于传统航空煤油（约44-45 MJ/kg）
  - 此参数关系到功能单位转换，特别是当选择"MJ"作为功能单位时
  - 能量密度越高，相同质量的燃料可以提供更多能量，对航空应用尤为重要

### 3.2 二氧化碳捕获(DAC)参数

```python
model.set_carbon_capture_data(
    capture_efficiency=80.0,    # CO₂捕获效率 (%)
                               # - 直接影响实际CO₂捕获量
                               # - 典型范围：75-85%
  
    energy_requirement=30.0,    # 能量需求 (MJ/kg CO₂)
                               # - 捕获过程所需能量
                               # - 典型范围：25-35 MJ/kg
  
    ghg_emissions=0.08,         # 捕获过程排放 (kg CO₂e/kg CO₂)
                               # - 主要来自能源消耗
                               # - 使用绿电时约0.05-0.1
  
    water_usage=5.0,            # 用水量 (L/kg CO₂)
                               # - 捕获过程的水资源消耗
                               # - 典型范围：2-7 L/kg
  
    co2_capture_rate=3.1        # CO₂捕获率 (kg CO₂/kg fuel)
                               # - 基于C₁₂H₂₆化学计量关系
                               # - 12 mol CO₂/mol C₁₂H₂₆
                               # - 528 g CO₂/170.33 g fuel = 3.1 kg/kg
)
```

#### 参数详解

* **capture_efficiency**: DAC系统捕获CO₂的效率，单位为百分比(%)。

  - 实际DAC系统通常无法捕获其处理的全部CO₂，效率在75-85%范围内
  - 效率越高，表示从空气流中提取的CO₂比例越大，但可能需要更高的能耗
  - 此参数影响实际需要处理的空气量，从而影响能耗和成本计算
  - 计算公式：实际CO₂需求 = 理论需求量 / (capture_efficiency / 100)
* **energy_requirement**: 捕获每千克CO₂所需的能量，单位为MJ/kg CO₂。

  - 目前商业DAC技术能耗在25-35 MJ/kg CO₂范围内
  - 包括吸附剂再生、空气处理、压缩等环节的能耗
  - 能量形式通常为热能和电能的组合
  - 此参数是DAC阶段碳足迹的关键驱动因素
* **ghg_emissions**: 捕获过程的直接温室气体排放，单位为kg CO₂e/kg CO₂。

  - 主要来源于捕获过程所用能源的间接排放
  - 使用可再生能源时，此值可低至0.05-0.1
  - 使用化石能源时，此值可能超过0.5，导致净减排效益降低
  - 包括吸附剂生产、更换和废弃过程的排放
* **water_usage**: 捕获过程的水资源消耗，单位为L/kg CO₂。

  - 用于冷却系统、吸附剂再生和洗涤
  - 在干燥地区，水资源消耗可能是DAC部署的限制因素
  - 先进系统通过闭环设计可以减少水消耗
* **co2_capture_rate**: 生产每千克燃料需要捕获的CO₂量，单位为kg CO₂/kg fuel。

  - 对于C₁₂H₂₆，基于化学计量关系：每摩尔C₁₂H₂₆需要12摩尔CO₂
  - 计算过程：12摩尔 × 44 g/mol = 528g CO₂，而1摩尔C₁₂H₂₆重170.33g
  - 因此捕获率为528/170.33 ≈ 3.1 kg CO₂/kg fuel
  - 此参数直接决定了生产单位燃料的碳捕获需求量

### 3.3 电解参数

```python
model.set_electrolysis_data(
    co2_electrolysis_efficiency=65.0,  # CO₂电解效率 (%)
                                      # - AEM技术的典型效率
                                      # - 影响能量需求
                                      # - 典型范围：60-70%
  
    water_electrolysis_efficiency=75.0, # 水电解效率 (%)
                                       # - 影响H₂生产能耗
                                       # - 典型范围：70-80%
  
    electricity_source="renewable",     # 电力来源
                                       # - 可选值：renewable, grid_global,
                                       # - grid_eu, grid_us, grid_china,
                                       # - natural_gas, coal, solar,
                                       # - wind, hydro等
  
    energy_input_co=28.0,              # CO生产能量输入 (MJ/kg CO)
                                      # - AEM技术的典型能耗
                                      # - 典型范围：25-35 MJ/kg
  
    energy_input_h2=55.0,              # H₂生产能量输入 (MJ/kg H₂)
                                      # - 水电解制氢能耗
                                      # - 典型范围：50-60 MJ/kg
  
    water_usage=20.0,                  # 用水量 (L/kg H₂+CO)
                                      # - 主要用于水电解
                                      # - 典型范围：15-25 L/kg
  
    electricity_carbon_intensity=None  # 电力碳强度 (kg CO₂e/kWh)
                                      # - 若为None则根据电力来源自动设置
                                      # - renewable约为0.020
)
```

#### 参数详解

* **co2_electrolysis_efficiency**: CO₂电解为CO的能量效率，单位为百分比(%)。

  - 阴离子交换膜(AEM)技术的典型效率在60-70%范围内
  - 效率定义为：转化为CO的能量与输入电能的比率
  - 此参数影响实际能源消耗计算，效率越低，实际能耗越高
  - 计算方式：实际CO需求 = 理论CO需求 / (效率 / 100)
* **water_electrolysis_efficiency**: 水电解制氢的能量效率，单位为百分比(%)。

  - 商业质子交换膜(PEM)电解槽效率通常在70-80%范围
  - 效率受电流密度、温度、压力等因素影响
  - 此参数影响氢气生产的能源消耗和碳排放
  - 计算方式：实际H₂需求 = 理论H₂需求 / (效率 / 100)
* **electricity_source**: 电解过程使用的电力来源。

  - 电力来源对最终产品碳强度有决定性影响
  - "renewable"代表可再生能源组合，通常指风能、太阳能等
  - 不同电网的碳强度差异极大，从中国电网的0.638到风能的0.011 kg CO₂e/kWh
  - 此参数会自动设置electricity_carbon_intensity的默认值
* **energy_input_co**: 生产每千克一氧化碳(CO)所需的能量输入，单位为MJ/kg CO。

  - AEM技术的能耗通常在25-35 MJ/kg CO范围内
  - 包括电解过程能耗、气体分离和压缩能耗
  - 未来技术进步可能使此值降低
  - 此值与电解效率结合计算总能耗
* **energy_input_h2**: 生产每千克氢气(H₂)所需的能量输入，单位为MJ/kg H₂。

  - 当前水电解制氢能耗在50-60 MJ/kg H₂范围内
  - 氢能生产是整个路线中能耗最高的环节之一
  - 技术进步趋势是降低此能耗，提高系统效率
  - 氢能的能量密度(120-142 MJ/kg)高于能耗，确保了正能量回报
* **water_usage**: 电解过程的水资源消耗，单位为L/kg (H₂+CO)。

  - 主要用于水电解产氢
  - 按理论计算，生产1kg氢气需要约9L水，但实际工艺需求更高
  - 包括冷却水、净化水等辅助用水
  - 在缺水地区可能需要考虑海水淡化，增加能耗和成本
* **electricity_carbon_intensity**: 电力的碳强度，单位为kg CO₂e/kWh。

  - 若为None，则根据electricity_source自动设置
  - 对于"renewable"默认值为0.020 kg CO₂e/kWh
  - 此参数直接决定电解过程的间接碳排放
  - 碳强度越低，SAF的生命周期减排潜力越大

### 3.4 费托合成参数

```python
model.set_conversion_data(
    technology="Fischer-Tropsch",  # 技术类型
                                  # - 目前仅支持FT合成
  
    efficiency=0.65,              # 能量转化效率 (MJ fuel/MJ feedstock)
                                 # - 原料能量转化为燃料能量的效率
                                 # - 典型范围：0.60-0.70
  
    ghg_emissions=0.2,            # 合成过程排放 (kg CO₂e/kg fuel)
                                 # - 主要来自催化剂再生和工艺排放
                                 # - 典型范围：0.1-0.3
  
    energy_input=25.0,            # 能量输入 (MJ/kg fuel)
                                 # - 合成过程外部能量需求
                                 # - 典型范围：20-30 MJ/kg
  
    water_usage=5.0,              # 用水量 (L/kg fuel)
                                 # - 主要用于冷却和分离
                                 # - 典型范围：3-7 L/kg
  
    syngas_requirement=2.13,      # 合成气需求 (kg syngas/kg fuel)
                                 # - 基于C₁₂H₂₆化学计量关系
                                 # - 每摩尔C₁₂H₂₆需12摩尔CO和13摩尔H₂
                                 # - 362 g syngas/170.33 g fuel = 2.13 kg/kg
  
    co_h2_ratio=0.923            # CO:H₂比例
                                 # - 基于C₁₂H₂₆要求的比例(12:13)
)
```

#### 参数详解

* **technology**: 合成技术类型。

  - 目前模型仅支持"Fischer-Tropsch"(FT)合成
  - FT合成是将合成气转化为线性烃类的催化过程
  - 不同FT技术有高温(HTFT)和低温(LTFT)之分，影响产物分布
  - 此参数预留未来支持其他合成路线，如甲醇转化为汽油(MTG)
* **efficiency**: 能量转化效率，单位为MJ fuel/MJ feedstock。

  - 表示合成气中的化学能转化为最终燃料的比例
  - 典型范围在0.60-0.70之间
  - 受催化剂性能、反应条件、选择性等因素影响
  - 此效率不考虑外部能量输入，仅指化学能转化效率
* **ghg_emissions**: 合成过程的直接温室气体排放，单位为kg CO₂e/kg fuel。

  - 主要来源包括：
    1. 催化剂再生过程中碳沉积物的燃烧
    2. 工艺气体的逃逸排放
    3. 设备泄漏
    4. 能源使用的直接排放
  - 典型范围在0.1-0.3 kg CO₂e/kg fuel
  - 排放量受工艺设计和操作条件影响
* **energy_input**: 合成过程的外部能量需求，单位为MJ/kg fuel。

  - 包括加热、压缩、搅拌、产物分离等过程的能耗
  - 不包括合成气本身的能量含量
  - 典型范围在20-30 MJ/kg fuel
  - FT反应是放热反应，但整体工艺仍需外部能量输入
* **water_usage**: 合成过程的水资源消耗，单位为L/kg fuel。

  - 主要用于反应冷却和产物分离
  - 水消耗随工艺条件和设备设计变化
  - 典型范围在3-7 L/kg fuel
  - 先进的工艺设计可通过水循环减少消耗
* **syngas_requirement**: 生产单位燃料所需的合成气量，单位为kg syngas/kg fuel。

  - 对于C₁₂H₂₆，基于化学计量关系计算：
    1. 每摩尔C₁₂H₂₆需要12摩尔CO和13摩尔H₂
    2. CO质量: 12摩尔 × 28 g/mol = 336 g
    3. H₂质量: 13摩尔 × 2 g/mol = 26 g
    4. 合成气总质量: 362 g
    5. C₁₂H₂₆摩尔质量: 170.33 g
    6. 因此需求比: 362/170.33 ≈ 2.13 kg/kg
  - 此参数影响资源需求量和成本计算
* **co_h2_ratio**: 合成气中CO与H₂的摩尔比例。

  - 对于C₁₂H₂₆，基于化学计量关系为12:13，即0.923
  - 此比例影响合成气组成和产物分布
  - 比例偏离化学计量比会导致原料利用率下降
  - 实际操作中可能略微调整以优化产品选择性

### 3.5 运输参数

```python
model.set_distribution_data(
    transport_distance=500.0,  # 运输距离 (km)
                              # - 生产地到使用地的距离
  
    transport_mode="truck",    # 运输方式
                              # - 可选："truck", "rail", "ship"
  
    ghg_emissions=0.05,       # 运输过程排放 (kg CO₂e/kg fuel)
                              # - 与运输方式和距离相关
                              # - 典型范围：0.03-0.08
  
    energy_input=2.0          # 能量输入 (MJ/kg fuel)
                              # - 运输过程能量消耗
                              # - 典型范围：1.5-3.0
)
```

#### 参数详解

* **transport_distance**: 运输距离，单位为km。

  - 表示从生产设施到终端使用点的平均距离
  - 对于区域性分布的SAF，典型距离为300-700 km
  - 距离越长，运输环节的排放和能耗贡献越大
  - 在实际项目中，应根据具体的地理位置设置
* **transport_mode**: 运输方式。

  - "truck": 公路运输，适合中短距离和陆地运输
  - "rail": 铁路运输，适合长距离陆地运输，碳强度低于公路
  - "ship": 船舶运输，适合跨洋远距离运输
  - 不同运输方式有不同的排放因子和能耗特性
* **ghg_emissions**: 运输过程的温室气体排放，单位为kg CO₂e/kg fuel。

  - 排放量与运输方式、距离和效率相关
  - 卡车运输的典型值在0.03-0.08 kg CO₂e/kg fuel范围
  - 包括燃料燃烧的直接排放和基础设施的间接排放
  - 在生命周期评估中，运输通常贡献5-10%的总排放
* **energy_input**: 运输过程的能量消耗，单位为MJ/kg fuel。

  - 包括运输工具的燃料消耗和相关基础设施的能耗
  - 典型范围在1.5-3.0 MJ/kg fuel
  - 不同运输方式的能效差异：通常船舶>铁路>卡车
  - 在总能耗中，运输环节通常占比较低

## 4. 计算方法详解

### 4.1 生命周期排放计算

#### 归一化处理

所有计算结果根据功能单位进行归一化：

```python
# 单位转换因子
if functional_unit == "MJ":
    normalization_factor = 1 / energy_density  # kg fuel/MJ
elif functional_unit == "kg":
    normalization_factor = 1  # kg fuel/kg
elif functional_unit == "L":
    normalization_factor = 0.8  # kg fuel/L (假设密度约0.8)
```

**归一化处理说明**：

* 归一化是将所有计算结果统一到选定的功能单位上，确保结果具有可比性
* 当功能单位为"MJ"时，normalization_factor为1/energy_density (kg fuel/MJ)，表示提供每MJ能量需要多少kg燃料
* 当功能单位为"kg"时，normalization_factor为1，表示计算结果基于每kg燃料
* 当功能单位为"L"时，normalization_factor为0.8 (kg fuel/L)，基于SAF燃料密度约为0.8 kg/L的假设
* 归一化因子应用于所有环境影响指标（GHG排放、能耗、水耗等）

#### 碳捕获阶段排放

```python
# 考虑捕获效率计算实际CO₂需求量
actual_co2_needed = co2_capture_rate / (capture_efficiency / 100)
carbon_capture_ghg = ghg_emissions * actual_co2_needed * normalization_factor
```

**计算逻辑说明**：

* 首先计算实际CO₂需求量(actual_co2_needed)：由于捕获效率小于100%，实际需要处理的CO₂量大于理论量
* 例如：若理论需要捕获3.1 kg CO₂/kg fuel，捕获效率为80%，则实际需要处理3.1/(80/100) = 3.875 kg CO₂
* 碳捕获阶段排放计算考虑了捕获过程本身的排放强度(ghg_emissions)乘以实际处理量
* 最后应用归一化因子，转换为每功能单位的排放量

#### 电解阶段排放

```python
# 转换电力碳强度单位(kg CO₂e/kWh → kg CO₂e/MJ)
elec_intensity_mj = electricity_carbon_intensity / 3.6  # 1 kWh = 3.6 MJ

# 计算所需CO和H₂量
total_syngas_needed = syngas_requirement * normalization_factor
co_needed = total_syngas_needed * (co_h2_ratio / (1 + co_h2_ratio))
h2_needed = total_syngas_needed * (1 / (1 + co_h2_ratio))

# 考虑电解效率影响
actual_co_needed = co_needed / (co2_electrolysis_efficiency / 100)
actual_h2_needed = h2_needed / (water_electrolysis_efficiency / 100)

# 计算排放
co_emissions = actual_co_needed * energy_input_co * elec_intensity_mj
h2_emissions = actual_h2_needed * energy_input_h2 * elec_intensity_mj
electrolysis_ghg = co_emissions + h2_emissions
```

**计算逻辑说明**：

* 首先将电力碳强度单位从kg CO₂e/kWh转换为kg CO₂e/MJ，便于与能量输入单位匹配
* 计算每功能单位所需的合成气总量(total_syngas_needed)
* 根据CO:H₂比例(co_h2_ratio)计算所需的CO量和H₂量
* 考虑电解效率影响，计算实际需要投入生产的CO和H₂量
  - 例如：若CO需求为0.040 kg/MJ，电解效率为65%，则实际需要处理的量为0.040/(65/100) = 0.062 kg/MJ
* 分别计算CO电解和H₂电解的碳排放：
  - CO排放 = 实际CO生产量 × CO单位能耗 × 电力碳强度
  - H₂排放 = 实际H₂生产量 × H₂单位能耗 × 电力碳强度
* 电解阶段总排放是CO和H₂生产排放之和

#### 费托合成阶段排放

```python
conversion_ghg = ghg_emissions * normalization_factor
```

**计算逻辑说明**：

* 费托合成阶段排放计算相对简单，基于工艺直接排放因子(ghg_emissions)
* 应用归一化因子，转换为每功能单位的排放量
* 此处排放不包括能源消耗导致的间接排放，仅指合成过程本身的直接排放

#### 运输阶段排放

```python
distribution_ghg = ghg_emissions * normalization_factor
```

**计算逻辑说明**：

* 类似费托合成阶段，运输阶段排放基于直接排放因子(ghg_emissions)
* 应用归一化因子，转换为每功能单位的排放量
* 排放因子已综合考虑运输距离和运输方式的影响

#### 使用阶段排放

```python
# DAC路径下通常为零(碳中和)
use_phase_ghg = combustion_emissions * normalization_factor
```

**计算逻辑说明**：

* 使用阶段排放主要来自燃料燃烧
* 当CO₂来源为DAC时，燃烧排放通常设为零，基于碳中和原理
* 如果来源不是DAC，则应根据燃料碳含量和碳循环分析设置适当的排放值
* 应用归一化因子，转换为每功能单位的排放量

#### 总排放计算

```python
total_ghg = carbon_capture_ghg + electrolysis_ghg + conversion_ghg + distribution_ghg + use_phase_ghg
```

**计算逻辑说明**：

* 总排放是各阶段排放的简单累加
* 所有阶段排放已统一到相同的功能单位，可以直接相加
* 此总排放用于后续减排率计算和结果分析

### 4.2 能源消耗计算

#### 碳捕获能耗

```python
carbon_capture_energy = energy_requirement * actual_co2_needed * normalization_factor
```

**计算逻辑说明**：

* 碳捕获能耗基于单位捕获能耗(energy_requirement)和实际捕获量(actual_co2_needed)
* 实际捕获量已考虑捕获效率的影响
* 应用归一化因子，转换为每功能单位的能耗

#### 电解能耗

```python
# 考虑电解效率
actual_co_needed = co_needed / (co2_electrolysis_efficiency / 100)
actual_h2_needed = h2_needed / (water_electrolysis_efficiency / 100)

co_energy = actual_co_needed * energy_input_co
h2_energy = actual_h2_needed * energy_input_h2
electrolysis_energy = (co_energy + h2_energy) * normalization_factor
```

**计算逻辑说明**：

* 首先考虑电解效率，计算实际CO和H₂生产量
* 分别计算CO电解和H₂电解的能耗：
  - CO能耗 = 实际CO生产量 × CO单位能耗
  - H₂能耗 = 实际H₂生产量 × H₂单位能耗
* 电解阶段总能耗是CO和H₂生产能耗之和
* 应用归一化因子，转换为每功能单位的能耗

#### 费托合成能耗

```python
conversion_energy = energy_input * normalization_factor
```

**计算逻辑说明**：

* 费托合成能耗基于单位能耗因子(energy_input)
* 此能耗指合成过程所需的外部能量输入，不包括合成气的能量含量
* 应用归一化因子，转换为每功能单位的能耗

#### 运输能耗

```python
distribution_energy = energy_input * normalization_factor
```

**计算逻辑说明**：

* 运输能耗基于单位能耗因子(energy_input)
* 能耗因子综合考虑运输距离、运输方式和燃料效率
* 应用归一化因子，转换为每功能单位的能耗

#### 总能耗计算

```python
total_energy = carbon_capture_energy + electrolysis_energy + conversion_energy + distribution_energy
```

**计算逻辑说明**：

* 总能耗是各阶段能耗的简单累加
* 所有阶段能耗已统一到相同的功能单位，可以直接相加
* 此总能耗用于计算能源回报率(EROI)和能源效率分析

### 4.3 水资源使用计算

```python
carbon_capture_water = water_usage * actual_co2_needed * normalization_factor
electrolysis_water = water_usage * total_syngas_needed
conversion_water = water_usage * normalization_factor
total_water = carbon_capture_water + electrolysis_water + conversion_water
```

**计算逻辑说明**：

* 各阶段水资源使用基于对应的用水因子和处理量
* 碳捕获用水 = 单位CO₂捕获用水量 × 实际CO₂捕获量
* 电解用水 = 单位合成气生产用水量 × 总合成气需求量
* 费托合成用水 = 单位费托合成用水量 × 归一化因子
* 总用水量是各阶段用水量的简单累加
* 所有阶段用水量已统一到相同的功能单位，可以直接相加

### 4.4 减排率计算

```python
# 化石航油基准排放
fossil_jet_emissions = 89.0  # g CO₂e/MJ

# 将SAF排放从kg转换为g
saf_emissions = total_ghg * 1000  # kg to g

# 计算减排率
reduction = (fossil_jet_emissions - saf_emissions) / fossil_jet_emissions * 100  # %
```

**计算逻辑说明**：

* 使用欧盟RED II指令中化石航油的基准排放值89.0 g CO₂e/MJ
* 将SAF的计算排放从kg CO₂e转换为g CO₂e，与基准单位保持一致
* 减排率计算公式：(基准排放 - SAF排放) / 基准排放 × 100%
* 正值表示减排，负值表示增排
* 减排率是评价SAF环境效益的关键指标：
  - > 65%：满足欧盟RED II标准
    >
  - > 10%：满足CORSIA最低要求
    >

## 5. 电力来源分析

模型支持分析不同电力来源对SAF碳强度的影响。内置的电力碳强度值(kg CO₂e/kWh)如下：

| 电力来源      | 碳强度 | 说明                   |
| ------------- | ------ | ---------------------- |
| renewable     | 0.020  | 通用可再生能源         |
| renewable_mix | 0.030  | 太阳能、风能和水电混合 |
| grid_global   | 0.475  | 全球平均电网           |
| grid_eu       | 0.253  | 欧盟平均电网           |
| grid_us       | 0.389  | 美国平均电网           |
| grid_china    | 0.638  | 中国平均电网           |
| natural_gas   | 0.410  | 天然气发电             |
| coal          | 0.820  | 煤电                   |
| solar         | 0.048  | 太阳能                 |
| wind          | 0.011  | 风能                   |
| hydro         | 0.024  | 水电                   |
| nuclear       | 0.012  | 核电                   |

### 电力来源分析方法

模型提供了 `analyze_electricity_sources`方法，可以评估不同电力来源对SAF碳强度的影响：

```python
electricity_analysis = model.analyze_electricity_sources()
```

此方法将：

1. 保存当前电力相关参数
2. 对每种电力来源进行LCA计算
3. 恢复原始参数设置
4. 返回包含所有电力来源分析结果的DataFrame

分析结果包括：

- **carbon_intensity**: 电力碳强度(kg CO₂e/kWh)
- **saf_emissions_mjbasis**: SAF碳强度(g CO₂e/MJ)
- **emission_reduction**: 相对于化石航油的减排率(%)
- **electrolysis_emissions**: 电解阶段排放(g CO₂e/MJ)
- **electrolysis_contribution**: 电解排放占总排放的百分比(%)

### 电力来源重要性分析

电力来源对SAF碳强度的影响极为显著，这是因为：

1. **高电力依赖性**: e-SAF生产过程中，电解阶段(CO₂电解和水电解)通常消耗总能量的70-80%
2. **碳强度差异大**: 不同电力来源的碳强度差别巨大

   - 煤电(0.820 kg CO₂e/kWh)的碳强度约为风能(0.011 kg CO₂e/kWh)的75倍
   - 即使是天然气发电(0.410 kg CO₂e/kWh)也比可再生能源高出约20倍
3. **关键策略意义**:

   - 使用可再生能源可实现65-80%的减排
   - 使用化石燃料发电可能导致负减排率，即SAF排放高于传统航油
   - 电力碳强度是项目规划和政策制定的关键考量

### 可视化方法

模型提供三种可视化方式分析电力来源影响：

```python
# 不同电力来源的SAF碳强度对比
model.plot_electricity_analysis(electricity_analysis, plot_type="emissions")

# 不同电力来源的减排率对比
model.plot_electricity_analysis(electricity_analysis, plot_type="reduction")

# 电解阶段排放在总排放中的占比
model.plot_electricity_analysis(electricity_analysis, plot_type="contribution")
```

这些可视化图表有助于:

- 直观评估电力来源对项目环境效益的影响
- 确定关键减排阈值的实现条件
- 为政策制定和项目规划提供参考依据

## 6. 注意事项与建议

### 6.1 单位一致性

**重要性**: 确保所有输入参数使用指定单位对于获得正确结果至关重要。

**关键注意点**:

- 能量单位统一使用MJ，而非kWh或其他单位
- 温室气体排放使用kg CO₂e，而非吨或g
- 质量单位统一使用kg，而非吨或g
- 效率参数使用百分比(%)，而非小数

**常见错误**:

- 混淆电力碳强度的单位，误用g CO₂e/kWh而非kg CO₂e/kWh
- 混淆能量密度单位，误用MJ/L而非MJ/kg
- 将电解效率以小数输入(如0.65)而非百分比(65.0)

**自动转换**:

- 模型会自动根据功能单位进行单位转换
- 当功能单位为"MJ"时，所有基于质量的参数会自动转换为能量基准
- 报告减排率时，排放会自动转换为g CO₂e/MJ便于与标准比较

### 6.2 参数合理性

**效率参数**:

- 所有效率参数不应超过100%，这违反能量守恒原理
- 极高的效率值(>95%)通常不符合实际技术水平，应谨慎使用
- 应考虑技术成熟度，实验室效率通常高于商业化效率

**能量输入**:

- 能量输入应反映实际工艺能耗，包括主要和辅助过程
- 过低的能耗可能忽略了辅助系统(如压缩、分离、净化)
- 过高的能耗可能重复计算了某些能源流

**CO:H₂比例**:

- CO:H₂比例应基于目标产物的化学计量关系
- 对于C₁₂H₂₆，理论比例为12:13(约0.923)
- 偏离理论比例会导致原料利用率降低或产品分布改变
- 实际操作可能需要轻微调整比例以优化催化性能

**参数之间的相互关系**:

- 捕获效率与能耗通常存在权衡，高效率可能需要更高能耗
- 电解效率与能耗有反比关系，应保持一致性
- 合成气需求量与CO:H₂比例相关，更改比例时应同步调整需求量

### 6.3 电力来源选择

**环境影响决定因素**:

- 电力来源是整个生命周期环境影响的主要决定因素
- 即使其他参数优化到极致，使用煤电仍将导致较高的碳排放
- 对于相同工艺条件，仅切换电力来源可导致减排率从-450%到+80%的巨大差异

**电力组合考量**:

- 大规模项目通常依赖混合电力来源
- "renewable_mix"(0.030 kg CO₂e/kWh)比单一可再生能源略高
- 区域电网(如grid_eu、grid_us)可能因时间变化而碳强度不同
- 应考虑项目地点的实际可用电力来源

**政策合规性**:

- 欧盟RED II要求SAF减排率>65%，这通常需要低碳电力(<0.1 kg CO₂e/kWh)
- CORSIA要求SAF减排率>10%，可接受部分化石能源混合的电力
- 政策框架可能要求特定比例的可再生电力用于SAF生产

**经济与环境平衡**:

- 可再生电力通常价格较高，但带来更好的环境效益
- 考虑时间匹配性：间歇性可再生能源可能需要存储或备用系统
- 优先使用低碳电力于电解等高电力消耗环节

### 6.4 结果解释

**减排率标准**:

- 减排率>65%: 满足欧盟RED II标准，被认为是高质量SAF
- 减排率>50%: 被视为显著减排，符合多数国家的激励计划要求
- 减排率>10%: 满足CORSIA最低要求，允许用于国际航空减排
- 减排率<0%: 表示相比传统航油反而增加排放，不应被推广

**敏感性分析**:

- 使用可再生电力时，电解效率和能耗参数对减排率影响最大
- 使用化石电力时，电力碳强度的影响远大于其他参数
- 高效DAC技术(低能耗、高捕获效率)对总体减排率有显著影响
- 运输阶段通常对整体结果影响较小(<5%)

**结果不确定性**:

- 所有模型参数都有不确定性范围，应考虑这种不确定性对结果的影响
- 技术进步可能降低能耗和提高效率，导致未来减排率提高
- 电网碳强度随时间变化，长期项目应考虑这种变化

**跨标准比较**:

- 不同标准(如RED II、CORSIA、LCFS)可能使用不同的化石燃料基准值
- RED II使用94 g CO₂e/MJ，而其他可能使用89 g CO₂e/MJ或其他值
- 计算方法学差异可能导致相同工艺在不同标准下获得不同减排率

### 6.5 模型局限性

**代表性成分假设**:

- 模型基于C₁₂H₂₆作为SAF的代表性组分，这是一种简化
- 实际SAF是多种烃类化合物的混合物，C₉-C₁₆范围内的烃类
- 不同碳链长度的烃类具有不同的物理化学性质和环境影响
- 此简化可能导致理论计算与实际产品存在差异

**系统边界限制**:

- 未考虑设备制造和废弃阶段的环境影响
- 未包括催化剂生产和更换的完整影响
- 忽略了基础设施建设的间接排放
- 这些被忽略的影响通常占总生命周期影响的5-10%

**参数不确定性**:

- 各参数为平均值，实际项目有较大波动范围
- 新技术的参数可能缺乏大规模验证数据
- 随着技术进步，参数值会随时间变化
- 应进行敏感性分析和蒙特卡洛模拟评估不确定性

**方法学局限**:

- 使用100年全球变暖潜能值(GWP100)，可能低估短期气候影响
- 未考虑间接土地利用变化
- 仅评估温室气体排放、能耗和水耗，未包括其他环境影响类别
- 不包括社会经济影响分析

### 6.6 实际应用建议

**参数选择**:

- 使用保守参数进行基本评估，避免过于乐观的假设
- 对关键参数进行敏感性分析，识别改进重点
- 根据实际地理位置和技术选择调整输入参数
- 随着设计细化逐步精确化参数

**减排策略优先级**:

1. 使用低碳电力，这是最有效的减排措施
2. 提高电解效率，直接降低能耗和排放
3. 优化DAC技术，降低捕获能耗
4. 改进FT合成选择性，提高目标产物产率
5. 考虑能量集成，利用过程余热降低外部能源需求

**政策合规性考量**:

- 提前了解目标市场的监管要求
- 保留详细的计算过程和参数选择依据
- 考虑不同情景下的合规性风险
- 探索碳信用和激励机制对经济可行性的影响

**技术路线选择**:

- 综合评估不同技术组合的环境绩效
- 考虑放大效应：实验室到工业规模的效率和能耗变化
- 评估技术成熟度与环境绩效的平衡
- 关注未来技术进步趋势，制定阶段性优化计划
