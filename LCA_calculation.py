#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

class SAF_LCA_Model:
    """
    Life Cycle Assessment (LCA) Model for Sustainable Aviation Fuel (SAF)
    固定参数：pathway="FT", functional_unit="MJ", co2_source="DAC"
    """
    
    def __init__(self):
        """
        Initialize the SAF LCA model with fixed parameters
        
        固定配置:
        -----------
        pathway : "FT" (Fischer-Tropsch)
            生产路径固定为Fischer-Tropsch合成
        functional_unit : "MJ"
            功能单位固定为MJ
        co2_source : "DAC" (Direct Air Capture)
            CO2来源固定为直接空气捕获
        """
        # 固定关键参数 - 不允许外部修改
        self.pathway = "FT"  # 固定为Fischer-Tropsch路径
        self.functional_unit = "MJ"  # 固定功能单位为MJ
        self.co2_source = "DAC"  # 固定CO2来源为直接空气捕获
        
        print(f"SAF LCA Model Initialization Complete - Fixed Configuration:")
        print(f"  Production Pathway: {self.pathway} (Fischer-Tropsch)")
        print(f"  Functional Unit: {self.functional_unit}")
        print(f"  CO2 Source: {self.co2_source} (Direct Air Capture)")
        print(f"  Application: LCA analysis for DAC → Electrolysis → FT synthesis pathway")
        
        # 数据存储 (DAC路径不需要feedstock_data)
        self.conversion_data = {}
        self.distribution_data = {}
        self.use_phase_data = {}
        self.carbon_capture_data = {}
        self.electrolysis_data = {}
        
        # GHG characterization factors (kg CO2e per kg)
        self.ghg_factors = {
            "CO2": 1,
            "CH4": 28,  # GWP100
            "N2O": 265  # GWP100
        }
        
        # Initialize results
        self.results = {
            "ghg_emissions": {},
            "energy_consumption": {},
            "water_usage": {},
            "land_use": {}
        }
    
    def set_conversion_data(self, technology, efficiency, ghg_emissions, 
                           energy_input, water_usage,
                           syngas_requirement=None, co_h2_ratio=None):
        """
        Set conversion process data
        
        Parameters:
        -----------
        technology : str
            Conversion technology
        efficiency : float
            Conversion efficiency (MJ fuel/MJ feedstock)
        ghg_emissions : float
            GHG emissions from conversion (kg CO2e per kg fuel)
        energy_input : float
            Energy input for conversion (MJ per kg fuel)
        water_usage : float
            Water usage (L per kg fuel)
        syngas_requirement : float, optional
            Syngas requirement for FT synthesis (kg syngas per kg fuel)
        co_h2_ratio : float, optional
            CO:H2 ratio for FT synthesis
        """
        self.conversion_data = {
            "technology": technology,
            "efficiency": efficiency,
            "ghg_emissions": ghg_emissions,
            "energy_input": energy_input,
            "water_usage": water_usage
        }
        
        # Add additional parameters for e-fuel pathway if provided
        if syngas_requirement is not None:
            self.conversion_data["syngas_requirement"] = syngas_requirement
        
        if co_h2_ratio is not None:
            self.conversion_data["co_h2_ratio"] = co_h2_ratio
        
        # 打印参数信息
        print(f"Conversion Process Parameters Set:")
        print(f"  Technology: {technology}")
        print(f"    └─ Explanation: Fischer-Tropsch synthesis converts syngas (CO+H2) to liquid hydrocarbons")
        print(f"  Efficiency: {efficiency:.3f}")
        print(f"    └─ Explanation: Overall energy conversion efficiency from syngas to liquid fuel")
        print(f"  GHG Emissions: {ghg_emissions:.3f} kg CO2e/kg")
        print(f"    └─ Explanation: Process emissions from heating, catalyst regeneration, and utilities")
        print(f"  Energy Input: {energy_input:.1f} MJ/kg")
        print(f"    └─ Explanation: Additional energy needed for heating, compression, and separation processes")
        
        # Additional parameter explanations if provided
        if syngas_requirement is not None:
            print(f"  Syngas Requirement: {syngas_requirement:.2f} kg syngas/kg fuel")
            print(f"    └─ Explanation: Stoichiometric requirement based on C₁₂H₂₆ molecular formula")
        
        if co_h2_ratio is not None:
            print(f"  CO:H2 Ratio: {co_h2_ratio:.3f}")
            if abs(co_h2_ratio - 0.923) < 0.1:
                print(f"    └─ Explanation: Optimized ratio for C₁₂H₂₆ production (12 CO : 13 H2)")
            else:
                print(f"    └─ Explanation: Carbon monoxide to hydrogen molar ratio in syngas feed")
    
    def set_distribution_data(self, transport_distance, transport_mode="truck", 
                             fuel_density=0.8, silent=False):
        """
        Set distribution stage data based on transport mode and distance
        基于运输方式和距离动态计算运输排放和能耗
        
        Parameters:
        -----------
        transport_distance : float
            Transport distance (km)
        transport_mode : str
            Transport mode: "truck", "rail", "ship", "pipeline", "barge"
        fuel_density : float
            SAF density (kg/L), default 0.8 kg/L
        silent : bool
            If True, suppress print output
        """
        
        # 运输方式排放因子 (kg CO2e/tonne-km)
        # 数据来源：IPCC Guidelines, EcoTransIT等
        emission_factors = {
            "truck": 0.062,        # 长途货运卡车
            "rail": 0.022,         # 铁路货运
            "ship": 0.015,         # 海运货船
            "barge": 0.031,        # 内河驳船
            "pipeline": 0.002,     # 管道运输 (如果适用)
        }
        
        # 运输方式能耗因子 (MJ/tonne-km)
        # 基于燃料消耗和效率计算
        energy_factors = {
            "truck": 2.1,          # 卡车柴油消耗
            "rail": 0.6,           # 铁路电力/柴油消耗
            "ship": 0.4,           # 船舶重油消耗
            "barge": 0.8,          # 驳船柴油消耗
            "pipeline": 0.1,       # 管道泵送能耗
        }
        
        # 验证运输方式
        if transport_mode not in emission_factors:
            available_modes = list(emission_factors.keys())
            raise ValueError(f"不支持的运输方式: {transport_mode}. 可选方式: {available_modes}")
        
        # 获取对应的排放因子和能耗因子
        emission_factor = emission_factors[transport_mode]  # kg CO2e/tonne-km
        energy_factor = energy_factors[transport_mode]      # MJ/tonne-km
        
        # 计算每kg燃料的运输排放和能耗
        # 1 kg fuel = 0.001 tonne
        fuel_weight_tonne = 0.001  # tonne per kg fuel
        
        # 计算运输阶段的排放和能耗 (per kg fuel)
        transport_emissions = emission_factor * fuel_weight_tonne * transport_distance  # kg CO2e/kg fuel
        transport_energy = energy_factor * fuel_weight_tonne * transport_distance       # MJ/kg fuel
        
        # 存储计算结果
        self.distribution_data = {
            "transport_distance": transport_distance,
            "transport_mode": transport_mode,
            "fuel_density": fuel_density,
            "emission_factor": emission_factor,
            "energy_factor": energy_factor,
            "ghg_emissions": transport_emissions,
            "energy_input": transport_energy
        }
        
        # 打印参数设置信息 (简洁版本，适合setup阶段)
        if not silent:
            print(f"Distribution Parameters Set:")
            print(f"  Transport Mode: {transport_mode}")
            
            # Transport mode specific explanations
            mode_explanations = {
                "truck": "Road transport via heavy-duty freight trucks (flexible but higher emissions)",
                "rail": "Railway freight transport (energy efficient for long distances)",
                "ship": "Maritime transport via cargo vessels (lowest emissions for intercontinental)",
                "barge": "Inland waterway transport via river/canal barges (efficient for inland routes)",
                "pipeline": "Pipeline transport (lowest emissions but limited to liquid fuels)"
            }
            
            if transport_mode in mode_explanations:
                print(f"    └─ Explanation: {mode_explanations[transport_mode]}")
            
            print(f"  Transport Distance: {transport_distance} km")
            if transport_distance <= 100:
                print(f"    └─ Explanation: Short distance transport (local/regional distribution)")
            elif transport_distance <= 500:
                print(f"    └─ Explanation: Medium distance transport (national distribution)")
            elif transport_distance <= 2000:
                print(f"    └─ Explanation: Long distance transport (continental distribution)")
            else:
                print(f"    └─ Explanation: Very long distance transport (intercontinental distribution)")
            
            print(f"  Emission Factor: {emission_factor} kg CO2e/tonne-km")
            print(f"    └─ Explanation: Specific emissions per unit mass and distance for {transport_mode} transport")
            print(f"  Energy Factor: {energy_factor} MJ/tonne-km") 
            print(f"    └─ Explanation: Energy consumption per unit mass and distance for {transport_mode} transport")
    
    def set_use_phase_data(self, combustion_emissions, energy_density):
        """
        Set use phase data
        
        Parameters:
        -----------
        combustion_emissions : float
            GHG emissions from fuel combustion (kg CO2e per kg fuel)
        energy_density : float
            Energy density of fuel (MJ per kg)
        """
        self.use_phase_data = {
            "combustion_emissions": combustion_emissions,
            "energy_density": energy_density
        }
        
        # 打印参数设置信息和解释
        print(f"Use Phase Parameters Set:")
        print(f"  Energy Density: {energy_density} MJ/kg")
        print(f"    └─ Explanation: Higher heating value of C₁₂H₂₆ SAF (similar to conventional jet fuel)")
        print(f"  Combustion Emissions: {combustion_emissions} kg CO2e/kg")
        if combustion_emissions == 0.0:
            print(f"    └─ Explanation: Carbon neutral combustion (CO2 from DAC is recycled back to atmosphere)")
        else:
            print(f"    └─ Explanation: Direct combustion emissions during aircraft operation")
    
    def set_carbon_capture_data(self, capture_efficiency, energy_requirement, 
                               ghg_emissions, water_usage, co2_capture_rate):
        """
        Set carbon capture data for Direct Air Capture (DAC) or other CO2 sources
        
        Parameters:
        -----------
        capture_efficiency : float
            CO2 capture efficiency (%)
        energy_requirement : float
            Energy input for carbon capture (MJ per kg CO2)
        ghg_emissions : float
            GHG emissions from capture process (kg CO2e per kg CO2 captured)
        water_usage : float
            Water usage (L per kg CO2 captured)
        co2_capture_rate : float
            Amount of CO2 captured and used per kg of fuel produced (kg CO2/kg fuel)
        """
        self.carbon_capture_data = {
            "capture_efficiency": capture_efficiency,
            "energy_requirement": energy_requirement,
            "ghg_emissions": ghg_emissions,
            "water_usage": water_usage,
            "co2_capture_rate": co2_capture_rate
        }
        
        # 打印参数设置信息
        print(f"Carbon Capture (DAC) Parameters Set:")
        print(f"  Efficiency: {capture_efficiency}%")
        print(f"    └─ Explanation: DAC system captures {capture_efficiency}% of target CO2 from ambient air")
        print(f"  Energy Requirement: {energy_requirement} MJ/kg CO2")
        print(f"    └─ Explanation: Energy needed for air compression, heating, and CO2 separation/purification")
    
    def set_electrolysis_data(self, co2_electrolysis_efficiency, water_electrolysis_efficiency,
                             electricity_source, energy_input_co, energy_input_h2, water_usage,
                             electricity_carbon_intensity=None, silent=False):
        """
        Set electrolysis data for CO2 to CO conversion and H2 production
        
        Parameters:
        -----------
        co2_electrolysis_efficiency : float
            Efficiency of CO2 to CO conversion (%)
        water_electrolysis_efficiency : float
            Efficiency of water electrolysis for H2 production (%)
        electricity_source : str
            Source of electricity (e.g., "grid", "renewable", "mixed")
        energy_input_co : float
            Energy input for CO2 electrolysis (MJ per kg CO)
        energy_input_h2 : float
            Energy input for water electrolysis (MJ per kg H2)
        water_usage : float
            Water usage for electrolysis (L per kg H2+CO produced)
        electricity_carbon_intensity : float, optional
            Carbon intensity of electricity (kg CO2e/kWh). If None, will be set based on electricity_source.
        silent : bool
            If True, suppress print output
        """
        # Define carbon intensities for different electricity sources (kg CO2e/kWh)
        electricity_carbon_intensities = {
            "grid_global": 0.475,       # Global average grid electricity
            "grid_eu": 0.253,           # European Union average
            "grid_china": 0.638,        # China average
            "grid_us": 0.389,           # US average
            "natural_gas": 0.410,       # Natural gas combined cycle
            "coal": 0.820,              # Coal power plants
            "solar": 0.048,             # Solar PV
            "wind": 0.011,              # Wind power
            "hydro": 0.024,             # Hydroelectric
            "nuclear": 0.012,           # Nuclear power
            "biomass": 0.230,           # Biomass power
            "renewable_mix": 0.030,     # Mix of solar, wind, and hydro
            "low_carbon_mix": 0.100,    # Mix of renewables and nuclear
            "renewable": 0.020          # Generic renewable (default)
        }
        
        # If electricity_carbon_intensity is not provided, set it based on the source
        if electricity_carbon_intensity is None:
            if electricity_source in electricity_carbon_intensities:
                electricity_carbon_intensity = electricity_carbon_intensities[electricity_source]
            else:
                # Default to renewable if source not recognized
                electricity_carbon_intensity = electricity_carbon_intensities["renewable"]
                if not silent:
                    print(f"Warning: Electricity source '{electricity_source}' not recognized. Using default value.")
        
        self.electrolysis_data = {
            "co2_electrolysis_efficiency": co2_electrolysis_efficiency,
            "water_electrolysis_efficiency": water_electrolysis_efficiency,
            "electricity_source": electricity_source,
            "electricity_carbon_intensity": electricity_carbon_intensity,
            "energy_input_co": energy_input_co,
            "energy_input_h2": energy_input_h2,
            "water_usage": water_usage
        }
        
        # 打印参数设置信息
        if not silent:
            print(f"Electrolysis Parameters Set:")
            print(f"  Electricity Source: {electricity_source}")
            print(f"    └─ Explanation: Power source for CO2-to-CO and H2O-to-H2 electrolysis processes")
            print(f"  Carbon Intensity: {electricity_carbon_intensity:.3f} kg CO2e/kWh")
            if electricity_carbon_intensity <= 0.05:
                print(f"    └─ Explanation: Very low carbon electricity (renewable/nuclear sources)")
            elif electricity_carbon_intensity <= 0.20:
                print(f"    └─ Explanation: Low carbon electricity (mixed renewable/low-carbon sources)")
            elif electricity_carbon_intensity <= 0.40:
                print(f"    └─ Explanation: Medium carbon electricity (mixed grid sources)")
            else:
                print(f"    └─ Explanation: High carbon electricity (fossil fuel dominated grid)")
    
    def analyze_electricity_sources(self, electricity_sources=None):
        """
        Analyze the impact of different electricity sources on SAF carbon intensity
        固定参数分析：仅改变电力来源，保持pathway="FT", functional_unit="MJ", co2_source="DAC"
        
        Parameters:
        -----------
        electricity_sources : list, optional
            List of electricity sources to analyze. If None, a default set will be used.
            
        Returns:
        --------
        DataFrame: Results of electricity source analysis
        """
        print(f"Starting Electricity Source Sensitivity Analysis - Fixed Configuration:")
        print(f"  Pathway: {self.pathway} (Fixed)")
        print(f"  Functional Unit: {self.functional_unit} (Fixed)")
        print(f"  CO2 Source: {self.co2_source} (Fixed)")
        print("  Variable Parameter: Electricity Source")
        
        # If no sources provided, use a default set
        if electricity_sources is None:
            electricity_sources = [
                "renewable_mix", "grid_global", "grid_eu", "grid_us", 
                "grid_china", "natural_gas", "coal", "solar", "wind", "hydro", "renewable"
            ]
        
        # Store original parameters to restore later
        original_source = self.electrolysis_data.get("electricity_source", "renewable")
        original_intensity = self.electrolysis_data.get("electricity_carbon_intensity", 0.020)
        original_co = self.electrolysis_data.get("energy_input_co", 28.0)
        original_h2 = self.electrolysis_data.get("energy_input_h2", 55.0)
        
        results = []
        
        print(f"  Analyzing {len(electricity_sources)} electricity sources...")
        
        # Run analysis for each electricity source
        for source in electricity_sources:
            # Update the electricity source and recalculate (silent mode)
            self.set_electrolysis_data(
                co2_electrolysis_efficiency=self.electrolysis_data["co2_electrolysis_efficiency"],
                water_electrolysis_efficiency=self.electrolysis_data["water_electrolysis_efficiency"],
                electricity_source=source,  # New source
                energy_input_co=original_co,
                energy_input_h2=original_h2,
                water_usage=self.electrolysis_data["water_usage"],
                electricity_carbon_intensity=None,  # Use default from source
                silent=True
            )
            
            # Calculate LCA with new parameters (silent mode)
            self.calculate_lca(silent=True)
            
            # 直接计算减排率而不调用函数（固定使用MJ基准）
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g (固定MJ基准)
                
            emission_reduction = (89.0 - saf_emissions) / 89.0 * 100
            
            # Store results
            results.append({
                'electricity_source': source,
                'carbon_intensity': self.electrolysis_data["electricity_carbon_intensity"],
                'saf_emissions_mjbasis': saf_emissions,
                'emission_reduction': emission_reduction,
                'electrolysis_emissions': self.results["ghg_emissions"]["electrolysis"] * 1000,  # 固定MJ基准
                'total_emissions': saf_emissions
            })
        
        # Restore original parameters (silent mode)
        self.set_electrolysis_data(
            co2_electrolysis_efficiency=self.electrolysis_data["co2_electrolysis_efficiency"],
            water_electrolysis_efficiency=self.electrolysis_data["water_electrolysis_efficiency"],
            electricity_source=original_source,
            energy_input_co=original_co,
            energy_input_h2=original_h2,
            water_usage=self.electrolysis_data["water_usage"],
            electricity_carbon_intensity=original_intensity,
            silent=True
        )
        
        # 重新计算以恢复原始结果 (silent mode)
        self.calculate_lca(silent=True)
        
        # Create DataFrame from results
        df = pd.DataFrame(results)
        
        # Calculate electrolysis contribution to total emissions
        df['electrolysis_contribution'] = df['electrolysis_emissions'] / df['total_emissions'] * 100
        
        print(f"  Electricity source analysis completed ({len(results)} scenarios)")
        
        return df
    
    def analyze_transport_modes(self, transport_modes=None, base_distance=500):
        """
        Analyze the impact of different transport modes on SAF carbon intensity
        分析不同运输方式对SAF碳强度的影响
        
        Parameters:
        -----------
        transport_modes : list, optional
            List of transport modes to analyze. If None, all available modes will be used.
        base_distance : float
            Base transport distance for comparison (km)
            
        Returns:
        --------
        DataFrame: Results of transport mode analysis
        """
        print(f"Starting Transport Mode Sensitivity Analysis - Fixed Configuration:")
        print(f"  Pathway: {self.pathway} (Fixed)")
        print(f"  Functional Unit: {self.functional_unit} (Fixed)")
        print(f"  CO2 Source: {self.co2_source} (Fixed)")
        print(f"  Base Distance: {base_distance} km")
        print("  Variable Parameter: Transport Mode")
        
        # If no modes provided, use all available modes
        if transport_modes is None:
            transport_modes = ["truck", "rail", "ship", "barge", "pipeline"]
        
        # Store original parameters to restore later
        original_distance = self.distribution_data.get("transport_distance", 500)
        original_mode = self.distribution_data.get("transport_mode", "truck")
        original_density = self.distribution_data.get("fuel_density", 0.8)
        
        results = []
        
        print(f"  Analyzing {len(transport_modes)} transport modes...")
        
        # Run analysis for each transport mode
        for mode in transport_modes:
            # Update the transport mode and recalculate (silent mode)
            self.set_distribution_data(
                transport_distance=base_distance,
                transport_mode=mode,
                fuel_density=original_density,
                silent=True
            )
            
            # Calculate LCA with new parameters (silent mode)
            self.calculate_lca(silent=True)
            
            # 计算减排率（固定使用MJ基准）
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g (固定MJ基准)
            emission_reduction = (89.0 - saf_emissions) / 89.0 * 100
            
            # Store results
            results.append({
                'transport_mode': mode,
                'emission_factor': self.distribution_data["emission_factor"],
                'energy_factor': self.distribution_data["energy_factor"],
                'transport_emissions': self.results["ghg_emissions"]["distribution"] * 1000,  # 固定MJ基准
                'saf_emissions_mjbasis': saf_emissions,
                'emission_reduction': emission_reduction,
                'total_emissions': saf_emissions
            })
        
        # Restore original parameters (silent mode)
        self.set_distribution_data(
            transport_distance=original_distance,
            transport_mode=original_mode,
            fuel_density=original_density,
            silent=True
        )
        
        # 重新计算以恢复原始结果 (silent mode)
        self.calculate_lca(silent=True)
        
        # Create DataFrame from results
        df = pd.DataFrame(results)
        
        # Calculate transport contribution to total emissions
        df['transport_contribution'] = df['transport_emissions'] / df['total_emissions'] * 100
        
        print(f"  Transport mode analysis completed ({len(results)} scenarios)")
        
        return df
    
    def plot_electricity_analysis(self, results_df, plot_type="emissions"):
        """
        Plot the results of electricity source analysis
        
        Parameters:
        -----------
        results_df : DataFrame
            DataFrame from analyze_electricity_sources method
        plot_type : str
            Type of plot: "emissions", "reduction", or "contribution"
        """
        plt.figure(figsize=(12, 6))
        
        if plot_type == "emissions":
            # Sort by emissions
            sorted_df = results_df.sort_values('saf_emissions_mjbasis', ascending=False)
            
            # Create bar plot
            plt.bar(sorted_df['electricity_source'], sorted_df['saf_emissions_mjbasis'], color='darkblue')
            plt.axhline(y=89.0, color='r', linestyle='-', label='Conventional Jet Fuel (89 g CO2e/MJ)')
            
            plt.title('SAF Carbon Intensity by Electricity Source')
            plt.ylabel('Carbon Intensity (g CO2e/MJ)')
            plt.xlabel('Electricity Source')
            plt.xticks(rotation=45)
            plt.legend()
            
        elif plot_type == "reduction":
            # Sort by reduction
            sorted_df = results_df.sort_values('emission_reduction', ascending=True)
            
            # Create bar plot
            bars = plt.bar(sorted_df['electricity_source'], sorted_df['emission_reduction'], color='green')
            
            # Add threshold line for CORSIA (min 10% reduction)
            plt.axhline(y=10, color='orange', linestyle='--', label='CORSIA Minimum (10%)')
            
            # Add threshold line for EU RED II (min 65% reduction)
            plt.axhline(y=65, color='r', linestyle='--', label='EU RED II Target (65%)')
            
            plt.title('GHG Emission Reduction by Electricity Source')
            plt.ylabel('Emission Reduction (%)')
            plt.xlabel('Electricity Source')
            plt.xticks(rotation=45)
            plt.legend()
            
            # Add values on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
                
        elif plot_type == "contribution":
            # Sort by contribution
            sorted_df = results_df.sort_values('electrolysis_contribution', ascending=False)
            
            # Create stacked bar plot
            plt.bar(sorted_df['electricity_source'], 
                   sorted_df['electrolysis_emissions'], 
                   label='Electrolysis Emissions', color='orange')
            
            plt.bar(sorted_df['electricity_source'], 
                   sorted_df['total_emissions'] - sorted_df['electrolysis_emissions'],
                   bottom=sorted_df['electrolysis_emissions'], 
                   label='Other Process Emissions', color='blue')
            
            plt.title('Contribution of Electrolysis to Total Emissions')
            plt.ylabel('Emissions (g CO2e/MJ)')
            plt.xlabel('Electricity Source')
            plt.xticks(rotation=45)
            plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        return plt
    
    def plot_transport_analysis(self, results_df, plot_type="emissions"):
        """
        Plot the results of transport mode analysis
        
        Parameters:
        -----------
        results_df : DataFrame
            DataFrame from analyze_transport_modes method
        plot_type : str
            Type of plot: "emissions", "factors", or "contribution"
        """
        plt.figure(figsize=(10, 6))
        
        if plot_type == "emissions":
            # Sort by emissions
            sorted_df = results_df.sort_values('saf_emissions_mjbasis', ascending=False)
            
            # Create bar plot
            plt.bar(sorted_df['transport_mode'], sorted_df['saf_emissions_mjbasis'], color='brown')
            plt.axhline(y=89.0, color='r', linestyle='-', label='Conventional Jet Fuel (89 g CO2e/MJ)')
            
            plt.title('SAF Carbon Intensity by Transport Mode')
            plt.ylabel('Carbon Intensity (g CO2e/MJ)')
            plt.xlabel('Transport Mode')
            plt.xticks(rotation=45)
            plt.legend()
            
        elif plot_type == "factors":
            # Plot emission and energy factors
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Emission factors
            ax1.bar(results_df['transport_mode'], results_df['emission_factor'], color='red', alpha=0.7)
            ax1.set_title('Emission Factors by Transport Mode')
            ax1.set_ylabel('Emission Factor (kg CO2e/tonne-km)')
            ax1.set_xlabel('Transport Mode')
            ax1.tick_params(axis='x', rotation=45)
            
            # Energy factors
            ax2.bar(results_df['transport_mode'], results_df['energy_factor'], color='blue', alpha=0.7)
            ax2.set_title('Energy Factors by Transport Mode')
            ax2.set_ylabel('Energy Factor (MJ/tonne-km)')
            ax2.set_xlabel('Transport Mode')
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
        elif plot_type == "contribution":
            # Sort by contribution
            sorted_df = results_df.sort_values('transport_contribution', ascending=False)
            
            # Create stacked bar plot
            plt.bar(sorted_df['transport_mode'], 
                   sorted_df['transport_emissions'], 
                   label='Transport Emissions', color='brown')
            
            plt.bar(sorted_df['transport_mode'], 
                   sorted_df['total_emissions'] - sorted_df['transport_emissions'],
                   bottom=sorted_df['transport_emissions'], 
                   label='Other Process Emissions', color='lightblue')
            
            plt.title('Contribution of Transport to Total Emissions')
            plt.ylabel('Emissions (g CO2e/MJ)')
            plt.xlabel('Transport Mode')
            plt.xticks(rotation=45)
            plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        return plt
    
    def calculate_lca(self, silent=False):
        """
        Calculate the full life cycle assessment for DAC → Electrolysis → FT pathway
        固定路径：DAC → 电解 → Fischer-Tropsch，功能单位：MJ
        
        Parameters:
        -----------
        silent : bool
            If True, suppress print output
        """
        # Check if all required data is available
        if not all([self.carbon_capture_data, self.electrolysis_data,
                   self.conversion_data, self.distribution_data, self.use_phase_data]):
            raise ValueError("Missing required data for LCA calculation for DAC → Electrolysis → FT pathway")
        
        if not silent:
            print(f"Calculating LCA - Fixed Configuration:")
            print(f"  Pathway: {self.pathway} (Fischer-Tropsch)")
            print(f"  Functional Unit: {self.functional_unit}")
            print(f"  CO2 Source: {self.co2_source} (Direct Air Capture)")
        
        # Calculate GHG emissions for each stage (kg CO2e per functional unit)
        energy_density = self.use_phase_data["energy_density"]  # MJ/kg
        
        # Normalize to functional unit (固定为MJ)
        normalization_factor = 1 / energy_density  # 固定使用MJ基准
        
        # Carbon capture stage (DAC) - 固定为直接空气捕获
        # 考虑捕获效率影响
        actual_co2_needed = self.carbon_capture_data["co2_capture_rate"] / (self.carbon_capture_data["capture_efficiency"] / 100)
        carbon_capture_ghg = self.carbon_capture_data["ghg_emissions"] * actual_co2_needed * normalization_factor
        
        # Electrolysis stage (CO2 to CO and H2O to H2)
        # Convert electricity carbon intensity from kg CO2e/kWh to kg CO2e/MJ
        elec_intensity_mj = self.electrolysis_data["electricity_carbon_intensity"] / 3.6  # 1 kWh = 3.6 MJ
        
        # Calculate CO and H2 production emissions
        co_h2_ratio = self.conversion_data.get("co_h2_ratio", 0.5)  # Default 1:2 ratio (CO:H2) if not specified
        total_syngas_needed = self.conversion_data.get("syngas_requirement", 2.5) * normalization_factor
        
        co_needed = total_syngas_needed * (co_h2_ratio / (1 + co_h2_ratio))
        h2_needed = total_syngas_needed * (1 / (1 + co_h2_ratio))
        
        # 考虑电解效率影响
        actual_co_needed = co_needed / (self.electrolysis_data["co2_electrolysis_efficiency"] / 100)
        actual_h2_needed = h2_needed / (self.electrolysis_data["water_electrolysis_efficiency"] / 100)
        
        # 修正的排放计算
        co_emissions = actual_co_needed * self.electrolysis_data["energy_input_co"] * elec_intensity_mj
        h2_emissions = actual_h2_needed * self.electrolysis_data["energy_input_h2"] * elec_intensity_mj
        
        electrolysis_ghg = co_emissions + h2_emissions
        
        # Conversion stage (Fischer-Tropsch)
        conversion_ghg = self.conversion_data["ghg_emissions"] * normalization_factor
        
        # Distribution stage
        distribution_ghg = self.distribution_data["ghg_emissions"] * normalization_factor
        
        # Use phase (assumed to be carbon neutral when CO2 from air is used)
        use_phase_ghg = self.use_phase_data["combustion_emissions"] * normalization_factor
        
        # Total emissions
        total_ghg = carbon_capture_ghg + electrolysis_ghg + conversion_ghg + distribution_ghg + use_phase_ghg
        
        # Store results
        self.results["ghg_emissions"] = {
            "carbon_capture": carbon_capture_ghg,
            "electrolysis": electrolysis_ghg,
            "conversion": conversion_ghg,
            "distribution": distribution_ghg,
            "use_phase": use_phase_ghg,
            "total": total_ghg
        }
        
        # Calculate energy consumption
        # Carbon capture energy
        carbon_capture_energy = (self.carbon_capture_data["energy_requirement"] * actual_co2_needed) * normalization_factor
        
        # Electrolysis energy - 考虑电解效率
        co_energy = actual_co_needed * self.electrolysis_data["energy_input_co"]
        h2_energy = actual_h2_needed * self.electrolysis_data["energy_input_h2"]
        electrolysis_energy = co_energy + h2_energy  # 修正：删除重复的归一化
        
        # Conversion and distribution energy
        conversion_energy = self.conversion_data["energy_input"] * normalization_factor
        distribution_energy = self.distribution_data["energy_input"] * normalization_factor
        
        # Total energy
        total_energy = carbon_capture_energy + electrolysis_energy + conversion_energy + distribution_energy
        
        self.results["energy_consumption"] = {
            "carbon_capture": carbon_capture_energy,
            "electrolysis": electrolysis_energy,
            "conversion": conversion_energy,
            "distribution": distribution_energy,
            "total": total_energy
        }
        
        # Calculate water usage
        carbon_capture_water = self.carbon_capture_data["water_usage"] * actual_co2_needed * normalization_factor
        electrolysis_water = self.electrolysis_data["water_usage"] * total_syngas_needed
        conversion_water = self.conversion_data["water_usage"] * normalization_factor
        
        self.results["water_usage"] = {
            "carbon_capture": carbon_capture_water,
            "electrolysis": electrolysis_water,
            "conversion": conversion_water,
            "total": carbon_capture_water + electrolysis_water + conversion_water
        }
        
        # No land use for e-fuel pathway
        self.results["land_use"] = {
            "total": 0
        }
        
        return self.results
    
    def calculate_emission_reduction(self, fossil_jet_emissions=89.0, silent=False):
        """
        Calculate emission reduction compared to conventional jet fuel
        Fixed functional unit: MJ
        
        Parameters:
        -----------
        fossil_jet_emissions : float
            Life cycle GHG emissions of fossil jet fuel (g CO2e/MJ)
            Default value is 89.0 g CO2e/MJ based on EU RED II
        silent : bool
            If True, suppress print output
            
        Returns:
        --------
        float: Emission reduction percentage
        """
        if not self.results["ghg_emissions"]:
            self.calculate_lca()
            
        # Fixed use MJ basis for calculation
        saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g (fixed MJ basis)
            
        reduction = (fossil_jet_emissions - saf_emissions) / fossil_jet_emissions * 100
        
        if not silent:
            print(f"Emission Reduction Calculation (Fixed MJ Basis):")
            print(f"  Conventional Jet Fuel Emissions: {fossil_jet_emissions:.1f} g CO2e/MJ")
            print(f"  SAF Emissions: {saf_emissions:.1f} g CO2e/MJ")
            print(f"  Emission Reduction: {reduction:.1f}%")
        
        return reduction
    
    def print_results(self, show_detailed=True, show_summary=True, show_benchmarks=True):
        """
        Print comprehensive LCA results in a structured format
        
        Parameters:
        -----------
        show_detailed : bool
            Show detailed breakdown by life cycle stages
        show_summary : bool
            Show summary statistics and key indicators
        show_benchmarks : bool
            Show comparison with conventional jet fuel and policy benchmarks
        """
        if not self.results["ghg_emissions"]:
            print("No LCA results available. Please run calculate_lca() first.")
            return
        
        # Header
        print("\n" + "="*80)
        print("SAF LIFE CYCLE ASSESSMENT RESULTS")
        print("="*80)
        print(f"Configuration: {self.pathway} SAF | {self.functional_unit} basis | {self.co2_source} CO2 source")
        print("-"*80)
        
        # Summary Section
        if show_summary:
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # g CO2e/MJ
            fossil_emissions = 89.0  # g CO2e/MJ
            reduction = (fossil_emissions - saf_emissions) / fossil_emissions * 100
            
            print("\n📊 KEY PERFORMANCE INDICATORS")
            print("-"*40)
            print(f"{'Total GHG Emissions:':<25} {saf_emissions:>8.1f} g CO2e/MJ")
            print(f"{'vs Fossil Jet Fuel:':<25} {fossil_emissions:>8.1f} g CO2e/MJ")
            print(f"{'Emission Reduction:':<25} {reduction:>8.1f} %")
            print(f"{'Total Energy Input:':<25} {self.results['energy_consumption']['total']:>8.2f} MJ/MJ")
            print(f"{'Total Water Usage:':<25} {self.results['water_usage']['total']:>8.2f} L/MJ")
        
        # Detailed Breakdown
        if show_detailed:
            print("\n🔍 DETAILED BREAKDOWN BY LIFE CYCLE STAGE")
            print("-"*50)
            
            # GHG Emissions
            print("\nGHG Emissions (g CO2e/MJ):")
            emissions = self.results["ghg_emissions"]
            stages_order = ["carbon_capture", "electrolysis", "conversion", "distribution", "use_phase"]
            stage_names = {
                "carbon_capture": "Carbon Capture (DAC)",
                "electrolysis": "Electrolysis",
                "conversion": "Fischer-Tropsch",
                "distribution": "Distribution",
                "use_phase": "Use Phase"
            }
            
            for stage in stages_order:
                if stage in emissions:
                    value = emissions[stage] * 1000
                    percentage = (value / (emissions["total"] * 1000)) * 100
                    print(f"  {stage_names[stage]:<20} {value:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'TOTAL':<20} {emissions['total']*1000:>8.2f} (100.0%)")
            
            # Energy Consumption
            print("\nEnergy Consumption (MJ input per MJ fuel):")
            energy = self.results["energy_consumption"]
            for stage in stages_order:
                if stage in energy:
                    value = energy[stage]
                    percentage = (value / energy["total"]) * 100
                    print(f"  {stage_names[stage]:<20} {value:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'TOTAL':<20} {energy['total']:>8.2f} (100.0%)")
            
            # Water Usage
            print("\nWater Usage (L per MJ fuel):")
            water = self.results["water_usage"]
            for stage in ["carbon_capture", "electrolysis", "conversion"]:
                if stage in water:
                    value = water[stage]
                    percentage = (value / water["total"]) * 100 if water["total"] > 0 else 0
                    print(f"  {stage_names[stage]:<20} {value:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'TOTAL':<20} {water['total']:>8.2f} (100.0%)")
        
        # Benchmarks and Policy Compliance
        if show_benchmarks:
            print("\n📋 POLICY BENCHMARK COMPLIANCE")
            print("-"*40)
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000
            reduction = (89.0 - saf_emissions) / 89.0 * 100
            
            # CORSIA compliance
            corsia_status = "✅ PASS" if reduction >= 10 else "❌ FAIL"
            print(f"CORSIA (≥10% reduction):     {corsia_status} ({reduction:.1f}%)")
            
            # EU RED II compliance
            red_status = "✅ PASS" if reduction >= 65 else "❌ FAIL"
            print(f"EU RED II (≥65% reduction):  {red_status} ({reduction:.1f}%)")
            
            # California LCFS
            lcfs_status = "✅ PASS" if reduction >= 20 else "❌ FAIL"
            print(f"CA LCFS (≥20% reduction):    {lcfs_status} ({reduction:.1f}%)")
        
        print("\n" + "="*80)
    
    def print_sensitivity_summary(self, electricity_df=None, transport_df=None):
        """
        Print summary of sensitivity analysis results
        
        Parameters:
        -----------
        electricity_df : DataFrame, optional
            Results from electricity source analysis
        transport_df : DataFrame, optional
            Results from transport mode analysis
        """
        print("\n🔄 SENSITIVITY ANALYSIS SUMMARY")
        print("="*50)
        
        if electricity_df is not None and not electricity_df.empty:
            print("\nElectricity Source Impact:")
            min_emissions = electricity_df['saf_emissions_mjbasis'].min()
            max_emissions = electricity_df['saf_emissions_mjbasis'].max()
            best_source = electricity_df.loc[electricity_df['saf_emissions_mjbasis'].idxmin(), 'electricity_source']
            worst_source = electricity_df.loc[electricity_df['saf_emissions_mjbasis'].idxmax(), 'electricity_source']
            
            print(f"  Range: {min_emissions:.1f} - {max_emissions:.1f} g CO2e/MJ")
            print(f"  Best option: {best_source} ({min_emissions:.1f} g CO2e/MJ)")
            print(f"  Worst option: {worst_source} ({max_emissions:.1f} g CO2e/MJ)")
            print(f"  Impact span: {max_emissions - min_emissions:.1f} g CO2e/MJ")
        
        if transport_df is not None and not transport_df.empty:
            print("\nTransport Mode Impact:")
            min_emissions = transport_df['saf_emissions_mjbasis'].min()
            max_emissions = transport_df['saf_emissions_mjbasis'].max()
            best_mode = transport_df.loc[transport_df['saf_emissions_mjbasis'].idxmin(), 'transport_mode']
            worst_mode = transport_df.loc[transport_df['saf_emissions_mjbasis'].idxmax(), 'transport_mode']
            
            print(f"  Range: {min_emissions:.1f} - {max_emissions:.1f} g CO2e/MJ")
            print(f"  Best option: {best_mode} ({min_emissions:.1f} g CO2e/MJ)")
            print(f"  Worst option: {worst_mode} ({max_emissions:.1f} g CO2e/MJ)")
            print(f"  Impact span: {max_emissions - min_emissions:.1f} g CO2e/MJ")
        
        print("="*50)
    
    def plot_results(self, plot_type="emissions_breakdown"):
        """
        Plot LCA results
        
        Parameters:
        -----------
        plot_type : str
            Type of plot to generate
        """
        plt.figure(figsize=(10, 6))
        
        if plot_type == "emissions_breakdown":
            # Emissions breakdown by life cycle stage
            emissions = self.results["ghg_emissions"]
            stages = [k for k in emissions.keys() if k != "total"]
            values = [emissions[k] for k in stages]
            
            plt.bar(stages, values)
            plt.title(f"GHG Emissions Breakdown for {self.pathway} SAF")
            plt.ylabel(f"GHG Emissions (kg CO2e/{self.functional_unit})")
            plt.xticks(rotation=45)
            
        elif plot_type == "energy_breakdown":
            # Energy consumption breakdown
            energy = self.results["energy_consumption"]
            stages = [k for k in energy.keys() if k != "total"]
            values = [energy[k] for k in stages]
            
            plt.bar(stages, values)
            plt.title(f"Energy Consumption Breakdown for {self.pathway} SAF")
            plt.ylabel(f"Energy Consumption (MJ/{self.functional_unit})")
            plt.xticks(rotation=45)
            
        elif plot_type == "comparison":
            # Comparison with fossil jet fuel (fixed MJ basis)
            fossil_jet_emissions = 89.0  # g CO2e/MJ
            
            # Fixed use MJ basis for calculation
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g (fixed MJ basis)
            
            # Calculate emission reduction directly without calling function (avoid duplicate printing)
            reduction_pct = (fossil_jet_emissions - saf_emissions) / fossil_jet_emissions * 100
            
            emissions = [89.0, saf_emissions]  # Fossil jet vs SAF
            plt.bar(["Fossil Jet Fuel", f"{self.pathway} SAF (Fixed Config)"], emissions)
            plt.title(f"Emissions Comparison (Fixed MJ Basis): {reduction_pct:.1f}% Reduction")
            plt.ylabel("GHG Emissions (g CO2e/MJ)")
            
        plt.tight_layout()
        plt.show()
    
    def run_complete_analysis(self, show_plots=True, save_results=False):
        """
        Run complete LCA analysis with structured output
        
        Parameters:
        -----------
        show_plots : bool
            Whether to show all plots
        save_results : bool
            Whether to save results to files
            
        Returns:
        --------
        dict: Dictionary containing all analysis results
        """
        print("🚀 STARTING COMPLETE SAF LCA ANALYSIS")
        print("="*60)
        
        # Step 1: Basic LCA calculation
        print("📊 Step 1: Calculating basic LCA...")
        self.calculate_lca()
        print("✓ Basic LCA calculation completed")
        
        # Step 2: Sensitivity analyses
        print("\n🔍 Step 2: Running sensitivity analyses...")
        electricity_analysis = self.analyze_electricity_sources()
        transport_analysis = self.analyze_transport_modes()
        print("✓ All sensitivity analyses completed")
        
        # Step 3: Print structured results
        print("\n📋 Step 3: Generating comprehensive results...")
        self.print_results()
        self.print_sensitivity_summary(electricity_analysis, transport_analysis)
        
        # Step 4: Generate plots if requested
        if show_plots:
            print("\n📈 Step 4: Generating visualizations...")
            
            # Basic LCA plots
            self.plot_results(plot_type="emissions_breakdown")
            self.plot_results(plot_type="energy_breakdown")
            self.plot_results(plot_type="comparison")
            
            # Sensitivity analysis plots
            self.plot_electricity_analysis(electricity_analysis, plot_type="emissions")
            self.plot_electricity_analysis(electricity_analysis, plot_type="reduction")
            self.plot_electricity_analysis(electricity_analysis, plot_type="contribution")
            
            self.plot_transport_analysis(transport_analysis, plot_type="emissions")
            self.plot_transport_analysis(transport_analysis, plot_type="factors")
            self.plot_transport_analysis(transport_analysis, plot_type="contribution")
            
            print("✓ All visualizations generated")
        
        # Compile results
        results_package = {
            "lca_results": self.results,
            "electricity_analysis": electricity_analysis,
            "transport_analysis": transport_analysis,
            "emission_reduction": self.calculate_emission_reduction(silent=True)
        }
        
        print("\n✅ ANALYSIS COMPLETE!")
        print("="*60)
        return results_package


# Example usage
if __name__ == "__main__":
    # ============================================================================
    # SAF LCA MODEL PARAMETER OVERVIEW
    # ============================================================================
    print("📋 SAF LCA Model - Complete Parameter Guide")
    print("="*80)
    print("This model requires 5 main parameter groups for DAC → Electrolysis → FT pathway:")
    print("\n1️⃣  USE PHASE PARAMETERS:")
    print("   • energy_density: Energy content of SAF (MJ/kg)")
    print("   • combustion_emissions: CO2 emissions from burning fuel (kg CO2e/kg)")
    print("\n2️⃣  CARBON CAPTURE (DAC) PARAMETERS:")
    print("   • capture_efficiency: CO2 capture efficiency (%)")  
    print("   • energy_requirement: Energy for CO2 capture (MJ/kg CO2)")
    print("   • ghg_emissions: Process emissions (kg CO2e/kg CO2)")
    print("   • water_usage: Water consumption (L/kg CO2)")
    print("   • co2_capture_rate: CO2 needed per fuel (kg CO2/kg fuel)")
    print("\n3️⃣  ELECTROLYSIS PARAMETERS:")
    print("   • co2_electrolysis_efficiency: CO2→CO conversion efficiency (%)")
    print("   • water_electrolysis_efficiency: H2O→H2 conversion efficiency (%)")
    print("   • electricity_source: Power source type (wind/solar/grid/etc.)")
    print("   • energy_input_co: Energy for CO production (MJ/kg CO)")
    print("   • energy_input_h2: Energy for H2 production (MJ/kg H2)")
    print("   • water_usage: Water consumption (L/kg syngas)")
    print("\n4️⃣  CONVERSION (FT) PARAMETERS:")
    print("   • technology: Process type (Fischer-Tropsch)")
    print("   • efficiency: Energy conversion efficiency")
    print("   • ghg_emissions: Process emissions (kg CO2e/kg fuel)")
    print("   • energy_input: Additional energy needed (MJ/kg fuel)")
    print("   • water_usage: Water consumption (L/kg fuel)")
    print("   • syngas_requirement: Syngas needed (kg syngas/kg fuel)")
    print("   • co_h2_ratio: CO:H2 molar ratio in syngas")
    print("\n5️⃣  DISTRIBUTION PARAMETERS:")
    print("   • transport_distance: Distance to transport fuel (km)")
    print("   • transport_mode: Method (truck/rail/ship/barge/pipeline)")
    print("   • fuel_density: SAF density (kg/L)")
    print("="*80)
    print("🚀 Starting parameter setup...\n")
    
    # Create SAF LCA model instance for DAC → Electrolysis → FT pathway
    model = SAF_LCA_Model()
    
    # ============================================================================
    # STEP 1: SET UP MODEL PARAMETERS
    # ============================================================================
    print("Setting up model parameters...")
    
    # Use phase (carbon neutral if CO2 from air)
    model.set_use_phase_data(
        combustion_emissions=0.0,  # kg CO2e/kg fuel (carbon neutral with DAC)
        energy_density=43.0        # MJ/kg fuel (updated to C₁₂H₂₆ energy density)
    )

    # Carbon capture: Direct Air Capture (DAC)
    model.set_carbon_capture_data(
        capture_efficiency=80.0,    # %
        energy_requirement=20.0,    # MJ/kg CO2
        ghg_emissions=0.08,         # kg CO2e/kg CO2 captured (using green electricity)
        water_usage=5.0,            # L/kg CO2 captured
        co2_capture_rate=3.1        # kg CO2/kg fuel (based on C₁₂H₂₆ calculation)
    )
    
    # Electrolysis for CO2 to CO and H2O to H2
    model.set_electrolysis_data(
        co2_electrolysis_efficiency=65.0,  # % (typical efficiency for AEM technology)
        water_electrolysis_efficiency=75.0, # %
        electricity_source="wind",     # using renewable electricity
        energy_input_co=28.0,              # MJ/kg CO (lower energy consumption for AEM technology)
        energy_input_h2=55.0,              # MJ/kg H2
        water_usage=20.0,                  # L/kg H2+CO produced
        electricity_carbon_intensity=None
    )
    
    # Conversion process: Fischer-Tropsch
    model.set_conversion_data(
        technology="Fischer-Tropsch",
        efficiency=0.65,          # MJ fuel/MJ feedstock, temporarily unused
        ghg_emissions=0.2,        # kg CO2e/kg fuel
        energy_input=25.0,        # MJ/kg fuel
        water_usage=5.0,          # L/kg fuel
        syngas_requirement=2.13,  # kg syngas/kg fuel (based on C₁₂H₂₆ calculation)
        co_h2_ratio=0.923        # CO:H2 ratio (12:13 based on C₁₂H₂₆ calculation)
    )
    
    # Distribution
    model.set_distribution_data(
        transport_distance=500.0,  # km
        transport_mode="truck",
        fuel_density=0.8
    )
    
    print("Model setup complete!\n")
    
    # ============================================================================
    # STEP 2: RUN COMPLETE ANALYSIS
    # ============================================================================
    # This replaces all the scattered print statements and plot calls
    analysis_results = model.run_complete_analysis(show_plots=True, save_results=False)
    
    # ============================================================================
    # STEP 3: OPTIONAL - ACCESS SPECIFIC RESULTS
    # ============================================================================
    # If you need to access specific results programmatically:
    
    # Access basic LCA results
    lca_results = analysis_results["lca_results"]
    emission_reduction = analysis_results["emission_reduction"]
    
    # Access sensitivity analysis DataFrames
    electricity_df = analysis_results["electricity_analysis"]
    transport_df = analysis_results["transport_analysis"]
    
    # Example: Find best electricity source
    if not electricity_df.empty:
        best_elec_source = electricity_df.loc[electricity_df['saf_emissions_mjbasis'].idxmin()]
        print(f"\n💡 Best electricity source: {best_elec_source['electricity_source']} "
              f"({best_elec_source['saf_emissions_mjbasis']:.1f} g CO2e/MJ)")
    
    # Example: Find best transport mode
    if not transport_df.empty:
        best_transport = transport_df.loc[transport_df['saf_emissions_mjbasis'].idxmin()]
        print(f"🚛 Best transport mode: {best_transport['transport_mode']} "
              f"({best_transport['saf_emissions_mjbasis']:.1f} g CO2e/MJ)")

# %%
