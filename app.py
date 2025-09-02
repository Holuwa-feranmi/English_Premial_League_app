import pandas as pd 
import  streamlit as st
import altair as alt

@st.cache_data
def load_data():
    df = pd.read_csv("database.csv")

    # Keep only the part before the dash as integer
    df["Age"] = df["Age"].astype(str).str.split("-").str[0].astype(int)

    df = df.rename(columns={'#': 'Jersey Number'})


    # Convert everything to string first
    df["Pass Completion %"] = df["Pass Completion %"].astype(str)

    # Remove unwanted characters (like %, spaces, words)
    df["Pass Completion %"] = df["Pass Completion %"].str.replace(r"[^0-9.]", "", regex=True)

    # Handle empty strings ("") by replacing them with NaN
    df["Pass Completion %"] = df["Pass Completion %"].replace("", None)

    # Convert to numeric (float)
    df["Pass Completion %"] = pd.to_numeric(df["Pass Completion %"], errors="coerce")


    st.title("⚽ Premier League Data Analyzer")


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
    
    top_scorer = df.groupby("Player")["Goals"].sum().reset_index().sort_values(by="Goals", ascending=False).iloc[0]
    col1.metric("🏆 Top Scorer", top_scorer["Player"], f'{int(top_scorer["Goals"])} Goals')

    # KPI 2: Assist Leader
    assist_leader = df.groupby("Player")["Assists"].sum().reset_index().sort_values(by="Assists", ascending=False).iloc[0]
    col2.metric("🎯 Assist King", assist_leader["Player"], f'{int(assist_leader["Assists"])} Assists')

    # KPI 3: Most Minutes Played
    most_minutes = df.groupby("Player")["Minutes"].sum().reset_index().sort_values(by="Minutes", ascending=False).iloc[0]
    col3.metric("🕒 Iron Man", most_minutes["Player"], f'{int(most_minutes["Minutes"])} mins')

    # Second row of KPIs
    col4, col5, col6 = st.columns(3)

    # KPI 4: Best Goals per 90
    player_gp90 = df.groupby("Player").agg({"Goals": "sum", "Minutes": "sum"}).reset_index()
    player_gp90["Goals_per_90"] = player_gp90.apply(lambda x: (x["Goals"] / x["Minutes"]) * 90 if x["Minutes"] > 0 else 0, axis=1)
    best_gp90 = player_gp90.loc[player_gp90["Goals_per_90"].idxmax()]
    col4.metric("⚡ Goals per 90", best_gp90["Player"], f'{best_gp90["Goals_per_90"]:.2f}')


    # KPI 5: Pass Accuracy Leader
    pass_leader = df.groupby("Player")["Pass Completion %"].sum().reset_index().sort_values(by="Pass Completion %", ascending=False).iloc[0]
    col5.metric("🎯 Pass Accuracy", pass_leader["Player"], f'{int(pass_leader["Pass Completion %"])}%')

    # KPI 6: Discipline (most yellow cards)
    discipline = df.groupby("Player")["Yellow Cards"].sum().reset_index().sort_values(by="Yellow Cards", ascending=False).iloc[0]
    col6.metric("🟨 Most Booked", discipline["Player"], f'{int(discipline["Yellow Cards"])} Yellows')

    # Section 4 (Research Question and Analysis)
    st.subheader("🔥 10 Mind-Blowing Football Questions")
    # Question 1: Who are the top 10 scorers?
    st.write("### 1. Player with the highest Goals ")
    top_scorers = df.groupby("Player")["Goals"].sum().reset_index().nlargest(10, "Goals")
    st.write(top_scorers)

    chart_1 = alt.Chart(top_scorers).mark_bar().encode(
        x=alt.X('Player:N', sort='-y', title='Player'),
        y=alt.Y('Goals:Q', title='Number of Goals'),
        color=alt.Color('Goals:Q', scale=alt.Scale(scheme='plasma'), title='Goals'),
        tooltip=['Player', 'Goals']
    ).properties(width=600, height=400, title="Top 10 Goal Scorers")

    st.altair_chart(chart_1, use_container_width=True)

    # Question 2. Who are the top 10 Best Assists
    st.write("### 2. Who are the top 10 players with the most assists?")
    best_assists = df.groupby("Player")["Assists"].sum().reset_index().nlargest(10, "Assists")
    st.write(best_assists)

    chart_2 = alt.Chart(best_assists).mark_bar().encode(
        x=alt.X("Player:N", sort="-y", title="Player"),
        y=alt.Y("Assists:Q", title="Number of Assists"),
        color=alt.Color("Assists:Q", scale=alt.Scale(scheme="cividis"), title="Assists"),
        tooltip=["Player", "Assists"]
    ).properties(width=600, height=480, title="Top 10 Assisters")
    st.altair_chart(chart_2, use_container_width=True)

    st.write("### 3. Who are the top 5 players with the most yellow cards?")
    cards = df.groupby("Player")["Yellow Cards"].sum().reset_index().nlargest(5, "Yellow Cards")
    st.write(cards)

    chart_3 = alt.Chart(cards).mark_bar().encode(
        x=alt.X('Player:N', sort='-y', title='Player'),
        y=alt.Y('Yellow Cards:Q', title='Number of Cards'),
        color=alt.Color('Yellow Cards:Q', scale=alt.Scale(scheme='inferno'), title='Cards'),
        tooltip=['Player', 'Yellow Cards']
    ).properties(width=600, height=400, title="Top 5 Players with the Most Yellow Cards")

    st.altair_chart(chart_3, use_container_width=True)

    st.write("### 4. What are the top 10 teams with the highest number of goals scored?")
    team_goals = df.groupby('Team')['Goals'].sum().reset_index().nlargest(10, 'Goals')
    st.write(team_goals)

    # Create chart
    chart_4 = alt.Chart(team_goals).mark_bar().encode(
        x=alt.X('Team:N', sort='-y', title='Team'),
        y=alt.Y('Goals:Q', title='Number of Goals'),
        color=alt.Color('Goals:Q', scale=alt.Scale(scheme='turbo'), title='Goals'),
        tooltip=['Team', 'Goals']
    ).properties(width=600, height=400, title="Top 10 Teams by Goals")

    st.altair_chart(chart_4, use_container_width=True)



    st.write("### 5. Who are the top 10 players with the most successful dribbles?")
    dribbles = df.groupby('Player')['Dribbles'].sum().reset_index().nlargest(10, 'Dribbles')
    st.write(dribbles)

    # Create chart
    chart_5 = alt.Chart(dribbles).mark_bar().encode(
        x=alt.X("Player:N", sort="-y", title="Player"),
        y=alt.Y("Dribbles:Q", title="Number of Dribbles"),
        color=alt.Color("Dribbles:Q", scale=alt.Scale(scheme="tealblues"), title="Dribbles"),
        tooltip=["Player", "Dribbles"]
    ).properties(width=600, height=400, title="Top 10 Player by Dribbles")

    st.altair_chart(chart_5, use_container_width=True)


    st.write("### 6. Which position has the most goals scored?")
    position = df.groupby("Position")["Goals"].sum().reset_index().nlargest(10, "Goals")
    st.write(position)

    # Create chart
    chart_6 = alt.Chart(position).mark_bar().encode(
        x=alt.X("Position:N", sort="-y", title="Position"),
        y=alt.Y("Goals:Q", title="Number of Goals"),
        color=alt.Color("Goals:Q", scale=alt.Scale(scheme="cividis"), title="Goals"),
        tooltip=["Position", "Goals"]
    ).properties(width=600, height=400, title="Top 10 Player by Dribbles")

    st.altair_chart(chart_6, use_container_width=True)


    st.write("### 7. Who are the top 10 players with the most successful dribbles?")
    pass_progression = df.groupby('Player')['Progressive Passes'].sum().reset_index().nlargest(10, 'Progressive Passes')
    st.write(pass_progression )

    # Create chart
    chart_7 = alt.Chart(pass_progression ).mark_bar().encode(
        x=alt.X("Player:N", sort="-y", title="Player"),
        y=alt.Y("Progressive Passes:Q", title="Number of passes"),
        color=alt.Color("Progressive Passes:Q", scale=alt.Scale(scheme="plasma"), title="Progressive Passes"),
        tooltip=["Player", "Progressive Passes"]
    ).properties(width=600, height=400, title="Top 10 Player by Progressive Passes")

    st.altair_chart(chart_7, use_container_width=True)












            








except FileNotFoundError:
    st.error("The file was not found. Please check the file path.")
except pd.errors.EmptyDataError:
    st.error("The file is empty. Please check the file contents.")
except Exception as e:
    st.error(f"An error occurred: {e}")