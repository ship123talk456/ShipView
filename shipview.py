import streamlit as st
import pandas as pd
import asyncio
import websockets
import json

# 设置页面配置
st.set_page_config(page_title="船舶信息显示与实时位置", layout="wide")

# 读取CSV文件
def load_ship_data(filename):
    return pd.read_csv(filename)

# 创建WebSocket订阅消息
def create_subscription_message(api_key, imo_numbers):
    return json.dumps({
        "APIKey": "9e6aa141ba5aaf48fd35461cabc4902ab00d4e6e",
        "BoundingBoxes": [[[-90, -180], [90, 180]]],  # 全球范围
        "FiltersShipMMSI": imo_numbers,  # 指定的 IMO number 列表
        "FilterMessageTypes": ["PositionReport"]  # 只订阅位置报告消息
    })

# 连接到AISStream并订阅数据
async def subscribe_to_aistream(api_key, imo_numbers):
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        # 创建订阅消息
        subscription_message = create_subscription_message(api_key, imo_numbers)
        await websocket.send(subscription_message)

        # 接收并返回消息
        async for message in websocket:
            return json.loads(message)

# 显示船舶信息和地图
def display_ship_info_and_map(df, ship_data):
    col1, col2 = st.columns([1, 4])  # 左侧列表占五分之一，右侧地图占五分之四

    with col1:
        st.write("## 船舶列表")
        st.dataframe(df)

    with col2:
        st.write("## 船舶实时位置图")
        if ship_data:
            # 假设返回的数据中有纬度和经度字段
            lat = ship_data.get('MetaData', {}).get('Latitude', 0)
            lon = ship_data.get('MetaData', {}).get('Longitude', 0)
            st.map({f"{ship_data.get('Message', {}).get('ShipName', 'Unknown Ship')}": (lat, lon)})

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
    ship_data = asyncio.run(subscribe_to_aistream("your_api_key", imo_numbers))

    # 显示船舶信息和地图
    display_ship_info_and_map(df, ship_data)

if __name__ == "__main__":
    main()
