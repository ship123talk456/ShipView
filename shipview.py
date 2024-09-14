import streamlit as st
import pandas as pd
import asyncio
import websockets
import json
import time
from streamlit_folium import st_folium
import folium

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
        "FiltersShipMMSI": imo_numbers,  # 指定的 IMO number 列表
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
    col1, col2 = st.columns([1, 1])  # 左侧表格，右侧地图

    with col1:
        st.write("## 船舶列表")
        search_term = st.text_input("输入船名搜索")
        if search_term:
            df = df[df["Name of ship"].str.contains(search_term, case=False)]
        st.dataframe(df)

    with col2:
        st.write("## 船舶实时位置图")
        # 创建一个初始的地图
        map_center = [0, 0]  # 设置地图中心
        m = folium.Map(location=map_center, zoom_start=2)
        
        if ship_data:
            lat = ship_data.get('MetaData', {}).get('Latitude', 0)
            lon = ship_data.get('MetaData', {}).get('Longitude', 0)
            ship_name = ship_data.get('Message', {}).get('ShipName', 'Unknown Ship')
            
            # 添加船舶位置到地图上
            folium.Marker([lat, lon], tooltip=ship_name).add_to(m)
        
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
    imo_numbers = df['IMO number'].tolist()

    # 使用异步任务获取船舶实时数据
    api_key = "9e6aa141ba5aaf48fd35461cabc4902ab00d4e6e"
    if st.button("获取船舶实时位置"):
        ship_data = get_ship_data(api_key, imo_numbers)
        display_ship_info_and_map(df, ship_data)
    else:
        display_ship_info_and_map(df, None)

if __name__ == "__main__":
    main()
