import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import time

def calctimediff(time1, time2):
    time1 = datetime.fromisoformat(time1)
    time2 = datetime.fromisoformat(time2)
    diff = time1-time2
    return abs(int(diff.total_seconds()))

stops = [[{"id": "942E95B4336BDFA7", "name": "往順利方向"},
         {"id": "9A16E73DC0B9AF6C", "name": "往順利方向"}],
         [{"id": "29740CCBBD82FC33", "name": "往順利方向"}],
         [{"id": "3BA9C90738A8600D", "name": "往彩虹方向"}],
         [{"id": "58611212645F0AB1", "name": "往彩虹方向"}],
         [{"id": "6D1FFB57C26F1108", "name": "彩雲總站"},
         {"id": "09680C5849BFA077", "name": "彩雲總站"},
         {"id": "177A516A81E9DEA5", "name": "彩雲總站"}]]
url = "https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/"
st.set_page_config(page_title="Bus ETA Information")
placeholder = st.empty()
container = st.container()
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

while True:
    for direction in stops:
        formatted = {}
        for stop in direction:
            response = requests.get(url+stop['id']) 
            if response.status_code == 200:
                data = response.json()['data']
                for i in data:
                    if i['eta'] != None and i["dest_en"] != "CHOI WAN" and i['eta_seq'] <= 3:
                        try:
                            tmp = formatted[str(i['route'])]
                            del tmp
                        except KeyError:
                            formatted[str(i['route'])] = {}
                            formatted[str(i['route'])]["Destination"] = i["dest_tc"]
                            formatted[str(i["route"])]["ETA"] = []
                        formatted[str(i['route'])]["ETA"].append(i["eta"])         
            else:
                print("Request failed with status code:", response.status_code)
        for i in formatted:
            formatted[i]['ETA'] = sorted(list(set(formatted[i]['ETA'])))
            s = []
            for j in formatted[i]["ETA"]:
                diff = calctimediff(j, datetime.now(pytz.timezone("Hongkong")).isoformat())
                mins = diff//60
                secs = diff%60
                if mins == 0:
                    s.append("<1")
                else:
                    if secs > 30:
                        mins+=1
                    s.append(f"{mins}")
            formatted[i]['ETA'] = '     | '.join(s)
            del s

        df = pd.DataFrame(formatted).transpose()
        with placeholder.container():
            st.header('巴士到站資訊')
            st.write(f"{direction[0]['name']} {stops.index(direction)+1}/{len(stops)}")
            st.table(df)
            st.write(f"最後更新: {str(datetime.now(pytz.timezone('Hongkong')))[:-13]}")
            st.caption("Made with ❤ by Bonfire")
        time.sleep(5.5)