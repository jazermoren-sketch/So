def match_from_club(club):

    members = club["members"]

    if len(members) < 2:
        return None

    players = members[:4]
    club["members"] = members[4:]

    return players