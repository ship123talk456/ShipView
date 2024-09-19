import streamlit as st
import pandas as pd
import asyncio
import websockets
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# 设置页面配置
st.set_page_config(page_title="船舶信息显示与实时位置", layout="wide")

# 读取CSV文件
def load_ship_data(filename):
    return pd.read_csv(filename)

# 创建WebSocket订阅消息
def create_subscription_message(api_key, imo_numbers):
    return json.dumps({
        "APIKey": api_key,
        "BoundingBoxes": [[[-90, -180], [90, 180]]],  # 全球范围
        "FiltersShipMMSI": mmsi,  # 指定的 IMO number 列表
        "FilterMessageTypes": ["PositionReport"]  # 只订阅位置报告消息
    })

# 连接到AISStream并订阅数据
async def subscribe_to_aistream(api_key, imo_numbers):
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscription_message = create_subscription_message(api_key, imo_numbers)
        await websocket.send(subscription_message)
        async for message in websocket:
            return json.loads(message)

# 异步调用WebSocket
def get_ship_data(api_key, imo_numbers):
    return asyncio.run(subscribe_to_aistream(api_key, imo_numbers))

# 显示船舶信息和地图
def display_ship_info_and_map(df, ship_data):
    col1, col2 = st.columns([1, 3])  # 左侧表格，右侧地图

    with col1:
        st.write("## 船舶列表")
        search_term = st.text_input("输入船名搜索")
        if search_term:
            df = df[df["Name of ship"].str.contains(search_term, case=False)]
        st.dataframe(df)

    with col2:
        st.write("## 船舶实时位置图")
        
        # 创建地图并设置初始位置
        map_center = [0, 0]
        m = folium.Map(location=map_center, zoom_start=2)
        
        # 使用 MarkerCluster 以便更好地显示多个点
        marker_cluster = MarkerCluster().add_to(m)
        
        if ship_data:
            for ship in ship_data.get('Message', {}).get('Ships', []):
                lat = ship.get('Latitude', 0)
                lon = ship.get('Longitude', 0)
                ship_name = ship.get('ShipName', 'Unknown Ship')
                ais_time = ship.get('Timestamp', 'Unknown Time')
                
                # 在地图上添加一个小红点，并在鼠标点击时显示弹窗
                popup_info = f"船名: {ship_name}<br>AIS时间: {ais_time}"
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=popup_info
                ).add_to(marker_cluster)
        
        # 显示地图
        st_folium(m, width=700, height=500)

# 主函数
def main():
    st.title('船舶信息显示与实时位置')

    # 指定CSV文件路径
    filename = 'shiplist.csv'
    
    # 读取CSV文件
    df = load_ship_data(filename)
    
    # 获取IMO号码列表
    mmsi = df['MMSI'].tolist()

    # 使用布局，将按钮移动到右侧地图的下方
    col1, col2 = st.columns([1, 12])

    with col2:
        if st.button("获取船舶实时位置"):
            # 使用异步任务获取船舶实时数据
            api_key = "9e6aa141ba5aaf48fd35461cabc4902ab00d4e6e"
            ship_data = get_ship_data(api_key, mmsi)
            display_ship_info_and_map(df, ship_data)
        else:
            display_ship_info_and_map(df, None)

if __name__ == "__main__":
    main()
