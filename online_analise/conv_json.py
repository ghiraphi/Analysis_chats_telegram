import json
import os
import pandas as pd
import re
import datetime
import matplotlib
import matplotlib.pyplot as plt
from online_analise import name_chat_get

# load data from JSON file into a Python object
with open(os.path.join(os.path.dirname(__file__), 'files/channel_messages.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
# Your API ID and hash
api_id = 'enter value'
api_hash = 'enter value'
name_group = '@enter value'
# Your phone number, including the country code
phone = '+7enter value'
# словари для графиков
patterns_get = r'(помочь|может кто|ищем|у кого нибудь|у кого-нибудь|мы семья|можно нам|может ' \
               r'есть|попросить|отправляете|может быть у|прошу|нужда.*|очень ну.*|мы беженцы|.*ищу|помогите|у кого ' \
               r'то|у кого-то|высылаете|.*ехали) '
patterns_give = r'(напишу|напишите|где вы|вы где|отдам|могу отправить|не пересылаю|могу отдать|какой город|в каком ' \
                r'вы.*|вы в каком|самовывоз) '
# создание основого датафрейма
def create_dataframe(patterns_get, patterns_give):
    # create a list of dictionaries with date and text for each message
    messages = []
    for message in data:
        if message['_'] == 'Message':
            text=message['message']
            present_text = 1 if re.search('[а-я][а-я]+', text) else 0
            matches_give = 1 if len(re.findall(patterns_give, text)) > 0 else 0
            matches_get = 1 if len(re.findall(patterns_get, text)) > 0 else 0
            rez_media = 0 if str(message['media'])=="None" else 1
            messages.append({'date': message['date'],  'message': present_text, 'media': rez_media, 'give': matches_give, 'get': matches_get, 'text': text})
    # create a Pandas DataFrame from the list of dictionaries
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(messages)
    df.to_csv(os.path.join(os.path.dirname(__file__), 'files/data.csv'), index=False)
    print(df[:10])
create_dataframe(patterns_get, patterns_give)
# создание сгруппированного по дате датафрейма - W - неделя, m - месяц, D - день
def create_group_dataframe(period):  # W - неделя, m - месяц, D - день
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'files/data.csv'))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    if period == 'W':
        name_time = 'неделю'
    elif period == 'm':
        name_time = 'месяц'
    elif period == 'D':
        name_time = 'день'
    df['date'] = pd.to_datetime(df.iloc[:, 0], format='%Y-%m-%d %H:%M:%S')
    # group by day and sum the numeric columns for each day
    df = df.groupby(pd.Grouper(key='date', freq=period)).sum(numeric_only=True)  # W - неделя, m - месяц, D - день
    df.index = df.index.strftime('%Y-%m-%d').str[0:10]
    print(df)
    return df, name_time
df, name_time = create_group_dataframe('W')

print('построение графика - создан')

# построение графика
def bild_graph(df, name_time):
    rolling_window = 4  # вычислить скользящее среднее
    rolling_avg = df['message'].rolling(window=rolling_window).mean()
    columns_list = df.columns.tolist()
    matplotlib.use('Agg')
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.subplots_adjust(top=0.95)
    # plot the first column on the first y-axis
    ax.plot(df.index, df['get'], color='red', label='Количество сообщений, где люди просили о помощи')
    ax.plot(df.index, df['give'], color='blue', label='Количество сообщений, где люди хотели помочь')
    ax.plot(df.index, df['message'], color='violet', label='Количество сообщений всего')
    ax.tick_params(axis='y')
    ax.tick_params(axis='x', rotation=90, labelsize=5)
    ax.grid(True, alpha=0.3)
    ax.plot(df.index, rolling_avg, color='black',
            label=f'Скользящее среднее сообщений всего (расчёт за {rolling_window} дня)')
    # set the labels, ticks and grid
    ax.set_xlabel(f'Периоды за {name_time} - с начала работы по сейчас')
    ax.set_ylabel('Количество')
    ax.set_xticks(df.index)
    # add a bar chart using the 'invited' column of the dataframe - временно скрыто
    # bar_column = 'invited'
    # bar_width = 0.5
    # ax.bar(df.index, df[bar_column], width=bar_width, alpha=0.5, color='green',
    #        label='Количество новых участников в чате')
    ax.set_xlim(df.index[0], df.index[-1])
    # set the legend
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc='upper right', fontsize=6)
    now = datetime.datetime.now()
    upd=now.strftime("%d-%m-%Y %H:%M:%S")
    # add a title to the graph
    plt.title(f'Статистика чата - {name_chat_get.get_name(api_id, api_hash, phone, name_group)} - сгруппировано по {name_time}. Обновлено в {upd}')
    # display the graph
    plt.savefig(os.path.join(os.path.dirname(__file__), 'files/my_plot.png'), dpi=300)
bild_graph(df, name_time)
