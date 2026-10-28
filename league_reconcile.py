"""Advance an older standings table only after every club's baseline reconciles."""
import re


def advance_table(rows, results, aliases):
    def key(name):
        name = aliases.get(name, name)
        name = {'Weymouth': 'Weymouth FC', 'SC Inkberrow': 'Sporting Club Inkberrow'}.get(name, name)
        return re.sub(r'[^a-z0-9]', '', name.lower())

    clubs = {key(row['team']) for row in rows}
    if len(clubs) != 22 or len(rows) != 22:
        return rows, []
    matches, seen = [], set()
    for match in results:
        score = re.fullmatch(r'(\d+)\s*-\s*(\d+)', match.get('score', ''))
        day = match.get('date', '')
        home, away = key(match['home']), key(match['away'])
        identity = (home, away)
        if not score or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day) or home not in clubs or away not in clubs or identity in seen:
            return rows, []
        seen.add(identity)
        matches.append((day, home, away, *map(int, score.groups())))

    records = {club: dict(p=0, w=0, d=0, l=0, gf=0, ga=0, gd=0, pts=0) for club in clubs}
    def apply(match):
        _, home, away, hg, ag = match
        for club, gf, ga in ((home, hg, ag), (away, ag, hg)):
            record = records[club]
            record['p'] += 1
            record['gf'] += gf
            record['ga'] += ga
            record['gd'] = record['gf'] - record['ga']
            record['w' if gf > ga else 'd' if gf == ga else 'l'] += 1
            record['pts'] += 3 if gf > ga else 1 if gf == ga else 0

    baseline = sum(int(row['p']) for row in rows)
    matches.sort()
    for index, match in enumerate(matches):
        apply(match)
        if 2 * (index + 1) != baseline:
            continue
        # Require the complete source table, including its points, to match.
        # Unknown deductions, missing fixtures or conflicting scores stop advancement.
        if any(any(int(row[field]) != records[key(row['team'])][field]
                   for field in records[key(row['team'])]
                   if row.get(field) not in (None, '')) for row in rows):
            return rows, []
        later = matches[index + 1:]
        if not later or later[0][0] <= match[0]:
            return rows, []
        for remaining in later:
            apply(remaining)
        updated = [{**row, **records[key(row['team'])]} for row in rows]
        updated.sort(key=lambda row: (-row['pts'], -row['gd'], -row['gf'], row['team']))
        for position, row in enumerate(updated, 1):
            row['pos'] = position
        return updated, sorted({item[0] for item in later})
    return rows, []
