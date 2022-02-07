#!/usr/bin/env python

import fill_untappd
import yaml, json, sqlite3,  dateparser,os, sys
from pprint import pprint
# from airtable import Airtable
import pandas as pd


def main():
    fill_untappd.run()
    conn = sqlite3.connect("./db/untappd.db")
    df = pd.read_sql_query("select * from checkins;", conn)
    jsons  = df.json.apply(lambda j: json.loads(j))

    venues = jsons.apply(
        lambda x: 
        pd.concat([
            pd.Series(x["venue"]),
            pd.Series(x["user"])[["user_name"]],
            pd.Series(x["beer"]),
            pd.Series(x)[["checkin_id","created_at","rating_score"]]
            ])
            )

    venues_info = pd.concat([venues, 
    pd.concat([
        venues['contact'].apply(lambda x: pd.Series(x)),
        venues['location'].apply(lambda x: pd.Series(x)),
    ], axis = 1)],axis=1).set_index(["venue_slug","beer_slug"])

    venue_users = venues_info.groupby(["venue_slug","beer_slug"]).user_name.apply(','.join).rename("user_names")
    venue_rating = venues_info.groupby(["venue_slug","beer_slug"]).rating_score.sum().rename("total_rating")
    venue_counts = venues_info.groupby(["venue_slug","beer_slug"]).size().rename("n_checkins").astype(int)
    venue_last_checkin = venues_info.groupby(["venue_slug","beer_slug"]).created_at.apply(lambda x: x.apply(lambda y:dateparser.parse(y)).max()).rename("last_checkin")


    venues_info_dedup = venues_info.loc[~venues_info.index.duplicated()]
    venues_annotated = venues_info_dedup.join(pd.concat([venue_users, venue_rating, venue_counts,venue_last_checkin],axis=1))

    venues_annotated = venues_annotated.loc[ lambda x: x.venue_url != ""]
    venues_annotated = venues_annotated.loc[ venues_annotated.venue_url.notna()]
    venues_annotated = venues_annotated.loc[ lambda x: x.venue_city != ""]
    venues_annotated = venues_annotated.loc[ venues_annotated.venue_city.notna()]


    cans = pd.read_csv("../_data/cans.csv")

    for i, r in cans.iterrows():
        s = yaml.dump(r.to_dict(), default_flow_style=False)
        with open(f"../_cans/{r.code}.md","w") as f:
            f.write("---\n"),
            f.write(s)
            f.write("\n---\n")

    cans["untappd_id"] = cans.untappd.str.extract('(\d*$)').astype(int)

    venue_beers_annotated = venues_annotated.loc[lambda x: x.venue_id.notna()]
    venue_beers_annotated = venue_beers_annotated.join(cans.set_index("untappd_id")[["code"]], on ="bid")
    venue_beers_annotated = venue_beers_annotated.rename({"code":"can_code"}, axis = "columns")
    venue_beers_annotated["venue_id"] = venue_beers_annotated["venue_id"].astype(int)
    venue_beers_annotated.n_checkins = venue_beers_annotated.n_checkins.astype(int)

    venue_beers_annotated.to_csv("../_data/venue_beers.csv")

    venues_annotated = venue_beers_annotated.reset_index()[["venue_name","venue_slug","primary_category","contact","venue_id","lat","lng","venue_city" , "venue_address","venue_country","venue_city",	"venue_country",	"venue_state",'venue_url']]
    venues_annotated.to_csv("../_data/venues.csv")

if __name__ == "__main__":
    print(sys.argv)
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
    main()