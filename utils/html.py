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

def gen_html_table_from_player_stats(player_stats_list):
    if not player_stats_list:
        return "<p>No history found for this player.</p>"

    # player_stats_list[0] is now a Row object, which has .keys()
    all_headers = player_stats_list[0].keys()
    
    # Optional: Filter out internal IDs to keep the table clean
    exclude = ['stat_id', 'player_id']
    headers = [h for h in all_headers if h not in exclude]

    # Generate Header HTML
    header_html = "".join(f"<th>{h.replace('_', ' ').title()}</th>" for h in headers)
    
    # Generate Row HTML
    rows_html = ""
    for row in player_stats_list:
        cells = ""
        for h in headers:
            val = row[h]
            # Clean up floats (like KDR or HSKR)
            if isinstance(val, float):
                val = f"{val:.2f}"
            # Handle None/Null values
            if val is None:
                val = "-"
            cells += f"<td>{val}</td>"
        rows_html += f"<tr>{cells}</tr>"

    style = """
    <style>
        .stats-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.9em; }
        .stats-table th { background: #333; color: white; padding: 10px; position: sticky; top: 0; }
        .stats-table td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        .stats-table tr:nth-child(even) { background: #f9f9f9; }
        .stats-table tr:hover { background: #f1f1f1; }
    </style>
    """
    
    return f"{style}<div style='overflow-x:auto;'><table class='stats-table'><thead>{header_html}</thead><tbody>{rows_html}</tbody></table></div>"

def gen_html_table_of_players(player_rows):
    rows = "".join(
        f"<tr><td><a href='/player/{row['name']}'>{row['name']}</a></td></tr>" 
        for row in player_rows
    )
    return "<table><tr><th>Player Name</th></tr>" + rows + "</table>"