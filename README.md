# this makes thumbnails for different dashboards

download dashboards.csv from 
https://docs.google.com/spreadsheets/d/19c4qXVEgAgZmy1LuQXkLESaZr1cCt8n_WjAeu7nTs00/edit?gid=0#gid=0

Simplest:
python filterthumbs.py --refresh-thumbnails
Generates:
https://dosgoodcu.github.io/thubplay/all_dashboards_cached.html

Then repeat (some problem with naming with option above)
python filterthumbs.py
Filterthubs command line examples
python filterthumbs.py

https://dosgoodcu.github.io/thubplay/all_dashboards.html
https://dosgoodcu.github.io/thubplay/region_westafrica_dashboards.html
https://dosgoodcu.github.io/thubplay/region_westafrica_restricted_false_dashboards.html
https://dosgoodcu.github.io/thubplay/region_westafrica_type_publicmonitoringdashboard_restricted_false_dashboards.html
https://dosgoodcu.github.io/thubplay/restricted_false_dashboards.html
https://dosgoodcu.github.io/thubplay/type_designdashboard_dashboards.html
https://dosgoodcu.github.io/thubplay/type_designdashboard_restricted_false_dashboards.html
https://dosgoodcu.github.io/thubplay/type_publicmonitoringdashboard_dashboards.html
https://dosgoodcu.github.io/thubplay/type_publicmonitoringdashboard_restricted_false_dashboards.html
Hand edited titles:
https://dosgoodcu.github.io/thubplay/unrestricted_dashboards.html

Maybe its supposed to be filter, not finter…

python filterthumbs.py --finter Restricted FALSE
python filterthumbs.py --filter Type "Design Dashboard" Restricted FALSE
filterthumbs.py --filter Type "Public Monitoring Dashboard" Restricted FALSE
python filterthumbs.py --filter Region "West Africa" Type "Public Monitoring Dashboard" Restricted FALSE
python filterthumbs.py --filter Region "West Africa" Restricted FALSE
python filterthumbs.py --filter Country "Ethiopia" Restricted FALSE

Cached version (everything, including csv in cached directory):
python3 filterthumbscached.py --filter Restricted FALSE
