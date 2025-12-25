def gen_html_from_players(players):
    rows = "".join(
        f"<tr><td>{p.get('username')}</td>"
        f"<td>{p.get('Prestige', 0)}</td>"
        f"<td>{p.get('Rank')}</td>"
        f"<td>{p.get('kills', 0)}</td>"
        f"<td>{p.get('deaths', 0)}</td>"
        f"<td>{round(p.get('kills', 0) / p.get('deaths', 1) if p.get('deaths', 0) > 0 else 0, 4)}</td></tr>"
        for p in players
    )
    return "<table><tr><th>Username</th><th>Prestige</th><th>Rank</th><th>Kills</th><th>Deaths</th><th>KDR</th></tr>" + rows + "</table>"