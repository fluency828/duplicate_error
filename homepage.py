import streamlit as st
import numpy as np
import pandas as pd
import datetime
import io


########################## 正式开始网页！###################

st.title('长停故障记录分析')

st.markdown('# 需要计算的空表格')
st.markdown('### 需要确认，该空表格严格按照如下格式对表头标题进行命名')
st.image('image/main_error_format.jpg')

main_error_path = st.sidebar.file_uploader("上传重要故障的空表格，文件格式要求为xlsx")
main_error = pd.read_excel(main_error_path if main_error_path else '数据示例/重复故障.xlsx')
st.write(main_error)

st.markdown('# 当月所有故障的统计表')
st.markdown('### 需要确认，停机记录表格严格按照如下格式对表头标题进行命名')
st.image('image/all_error_record_format.jpg')

error_all_path = st.sidebar.file_uploader("上传所有故障的表格，文件格式要求为xlsx")
error_all = pd.read_excel(error_all_path if error_all_path else '数据示例/昆头岭明阳4月故障.xlsx')

st.write(error_all)

month = st.sidebar.selectbox(label = '请选择月份',options=list(np.arange(1,13)))

manual_path = st.sidebar.file_uploader("故障处理手册，文件格式要求为xlsx")
manual_df =  pd.read_excel(error_all_path if manual_path else '数据示例/error_manual.xlsx')

st.markdown('# 故障复位手册')
st.write(manual_df)
manual = manual_df.set_index('长时间停机故障').T.to_dict()
# st.write(manual)

error_all = error_all[error_all['故障描述']!='系统正常'].reset_index(drop=True)
error_all['故障描述'] = np.array(list(error_all['故障描述'].str.split('（')))[:,0]
error_all['停机时间'] = pd.to_datetime(error_all['停机时间'])
# error_all['停机时间'] = error_all['停机时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
error_all['恢复时间'] = pd.to_datetime(error_all['恢复时间'])
# error_all['恢复时间']  = error_all['恢复时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
error_all['start当天8点'] = pd.to_datetime(error_all['停机时间'].dt.strftime('%Y-%m-%d')+' 08:00')
error_all['start当天18点'] = pd.to_datetime(error_all['停机时间'].dt.strftime('%Y-%m-%d')+' 18:00')

# error_all['start前一天18点'] = pd.to_datetime((error_all['停机时间']-datetime.timedelta(days=1)).dt.strftime('%Y-%m-%d')+' 18:00')
error_all['start后一天8点'] = pd.to_datetime((error_all['停机时间']+datetime.timedelta(days=1)).dt.strftime('%Y-%m-%d')+' 08:00')
error_all['end当天8点'] = pd.to_datetime(error_all['恢复时间'].dt.strftime('%Y-%m-%d')+' 08:00')
error_all['end当天18点'] = pd.to_datetime(error_all['恢复时间'].dt.strftime('%Y-%m-%d')+' 18:00')

error_all['end前一天18点'] = pd.to_datetime((error_all['恢复时间']-datetime.timedelta(days=1)).dt.strftime('%Y-%m-%d')+' 18:00')
# error_all['end后一天8点'] = pd.to_datetime((error_all['恢复时间']+datetime.timedelta(days=1)).dt.strftime('%Y-%m-%d')+' 08:00')
error_all['start_day_time'] = np.where(error_all['停机时间']<error_all['start当天8点']\
                                       ,error_all['start当天8点']\
                                        ,error_all['停机时间'])
error_all['start_day_time'] = np.where(error_all['start_day_time']>error_all['start当天18点']\
                                       ,error_all['start后一天8点']\
                                        ,error_all['start_day_time'])

error_all['end_day_time'] = np.where(error_all['恢复时间']>error_all['end当天18点']\
                                       ,error_all['end当天18点']\
                                        ,error_all['恢复时间'])
error_all['end_day_time'] = np.where(error_all['end_day_time']<error_all['end当天8点']\
                                       ,error_all['end前一天18点']\
                                        ,error_all['end_day_time'])
# error_all
error_all['last_day_time'] = (error_all['end_day_time']-error_all['start_day_time'])/pd.Timedelta(hours=1)
error_all['last_day_time'] = np.where(error_all['last_day_time'] <0,0,error_all['last_day_time'])
error_all['day_dif'] = (error_all['end_day_time'].dt.date-error_all['start_day_time'].dt.date)/pd.Timedelta(days=1)
error_all['day_dif'] = np.where(error_all['day_dif'] <0,0,error_all['day_dif'] )
error_all['last_day_time'] = error_all['last_day_time']-14*error_all['day_dif']
# error_all['last_day_time'] = np.where((error_all['last_day_time'] >10)&(error_all['last_day_time'] ), error_all['last_day_time'], error_all['last_day_time'])
# error_all.describe()
error_all['停机时长(h)'] =  (error_all['恢复时间']-error_all['停机时间'])/pd.Timedelta(hours=1)


main_error['备注'] = ''
main_error['day_time'] = 0
main_error['时长']=0
main_error['数据说明'] = ''
for i,duplicate_info in main_error.iterrows():
    # wtg,error_names,_,last_time = duplicate_info[:4]
    wtg = duplicate_info['风机名称']
    error_names = duplicate_info['长时间停机故障']
    last_time = duplicate_info['总停机时长（h）']
    data_df = error_all[(error_all['风机名称']==wtg) &(error_all['故障描述']==error_names)].reset_index(drop=True)
    data_df = data_df.sort_values(by='停机时间').reset_index(drop=True)
    print(data_df[['停机时间','恢复时间']])
    remark = f'1.故障共停机{data_df.shape[0]}次：\n'
    for j,error_info in data_df.iterrows():
        start_time = error_info['停机时间']
        end_time = error_info['恢复时间']
        last_hours = error_info['停机时长(h)']
        remark+=f'第{j+1}次发生在{str(start_time)[:22]}，{str(end_time)[:22]}结束，共持续{round(last_hours,2)}h;\n'
    fuwei = manual[error_names]["description"] if error_names in manual else None
    description = f'1.该故障在{month}月报出过{data_df.shape[0]}次;\n2.根据工作票记录\n3.{fuwei}'
    main_error.loc[i,'备注'] = remark
    main_error.loc[i,'day_time'] = round(sum(data_df['last_day_time']),2)
    main_error.loc[i,'时长'] = round(sum(data_df['停机时长(h)']),2)
    main_error.loc[i,'数据说明'] = description

main_error['上个月重复性故障']='否'
main_error['TOP6风机故障原因和解决方案']=''
# main_error['数据说明']=''
# main_error['故障名称'] = main_error['故障名称'].str.split('_').str[-1]
main_error = main_error[['风机名称', '长时间停机故障', '上个月重复性故障', '时长', 'day_time',  'TOP6风机故障原因和解决方案','备注',
       '数据说明']]

st.markdown('# 计算结果')
st.markdown('#### 请确保在左侧侧边栏中选择了正确的月份')
st.write(main_error)



def to_excel(df):
    output = io.BytesIO()
    df.to_excel(output, index=False)
    processed_data = output.getvalue()
    output.close()
    return processed_data
df_csv = to_excel(main_error)
st.download_button(label='📥 点击下载计算结果',
                                data=df_csv,
                                file_name= '长停故障.xlsx')