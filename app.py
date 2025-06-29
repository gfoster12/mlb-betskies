import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import os

# --- Config ---
DATA_PATH = "data/upcoming_games_predictions.csv"
PLAYER_STATS_PATH = "data/player_hr_rates_2024.csv"           # player_id,player_name,team,hr_rate,hr,pa
PITCHER_STATS_PATH = "data/pitcher_stats_2024.csv"            # player_id,player_name,team,ERA,K9,BB9,WHIP
TEAM_STATS_PATH = "data/team_stats_2024.csv"                  # team,win_pct,hr_rate,era,other stats
LIVE_ODDS_PATH = "data/live_odds.csv"                         # gamePk,away_team,home_team,away_odds,home_odds,draw_odds,source,last_updated

# --- Load data ---
def load_predictions():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    df = pd.read_csv(DATA_PATH)
    if "gameDate" in df.columns:
        df["gameDate"] = pd.to_datetime(df["gameDate"])
    if "home_win_prob" in df.columns:
        df["home_win_prob"] = (df["home_win_prob"] * 100).round(1)
    if "away_win_prob" in df.columns:
        df["away_win_prob"] = (df["away_win_prob"] * 100).round(1)
    return df

def load_player_stats():
    if not os.path.exists(PLAYER_STATS_PATH):
        return pd.DataFrame()
    df = pd.read_csv(PLAYER_STATS_PATH)
    df["player_id"] = df["player_id"].astype(str)
    return df

def load_pitcher_stats():
    if not os.path.exists(PITCHER_STATS_PATH):
        return pd.DataFrame()
    df = pd.read_csv(PITCHER_STATS_PATH)
    df["player_id"] = df["player_id"].astype(str)
    return df

def load_team_stats():
    if not os.path.exists(TEAM_STATS_PATH):
        return pd.DataFrame()
    df = pd.read_csv(TEAM_STATS_PATH)
    return df

def load_live_odds():
    if not os.path.exists(LIVE_ODDS_PATH):
        return pd.DataFrame()
    df = pd.read_csv(LIVE_ODDS_PATH)
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    return df

app = Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
])

app.title = "MLB Betskies Predictions"

app.layout = html.Div([
    html.Div([
        html.H1("MLB Betskies Dashboard", className="display-4"),
        html.P("Daily MLB game predictions, advanced stats, and picks.", className="lead"),
        html.Hr(),
    ], className="text-center my-4"),

    html.Div([
        html.Label("Filter by Date:"),
        dcc.DatePickerSingle(
            id="date-picker",
            min_date_allowed=None,
            max_date_allowed=None,
            initial_visible_month=None,
            date=None,
        ),
        dcc.Dropdown(
            id="team-filter",
            placeholder="Filter by team...",
            multi=True
        ),
    ], className="row mb-4 justify-content-center"),

    html.Div([
        html.H4("Today's & Upcoming Predictions"),
        dash_table.DataTable(
            id='pred-table',
            columns=[
                {"name": "Date", "id": "gameDate"},
                {"name": "Away", "id": "away_team"},
                {"name": "Home", "id": "home_team"},
                {"name": "Pick", "id": "pick"},
                {"name": "Home Win %", "id": "home_win_prob"},
                {"name": "Away Win %", "id": "away_win_prob"},
                {"name": "Stadium", "id": "venue"},
                {"name": "Weather", "id": "weather_summary"},
                {"name": "Pitchers", "id": "pitchers"},
                {"name": "Home Odds", "id": "home_odds"},
                {"name": "Away Odds", "id": "away_odds"},
            ],
            data=[],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold"},
            page_size=20,
            filter_action="native",
            sort_action="native",
            row_selectable="single",
        )
    ], className="mb-5"),

    html.Div(id="game-details"),

    html.Hr(),
    html.Footer([
        html.P("Powered by MLB Betskies · Advanced ML & Data Engineering · 2025"),
    ], className="text-center text-muted my-2"),
], className="container")

@app.callback(
    [Output('pred-table', 'data'),
     Output('date-picker', 'min_date_allowed'),
     Output('date-picker', 'max_date_allowed'),
     Output('date-picker', 'initial_visible_month'),
     Output('date-picker', 'date'),
     Output('team-filter', 'options')],
    [Input('date-picker', 'date'),
     Input('team-filter', 'value')]
)
def update_table(date_val, teams_val):
    df = load_predictions()
    odds_df = load_live_odds()
    if df.empty:
        return [], None, None, None, None, []

    mindate = df["gameDate"].min().date()
    maxdate = df["gameDate"].max().date()
    initial = mindate

    teams = sorted(set(df["home_team"]).union(df["away_team"]))
    options = [{"label": t, "value": t} for t in teams]

    dff = df.copy()
    if date_val:
        dff = dff[dff["gameDate"].dt.date == pd.to_datetime(date_val).date()]
    if teams_val:
        dff = dff[dff["home_team"].isin(teams_val) | dff["away_team"].isin(teams_val)]

    def summarize_weather(row):
        if "temperature" in row and not pd.isna(row["temperature"]):
            return f"{row['temperature']:.0f}°F, {row.get('humidity', 0):.0f}% RH, {row.get('windspeed', 0):.0f} mph"
        return row.get('weather', '')

    def summarize_pitchers(row):
        hp = row.get("home_pitcher", "")
        ap = row.get("away_pitcher", "")
        return f"{ap} vs {hp}"

    if "weather_summary" not in dff:
        dff["weather_summary"] = dff.apply(summarize_weather, axis=1)
    if "pitchers" not in dff:
        dff["pitchers"] = dff.apply(summarize_pitchers, axis=1)

    # Merge in live odds by (gamePk) if available, else by team matchup/date
    if "gamePk" in dff.columns and not odds_df.empty and "gamePk" in odds_df.columns:
        dff = dff.merge(odds_df[["gamePk", "home_odds", "away_odds"]], on="gamePk", how="left")
    elif not odds_df.empty:
        dff = pd.merge(
            dff,
            odds_df[["home_team", "away_team", "home_odds", "away_odds"]],
            on=["home_team", "away_team"],
            how="left"
        )
    else:
        dff["home_odds"] = ""
        dff["away_odds"] = ""

    columns = [
        "gameDate", "away_team", "home_team", "pick",
        "home_win_prob", "away_win_prob", "venue",
        "weather_summary", "pitchers",
        "home_odds", "away_odds"
    ]
    dff = dff[columns]

    return dff.to_dict("records"), mindate, maxdate, initial, initial, options

@app.callback(
    Output('game-details', 'children'),
    Input('pred-table', 'selected_rows'),
    State('pred-table', 'data')
)
def show_details(selected, table_data):
    if not selected or not table_data:
        return ""
    idx = selected[0]
    row = table_data[idx]

    player_stats = load_player_stats()
    pitcher_stats = load_pitcher_stats()
    team_stats = load_team_stats()
    odds_df = load_live_odds()

    home_pitcher = row.get("home_pitcher", "")
    away_pitcher = row.get("away_pitcher", "")
    home_team = row.get("home_team", "")
    away_team = row.get("away_team", "")
    game_date = row.get("gameDate", "")

    home_pitcher_stats = pitcher_stats[pitcher_stats["player_name"] == home_pitcher]
    away_pitcher_stats = pitcher_stats[pitcher_stats["player_name"] == away_pitcher]

    home_team_stats = team_stats[team_stats["team"] == home_team]
    away_team_stats = team_stats[team_stats["team"] == away_team]

    home_odds, away_odds, draw_odds, odds_source, last_updated = "", "", "", "", ""
    if odds_df is not None and not odds_df.empty:
        mask = (
            (odds_df["home_team"] == home_team) &
            (odds_df["away_team"] == away_team)
        )
        if "gameDate" in odds_df.columns and game_date:
            mask = mask & (pd.to_datetime(odds_df["gameDate"]) == pd.to_datetime(game_date))
        odds_row = odds_df[mask]
        if not odds_row.empty:
            odds_row = odds_row.iloc[0]
            home_odds = odds_row.get("home_odds", "")
            away_odds = odds_row.get("away_odds", "")
            draw_odds = odds_row.get("draw_odds", "")
            odds_source = odds_row.get("source", "")
            last_updated = odds_row.get("last_updated", "")

    try:
        pred_df = load_predictions()
        game_row = pred_df[
            (pred_df["home_team"] == home_team) &
            (pred_df["away_team"] == away_team) &
            (str(pred_df["gameDate"]) == str(row["gameDate"]))
        ].iloc[0]
        def get_top_hr_players(lineup_ids, team):
            if isinstance(lineup_ids, str):
                lineup_ids = eval(lineup_ids)
            subset = player_stats[(player_stats["player_id"].isin([str(pid) for pid in lineup_ids])) & (player_stats["team"] == team)]
            top = subset.sort_values("hr_rate", ascending=False).head(3)
            return top
        if "home_lineup_ids" in game_row and not pd.isna(game_row["home_lineup_ids"]):
            top_home = get_top_hr_players(game_row["home_lineup_ids"], home_team)
        else:
            top_home = pd.DataFrame()
        if "away_lineup_ids" in game_row and not pd.isna(game_row["away_lineup_ids"]):
            top_away = get_top_hr_players(game_row["away_lineup_ids"], away_team)
        else:
            top_away = pd.DataFrame()
    except Exception:
        top_home = top_away = pd.DataFrame()
    
    def make_pitcher_table(pitcher_stats_df, label):
        if pitcher_stats_df.empty:
            return html.P(f"{label} stats unavailable.")
        row = pitcher_stats_df.iloc[0]
        return html.Table([
            html.Tr([html.Th(label), html.Th("ERA"), html.Th("K/9"), html.Th("BB/9"), html.Th("WHIP")]),
            html.Tr([
                html.Td(row["player_name"]),
                html.Td(f"{row.get('ERA', 'N/A'):.2f}"),
                html.Td(f"{row.get('K9', 'N/A'):.2f}"),
                html.Td(f"{row.get('BB9', 'N/A'):.2f}"),
                html.Td(f"{row.get('WHIP', 'N/A'):.2f}")
            ])
        ], className="table table-sm table-bordered table-striped w-auto mb-2")

    def make_team_table(team_stats_df, label):
        if team_stats_df.empty:
            return html.P(f"{label} team stats unavailable.")
        row = team_stats_df.iloc[0]
        return html.Table([
            html.Tr([html.Th(label), html.Th("Win %"), html.Th("ERA"), html.Th("HR Rate")]),
            html.Tr([
                html.Td(row["team"]),
                html.Td(f"{row.get('win_pct', 'N/A'):.3f}"),
                html.Td(f"{row.get('era', 'N/A'):.2f}"),
                html.Td(f"{row.get('hr_rate', 'N/A'):.4f}")
            ])
        ], className="table table-sm table-bordered table-striped w-auto mb-2")

    def make_hr_table(df, label):
        if df.empty:
            return html.P(f"Top HR hitters for {label} unavailable.")
        header = [html.Th("Player"), html.Th("HR Rate"), html.Th("HR"), html.Th("PA")]
        rows = []
        for _, r in df.iterrows():
            rows.append(html.Tr([
                html.Td(r["player_name"]),
                html.Td(f"{r.get('hr_rate', 0):.4f}"),
                html.Td(f"{int(r.get('hr', 0))}"),
                html.Td(f"{int(r.get('pa', 0))}")
            ]))
        return html.Table([html.Tr(header)] + rows, className="table table-sm table-bordered table-striped w-auto mb-2")

    details = []
    details.append(html.H4(f"Game Details: {away_team} @ {home_team}"))
    details.append(html.P(f"Venue: {row['venue']}"))
    details.append(html.P(f"Date: {row['gameDate']}"))
    details.append(html.P(f"Weather: {row['weather_summary']}"))
    details.append(html.P(f"Pitching Matchup: {row['pitchers']}"))

    details.append(html.Hr())
    details.append(html.H5("Pitcher Advanced Stats"))
    details.append(
        html.Div([
            make_pitcher_table(away_pitcher_stats, "Away Pitcher"),
            make_pitcher_table(home_pitcher_stats, "Home Pitcher"),
        ], className="row")
    )
    details.append(html.H5("Team Advanced Stats"))
    details.append(
        html.Div([
            make_team_table(away_team_stats, "Away Team"),
            make_team_table(home_team_stats, "Home Team"),
        ], className="row")
    )
    details.append(html.H5("Top HR Hitters in Projected Lineup"))
    details.append(
        html.Div([
            html.Div([html.H6(f"{away_team}"), make_hr_table(top_away, "Away")], className="col-md-6"),
            html.Div([html.H6(f"{home_team}"), make_hr_table(top_home, "Home")], className="col-md-6"),
        ], className="row")
    )
    details.append(html.H5("Live Odds"))
    details.append(
        html.Table([
            html.Tr([
                html.Th(""),
                html.Th("Home"),
                html.Th("Away"),
                html.Th("Draw") if draw_odds else None,
                html.Th("Source"),
                html.Th("Updated"),
            ]),
            html.Tr([
                html.Td("Odds"),
                html.Td(home_odds),
                html.Td(away_odds),
                html.Td(draw_odds) if draw_odds else None,
                html.Td(odds_source),
                html.Td(str(last_updated) if last_updated else ""),
            ]),
        ], className="table table-sm table-bordered table-striped w-auto mb-2") if home_odds or away_odds else html.P("No odds data available for this game.")
    )
    return html.Div(details, className="card card-body my-3")

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)