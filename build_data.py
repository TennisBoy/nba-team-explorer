"""Fetch NBA rosters + per-game stats across multiple seasons -> nba_data.js"""
import json, time
from nba_api.stats.static import teams as static_teams
from nba_api.stats.endpoints import commonteamroster, leaguedashplayerstats

SEASONS = ["2025-26", "2024-25", "2023-24", "2022-23", "2021-22"]

# NBA champion by season (first season is post-cutoff, verified via NBA.com/ESPN)
CHAMPIONS = {
    "2025-26": "NYK",  # New York Knicks def. San Antonio Spurs 4-1
    "2024-25": "OKC",  # Oklahoma City Thunder
    "2023-24": "BOS",  # Boston Celtics
    "2022-23": "DEN",  # Denver Nuggets
    "2021-22": "GSW",  # Golden State Warriors
}

COLORS = {
    "ATL":"#E03A3E","BOS":"#007A33","BKN":"#000000","CHA":"#1D1160","CHI":"#CE1141",
    "CLE":"#860038","DAL":"#00538C","DEN":"#0E2240","DET":"#C8102E","GSW":"#1D428A",
    "HOU":"#CE1141","IND":"#002D62","LAC":"#C8102E","LAL":"#552583","MEM":"#5D76A9",
    "MIA":"#98002E","MIL":"#00471B","MIN":"#0C2340","NOP":"#0C2340","NYK":"#006BB6",
    "OKC":"#007AC1","ORL":"#0077C0","PHI":"#006BB6","PHX":"#1D1160","POR":"#E03A3E",
    "SAC":"#5A2D81","SAS":"#C4CED4","TOR":"#CE1141","UTA":"#002B5C","WAS":"#002B5C",
}
ACCENT = {
    "ATL":"#C1D32F","BOS":"#BA9653","BKN":"#FFFFFF","CHA":"#00788C","CHI":"#000000",
    "CLE":"#FDBB30","DAL":"#B8C4CA","DEN":"#FEC524","DET":"#1D42BA","GSW":"#FFC72C",
    "HOU":"#000000","IND":"#FDBB30","LAC":"#1D428A","LAL":"#FDB927","MEM":"#12173F",
    "MIA":"#F9A01B","MIL":"#EEE1C6","MIN":"#236192","NOP":"#C8102E","NYK":"#F58426",
    "OKC":"#EF3B24","ORL":"#C4CED4","PHI":"#ED174C","PHX":"#E56020","POR":"#000000",
    "SAC":"#63727A","SAS":"#000000","TOR":"#000000","UTA":"#F9A01B","WAS":"#E31837",
}

teams = sorted(static_teams.get_teams(), key=lambda t: t["full_name"])
ALL = {"seasons": SEASONS, "data": {}}

def fetch(fn, **kw):
    for a in range(4):
        try:
            return fn(**kw).get_data_frames()[0]
        except Exception as e:
            print("   retry:", e); time.sleep(2)
    return None

for season in SEASONS:
    champ = CHAMPIONS.get(season)
    print(f"\n=== SEASON {season} (champion {champ}) ===")
    ls = fetch(leaguedashplayerstats.LeagueDashPlayerStats,
               season=season, per_mode_detailed="PerGame")
    stat_by_pid = {}
    if ls is not None:
        for _, r in ls.iterrows():
            stat_by_pid[int(r["PLAYER_ID"])] = {
                "GP":int(r["GP"]),"MIN":round(float(r["MIN"]),1),
                "PTS":round(float(r["PTS"]),1),"REB":round(float(r["REB"]),1),
                "AST":round(float(r["AST"]),1),"STL":round(float(r["STL"]),1),
                "BLK":round(float(r["BLK"]),1),"FG_PCT":round(float(r["FG_PCT"]),3),
                "FG3_PCT":round(float(r["FG3_PCT"]),3),"FT_PCT":round(float(r["FT_PCT"]),3),
            }
    ALL["data"][season] = {}
    for i, t in enumerate(teams, 1):
        abbr = t["abbreviation"]
        print(f"[{season}][{i:2}/30] {abbr}")
        df = fetch(commonteamroster.CommonTeamRoster, team_id=t["id"], season=season)
        players = []
        if df is not None:
            for _, r in df.iterrows():
                pid = int(r["PLAYER_ID"])
                players.append({
                    "id":pid,"name":r["PLAYER"],"num":str(r["NUM"]),"pos":r["POSITION"],
                    "height":r["HEIGHT"],"weight":str(r["WEIGHT"]),
                    "age":None if r["AGE"] in (None,"") else float(r["AGE"]),
                    "exp":str(r["EXP"]),"s":stat_by_pid.get(pid),
                })
        ALL["data"][season][abbr] = {
            "id":t["id"],"name":t["full_name"],"city":t["city"],"nickname":t["nickname"],
            "abbr":abbr,"color":COLORS.get(abbr,"#1D428A"),"accent":ACCENT.get(abbr,"#fff"),
            "champion":abbr==champ,"players":players,
        }
        time.sleep(0.5)

with open("nba_data.js","w",encoding="utf-8") as f:
    f.write("window.NBA_DATA = ")
    json.dump(ALL, f, ensure_ascii=False)
    f.write(";\n")

tot = sum(len(v["players"]) for s in ALL["data"].values() for v in s.values())
print(f"\nWrote nba_data.js: {len(SEASONS)} seasons, {tot} player-rows")
