import streamlit as st

class ConclusionsPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):

        st.title("04 Summary & Recommendations")
        st.markdown(
            "Explore the summary of findings and actionable recommendations derived from our machine learning models.")

        tab_apriori, tab_kmeans, tab_em = st.tabs([
            "Apriori Algorithm",
            "K-means Clustering",
            "EM Clustering"
        ])

        with tab_apriori:
            self.render_apriori_content()

        with tab_kmeans:
            self.render_kmeans_content()

        with tab_em:
            self.render_em_content()

    def render_kmeans_content(self):
        st.header("Geographic Divide in Food Affordability")
        st.markdown("""
        The K-Means clustering reveals distinct geographic patterns in pricing. 
        Select a cluster below to dive into the specifics or use the **Policy Simulator** to estimate improvements.
        """)

        cluster_data = {
            "Cluster A (Mindanao)": {
                "Title": "The Budget-Friendly Zone",
                "Color": "green",
                "Regions": "Agusan del Norte, Bukidnon, Davao (Region XI)",
                "Findings": """
                **Why it's affordable:**
                *   These regions benefit from close proximity to agricultural production.
                *   Minimal transport costs for both crops and fish.
                """,
                "Recommendations": [
                    "**Monitoring:** Use these markets as a 'benchmark' for national price stability.",
                    "**Protection:** Ensure local agricultural advantages are protected from rapid urbanization."
                ],
                "Metric_Label": "Affordability Score",
                "Metric_Value": "High",
                "Metric_Delta": "Benchmark Region"
            },
            "Cluster B (Visayas)": {
                "Title": "The High-Staple Cost Zone",
                "Color": "orange",
                "Regions": "Central Visayas (Cebu, Bohol), Eastern Visayas",
                "Findings": """
                **The Struggle:**
                *   Highest prices for **Rice and Fish**.
                *   Driven by high logistics costs involved in inter-island shipping.
                """,
                "Recommendations": [
                    "**Policy:** Implement targeted rice/fisheries subsidies or 'Kadiwa' stores.",
                    "**Infrastructure:** Invest in RoRo (Roll-on/Roll-off) transport efficiency to lower shipping costs from Mindanao/Luzon."
                ],
                "Metric_Label": "Staple Price markup",
                "Metric_Value": "+15-20%",
                "Metric_Delta": "vs. Mindanao",
                "Delta_Color": "inverse"
            },
            "Cluster C (Luzon & W. Visayas)": {
                "Title": "The High-Veg Cost Zone",
                "Color": "red",
                "Regions": "Bicol, Western Visayas, Central Luzon",
                "Findings": """
                **The Struggle:**
                *   Pays nearly **₱30 more per kg** for vegetables than the budget cluster.
                *   Inefficiencies in cold chain or distribution networks for perishables (e.g., Eggplant).
                """,
                "Recommendations": [
                    "**Supply Chain:** Focus on Cold Chain Storage facilities to reduce spoilage.",
                    "**Agriculture:** Encourage urban gardening or local sourcing to reduce transport dependency."
                ],
                "Metric_Label": "Veggie Price Markup",
                "Metric_Value": "+₱30.00/kg",
                "Metric_Delta": "vs. Budget Cluster",
                "Delta_Color": "inverse"
            }
        }

        st.divider()
        col_sel, col_stat = st.columns([2, 1])

        with col_sel:
            selected_cluster = st.selectbox(
                " Select a Cluster to Analyze:",
                list(cluster_data.keys()),
                index=1
            )

        data = cluster_data[selected_cluster]

        with col_stat:
            st.metric(
                label=data["Metric_Label"],
                value=data["Metric_Value"],
                delta=data["Metric_Delta"],
                delta_color=data.get("Delta_Color", "normal")
            )

        st.subheader(f"{selected_cluster}: {data['Title']}")
        st.caption(f"  Key Areas: {data['Regions']}")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Key Findings")
            if data["Color"] == "green":
                st.success(data["Findings"])
            elif data["Color"] == "orange":
                st.warning(data["Findings"])
            else:
                st.error(data["Findings"])

        with c2:
            st.markdown("### Recommendations")
            for rec in data["Recommendations"]:
                st.info(rec)

        st.divider()
        st.subheader(" Interactive Policy Impact Simulator")
        st.markdown("""
        Use the controls below to simulate how infrastructure or policy improvements 
        could bridge the price gap for **Cluster B (Staples)** and **Cluster C (Vegetables)**.
        """)

        sim_col1, sim_col2 = st.columns(2)

        with sim_col1:
            st.markdown("**Infrastructure Investment Level**")
            efficiency_gain = st.slider(
                "Projected Improvement in Logistics/Cold Chain:",
                min_value=0,
                max_value=50,
                value=10,
                step=5,
                format="%d%%"
            )
            st.caption("Higher investment in RoRo (Visayas) or Cold Storage (Luzon) reduces waste and transport costs.")

        with sim_col2:

            initial_gap_veg = 30.00
            savings = initial_gap_veg * (efficiency_gain / 100)
            new_gap = initial_gap_veg - savings

            st.markdown("### Projected Savings (Vegetables)")

            sc1, sc2 = st.columns(2)
            with sc1:
                st.metric(
                    label="Price Reduction",
                    value=f"-₱{savings:.2f}",
                    delta=f"{efficiency_gain}% Efficiency"
                )
            with sc2:
                st.metric(
                    label="Remaining Price Gap",
                    value=f"₱{new_gap:.2f}",
                    delta="vs Cluster A",
                    delta_color="off"
                )

            if efficiency_gain > 25:
                st.success("High Impact! This level of investment significantly creates price parity with Mindanao.")
            else:
                st.warning("Moderate Impact. Further investment needed to match Cluster A prices.")

    def render_em_content(self):
        st.header("The 'Two-Factor' Market Analysis")
        st.markdown("""
        Expectation-Maximization (EM) clustering reveals that regions are not just defined by price, 
        but by **Volatility** (reliability). This creates a "Two-Factor" market segmentation.
        """)

        em_clusters = {
            "The Production Havens": {
                "Subtitle": "Low Price, Low Volatility",
                "Description": "Regions near agricultural sources that enjoy stable, affordable food.",
                "Color": "green",
                "Rec_Title": "Recommendation: Maintain & Monitor",
                "Rec_Body": "These areas are working well. No major intervention needed besides protecting agricultural lands."
            },
            "The High-Risk Zones": {
                "Subtitle": "High Price, High Volatility",
                "Description": "Areas (often islands) suffering a 'double burden': expensive food AND unreliable supply. This points to fundamental supply chain failures.",
                "Color": "red",
                "Rec_Title": "Recommendation: Targeted Price Stabilization",
                "Rec_Body": "**Action:** Direct investment in cold chain, storage, and specialized transport subsidies.\n\n**Rationale:** A targeted approach is more cost-effective than a national blanket policy for these vulnerable areas."
            },
            "The Efficient Hubs": {
                "Subtitle": "High Price, Low Volatility",
                "Description": "Urban centers (like NCR) where food is expensive due to markups, but supply is highly stable.",
                "Color": "blue",
                "Rec_Title": "Recommendation: Address Baseline Cost Drivers",
                "Rec_Body": "**Action:** Analyze non-logistical costs (local taxes, market fees, rent).\n\n**Rationale:** High prices here are structural, not due to supply instability. Requires regulatory solutions, not infrastructure."
            }
        }

        st.subheader("1. Regional Segmentation")

        white_container = """
                        <style>
                        .st-key-c6 {
                        background-color: #ffffff;
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
                        }
                        </style>
                        """

        st.markdown(white_container, unsafe_allow_html=True)

        selected_em = st.pills(
            "Select Market Type to Explore:",
            options=list(em_clusters.keys()),
            default=list(em_clusters.keys())[0],
            selection_mode="single"
        )

        if not selected_em:
            selected_em = list(em_clusters.keys())[0]

        data = em_clusters[selected_em]

        with st.container(border=True, key = "c6"):
            st.markdown(f"### {selected_em}")
            st.caption(f"**Profile:** {data['Subtitle']}")

            if data['Color'] == 'green':
                st.success(data['Description'])
            elif data['Color'] == 'red':
                st.error(data['Description'])
            else:
                st.info(data['Description'])

            st.markdown(f"**{data['Rec_Title']}**")
            st.write(data['Rec_Body'])

        st.divider()

        st.subheader("2. Price Drivers: Inflation vs. Seasonality")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Long-Term Trend")
            st.warning("**Inflation Driven**")
            st.caption(
                "Baseline food prices are consistently rising due to external macroeconomic factors (fuel, currency), not local issues.")

        with c2:
            st.markdown("#### Short-Term Cycles")
            st.info("**Seasonality Driven**")
            st.caption(
                "Fresh produce follows predictable patterns. We can predict 'Peak' and 'Lean' months to act before prices spike.")

        st.divider()

        st.subheader(" Interactive Feature: Regional Strategy Diagnoser")
        st.markdown("""
        Not sure which category a specific province falls into? 
        Adjust the sliders below based on observed **Price Levels** and **Supply Reliability** to see the recommended strategy.
        """)

        diag_c1, diag_c2 = st.columns([1, 1])

        with diag_c1:
            price_input = st.select_slider(
                "Average Food Price Level:",
                options=["Low", "Moderate", "High"],
                value="Moderate"
            )

            volatility_input = st.select_slider(
                "Supply Stability (Volatility):",
                options=["Stable (Low Volatility)", "Unpredictable (High Volatility)"],
                value="Stable (Low Volatility)"
            )

        with diag_c2:
            st.markdown("### Automated Prescription")

            if price_input == "Low" and volatility_input == "Stable (Low Volatility)":
                st.success("Result: **Production Haven**")
                st.write(
                    " **Strategy:** Minimal Intervention. Monitor to ensure land conversion doesn't reduce supply.")

            elif volatility_input == "Unpredictable (High Volatility)":

                st.error("Result: **High-Risk Zone**")
                st.write(
                    " **Strategy:** **Targeted Infrastructure.** Invest in cold storage and RoRo transport to smooth out the supply spikes.")
                st.caption("Matches Recommendation #1")

            elif price_input == "High" and volatility_input == "Stable (Low Volatility)":
                st.info("Result: **Efficient Hub**")
                st.write(
                    " **Strategy:** **Regulatory Review.** Investigate local taxes, market fees, and rent. Logistics are fine; administrative costs are the problem.")
                st.caption("Matches Recommendation #3")

            else:

                st.warning("Result: **Transition Market**")
                st.write(
                    " **Strategy:** Proactive Seasonal Management. Implement buffer stocking during lean months.")
                st.caption("Matches Recommendation #2")

    def render_apriori_content(self):
        st.header("Decoding Price Patterns: The Apriori Analysis")
        st.markdown("""
        The Apriori algorithm detects hidden "If-Then" rules in price data. 
        It moves beyond simple correlation to identify **Causality (Antecedents $\\to$ Consequents)**, 
        revealing how inflation spreads geographically and across product categories.
        """)

        st.subheader("1. Key Takeaways")
        white_container = """
        <style>
        .st-key-c1, .st-key-c2, .st-key-c3, .st-key-c4,
        .st-key-c5 {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
        }
        </style>
        """

        st.markdown(white_container, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True, key="c1"):
                st.markdown("#### Market Contagion")
                st.caption("Geography")
                st.info(
                    "**Findings:** Price shocks are rarely isolated. High prices in logistics hubs (e.g., Trading Centers) act as **Lead Indicators** for price hikes in dependent regions.")
                st.markdown("`Hubs` $\\to$ `Dependents`")

        with col2:
            with st.container(border=True, key="c2"):
                st.markdown("#### Substitution Effect")
                st.caption("Cross-Category")
                st.warning(
                    "**Findings:** When a primary protein (e.g., Pork) spikes, consumers shift to alternatives (e.g., Fish), driving the alternative's price up simultaneously.")
                st.markdown("`Pork High` $\\to$ `Fish High`")

        with col3:
            with st.container(border=True, key="c3"):
                st.markdown("#### Regional Clustering")
                st.caption("Containment")
                st.success(
                    "**Findings:** Some instability is contained within island groups, while 'Super Spreader' hubs transmit shocks across major island boundaries.")
                st.markdown("`Local` vs `National` Spillover")

        st.divider()

        st.subheader(" Interactive Feature: The Inflation Chain Simulator")
        st.markdown(
            "Select a real-world scenario identified by the model to see how the price shock travels and how to stop it.")

        pills_container = """
            <style> 
                div[data-testid="stPills"] {
                    transition: transform 0.5s ease;
                    margin-bottom: 10px;
                }

                div[data-testid="stPills"] button {
                    background-color: rgba(20, 44, 20, 0.5) !important;
                    color: #E4EB9C !important;
                    border-radius: 20px;
                    border: 1px solid #537B2F;
                    transition: all 0.3s ease;
                }

                div[data-testid="stPills"] button:hover {
                    transform: scale(1.05);
                    background-color: rgba(45, 81, 40, 0.7) !important;
                }

                div[data-testid="stPills"] button[aria-selected="true"] {
                    background-color: #537B2F !important;
                    color: white !important;
                    border-color: #E4EB9C !important;
                }
            </style>
        """

        st.markdown(pills_container, unsafe_allow_html=True)

        scenario_type = st.pills(
            "Select a Contagion Type:",
            ["Geographic Contagion (Region to Region)", "Substitution Effect (Product to Product)"],
            default="Geographic Contagion (Region to Region)",
            selection_mode="single"
        )

        c1, c2 = st.columns([1, 1])

        if scenario_type == "Geographic Contagion (Region to Region)":
            with c1:
                st.markdown("### The Trigger (Antecedent)")
                source_market = st.selectbox(
                    "Where is the price spiking?",
                    ["Nueva Ecija (Rice Granary)", "Davao City (Trading Hub)", "Cebu City (Logistics Hub)"]
                )
                st.write(f"**Event:** Rice prices hit 'High' threshold in **{source_market}**.")

            with c2:
                st.markdown("### The Impact (Consequent)")
                if source_market == "Nueva Ecija (Rice Granary)":
                    target = "Metro Manila"
                    impact_level = "High Confidence"
                elif source_market == "Davao City (Trading Hub)":
                    target = "Tagum / GenSan"
                    impact_level = "Very High Lift"
                else:
                    target = "Dumaguete / Bohol"
                    impact_level = "Moderate Lift"

                st.error(f"**Prediction:** Rice prices will rise in **{target}** within 1-2 weeks.")
                st.caption(f"Metric Strength: {impact_level}")

            with st.container(border=True, key = "c4"):
                st.markdown("### Recommended Action Plan")
                st.success("**Strategy: Establish 'Trigger-Based' Inventory Releases**")
                st.markdown(f"""
                *   **Immediate Action:** Do not wait for prices to rise in {target}. The moment {source_market} spikes, authorize buffer stock release in {target}.
                *   **Long Term:** Deploy field inspectors to **Audit Transport Corridors**. If {source_market} and {target} are strongly linked, there is likely a checkpoint or bottleneck on their specific route.
                """)

        else:
            with c1:
                st.markdown("### The Trigger (Antecedent)")
                primary_product = st.selectbox(
                    "Which primary commodity is expensive?",
                    ["Pork (Kasim)", "Chicken (Whole)", "Beef (Rump)"]
                )
                st.write(f"**Event:** {primary_product} prices spike due to supply issues.")

            with c2:
                st.markdown("### The Impact (Consequent)")
                substitute = "Fish (Galunggong)" if "Pork" in primary_product else "Eggs / Legumes"

                st.error(f"**Prediction:** Demand shifts, causing **{substitute}** prices to spike.")
                st.caption("Cause: Consumer panic substitution")

            with st.container(border=True, key = "c5"):
                st.markdown("### Recommended Action Plan")
                st.warning("**Strategy: Pre-emptive Subsidies on Substitutes**")
                st.markdown(f"""
                *   **Counter-Intuitive Move:** Don't just fix {primary_product}. Immediately subsidize or ease imports for **{substitute}**.
                *   **Public Info:** Run campaigns promoting "Non-Linked" alternatives (products with zero correlation in the Apriori results) to divert demand away from the stressed market.
                """)

        st.divider()

        st.subheader(" Smart Policy Response Calculator")
        st.markdown("""
        Not all price alerts require the same response. Use the model's metrics (**Lift** and **Frequency**) 
        to determine the correct government intervention intensity.
        """)

        col_input, col_output = st.columns([1, 1])

        with col_input:
            lift_input = st.slider(
                "Lift Value (Dependency Strength):",
                min_value=1.0,
                max_value=10.0,
                value=2.0,
                help="How strongly does Event A cause Event B? (>3 is very strong)"
            )

            antecedent_freq = st.slider(
                "Antecedent Frequency (How often is this market the 'Cause'?):",
                min_value=1,
                max_value=20,
                value=5,
                help="How many different rules start with this specific market?"
            )

        with col_output:
            st.markdown("### Triage Result")

            if antecedent_freq >= 10:
                st.error("** Recommendation: Targeted Price Freeze (Circuit Breaker)**")
                st.write(
                    f"This market appears as a cause in {antecedent_freq} different rules. It is an **Inflation Super-Spreader**.")
                st.caption("Action: Apply strict price ceilings here to protect all downstream dependents.")

            elif lift_input >= 5.0:
                st.warning("** Recommendation: Algorithm-Assisted Budget Allocation**")
                st.write(f"The dependency (Lift {lift_input}x) is extremely strong.")
                st.caption("Action: Allocate immediate emergency funds here. Prioritize this over lower-lift alerts.")

            else:
                st.info("** Recommendation: Standard Surveillance**")
                st.write("Correlation exists but is not critical yet.")
                st.caption("Action: Continue monitoring. No drastic intervention required yet.")

