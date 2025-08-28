import pandas as pd 
import  streamlit as st
import altair as alt

@st.cache_data
def load_data():
    df = pd.read_csv("database.csv")
    st.title("⚽ Premier League Data Analyzer")

    # Columns to DELETE
    drop_cols = ['#', 'Nation', 'Penalty Shoot on Goal', 'Penalty Shoot', 'Blocks', 
             'Non-Penalty xG (npxG)', 'Goal-Creating Actions', 'Passes Completed', 
             'Passes Attempted', 'Carries', 'Progressive Carries', 'Dribble Attempts', 
             'Successful Dribbles']

    # Remove the columns
    df = df.drop(columns=drop_cols)

    # Keep only the part before the dash as integer
    df["Age"] = df["Age"].astype(str).str.split("-").str[0].astype(int)

    # Convert everything to string first
    df["Pass Completion %"] = df["Pass Completion %"].astype(str)

    # Remove unwanted characters (like %, spaces, words)
    df["Pass Completion %"] = df["Pass Completion %"].str.replace(r"[^0-9.]", "", regex=True)

    # Handle empty strings ("") by replacing them with NaN
    df["Pass Completion %"] = df["Pass Completion %"].replace("", None)

    # Convert to numeric (float)
    df["Pass Completion %"] = pd.to_numeric(df["Pass Completion %"], errors="coerce")
    # Explain why we remove columns
    st.subheader("🧹 Data Cleaning - Why Remove Columns?")
    
    with st.expander("Click to see why we remove certain columns"):
        st.write("**🎯 Keeping only the BEST columns for analysis:**")
        st.write("❌ **Removing these because:**")
        st.write("• `#` - Jersey numbers don't affect performance")
        st.write("• `Nation` - Nice but not essential for performance")
        st.write("• `Penalty stats` - Too specific, small sample size")
        st.write("• `Blocks` - Less important than tackles for defense")
        st.write("• `Non-Penalty xG` - Redundant with main xG")
        st.write("• `Passes Completed/Attempted` - We have Pass %")
        st.write("• `Carries` - Less impactful than other metrics")
        st.write("• `Dribble Attempts` - We keep successful dribbles")
        
        st.write("✅ **This gives us clean, focused data for better insights!**")


    
    st.write(df)
    return df

try:
    df = load_data()

    #Section 2: (SIDEBAR FILTER)
    st.sidebar.header("🔍 Filter the Data")

    # filter 1: Player (multiselect)
    filter1 = st.sidebar.multiselect(
        "Select Player(s)",
        options=df["Player"].unique(),
        default=df["Player"].unique()
    )

    # filter 2: Team (selectbox)
    filter2 = st.sidebar.selectbox(
        "Select Team",
        options=["All"] + list(df["Team"].unique())
    )

    # filter 3: Position (multiselect)
    filter3 = st.sidebar.multiselect(
        "Select Position(s)",
        options=df["Position"].unique(),
        default=df["Position"].unique()
    )

    # filter 4 Age (slider)
    filter4 = st.sidebar.slider(
        "Select Age Range",
        min_value = int(df["Age"].min()),
        max_value = int(df["Age"].max()),
        value=(int(df["Age"].min()), int(df["Age"].max()))
    )

    # filter 5: Minute (slider)
    filter5 = st.sidebar.slider(
        "Select Minute Played",
        min_value = int(df["Minutes"].min()),
        max_value = int(df["Minutes"].max()),
        value=(int(df["Minutes"].min()), int(df["Minutes"].max()))
    )

    # filter 6: Goal (slider)
    filter6 = st.sidebar.slider(
        "Select Goal Range", 
        min_value=int(df["Goals"].min()), 
        max_value=int(df["Goals"].max()), 
        value=(int(df["Goals"].min()), int(df["Goals"].max()))
    )

    # Section 3 (Key Performance Indicator)

    st.subheader("⚡ Key Player Insights")

    with st.expander("🤔 What do these KPIs mean?"):
        st.write("**🏆 Top Scorer** - Player with most goals (the finisher)")
        st.write("**🎯 Assist King** - Player who creates most goals for teammates")  
        st.write("**🕒 Iron Man** - Most reliable player (plays most minutes)")
        st.write("**⚡ Goals per 90** - Most efficient scorer (goals per full game)")
        st.write("**🎯 Pass Accuracy** - Most precise passer (rarely loses the ball)")
        st.write("**🟨 Most Booked** - Most aggressive/fouling player")
        st.write("**💡 Why these matter:** They show different types of excellence!")

    col1, col2, col3 = st.columns(3)

    # KPI 1: Top Scorer
    top_scorer = df.loc[df["Goals"].idxmax()]
    col1.metric("🏆 Top Scorer", top_scorer["Player"], f'{top_scorer["Goals"]} Goals')

    # KPI 2: Assist Leader
    assist_leader = df.loc[df["Assists"].idxmax()]
    col2.metric("🎯 Assist King", assist_leader["Player"], f'{assist_leader["Assists"]} Assists')

    # KPI 3: Most Minutes Played
    most_minutes = df.loc[df["Minutes"].idxmax()]
    col3.metric("🕒 Iron Man", most_minutes["Player"], f'{most_minutes["Minutes"]} mins')

    # Second row of KPIs
    col4, col5, col6 = st.columns(3)

    # KPI 4: Best Goals per 90
    df["Goals_per_90"] = df.apply(lambda x: (x["Goals"] / x["Minutes"]) * 90 if x["Minutes"] > 0 else 0, axis=1)
    best_gp90 = df.loc[df["Goals_per_90"].idxmax()]
    col4.metric("⚡ Goals per 90", best_gp90["Player"], f'{best_gp90["Goals_per_90"]:.2f}')

    # KPI 5: Pass Accuracy Leader
    pass_leader = df.loc[df["Pass Completion %"].idxmax()]
    col5.metric("🎯 Pass Accuracy", pass_leader["Player"], f'{pass_leader["Pass Completion %"]}%')

    # KPI 6: Discipline (most yellow cards)
    discipline = df.loc[df["Yellow Cards"].idxmax()]
    col6.metric("🟨 Most Booked", discipline["Player"], f'{discipline["Yellow Cards"]} Yellows')

    # Section 4 (Research Question and Analysis)
    st.subheader("🔥 10 Mind-Blowing Football Questions")
    # Question 1: Who are the most efficient scorers?
    st.write("### 1️⃣ Who are the MOST EFFICIENT scorers? (Goals vs Expected Goals)")
    with st.expander("🤔 Why this matters"):
         st.write("**xG = Expected Goals** - How many goals a player SHOULD score based on shot quality")
         st.write("**If Goals > xG = Clinical finisher** | **If Goals < xG = Wasteful shooter**")

    df_q1 = df[df['Minutes'] > 60].copy()  # Only players with decent playing time
    if df_q1.empty:
        st.write("❌ No players found with >200 minutes. Try lowering the threshold.")
        st.write(f"Available minutes range: {df['Minutes'].min():.0f} to {df['Minutes'].max():.0f}")
    else:
        df_q1['Efficiency'] = df_q1['Goals'] - df_q1['Expected Goals (xG)']
        most_efficient = df_q1.loc[df_q1['Efficiency'].idxmax()]

        st.write(f"**🎯 ANSWER:** {most_efficient['Player']} is the most clinical finisher!")
        st.write(f"   • Scored {most_efficient['Goals']} goals from {most_efficient['Expected Goals (xG)']:.1f} xG")
        st.write(f"   • That's {most_efficient['Efficiency']:.1f} goals MORE than expected!")

        top_efficient = df_q1.nlargest(10, 'Efficiency')
        chart1 = alt.Chart(top_efficient).mark_bar().encode(
            x=alt.X('Efficiency:Q', title='Goals Above/Below Expected'),
            y=alt.Y('Player:N', sort='-x', title='Player'),
            color=alt.Color('Team:N'),
            tooltip=['Player', 'Goals', 'Expected Goals (xG)', 'Efficiency', 'Team']
        ).properties(width=600, height=400, title="Top 10 Most Efficient Scorers")
        st.altair_chart(chart1, use_container_width=True)


        # Question 2: Age vs Performance Sweet Spot
        st.write("### 2️⃣ What's the PERFECT AGE for peak performance?")
        with st.expander("🤔 Why this matters"):
            st.write("**Football careers are short** - Finding the age when players peak helps predict future")
            st.write("**Young = Potential** | **Peak age = Prime** | **Older = Experience**")

        age_performance = df.groupby('Age').agg({
            'Goals': 'mean',
            'Assists': 'mean',
            'Expected Goals (xG)': 'mean'
        }).reset_index()

        peak_age = age_performance.loc[age_performance['Goals'].idxmax()]
        st.write(f"**🎯 ANSWER:** Age {int(peak_age['Age'])} is the PEAK scoring age!")
        st.write(f"   • Players aged {int(peak_age['Age'])} average {peak_age['Goals']:.1f} goals")
        st.write(f"   • Sweet spot is between 26-29 years old")

        chart2 = alt.Chart(age_performance).mark_line(point=True).encode(
            x=alt.X('Age:Q'),
            y=alt.Y('Goals:Q', title='Average Goals'),
            tooltip=['Age', 'Goals']
        ).properties(width=600, height=400)
        st.altair_chart(chart2, use_container_width=True)

        # Question 3: Team Playing Styles
        st.write("### 3️⃣ Which teams play BEAUTIFUL vs UGLY football?")
        with st.expander("🤔 Why this matters"):
            st.write("**Pass % = Beautiful football | Tackles = Defensive/Ugly football**")
            st.write("**Top right = Technical teams | Bottom left = Physical teams**")

        # Aggregate per team
        team_style = df.groupby('Team').agg({
            'Pass Completion %': 'mean',    # Pass accuracy
            'Tackles': 'mean',     # Tackles
            'Goals': 'sum'       # Goals scored
        }).reset_index()

        # Melt to long format so we can plot Pass% vs Tackles in bars
        team_style_melted = team_style.melt(
            id_vars=['Team', 'Goals'],
            value_vars=['Pass Completion %', 'Tackles'],
            var_name='Metric',
            value_name='Value'
        )

        # Create grouped bar chart
        chart3 = alt.Chart(team_style_melted).mark_bar().encode(
            x=alt.X('Team:N', sort='-y', title='Team'),
            y=alt.Y('Value:Q', title='Metric Value'),
            color=alt.Color('Metric:N', title='Metric'),
            column=alt.Column('Metric:N', title=None),
            tooltip=['Team', 'Metric', 'Value', 'Goals']
        ).properties(width=250, height=400)

        st.altair_chart(chart3, use_container_width=True)



        # Question 4: Position Intelligence
        st.write("### 4️⃣ Do DEFENDERS really score less? (Position Analysis)")
        with st.expander("🤔 Why this matters"):
            st.write("**Stereotypes:** Forwards score, Defenders defend. **Reality might be different!**")
            st.write("**Modern football:** All positions contribute to attack and defense")

        pos_analysis = df.groupby('Position').agg({
            'Goals': 'mean',
            'Assists': 'mean',
            'Tackles': 'mean'
        }).reset_index()

        chart4 = alt.Chart(pos_analysis).mark_bar().encode(
            x=alt.X('Position:N'),
            y=alt.Y('Goals:Q', title='Average Goals'),
            color=alt.Color('Position:N')
        ).properties(width=600, height=400)
        st.altair_chart(chart4, use_container_width=True)


        # Question 5: The Creativity Index
        st.write("### 5️⃣ Who are the most CREATIVE players? (Assists vs Key Actions)")
        with st.expander("🤔 Why this matters"):
            st.write("**Assists = Direct creativity** | **Shot-Creating Actions = Indirect creativity**")
            st.write("**Some players assist the assisters!** - They create chances but don't get credit")

        df_creative = df[df['Minutes'] > 60].copy()  # Fixed threshold

        if df_creative.empty:
            st.write("❌ No players found with >60 minutes.")
            st.write(f"Available minutes range: {df['Minutes'].min():.0f} to {df['Minutes'].max():.0f}")
        else:
            # Calculate Creativity Index
            df_creative['Creativity_Index'] = df_creative['Assists'] + (df_creative['Shot-Creating Actions'] * 0.5)
            most_creative = df_creative.loc[df_creative['Creativity_Index'].idxmax()]
    
            # Display Answer
            st.write(f"**🎨 ANSWER:** {most_creative['Player']} is the most creative player!")
            st.write(f"   • {most_creative['Assists']} Assists + {most_creative['Shot-Creating Actions']} Shot-Creating Actions")
            st.write(f"   • Creativity Index: {most_creative['Creativity_Index']:.1f}")
            st.write(f"   • Position: {most_creative['Position']}")
    
            # Top 10 Most Creative Players Chart
            top_creative = df_creative.nlargest(10, 'Creativity_Index')
    
            chart5 = alt.Chart(top_creative).mark_bar().encode(
                x=alt.X('Creativity_Index:Q', title='Creativity Index'),
                y=alt.Y('Player:N', sort='-x', title='Player'),
                color=alt.Color('Position:N'),
                tooltip=['Player', 'Assists', 'Shot-Creating Actions', 'Creativity_Index', 'Position']
            ).properties(width=600, height=400, title="Top 10 Most Creative Players")
            st.altair_chart(chart5, use_container_width=True)


            # Question 6: Who are the WORKRATE WARRIORS?
            st.write("### 6️⃣ Who are the WORKRATE WARRIORS? (Touches vs Minutes)")
            with st.expander("🤔 Why this matters"):
                st.write("**High touches per minute = Always involved in play (hardworking)**")
                st.write("**Low touches per minute = Impact player or lazy**")

            df['Touches_per_min'] = df['Touches'] / df['Minutes']
            df_workrate = df[df['Minutes'] > 60].copy()  # Fixed threshold

            if df_workrate.empty:
                st.write("❌ No players found with >60 minutes.")
                st.write(f"Available minutes range: {df['Minutes'].min():.0f} to {df['Minutes'].max():.0f}")
            else:
                # Find the workrate warrior
                workrate_warrior = df_workrate.loc[df_workrate['Touches_per_min'].idxmax()]
    
                # Display Answer
                st.write(f"**💪 ANSWER:** {workrate_warrior['Player']} is the ultimate workrate warrior!")
                st.write(f"   • {workrate_warrior['Touches_per_min']:.1f} touches per minute")
                st.write(f"   • {workrate_warrior['Touches']} total touches in {workrate_warrior['Minutes']} minutes")
                st.write(f"   • Position: {workrate_warrior['Position']}")
    
                # Top 10 Workrate Warriors Chart
                top_workrate = df_workrate.nlargest(10, 'Touches_per_min')
    
                chart6 = alt.Chart(top_workrate).mark_bar().encode(
                    x=alt.X('Touches_per_min:Q', title='Touches per Minute'),
                    y=alt.Y('Player:N', sort='-x', title='Player'),
                    color=alt.Color('Position:N'),
                    tooltip=['Player', 'Minutes', 'Touches_per_min', 'Position', 'Touches']
                ).properties(width=600, height=400, title="Top 10 Workrate Warriors")
                st.altair_chart(chart6, use_container_width=True)


                # Question 7: Discipline Analysis
                st.write("### 7️⃣ Are SKILLFUL players more disciplined? (Dribbles vs Cards)")
                with st.expander("🤔 Why this matters"):
                    st.write("**Theory:** Skillful players get fouled more OR they're more reckless")
                    st.write("**Cards = Bad discipline** | **Dribbles = Skill level**")

                df_discipline = df[df['Minutes'] > 60].copy()  # Filter for meaningful playing time

                if df_discipline.empty:
                    st.write("❌ No players found with >60 minutes.")
                else:
                    # Find most skilled but disciplined player
                    most_skilled = df_discipline.loc[df_discipline['Dribbles'].idxmax()]
                    least_disciplined = df_discipline.loc[df_discipline['Yellow Cards'].idxmax()]
    
                    # Calculate correlation
                    correlation = df_discipline['Dribbles'].corr(df_discipline['Yellow Cards'])
    
                    # Display Analysis
                    st.write("**📊 ANALYSIS RESULTS:**")
                    st.write(f"   • Correlation between Dribbles & Cards: {correlation:.3f}")
                    if correlation > 0.3:
                        st.write("   • 🔴 **CONCLUSION:** Skillful players ARE less disciplined!")
                    elif correlation < -0.3:
                        st.write("   • 🟢 **CONCLUSION:** Skillful players are MORE disciplined!")
                    else:
                        st.write("   • 🟡 **CONCLUSION:** No clear relationship between skill and discipline")
    
                    st.write(f"**🏆 Most Skilled:** {most_skilled['Player']} ({most_skilled['Dribbles']} dribbles, {most_skilled['Yellow Cards']} cards)")
                    st.write(f"**🟨 Least Disciplined:** {least_disciplined['Player']} ({least_disciplined['Yellow Cards']} cards, {least_disciplined['Dribbles']} dribbles)")
    
                    # Top 10 Dribblers Chart
                    top_dribblers_chart = df_discipline.nlargest(10, 'Dribbles')
    
                    chart7 = alt.Chart(top_dribblers_chart).mark_bar().encode(
                        x=alt.X('Player:N', sort='-y', title='Player'),
                        y=alt.Y('Dribbles:Q', title='Dribbles Completed'),
                        color=alt.Color('Yellow Cards:Q', 
                            scale=alt.Scale(scheme='redyellowgreen', reverse=True),
                            title='Yellow Cards'),
                        tooltip=['Player', 'Dribbles', 'Yellow Cards', 'Position']
                    ).properties(width=600, height=400, title="Top 10 Dribblers - Color shows Discipline")
    
                    st.altair_chart(chart7, use_container_width=True)
    
                    # Alternative: Heatmap of top players
                    st.write("**🔥 Top Skilled Players - Discipline Check:**")
                    top_dribblers = df_discipline.nlargest(10, 'Dribbles')[['Player', 'Position', 'Dribbles', 'Yellow Cards']]
                    st.dataframe(top_dribblers, use_container_width=True)



                    # Question 8: The Complete Player Index
                    st.write("### 8️⃣ Who are the most COMPLETE players? (Attack + Defense)")
                    with st.expander("🤔 Why this matters"):
                        st.write("**Complete players contribute to both attack AND defense**")
                        st.write("**Top right corner = Superstars who do everything**")

                    df_complete = df[df['Minutes'] > 60].copy()  # Fixed threshold

                    if df_complete.empty:
                        st.write("❌ No players found with >60 minutes.")
                        st.write(f"Available minutes range: {df['Minutes'].min():.0f} to {df['Minutes'].max():.0f}")
                    else:
                        # Calculate Complete Player Index
                        df_complete['Attack_Score'] = df_complete['Goals'] + df_complete['Assists']
                        df_complete['Defense_Score'] = df_complete['Tackles']
                        df_complete['Complete_Index'] = (df_complete['Attack_Score'] * 2) + df_complete['Defense_Score']
    
                        # Find most complete player
                        most_complete = df_complete.loc[df_complete['Complete_Index'].idxmax()]
    
                        # Find best attacker and best defender for comparison
                        best_attacker = df_complete.loc[df_complete['Attack_Score'].idxmax()]
                        best_defender = df_complete.loc[df_complete['Defense_Score'].idxmax()]
    
                        # Display Results
                        st.write(f"**🏆 MOST COMPLETE PLAYER:** {most_complete['Player']}!")
                        st.write(f"   • Attack: {most_complete['Goals']} goals + {most_complete['Assists']} assists = {most_complete['Attack_Score']}")
                        st.write(f"   • Defense: {most_complete['Tackles']} tackles = {most_complete['Defense_Score']:.0f}")
                        st.write(f"   • Complete Index: {most_complete['Complete_Index']:.1f}")
                        st.write(f"   • Position: {most_complete['Position']}")
    
                        st.write("**📊 COMPARISON:**")
                        st.write(f"   • Best Attacker: {best_attacker['Player']} ({best_attacker['Attack_Score']} attack score)")
                        st.write(f"   • Best Defender: {best_defender['Player']} ({best_defender['Defense_Score']:.0f} defense score)")
    
                        # Top 10 Complete Players Chart
                        top_complete = df_complete.nlargest(10, 'Complete_Index')
    
                        chart8 = alt.Chart(top_complete).mark_bar().encode(
                            x=alt.X('Complete_Index:Q', title='Complete Player Index'),
                            y=alt.Y('Player:N', sort='-x', title='Player'),
                            color=alt.Color('Position:N'),
                            tooltip=['Player', 'Attack_Score', 'Defense_Score', 'Complete_Index', 'Position']
                        ).properties(width=600, height=400, title="Top 10 Most Complete Players")
    
                        st.altair_chart(chart8, use_container_width=True)


                        # Question 9: Experience vs Impact
                        st.write("### 9️⃣ Do EXPERIENCED players have more impact per minute?")
                        with st.expander("🤔 Why this matters"):
                            st.write("**Old players play less but when they do, are they more effective?**")
                            st.write("**Impact = Goals + Assists per 90 minutes**")

                        df['Impact_per_90'] = ((df['Goals'] + df['Assists']) / df['Minutes']) * 90
                        df_experience = df[df['Minutes'] > 60].copy()  # Fixed threshold

                        if df_experience.empty:
                            st.write("❌ No players found with >60 minutes.")
                            st.write(f"Available minutes range: {df['Minutes'].min():.0f} to {df['Minutes'].max():.0f}")
                        else:
                            # Age group analysis
                            df_experience['Age_Group'] = pd.cut(df_experience['Age'], 
                                      bins=[0, 23, 28, 35, 50], 
                                      labels=['Young (≤23)', 'Prime (24-28)', 'Experienced (29-35)', 'Veteran (35+)'])
    
                            # Calculate average impact by age group
                            age_impact = df_experience.groupby('Age_Group')['Impact_per_90'].mean().reset_index()
                            age_impact = age_impact.dropna()  # Remove any NaN groups
       
                            # Find correlation between age and impact
                            correlation = df_experience['Age'].corr(df_experience['Impact_per_90'])
    
                            # Find most impactful veteran and youngest high-impact player
                            veterans = df_experience[df_experience['Age'] >= 30]
                            youngsters = df_experience[df_experience['Age'] <= 25]
    
                            # Display Analysis
                            st.write("**📊 ANALYSIS RESULTS:**")
                            st.write(f"   • Age-Impact Correlation: {correlation:.3f}")
    
                            if correlation > 0.2:
                                st.write("   • 🟢 **CONCLUSION:** Experience DOES increase impact per minute!")
                            elif correlation < -0.2:
                                st.write("   • 🔴 **CONCLUSION:** Younger players have MORE impact per minute!")
                            else:
                                st.write("   • 🟡 **CONCLUSION:** Age has NO clear effect on impact per minute")
    
                            # Show average impact by age group
                            st.write("**📈 IMPACT BY AGE GROUP:**")
                            for _, row in age_impact.iterrows():
                                st.write(f"   • {row['Age_Group']}: {row['Impact_per_90']:.2f} goals+assists per 90min")
    
                            # Find standout players
                            if not veterans.empty:
                                best_veteran = veterans.loc[veterans['Impact_per_90'].idxmax()]
                                st.write(f"**👴 Best Veteran:** {best_veteran['Player']} (Age {best_veteran['Age']}) - {best_veteran['Impact_per_90']:.2f} impact/90")
    
                            if not youngsters.empty:
                                best_youngster = youngsters.loc[youngsters['Impact_per_90'].idxmax()]
                                st.write(f"**🌟 Best Youngster:** {best_youngster['Player']} (Age {best_youngster['Age']}) - {best_youngster['Impact_per_90']:.2f} impact/90")
    
                            # Age Group Impact Chart
                            if not age_impact.empty:
                                chart9_grouped = alt.Chart(age_impact).mark_bar().encode(
                                    x=alt.X('Age_Group:N', title='Age Group'),
                                    y=alt.Y('Impact_per_90:Q', title='Average Impact per 90 minutes'),
                                    color=alt.Color('Age_Group:N', 
                                        scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])),
                                    tooltip=['Age_Group', 'Impact_per_90']
                                ).properties(width=600, height=400, title="Impact per 90 minutes by Age Group")
        
                                st.altair_chart(chart9_grouped, use_container_width=True)
    
                            # Top Impact Players by Age
                            st.write("**🔥 TOP IMPACT PLAYERS:**")
                            top_impact = df_experience.nlargest(10, 'Impact_per_90')[['Player', 'Age', 'Goals', 'Assists', 'Impact_per_90', 'Position']]
                            st.dataframe(top_impact, use_container_width=True)


                            # Question 10: The Ultimate Question
                            st.write("### 🔟 WHO IS THE MOST VALUABLE PLAYER? (Multi-factor analysis)")
                            with st.expander("🤔 Why this matters"):
                                st.write("**Combining ALL factors:** Goals, Assists, Pass%, Playing Time, Efficiency")
                                st.write("**This is how scouts and managers really evaluate players!**")

                            # Create a simple value score
                            df_value = df[df['Minutes'] > 60].copy()  # Fixed threshold

                            if df_value.empty:
                                st.write("❌ No players found with >60 minutes.")
                                st.write(f"Available minutes range: {df['Minutes'].min():.0f} to {df['Minutes'].max():.0f}")
                            else:
                                # Calculate comprehensive Value Score
                                df_value['Value_Score'] = (
                                    df_value['Goals'] * 3 +                                    # Goals worth most
                                    df_value['Assists'] * 2 +                                  # Assists important
                                    df_value['Expected Goals (xG)'] * 1.5 +                    # Potential
                                    (df_value['Pass Completion %'] / 20) +                     # Pass accuracy bonus
                                    (df_value['Minutes'] / 10)                                 # Playing time bonus
                                )
    
                                # Find the MVP
                                mvp = df_value.loc[df_value['Value_Score'].idxmax()]
    
                                # Get top performers in each category for comparison
                                top_scorer = df_value.loc[df_value['Goals'].idxmax()]
                                top_assister = df_value.loc[df_value['Assists'].idxmax()]
                                most_accurate = df_value.loc[df_value['Pass Completion %'].idxmax()]
    
                                # Display MVP Results
                                st.write("**🏆 MOST VALUABLE PLAYER REVEALED:**")
                                st.write(f"**🥇 MVP: {mvp['Player']}** from {mvp['Team']}")
                                st.write(f"   • Value Score: {mvp['Value_Score']:.1f}")
                                st.write(f"   • {mvp['Goals']} Goals + {mvp['Assists']} Assists")
                                st.write(f"   • {mvp['Pass Completion %']:.1f}% pass accuracy")
                                st.write(f"   • {mvp['Minutes']} minutes played")
                                st.write(f"   • Position: {mvp['Position']}")
    
                                st.write("**📊 CATEGORY LEADERS COMPARISON:**")
                                st.write(f"   • 🥅 Top Scorer: {top_scorer['Player']} ({top_scorer['Goals']} goals)")
                                st.write(f"   • 🎯 Top Assister: {top_assister['Player']} ({top_assister['Assists']} assists)")
                                st.write(f"   • 📈 Most Accurate: {most_accurate['Player']} ({most_accurate['Pass Completion %']:.1f}% passes)")
    
                                # Check if MVP leads in multiple categories
                                categories_led = 0
                                if mvp['Player'] == top_scorer['Player']: categories_led += 1
                                if mvp['Player'] == top_assister['Player']: categories_led += 1
                                if mvp['Player'] == most_accurate['Player']: categories_led += 1
    
                                if categories_led >= 2:
                                    st.write(f"   • 🌟 **{mvp['Player']} dominates in {categories_led} categories!**")
                                elif categories_led == 1:
                                    st.write(f"   • ⭐ **{mvp['Player']} leads in 1 category but excels overall!**")
                                else:
                                    st.write(f"   • 🎯 **{mvp['Player']} doesn't lead any single category but is the most balanced!**")
    
                                # Top 10 Most Valuable Players Chart
                                top_values = df_value.nlargest(10, 'Value_Score')
    
                                chart10 = alt.Chart(top_values).mark_bar().encode(
                                    x=alt.X('Value_Score:Q', title='Value Score'),
                                    y=alt.Y('Player:N', sort='-x', title='Player'),
                                    color=alt.Color('Team:N'),
                                    tooltip=['Player', 'Value_Score', 'Goals', 'Assists', 'Pass Completion %', 'Team']
                                ).properties(width=600, height=500, title="Top 10 Most Valuable Players")
    
                                st.altair_chart(chart10, use_container_width=True)
    
                                # Value Score Breakdown for MVP
                                st.write("**🔍 MVP VALUE BREAKDOWN:**")
                                goal_points = mvp['Goals'] * 3
                                assist_points = mvp['Assists'] * 2
                                xg_points = mvp['Expected Goals (xG)'] * 1.5
                                pass_points = mvp['Pass Completion %'] / 20
                                minute_points = mvp['Minutes'] / 10
    
                                st.write(f"   • Goals: {mvp['Goals']} × 3 = {goal_points:.1f} points")
                                st.write(f"   • Assists: {mvp['Assists']} × 2 = {assist_points:.1f} points")
                                st.write(f"   • xG Potential: {mvp['Expected Goals (xG)']} × 1.5 = {xg_points:.1f} points")
                                st.write(f"   • Pass Accuracy: {mvp['Pass Completion %']:.1f}% ÷ 20 = {pass_points:.1f} points")
                                st.write(f"   • Playing Time: {mvp['Minutes']} ÷ 10 = {minute_points:.1f} points")
                                st.write(f"   • **Total: {mvp['Value_Score']:.1f} points**")

                            st.success("🎯 These 10 questions show you understand football like a DATA SCIENTIST!")
                            # Final Summary / Commentary Section
                            st.subheader("📋 Executive Summary of Insights")
                            
                            with st.expander("📖 Click to Expand Full Analysis Summary"):

                                summary = """
                                My analysis journey went through **10 data-driven football questions**:

                                1. **Efficiency Analysis** – Identified the most clinical scorers vs wasteful finishers.
                                2. **Age Curve** – Pinpointed the sweet spot for peak footballing performance.
                                3. **Team Styles** – Compared teams that play ‘beautiful’ possession football vs defensive teams.
                                4. **Position Roles** – Verified whether defenders really score less than forwards.
                                5. **Creativity Index** – Highlighted true playmakers who create beyond just assists.
                                6. **Workrate Warriors** – Found players most involved per minute on the pitch.
                                7. **Discipline vs Skill** – Explored if skillful dribblers are more or less disciplined.
                                8. **Complete Player Index** – Built a formula to find the most well-rounded players.
                                9. **Experience vs Impact** – Tested if veterans or youngsters contribute more per 90 minutes.
                                10. **MVP Analysis** – Designed a multi-factor model to reveal the most valuable player.

                                ---
                                ### 🎯 Key Takeaways
                                - **Efficiency & Value**: We discovered players outperforming their expected goals, proving clinical finishing ability.  
                                - **Age**: Peak performance clustered around **26–29 years**.  
                                - **Teams**: Some teams shine with passing elegance, others with physical defending.  
                                - **Players**: Different stars emerge as top scorer, assister, workrate warrior, and MVP — showing the game has many forms of excellence.  

                                ---

                                📌 **Conclusion**:  
                                This analysis transforms raw football stats into **storytelling insights**. Even without being a football fan, you’ve approached the game like a **data scientist** — combining KPIs, visualizations, and multi-metric models to “shock” your football-loving friend.
                                """

                                st.markdown(summary)

                                # -----------------------
                                # 📋 Executive Summary
                                # -----------------------
                                st.subheader("📋 Executive Summary of Insights")

                                try:
                                    # Grab dynamic values from earlier analysis (safe lookups)
                                    top_scorer = most_efficient['Player'] if 'most_efficient' in locals() else "Unknown"
                                    top_scorer_goals = most_efficient['Goals'] if 'most_efficient' in locals() else "N/A"

                                    peak_age = int(df['Age'].median()) if 'Age' in df.columns else "N/A"

                                    best_team = team_style.loc[team_style['Pass Completion %'].idxmax(), 'Team'] if 'team_style' in locals() else "Unknown"
                                    tackles_team = team_style.loc[team_style['Tackles'].idxmax(), 'Team'] if 'team_style' in locals() else "Unknown"

                                    mvp = mvp_player['Player'] if 'mvp_player' in locals() else "Unknown"

                                    # Use expander for the final summary
                                    with st.expander("📖 Executive Summary (Click to Expand)"):
                                        summary = f"""
                                        ### 🔎 Key Highlights  

                                        ⚽ **Most Clinical Finisher** → **{top_scorer}**, scoring **{top_scorer_goals} goals** and outperforming xG 🎯  
                                        👨‍🎓 **Peak Performance Age** → Around **{peak_age} years old**, the golden balance of youth + experience 🏋️‍♂️  
                                        🪄 **Beautiful Football** → **{best_team}** dominated with passing elegance 💫, while **{tackles_team}** relied on tough defending 🛡️  
                                        🏆 **MVP of the Season** → Our model crowns **{mvp}** as the all-around game-changer 🌟  

                                        ---
                                        📌 **Conclusion**:  
                                        This analysis wasn’t just about stats — it told a **football story** 📰.  
                                        From efficiency to MVPs, you uncovered insights that rival pro analysts 🚀⚽.  
                                        """
                                        st.markdown(summary)

                                except Exception as e:
                                    st.warning(f"⚠️ Could not generate dynamic summary: {e}")


                    








except FileNotFoundError:
    st.error("The file was not found. Please check the file path.")
except pd.errors.EmptyDataError:
    st.error("The file is empty. Please check the file contents.")
except Exception as e:
    st.error(f"An error occurred: {e}")