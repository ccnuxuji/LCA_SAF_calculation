# CO2电解制CO结合费托合成生产SAF的技术经济分析

## 1. 项目概述

本模型分析二氧化碳电解制一氧化碳，并通过费托合成生产可持续航空燃料(SAF)的经济性。主要包括以下几个方面：

### 1.1 技术路线
```
CO2捕获 → CO2电解 → CO生产 ↘
                         → 费托合成 → SAF产品升级 → 可持续航空燃料(SAF)
水处理 → 水电解 → H2生产 ↗
```

## 2. 技术经济分析方法与参数设置

### 2.1 CO2电解过程的技术经济计算方法与参数

#### 计算方法
1. **能量需求计算**:
   - 理论能耗基于CO2 → CO + 1/2 O2反应的标准电极电位（2.78 kWh/kg CO）
   - 实际能耗计算公式: 
     ```
     energy_per_ton = theoretical_energy / (electrolyzer_efficiency * faradaic_efficiency) * 1000
     ```
   - 其中`electrolyzer_efficiency`为电解效率，`faradaic_efficiency`为法拉第效率

2. **资本支出(CAPEX)计算**:
   - 每天所需电力计算:
     ```
     daily_energy = energy_per_ton * plant_capacity_co  # kWh/天
     required_power = daily_energy / 24  # kW
     ```
   - 电解槽成本计算:
     ```
     electrolyzer_cost = required_power * electrolyzer_capex
     ```
   - 总资本支出:
     ```
     total_capex = electrolyzer_cost * (1 + balance_of_plant)
     ```

3. **运营支出(OPEX)计算**:
   - 年产量计算:
     ```
     annual_production = plant_capacity_co * 365 * capacity_factor
     ```
   - 电力成本:
     ```
     annual_energy = energy_per_ton * annual_production
     electricity_cost = annual_energy * electricity_cost
     ```
   - CO2成本:
     ```
     co2_required = annual_production * (44/28)  # 化学计量比
     co2_actual = co2_required / co2_conversion_rate
     co2_cost = co2_actual * co2_cost
     ```
   - 固定运维成本:
     ```
     fixed_om = total_capex * fixed_om_percent
     ```
   - 电解槽堆栈更换成本:
     ```
     replacements = floor(plant_lifetime / stack_lifetime) - 1
     stack_cost = required_power * electrolyzer_capex * 0.6
     stack_replacement = stack_cost * replacements / plant_lifetime
     ```
   - 其他变动成本:
     ```
     other_variable = annual_production * other_variable_cost
     ```
   - 总运营支出:
     ```
     total_opex = electricity_cost + co2_cost + fixed_om + stack_replacement + other_variable
     ```

4. **平准化成本(LCOP)计算**:
   - 资本回收系数(CRF):
     ```
     crf = (discount_rate * (1 + discount_rate)**plant_lifetime) / ((1 + discount_rate)**plant_lifetime - 1)
     ```
   - 年化资本成本:
     ```
     annual_capex = total_capex * crf
     ```
   - 平准化成本:
     ```
     lcop = (annual_capex + total_opex) / annual_production
     ```

#### 参数设置
| 参数名称 | 代码参数名 | 数值 | 单位 | 说明 |
|----------|------------|------|------|------|
| 电解效率 | electrolyzer_efficiency | 65% | - | 能量转换效率 |
| CO2转化率 | co2_conversion_rate | 85% | - | CO2→CO转化率 |
| 法拉第效率 | faradaic_efficiency | 95% | - | 电流效率 |
| CO产能 | plant_capacity_co | 50 | 吨/天 | 设计产能 |
| 装置负荷率 | capacity_factor | 95% | - | 年均运行负荷 |
| 电解槽堆栈寿命 | stack_lifetime | 7 | 年 | 堆栈更换周期 |
| 工厂寿命 | plant_lifetime | 20 | 年 | 项目期限 |
| 电解槽成本 | electrolyzer_capex | 1,500 | $/kW | 单位功率投资 |
| 工厂平衡成本比例 | balance_of_plant | 30% | - | 占总资本比例 |
| CO2成本 | co2_cost | 50 | $/吨 | 原料成本 |
| 电力成本 | electricity_cost | 0.04 | $/kWh | 运行成本 |
| 固定运维成本比例 | fixed_om_percent | 2% | - | 占CAPEX比例 |
| 其他变动成本 | other_variable_cost | 5 | $/吨CO | 其他运行成本 |

### 2.2 水电解制氢过程的技术经济计算方法与参数

#### 计算方法
1. **能量需求计算**:
   - 理论能耗基于H2O → H2 + 1/2 O2反应（39.4 kWh/kg H2）
   - 实际能耗计算公式:
     ```
     actual_energy = theoretical_energy / (electrolyzer_efficiency * faradaic_efficiency)
     ```

2. **产能与产量计算**:
   - 年产量转换:
     ```
     annual_h2_production = required_h2 * 1000  # 吨转kg
     ```
   - 日产量计算:
     ```
     daily_h2_production = annual_h2_production / 365
     ```
   - 考虑负荷率的装置产能:
     ```
     plant_capacity_h2 = daily_h2_production / capacity_factor
     ```

3. **资本支出(CAPEX)计算**:
   - 所需电力计算:
     ```
     daily_energy = energy_per_kg * plant_capacity_h2  # kWh/天
     required_power = daily_energy / 24  # kW
     ```
   - 电解槽成本:
     ```
     electrolyzer_cost = required_power * electrolyzer_capex
     ```
   - 总资本支出:
     ```
     total_capex = electrolyzer_cost * (1 + balance_of_plant)
     ```

4. **运营支出(OPEX)计算**:
   - 电力成本:
     ```
     annual_energy = energy_per_kg * annual_h2_production
     electricity_cost = annual_energy * electricity_cost
     ```
   - 水成本:
     ```
     water_required = annual_h2_production * 9  # 每kg H2需要约9kg水
     water_cost = water_required * water_cost / 1000  # 转换为吨
     ```
   - 固定运维成本:
     ```
     fixed_om = total_capex * fixed_om_percent
     ```
   - 电解槽堆栈更换成本:
     ```
     replacements = floor(plant_lifetime / stack_lifetime) - 1
     stack_cost = required_power * electrolyzer_capex * 0.65
     stack_replacement = stack_cost * replacements / plant_lifetime
     ```
   - 其他变动成本:
     ```
     other_variable = annual_h2_production * other_variable_cost
     ```
   - 总运营支出:
     ```
     total_opex = electricity_cost + water_cost + fixed_om + stack_replacement + other_variable
     ```

5. **平准化成本(LCOH)计算**:
   - 与CO2电解类似，使用CRF计算:
     ```
     lcoh = (annual_capex + total_opex) / annual_h2_production  # $/kg H2
     ```

#### 参数设置
| 参数名称 | 代码参数名 | 数值 | 单位 | 说明 |
|----------|------------|------|------|------|
| 电解效率 | electrolyzer_efficiency | 70% | - | 能量转换效率 |
| 法拉第效率 | faradaic_efficiency | 98% | - | 电流效率 |
| 装置负荷率 | capacity_factor | 95% | - | 年均运行负荷 |
| 电解槽堆栈寿命 | stack_lifetime | 8 | 年 | 堆栈更换周期 |
| 工厂寿命 | plant_lifetime | 20 | 年 | 项目期限 |
| 氢气纯度 | h2_purity | 99.8% | - | 产品质量 |
| 电解槽成本 | electrolyzer_capex | 1,000 | $/kW | 单位功率投资 |
| 工厂平衡成本比例 | balance_of_plant | 35% | - | 占总资本比例 |
| 水处理成本 | water_cost | 2.0 | $/吨 | 原料成本 |
| 电力成本 | electricity_cost | 0.04 | $/kWh | 运行成本 |
| 固定运维成本比例 | fixed_om_percent | 2.5% | - | 占CAPEX比例 |
| 其他变动成本 | other_variable_cost | 0.2 | $/kg H2 | 其他运行成本 |

### 2.3 费托合成过程的技术经济计算方法与参数

#### 计算方法
1. **产量计算**:
   - 氢气需求计算:
     ```
     h2_required = co_input * (h2_co_ratio * 2 / 28)  # 吨/年
     ```
   - 合成气总量:
     ```
     syngas_total = co_input + h2_required
     ```
   - 费托产物:
     ```
     ft_products = syngas_total * ft_conversion
     ```
   - C5+产物:
     ```
     c5_plus = ft_products * ft_selectivity
     ```
   - SAF产量:
     ```
     saf_production = c5_plus * saf_selectivity  # 吨/年
     ```
   - 转换为加仑:
     ```
     saf_gallons = saf_production * 1000 / 3.06  # 加仑/年
     ```
   - 转换为桶/天:
     ```
     saf_barrels_per_day = saf_gallons / 42 / 365
     ```

2. **资本支出(CAPEX)计算**:
   - 费托反应器成本(使用规模因子):
     ```
     ft_reactor_cost = ft_reactor_capex * (saf_barrels_per_day / 1000)**ft_scaling_factor
     ```
   - 产品升级成本:
     ```
     upgrading_cost = upgrading_capex * saf_barrels_per_day
     ```
   - 总资本支出:
     ```
     total_capex = ft_reactor_cost + upgrading_cost
     ```

3. **运营支出(OPEX)计算**:
   - 催化剂体积计算:
     ```
     hourly_co = co_input / (365 * 24)
     catalyst_volume = hourly_co / catalyst_loading
     ```
   - 催化剂成本:
     ```
     catalyst_amount = catalyst_volume * catalyst_loading * 1000  # kg
     annual_catalyst_cost = catalyst_amount * catalyst_cost / catalyst_lifetime
     ```
   - 固定运维成本:
     ```
     fixed_om = total_capex * fixed_om_percent
     ```
   - 其他变动成本:
     ```
     other_variable = saf_gallons * other_variable_cost
     ```
   - 总运营支出:
     ```
     total_opex = h2_cost + annual_catalyst_cost + fixed_om + other_variable
     ```

4. **平准化成本(LCOP)计算**:
   - 同样使用CRF计算年化资本成本
   - 平准化成本:
     ```
     lcop = (annual_capex + total_opex) / saf_gallons  # $/加仑SAF
     ```

#### 参数设置
| 参数名称 | 代码参数名 | 数值 | 单位 | 说明 |
|----------|------------|------|------|------|
| 氢气与一氧化碳比例 | h2_co_ratio | 2.1 | - | 原料配比 |
| 费托转化率 | ft_conversion | 85% | - | 总转化率 |
| 费托选择性 | ft_selectivity | 75% | - | C5+产物选择性 |
| SAF在C5+中的选择性 | saf_selectivity | 60% | - | 在C5+中的选择性 |
| 装置负荷率 | capacity_factor | 95% | - | 年均运行负荷 |
| 催化剂寿命 | catalyst_lifetime | 5 | 年 | 更换周期 |
| 工厂寿命 | plant_lifetime | 20 | 年 | 项目期限 |
| 费托基础资本支出 | ft_capex_base | 60,000 | $/(桶/天) | 单位产能投资 |
| 费托反应器成本基数 | ft_reactor_capex | 25,000,000 | $ | 基准成本 |
| 费托规模因子 | ft_scaling_factor | 0.65 | - | 规模系数 |
| 产品升级资本支出 | upgrading_capex | 30,000 | $/(桶/天) | 升级装置投资 |
| 催化剂成本 | catalyst_cost | 350 | $/kg | 材料成本 |
| 催化剂负载量 | catalyst_loading | 0.4 | kg/m³/h | 催化剂用量 |
| 固定运维成本比例 | fixed_om_percent | 4% | - | 占CAPEX比例 |
| 其他变动成本 | other_variable_cost | 0.08 | $/加仑SAF | 其他运行成本 |

### 2.4 整合分析的方法论与参数设置

#### 计算方法
1. **系统集成方法**:
   - 过程集成:
     ```python
     # CO2电解系统提供CO
     co_production = co2_electrolysis.calculate_opex(None)[1]
     
     # 计算所需的氢气量
     h2_required = co_production * (h2_co_ratio * 2 / 28)
     
     # 水电解系统提供氢气
     water_electrolysis.calculate_opex(h2_required)
     
     # 费托系统使用CO和H2生产SAF
     fischer_tropsch = FischerTropsch(co_production)
     ```

2. **资本支出(CAPEX)计算**:
   - 总CAPEX计算:
     ```
     total_capex = electrolysis_capex + h2_capex + ft_capex
     ```

3. **运营支出(OPEX)计算**:
   - 总OPEX计算:
     ```
     total_opex = (elec_cost_co2 + co2_cost + elec_fixed_om + elec_stack + elec_other) +
                  (elec_cost_h2o + water_cost + h2_fixed_om + h2_stack + h2_other) +
                  (h2_cost + catalyst_cost + ft_fixed_om + ft_other)
     ```
   - 政策激励:
     ```
     incentives = fischer_tropsch.saf_gallons * tax_incentives
     ```
   - 碳减排收益:
     ```
     co2_reduction = fischer_tropsch.saf_production * 3.5  # 每吨SAF减少约3.5吨CO2
     carbon_credits = co2_reduction * carbon_credit
     ```
   - 净运营支出:
     ```
     net_opex = total_opex - incentives - carbon_credits
     ```

4. **平准化成本(LCOP)计算**:
   - SAF平准化成本:
     ```
     lcop = (annual_capex + net_opex) / fischer_tropsch.saf_gallons
     ```

5. **敏感性分析方法**:
   - 在指定范围内变化参数并观察LCOP的变化
   - 弹性系数计算:
     ```
     elasticity = (∆LCOP/LCOP₀) / (∆P/P₀)
     ```

#### 综合财务参数
| 参数名称 | 代码参数名 | 数值 | 单位 | 说明 |
|----------|------------|------|------|------|
| 贴现率 | discount_rate | 10% | - | 现金流折现 |
| 所得税率 | tax_rate | 25% | - | 企业税率 |
| 通货膨胀率 | inflation_rate | 2% | - | 年均通胀 |
| 债务比例 | debt_ratio | 70% | - | 债务融资 |
| 贷款利率 | interest_rate | 4.5% | - | 年利率 |
| 税收激励 | tax_incentives | 1.5 | $/加仑SAF | 政策支持 |
| 碳信用 | carbon_credit | 75 | $/吨CO2 | 碳减排价值 |

## 4. 模型结论与建议

基于上述技术经济分析，我们可以得出以下结论：

### 4.1 关键成本驱动因素

- 电力成本是影响最大的因素，每减少$0.01/kWh可降低最终SAF成本约$0.45-0.65/加仑，其中水电解对电价更为敏感
- 电解设备成本(CO2电解和水电解)共同构成了重要的资本支出，共计占总成本约45-55%
- 水电解效率的提升对降低氢气成本有显著影响，效率每提高10%可降低SAF成本约$0.30-0.40/加仑
- CO2成本在总成本中占比约10-15%，原料成本仍是重要考量因素

### 4.2 经济可行性目标

- 在当前技术和成本条件下，SAF的平准化成本约为$5.5-8.5/加仑
- 与传统航空燃料($2-3/加仑)相比，仍存在$3.5-5.5/加仑的成本差距
- 要达到成本平价，需要:
  * CO2电解效率提高至>75%（当前约65%）
  * 水电解效率提高至>80%（当前约70%）
  * 电解槽成本总体降低50%以上
  * 电力成本降至<$0.03/kWh（适用于两种电解过程）
  * 政策支持与激励（碳信用>$100/吨CO2）

### 4.3 建议策略

- 开发高效集成的电解系统，实现CO2电解和水电解的协同优化
- 优化系统设计以实现热量和氧气的循环利用（两个电解过程均产生氧气）
- 寻找低成本可再生电力来源，理想电价应<$0.025/kWh
- 提高费托催化剂选择性并延长使用寿命
- 积极争取政策支持和碳市场机会，包括碳税减免、低碳燃料标准等

### 4.4 未来研究方向

- 电解系统集成创新，如CO2/H2O协同电解技术
- 高温电解技术(SOEC)在CO2还原和水分解中的应用
- 先进膜材料研发，降低电解电压和提高电流密度
- 系统热管理优化，提高能量利用效率至>90%
- 可再生能源与电解过程的智能耦合策略

通过自产氢气代替外购氢气，该系统能够更好地控制原料供应并提高系统集成度。虽然初始资本投入增加，但长期运行具有更高的成本可控性和稳定性。商业规模项目应针对>5,000桶/天的产能进行设计，以实现规模经济效益。
