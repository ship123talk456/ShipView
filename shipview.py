import streamlit as st
import pandas as pd
import requests
import json

# 设置页面配置
st.set_page_config(page_title="船舶信息显示与实时位置", layout="wide")

# 读取CSV文件
def load_ship_data(filename):
    return pd.read_csv(filename)

# 获取船舶实时位置
def get_ship_realtime_position(ship_name):
    # 假设的API接口，需要替换为实际的API接口
    api_url = "https://api.example.com/ship_positions"
    params = {
        'ship_name': ship_name
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 主函数
def main():
    # 设置页面标题
    st.title('船舶信息显示与实时位置')

    # 指定CSV文件路径
    filename = 'shiplist.csv'
    
    # 读取CSV文件
    df = load_ship_data(filename)
    
    # 创建一个列表框来显示船舶信息
    col1, col2 = st.columns([1, 4])  # 左侧列表占五分之一，右侧地图占五分之四
    with col1:
        st.write("船舶列表：")
        for index, row in df.iterrows():
            ship_name = row['船舶名称']
            st.write(ship_name)
            # 获取并显示船舶的实时位置
            position = get_ship_realtime_position(ship_name)
            if position:
                st.write(f"位置：{position['latitude']}, {position['longitude']}")
            else:
                st.write("实时位置不可用")

    with col2:
        st.map(df)

if __name__ == "__main__":
    main()
