import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(page_title="船舶信息显示", page_icon="🚢")

# 读取CSV文件
def load_ship_data(filename):
    return pd.read_csv(filename)

# 主函数
def main():
    # 设置页面标题
    st.title('船舶信息显示')

    # 文件选择器
    file_buffer = st.file_uploader("选择一个CSV文件", type=["csv"])
    if file_buffer is not None:
        # 读取CSV文件
        df = pd.read_csv(file_buffer)
        # 显示数据
        st.write(df)

        # 添加一个表格来展示数据
        columns = df.columns
        data = df.values.tolist()
        st.write("以下是船舶信息：")
        st.table(df)

        # 添加搜索框
        search_query = st.text_input('搜索船舶名称')
        if search_query:
            # 过滤数据
            filtered_df = df[df['船舶名称'].str.contains(search_query, case=False, na=False)]
            st.write("搜索结果：")
            st.table(filtered_df)

if __name__ == "__main__":
    main()
