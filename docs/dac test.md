
# Abstract

Direct Air Capture (DAC) has emerged as a critical negative emission technology for achieving the Paris Agreement's 1.5°C target, offering unique advantages in addressing hard-to-abate emissions and historic atmospheric CO₂ accumulation. This comprehensive review examines the technological principles, economic viability, and social dimensions of DAC systems within the context of global climate mitigation strategies.

We analyze both liquid solvent-based and solid sorbent-based DAC technologies, evaluating their thermodynamic constraints, material innovations, and process optimizations. Current large-scale facilities demonstrate technological feasibility but face significant economic challenges with levelized costs ranging from $94-600/t CO₂. Life cycle assessments reveal net CO₂ removal efficiencies exceeding 90% when powered by low-carbon energy sources, though reliance on fossil fuel-based grids can result in net positive emissions.

Synthesizing findings from over 150 scientific publications, this review reveals that DAC deployment must scale from current capacities of 0.01 Mt CO₂/yr to 85 Mt/yr by 2030 and 980 Mt/yr by 2050 to meet climate targets. Critical barriers include high energy requirements (4-14 GJ/t CO₂), substantial capital investments, and policy uncertainties. Social acceptance studies indicate public concerns regarding moral hazard effects. Emerging innovations in metal-organic frameworks, electrochemical regeneration, and moisture-swing adsorption show promise for cost reductions through learning rates of 10-15%.

This review provides a holistic framework emphasizing that DAC must complement—not replace—aggressive emissions reductions and should be deployed equitably with robust monitoring, reporting, and verification systems.

# 1. Introduction

## 1.1 Global Carbon Budget and the Significance of DAC within the 1.5°C Target

The Intergovernmental Panel on Climate Change (IPCC) has identified a remaining global carbon budget of approximately 400-500 GtCO₂ for a 50-67% probability of limiting warming to 1.5°C above pre-industrial levels [103][104][105]. As of 2023, global CO₂ emissions remain at approximately 40 GtCO₂/yr, indicating that this budget will be exhausted within 10-12 years at current emission rates [108]. Atmospheric CO₂ concentrations have risen from ~280 ppm in pre-industrial times to ~420 ppm today, representing approximately 1,500 Gt CO₂ of anthropogenic emissions over the past 70 years [1][15]. At current emission trajectories, atmospheric CO₂ could reach ~900 ppm by 2100, resulting in catastrophic climate impacts [1][88].

To achieve the 1.5°C target, Integrated Assessment Models (IAMs) project the need for 100-1,000 GtCO₂ of cumulative carbon dioxide removal (CDR) by 2100, with annual removal rates reaching 8-15 GtCO₂/yr by mid-century [70][89][106]. Among negative emission technologies (NETs), Direct Air Capture with carbon storage (DACCS) plays a unique role due to its location-independence, scalability potential, and ability to address diffuse and historic emissions that cannot be captured at point sources [4][15][16].

The IPCC's Sixth Assessment Report emphasizes that limiting warming to 1.5°C requires CO₂ emissions to decline by approximately 45% from 2010 levels by 2030 and reach net-zero by 2050 [75][82][104][105]. However, even with aggressive emissions reductions, residual emissions from aviation, heavy industry, and agriculture will necessitate CDR technologies [72][73][89]. DAC offers several advantages: it can be deployed anywhere with adequate energy and storage access, does not compete directly with food production (unlike bioenergy with carbon capture and storage - BECCS), and provides verifiable, measurable carbon removal [4][6][16][19].

## 1.2 Comparison of DAC with Other Negative Emission Technologies

The carbon removal landscape encompasses various technologies, each with distinct characteristics, benefits, and limitations [57][58][97][110][142]. **Afforestation and reforestation (AR)** represent the most mature and cost-effective CDR approaches ($5-50/t CO₂), leveraging natural photosynthesis to sequester atmospheric CO₂ in biomass and soils [7][97]. However, AR faces significant constraints including limited land availability, competition with food production, vulnerability to climate change (wildfires, droughts), and reversibility concerns [70][97][110]. AR can realistically contribute 0.5-3.6 GtCO₂/yr globally [110][142].

**BECCS** combines biomass cultivation with point-source carbon capture, theoretically achieving negative emissions by capturing biogenic CO₂ from combustion or fermentation [57][97][110]. BECCS costs range from $15-400/t CO₂, with significant variability based on biomass type and logistics [7][40][97]. While BECCS offers energy co-production benefits, it faces critical limitations: massive land requirements (potentially 380-700 Mha for 5-10 GtCO₂/yr), water consumption (~600 m³/t CO₂), biodiversity impacts, and food security concerns [4][5][70][97]. Current BECCS deployment is minimal (~2 Mt CO₂/yr), and scaling to gigatonne levels raises serious sustainability questions [57][97][110].

**Enhanced weathering (EW)** and **ocean alkalinity enhancement (OAE)** accelerate natural mineral carbonation processes, with theoretical costs of $50-200/t CO₂ [58][97][116]. These approaches offer permanent storage (>10,000 years) and ocean acidification co-benefits but face uncertainties in quantification, monitoring, and potential ecosystem impacts [58][116]. Mineralization technologies are at lower technology readiness levels (TRL 3-5) compared to DAC [116].

**DAC** distinguishes itself through several unique attributes: location-independent deployment enabling proximity to storage sites or renewable energy sources [4][15][16]; minimal land footprint (~0.5-1 km²/Mt CO₂) compared to BECCS (~100-200 km²/Mt CO₂) [4][5][70]; low water consumption (~25 m³/t CO₂) [4][17]; and high permanence certainty when coupled with geological storage [6][16][18]. However, DAC currently faces significant challenges including high energy requirements (4-14 GJ/t CO₂) [7][40][90], elevated costs ($94-600/t CO₂) [5][38][87], and limited deployment (0.01 Mt CO₂/yr globally) [10][72].

Comparative life cycle assessments reveal that while BECCS requires 1.0-2.6 GJ/t CO₂, DAC consumes 5-14 GJ/t CO₂, making energy sourcing critical for net carbon removal [7][40][90][95]. Studies indicate that DAC powered by coal-based electricity results in net positive emissions, while renewable energy or waste heat enables >90% net removal efficiency [3][71][76].

## 1.3 Scope, Objectives, and Methodology of the Review

This comprehensive review synthesizes findings from 150+ peer-reviewed publications, industry reports, and technical assessments published between 2018-2025, with emphasis on ScienceDirect and other high-impact journals. Our methodology employed systematic literature searches using keywords: "direct air capture," "DAC," "negative emissions," "CO₂ removal," "carbon capture," "atmospheric CO₂," combined with filters for peer-reviewed articles, review papers, and techno-economic assessments.

**Inclusion criteria:**

- Studies published in English from 2018-2025

- Focus on DAC technologies, processes, materials, and systems

- Techno-economic analyses with transparent assumptions [38][87][91][93]

- Life cycle assessments with clear system boundaries [13][58][66][76]

- Policy, social acceptance, and governance studies [140][142][143][144]

- Pilot and commercial-scale deployment data [3][10][117][132][134]

**Exclusion criteria:**

- Point-source carbon capture technologies

- Carbon capture and utilization (CCU) without permanent storage

- Purely theoretical studies without experimental validation

- Conference abstracts without full publications

Our review adopts a multi-dimensional framework examining:

1. **Technological foundations**: Thermodynamic limits [90][92][95][98], sorbent/solvent materials [26][28][117][118][119][120][121], process configurations [4][9][12][26], and emerging innovations [12][26][125][127][128]

2. **Economic viability**: Cost structures (CAPEX/OPEX) [5][38][87][91], learning curves [87][113][119][123], financing mechanisms [46][108][116], and market development [2][43][49][51]

3. **Environmental performance**: Life cycle assessments [13][58][66][71][76][83], net carbon removal [3][66][76][139], and environmental co-impacts [58][70][129]

4. **Social and policy dimensions**: Public perception [140][142][144][151], governance frameworks [143][147][156][159], MRV systems [79][152][155][156], and ethical considerations [150][154][160]

5. **Scale-up pathways**: Current deployments [3][10][117][132][134][136], infrastructure requirements [10][51][56], and future projections [61][67][72][94]

This review aims to provide researchers, policymakers, investors, and technology developers with a holistic understanding of DAC's current status, challenges, and potential role in achieving global climate goals.

# 2. Principles of Direct Air Capture

## 2.1 Fundamentals of CO₂ Separation

### 2.1.1 Atmospheric CO₂ Concentration and Thermodynamic Challenges

Atmospheric CO₂ exists at a concentration of approximately 420 ppm (0.042% by volume), representing a partial pressure of ~42 Pa at sea level [1][15][90]. This extremely dilute concentration creates fundamental thermodynamic challenges for CO₂ separation [90][92][95][98]. In contrast, point-source flue gases contain 8-20% CO₂ (80,000-200,000 ppm), making separation 200-500 times more favorable from a concentration gradient perspective [4][90][98].

The theoretical minimum work required for isothermal, reversible separation of CO₂ from air can be calculated from Gibbs free energy considerations [90][92][98][111][112]:

W_min = RT ln(y_CO₂,concentrated / y_CO₂,ambient)

This equation quantifies the minimum thermodynamic work required to concentrate CO₂ from dilute atmospheric levels to pure form, where R is the gas constant, T is absolute temperature, and y represents mole fractions. For separating CO₂ from 420 ppm to 99.9% purity at 25°C, this yields approximately 20 kJ/mol CO₂ (~450 kJ/kg CO₂ or 0.125 kWh/kg CO₂) [90][98][111][112]. However, this represents an idealized, reversible process requiring infinite time and equipment size. Real processes must overcome kinetic limitations, mass transfer resistances, and heat losses, resulting in actual energy requirements 5-20 times higher than thermodynamic minima [90][95][98][111].

The entropy penalty of CO₂ separation is substantial [90][92][112]. Concentrating CO₂ from 420 ppm to 100% represents a change in entropy:

ΔS = -R ln(P_final / P_initial) = -R ln(101,325 / 42.4) = 64.5 J/(mol·K)

This entropy change equation captures the fundamental thermodynamic cost of "unmixing" CO₂ from air—creating order from disorder by concentrating a dilute species. At 298 K, this translates to a free energy requirement of approximately 19.2 kJ/mol [90][112]. The large volume of air that must be processed exacerbates this challenge: capturing 1 tonne of CO₂ requires processing ~1.9 million m³ of air at 420 ppm [1][15][16].

### 2.1.2 Minimum Energy Requirements and Entropy-Enthalpy Considerations

Comprehensive thermodynamic analyses reveal that DAC processes face distinct energy barriers depending on separation method [90][92][95][98][101]. For sorption-based systems, the total energy comprises (1) air contacting energy (fan work), (2) sorption heat, (3) regeneration energy, and (4) CO₂ compression [3][7][40][90]. The Carnot efficiency establishes theoretical limits for heat-to-work conversions [90][92]:

η_Carnot = 1 - (T_cold / T_hot)

This formula defines the maximum theoretical efficiency for converting heat into useful work based solely on the temperature difference between hot and cold reservoirs. For temperature swing adsorption with regeneration at 100°C (373 K) and ambient at 25°C (298 K), the Carnot efficiency is only 20.1%, indicating that thermal regeneration is inherently less efficient than isothermal separation [90][92][95].

Practical DAC systems consume 4-14 GJ/t CO₂, distributed approximately as [3][7][40][90][95]:

- Air contacting (fans): 50-300 kWh/t CO₂ (0.2-1.1 GJ/t CO₂)

- Regeneration heat: 4-10 GJ/t CO₂

- Compression (to 100 bar): 100-120 kWh/t CO₂ (0.36-0.43 GJ/t CO₂)

- Parasitic losses: 0.5-2 GJ/t CO₂

The large discrepancy between theoretical minimum work (~0.45 GJ/t CO₂) and actual consumption reflects: (1) finite mass transfer rates requiring driving forces, (2) non-idealities in sorbent-CO₂ interactions, (3) sensible heat requirements for temperature swing, (4) incomplete regeneration, and (5) equipment inefficiencies [90][95][98].

Recent studies applying exergy analysis to DAC processes reveal that the largest exergy destructions occur during: (1) non-isothermal sorbent heating (40-50%), (2) irreversible chemical reactions (20-30%), and (3) heat rejection (15-25%) [90][92][95]. These insights guide process optimization strategies toward isothermal or electrochemical regeneration methods [12][20][42][63][96].

## 2.2 Sorbent- and Solvent-Based DAC Systems

### 2.2.1 Solvent-Based DAC: Chemical Absorption Systems

**Aqueous Alkali Solutions (NaOH, KOH):**

Liquid solvent systems, exemplified by Carbon Engineering's technology, employ concentrated aqueous hydroxide solutions to chemically absorb CO₂ [6][18][21]:

CO₂(g) + 2OH⁻(aq) → CO₃²⁻(aq) + H₂O(l)

The process comprises three main steps [6][18][21][36][138]:

1. **Contacting**: Air flows through packed towers where it contacts potassium hydroxide (KOH, 1-2 M) solution, forming potassium carbonate (K₂CO₃)

2. **Pelletization**: The carbonate solution is converted to solid calcium carbonate (CaCO₃) pellets via reaction with Ca(OH)₂

3. **Calcination**: CaCO₃ pellets are heated to ~900°C to decompose into CaO and concentrated CO₂ stream

CaCO₃(s) --900°C--> CaO(s) + CO₂(g)

4. **Hydration**: CaO is rehydrated to regenerate Ca(OH)₂ for reuse

The high-temperature calcination step consumes approximately 5.25 GJ/t CO₂ (the heat of decomposition), plus additional sensible heat for heating pellets from ambient to 900°C (~1.5 GJ/t CO₂) [6][18][21]. Total thermal energy requirements reach 8-12 GJ/t CO₂, plus 1.5-2.5 GJ electrical equivalent/t CO₂ for air contacting, material handling, and compression [7][18][21][40].

**Advantages of liquid solvent systems [4][6][18][21][36]:**

- High CO₂ capture efficiency (>85%)

- Continuous operation capability

- Mature chemical processes (adapted from industrial soda ash production)

- Tolerance to humidity (water acts as solvent)

- Large-scale demonstration (Carbon Engineering, 1 Mt/yr design)

**Challenges [4][6][7][18][21]:**

- Extremely high regeneration temperatures (~900°C) requiring natural gas or alternative high-grade heat

- Potential for CaCO₃ sintering and material degradation over cycles

- Large equipment footprints for contactors and calciners

- Solvent losses and makeup requirements

- Capital-intensive infrastructure

**Amine Solutions:**

Amine-based solvents, adapted from post-combustion capture, can also be applied to DAC [12][25][27][35][118][119]. Monoethanolamine (MEA), diethanolamine (DEA), and methyldiethanolamine (MDEA) react reversibly with CO₂:

CO₂ + 2RNH₂ ⇌ RNHCOO⁻ + RNH₃⁺

Amine solvents typically require regeneration temperatures of 100-120°C, significantly lower than alkali systems [12][25][118]. However, at 420 ppm CO₂, amine absorption rates are slow, and the large liquid volumes required for dilute CO₂ capture create economic challenges [35][118]. Amine oxidative degradation in the presence of O₂ is also problematic [12][35]. Novel amine formulations (sterically hindered amines, piperazine blends) show improved kinetics and reduced degradation but remain under development for DAC applications [25][27][118][119].

### 2.2.2 Sorbent-Based DAC: Solid Adsorption Systems

Solid sorbent systems, pioneered by Climeworks and other developers, employ chemically or physically functionalized materials to capture CO₂ from air [4][15][24][26][117].

**Amine-Functionalized Sorbents:**

Amine-grafted or impregnated materials represent the most advanced solid sorbent class for DAC [12][25][27][33][35][117][118][119]. These materials chemically bind CO₂ through carbamate formation:

2R-NH₂ + CO₂ ⇌ R-NHCOO⁻ + R-NH₃⁺

Key material classes include [25][27][33][35][117][118][119]:

**Amine-grafted silicas**: Mesoporous silicas (SBA-15, MCM-41, KIT-6—high-surface-area materials with tunable pore sizes of 2-50 nm) grafted with aminosilanes (APTES, APTS) or polyamines (PEI, TEPA—amine-rich polymer chains) via post-synthesis functionalization [33][34][35][117]. These materials achieve CO₂ capacities of 1.5-3.0 mmol/g at 400 ppm and 25°C [25][33][35][117].

**Metal-organic framework (MOF) supported amines**: MOFs (crystalline materials with metal nodes connected by organic linkers, forming highly porous 3D structures) like MOF-177, MIL-101(Cr), and Mg₂(dobpdc) functionalized with primary, secondary, or tertiary amines [25][27][30][31]. Diamine-appended MOFs (mmen-Mg₂(dobpdc), e-2-Mg₂(dobpdc)) show exceptional DAC performance with capacities of 2.0-2.5 mmol/g at 400 ppm, rapid kinetics, and cooperative adsorption mechanisms enabling step-shaped isotherms ideal for temperature swing processes [27][30][31][34].

**Ion-exchange resins**: Commercially available resins (Lewatit VP OC 1065, IRA-900) modified with quaternary ammonium groups for anion exchange [29][127][131]. These materials operate via carbonate/bicarbonate exchange and can be regenerated via moisture swing or vacuum swing [127][131].

Regeneration of amine sorbents typically requires temperatures of 80-120°C under vacuum (0.1-0.3 bar) or steam purge (steam-assisted temperature-vacuum swing adsorption, S-TVSA) [12][24][26][71][74]. The heat of adsorption for amine-CO₂ interactions ranges from 60-90 kJ/mol CO₂, substantially lower than high-temperature calcination [26][33][35].

**Physical Adsorbents:**

Materials relying on physisorption (weak van der Waals forces rather than chemical bonding) offer advantages of lower regeneration energy and faster kinetics but face challenges with low CO₂ capacity at 420 ppm and moisture sensitivity [26][28][29][32][120].

**Zeolites**: Microporous aluminosilicates (crystalline materials with uniform pore sizes <2 nm, widely used in catalysis and gas separation) such as Zeolite 13X, Zeolite 5A, and SA-34, with high surface areas (600-800 m²/g) and tunable pore structures [28][32][34][120]. Under dry conditions, zeolites can achieve CO₂ capacities of 1.0-1.5 mmol/g at 400 ppm [25][28][32]. However, water co-adsorption dramatically reduces CO₂ uptake; at even 1% relative humidity, capacity drops by >80% [29][32][33]. This moisture sensitivity necessitates air pre-drying, adding significant energy penalties (3-5 GJ/t CO₂ for dehumidification) [29][33].

Recent developments in hydrophobic zeolites (high-silica MFI, CHA frameworks) and zeolitic templated carbons (ZTC) show improved moisture tolerance [32][34][35][130]. ZTC exhibits hydrophobicity (hydrophobic index >12) and maintains or even enhances CO₂ capacity in humid conditions due to favorable CO₂-H₂O interactions on carbon surfaces [34][35][130].

**MOFs**: Materials like MOF-199 (HKUST-1), MOF-74, NbOFFIVE-1-Ni, and UiO-66 feature high surface areas (1000-7000 m²/g) and tunable pore chemistry [25][27][30][31][126]. MOFs can achieve remarkable CO₂ uptake under dry conditions (2-4 mmol/g at 400 ppm for optimal materials) and allow precise engineering of adsorption sites through post-synthetic modification or defect engineering [27][30][31][126].

However, most MOFs suffer from structural instability upon exposure to moisture, with water causing framework collapse and permanent capacity loss [29][31][126]. Fluorinated MOFs (NbOFFIVE-1-Ni) and hydrophobic frameworks (ZIF-8) demonstrate improved water stability while maintaining CO₂ selectivity [31][126]. MOF-based DAC remains at TRL 3-5, requiring advances in scalable synthesis, structuring, and long-term stability demonstration [30][31][126].

**Structured Sorbents:**

Practical DAC systems require sorbents in structured forms (honeycombs, foams, laminates, coated monoliths) rather than powders to enable efficient air contacting with acceptable pressure drops [9][26][34][117]. Climeworks employs amine-functionalized cellulose fiber structures [24][71][132]; Global Thermostat uses amine-coated honeycomb monoliths [20]; and research groups are developing 3D-printed zeolite/MOF structures, electrospun nanofiber sorbents, and hierarchically porous materials to optimize the trade-off between capacity, kinetics, and pressure drop [34][117][126].

## 2.3 Hybrid and Emerging DAC Concepts

### 2.3.1 Electrochemical DAC

Electrochemical approaches offer potentially transformative advantages: all-electric operation (enabling full renewable energy integration), ambient temperature processing, and modular scalability [20][42][63][96][125][128][135]. Several mechanisms have been demonstrated:

**pH-Swing Electrochemical Systems:**

These systems exploit pH changes induced by electrochemical reactions to control CO₂ capture and release [42][63][96][125]. In the capture step, electrochemical reduction of quinones or metal complexes generates hydroxide ions, increasing solution pH and promoting CO₂ absorption as bicarbonate/carbonate:

Cathode: Q + e⁻ → Q•⁻

Q•⁻ + H₂O → QH + OH⁻

OH⁻ + CO₂ → HCO₃⁻

In the regeneration step, electrochemical oxidation reverses the process, decreasing pH and releasing CO₂ [42][63][96]:

Anode: QH → Q + H⁺ + e⁻

H⁺ + HCO₃⁻ → CO₂ + H₂O

Studies report energy consumptions of 1,000-2,500 kWh/t CO₂ (~3.6-9 GJ/t CO₂) for lab-scale systems, with theoretical potential to approach thermodynamic limits (~1,000 kWh/t CO₂) [20][42][63][96]. Companies like Captura (formerly Carbfix) and Carbon Collect are developing electrochemical DAC at pilot-scale [125][133].

**Electrochemically-Mediated Amine Regeneration:**

Applying electric fields to amine-based systems can reduce thermal regeneration requirements [128][135]. Electric swing adsorption (ESA) uses Joule heating or electromigration to selectively heat or mobilize amine groups, enabling lower overall energy consumption [128]. Laboratory demonstrations show 20-40% energy savings compared to conventional thermal swing [128].

**Advantages [3][20][42][63][96]**: All-electric (solar/wind powered), modular, fast cycling, no high-temperature requirements

**Challenges [42][63][96][125]**: Electrode stability, membrane fouling, scaling to large air volumes, techno-economic viability

### 2.3.2 Moisture-Swing Adsorption (MSA)

MSA exploits the humidity-dependent CO₂ binding strength of certain sorbents, particularly ion-exchange resins with quaternary ammonium functional groups [20][26][29][127][131]. In the capture phase, dry or low-humidity air (RH 10-30%) allows strong CO₂ binding as carbonate (CO₃²⁻). In regeneration, exposing the sorbent to high humidity (RH 60-90%) shifts the equilibrium, releasing CO₂ and converting carbonate to bicarbonate (HCO₃⁻) [20][127][131]:

R-N⁺CO₃²⁻ + H₂O → R-N⁺HCO₃⁻ + OH⁻

R-N⁺HCO₃⁻ + H₂O → R-N⁺OH⁻ + CO₂

MSA requires minimal external energy—primarily for humidity management and gentle heating (30-50°C)—with theoretical energy consumption as low as 1-3 GJ/t CO₂ [20][26][127]. However, CO₂ desorption kinetics are slow, requiring long cycle times (hours), and the regeneration stream produces dilute CO₂ requiring further processing [20][127][131].

Klaus Lackner's "mechanical trees" concept and Avnos' technology employ MSA [20][133]. Experimental demonstrations with IRA-900 resins show CO₂ capacities of 1.5-2.0 mmol/g with working capacities (swing between RH 20% and 60%) of 0.8-1.3 mmol/g [127][131].

**Advantages [20][26][127]**: Very low energy, passive operation potential, simple system

**Challenges [20][127][131]**: Slow kinetics, dilute CO₂ product, water management, sorbent stability over humidity cycles

### 2.3.3 Novel Materials: MOFs, COFs, and Hybrid Systems

**Covalent Organic Frameworks (COFs):**

COFs represent a newer class of porous materials with high surface areas (1000-5000 m²/g), excellent chemical stability, and tunable pore environments [126]. Amine-functionalized COFs show promising DAC properties with CO₂ capacities approaching MOF-supported amines but with superior hydrolytic stability [126]. However, COFs remain at early research stages (TRL 2-3) with limited scale-up demonstrations [126].

**Hybrid Materials:**

Combining multiple material types or mechanisms offers synergistic benefits [34][117][126]. Examples include:

- Zeolite-MOF composites capturing different moisture-CO₂ interactions

- Amine-functionalized hierarchical carbons balancing rapid diffusion with high capacity

- MOF-polymer mixed-matrix membranes for integrated capture-separation

- Photothermal materials (carbon-based, plasmonic nanoparticles) enabling solar-driven regeneration, reducing external heat requirements

**Ionic Liquids and Deep Eutectic Solvents:**

Task-specific ionic liquids (TSILs) functionalized with amines or carbenes offer tunable CO₂ affinity, negligible vapor pressure (no solvent loss), and potential for electrochemical or thermal regeneration [126]. However, high viscosity, cost, and limited kinetics at 420 ppm have prevented practical DAC applications to date [126].

Ongoing research focuses on hybrid capture materials, process intensification through advanced reactor designs (rotating beds, microchannel contactors), and integration of capture with utilization (in-situ conversion to fuels or chemicals) [9][29][117][126].
