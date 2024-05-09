import streamlit as st
import numpy as np
import pandas as pd
import datetime



########################## 正式开始网页！###################




st.title('需要计算的空表格')
st.markdown('### 需要确认，该空表格严格按照如下格式对表头标题进行命名')
st.image('image/main_error_format.jpg')

main_error_path = st.sidebar.file_uploader("上传重要故障的空表格，文件格式要求为xlsx")
try:
    main_error = pd.read_excel(main_error_path)
except:
    print('未上传文件')
    main_error = pd.read_excel('数据示例/重复故障.xlsx')
st.write(main_error)

st.title('当月所有故障的统计表')
st.markdown('### 需要确认，停机记录表格严格按照如下格式对表头标题进行命名')
st.image('image/all_error_record_format.jpg')

error_all_path = st.sidebar.file_uploader("上传所有故障的表格，文件格式要求为xlsx")
try:
    error_all = pd.read_excel(error_all_path)
except:
    print('未上传文件')
    error_all = pd.read_excel('数据示例/昆头岭明阳4月故障.xlsx')

st.write(error_all)


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
error_all
error_all['last_day_time'] = (error_all['end_day_time']-error_all['start_day_time'])/pd.Timedelta(hours=1)
error_all['last_day_time'] = np.where(error_all['last_day_time'] <0,0,error_all['last_day_time'])
error_all['day_dif'] = (error_all['end_day_time'].dt.date-error_all['start_day_time'].dt.date)/pd.Timedelta(days=1)
error_all['day_dif'] = np.where(error_all['day_dif'] <0,0,error_all['day_dif'] )
error_all['last_day_time'] = error_all['last_day_time']-14*error_all['day_dif']
# error_all['last_day_time'] = np.where((error_all['last_day_time'] >10)&(error_all['last_day_time'] ), error_all['last_day_time'], error_all['last_day_time'])
error_all.describe()
error_all['停机时长(h)'] =  (error_all['恢复时间']-error_all['停机时间'])/pd.Timedelta(hours=1)


main_error['备注'] = ''
main_error['day_time'] = 0
main_error['时长']=0
for i,duplicate_info in main_error.iterrows():
    wtg,error_names,_,last_time = duplicate_info[:4]
    data_df = error_all[(error_all['风机名称']==wtg) &(error_all['故障描述']==error_names)].reset_index(drop=True)
    data_df = data_df.sort_values(by='停机时间').reset_index(drop=True)
    print(data_df[['停机时间','恢复时间']])
    remark = f'1.故障共停机{data_df.shape[0]}次：\n'
    for j,error_info in data_df.iterrows():
        start_time = error_info['停机时间']
        end_time = error_info['恢复时间']
        last_hours = error_info['停机时长(h)']
        remark+=f'第{j+1}次发生在{str(start_time)[:22]}，{str(end_time)[:22]}结束，共持续{round(last_hours,2)}h;\n'
    main_error.loc[i,'备注'] = remark
    main_error.loc[i,'day_time'] = round(sum(data_df['last_day_time']),2)
    main_error.loc[i,'时长'] = round(sum(data_df['停机时长(h)']),2)

main_error['上个月重复性故障']='否'
main_error['TOP6风机故障原因和解决方案']=''
main_error['数据说明']=''
# main_error['故障名称'] = main_error['故障名称'].str.split('_').str[-1]
main_error = main_error[['风机名称', '长时间停机故障', '上个月重复性故障', '时长', 'day_time',  'TOP6风机故障原因和解决方案','备注',
       '数据说明']]

st.title('计算结果')
st.write(main_error)