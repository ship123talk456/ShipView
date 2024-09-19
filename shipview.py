import streamlit as st
import folium
import streamlit_folium as slf
import pandas as pd
import asyncio
import websockets
import json
from datetime import datetime, timezone

# 读取船舶信息
def load_ship_data():
    return pd.read_csv('shiplist.csv')

# 连接AIS Stream并获取船舶位置
async def connect_ais_stream(ship_data):
    ships = ship_data['MMSI'].tolist()
    group_size = 50
    groups = [ships[i:i + group_size] for i in range(0, len(ships), group_size)]

    while True:
        try:
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
                for group in groups:
                    subscribe_message = {
                        "APIKey": "9e6aa141ba5aaf48fd35461cabc4902ab00d4e6e",  # 替换为你的API Key
                        "BoundingBoxes": [[[-90, -180], [90, 180]]],
                        "FiltersShipMMSI":  ["368207620", "367719770", "211476060"],
                        "FilterMessageTypes": ["PositionReport"]}
                    
                    subscribe_message_json = json.dumps(subscribe_message)
                    await websocket.send(subscribe_message_json)

                    async for message_json in websocket:
                        try:
                            message = json.loads(message_json)
                            if "MessageType" in message:
                                message_type = message["MessageType"]

                                if message_type == "PositionReport":
                                    ais_message = message['Message']['PositionReport']
                                    ship_id = ais_message['UserID']
                                    ship_info = ship_data[ship_data['MMSI'] == ship_id]
                                    if not ship_info.empty:
                                        ship_name = ship_info['Name of ship'].values[0]
                                        flag = ship_info['Flag'].values[0]
                                        imo_number = ship_info['IMO number'].values[0]
                                        gross_tonnage = ship_info['Gross tonnage'].values[0]
                                        year_of_build = ship_info['Year of build'].values[0]
                                        # 更新地图上的船舶位置
                                        st.session_state[ship_name] = {
                                            'latitude': ais_message['Latitude'],
                                            'longitude': ais_message['Longitude'],
                                            'info': f"Name: {ship_name}, Flag: {flag}, IMO: {imo_number}, Gross tonnage: {gross_tonnage}, Year of build: {year_of_build}"
                                        }
                            else:
                                print(f"No 'MessageType' in message: {message_json}")
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                        except KeyError as e:
                            print(f"KeyError: {e} in message: {message_json}")
                        except Exception as e:
                            print(f"Unexpected error: {e}")
        except websockets.ConnectionClosedError as e:
            print(f"Connection closed: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

# 创建全屏地图
def create_map():
    m = folium.Map(location=[0, 0], zoom_start=2, tiles='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', attr='OpenStreetMap')
    return m

# Streamlit应用
def main():
    st.title('Real-time Ship Tracking')
    ship_data = load_ship_data()
    m = create_map()

    with st.spinner('Connecting to AIS Stream...'):
        asyncio.run(connect_ais_stream(ship_data))

    for ship_name, data in st.session_state.items():
        if isinstance(data, dict):
            folium.Marker(
                location=[data['latitude'], data['longitude']],
                popup=f"{ship_name}: {data['info']}"
            ).add_to(m)

    slf.folium(m)

if __name__ == "__main__":
    st.session_state['ship_data'] = None
    st.session_state['map'] = None
    main()
