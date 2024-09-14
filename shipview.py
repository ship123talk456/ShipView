import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="船舶信息显示与实时位置", layout="wide")

# 读取CSV文件
def load_ship_data(filename):
    return pd.read_csv(filename)

# 主函数
def main():
    # 设置页面标题
    st.title('船舶信息显示与实时位置')

    # 指定CSV文件路径
    filename = 'shiplist.csv'
    
    # 读取CSV文件
    df = load_ship_data(filename)
    
    # 创建两个列，左侧列表占五分之一，右侧地图占五分之四
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.write("## 船舶列表")
        # 显示船舶信息的表格
        st.dataframe(df)

    with col2:
        st.write("## 船舶实时位置图")
        # 由于没有提供实时位置的API，这里暂时留空
        # 一旦提供了API，可以使用例如st.map()或者folium地图来显示船舶位置

if __name__ == "__main__":
    main()
