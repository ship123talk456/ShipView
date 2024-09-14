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
    
    # 创建一个列表框来显示船舶信息
    col1, col2 = st.columns([1, 4])  # 左侧列表占五分之一，右侧地图占五分之四
    with col1:
        st.write("船舶列表：")
        # 显示船舶信息的列表框
        for index, row in df.iterrows():
            st.write(f"IMO号: {row['IMO number']}, 船舶名称: {row['Name of ship']}, 总吨位: {row['Gross tonnage']}, 建造年份: {row['Year of build']}, 船旗: {row['Flag']}")

    with col2:
        # 这里将添加地图控件的代码
        st.write("船舶实时位置图：")
        # 由于没有提供实时位置的API，这里暂时留空
        # 一旦提供了API，可以使用例如st.map()或者folium地图来显示船舶位置

if __name__ == "__main__":
    main()
