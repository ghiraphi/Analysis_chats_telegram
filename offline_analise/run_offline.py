from pathlib import Path
import matplotlib
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

# открываем экспортированный пакет html-файлов (история переписки)
folder = Path('files')
if folder.is_dir():
    folder_count = len([1 for file in folder.iterdir()])
    print(f"В папке есть {folder_count} объектов")
try:
    os.rename('files/messages.html', 'files/messages1.html')  # переименование для дальнейшей сортировки
except Exception as e:
    print(f"An error occurred: {e}")

# объединение в один html-файл
def merge_html_files(input_dir, output_file):
    input_dir = os.path.join(os.path.dirname(__file__), input_dir)
    output_file = os.path.join(os.path.dirname(__file__), output_file)
    # Get a list of all the HTML files in the input directory
    digit_regex = re.compile(r'\d+')

    file_list = sorted([f for f in os.listdir(input_dir) if f.endswith('.html') and re.search(r'.*messag.*', f)],
                       key=lambda x: int(digit_regex.search(x).group()) if digit_regex.search(x) else float('inf'))
    print(file_list)
    # Open the output file for writing
    with open(output_file, 'w', encoding='utf-8') as output:
        # Loop through each HTML file
        for filename in file_list:
            # Open the file for reading
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as file:
                # Read the contents of the file
                content = file.read()
                # If this is not the first file, remove any duplicate content
                if filename != file_list[0]:
                    content = content.replace(duplicate_content, '')
                # Write the contents to the output file
                output.write(content)
            # Store the last few lines of this file for comparison with the next file
            duplicate_content = content[-100:]
merge_html_files('files/', 'files/text.html')

# словари для графиков
patterns_get = r'(помочь|может кто|ищем|у кого нибудь|у кого-нибудь|мы семья|можно нам|может ' \
               r'есть|попросить|отправляете|может быть у|прошу|нужда.*|очень ну.*|мы беженцы|.*ищу|помогите|у кого ' \
               r'то|у кого-то|высылаете|.*ехали) '
patterns_give = r'(напишу|напишите|где вы|вы где|отдам|могу отправить|не пересылаю|могу отдать|какой город|в каком ' \
                r'вы.*|вы в каком|самовывоз) '

# создание основого датафрейма
def create_dataframe(patterns_get, patterns_give):
    totalhtml = []  # список для сообщений из html-файла
    f = open(os.path.join(os.path.dirname(__file__), 'files\\text.html'), 'rb')
    for line in f:  # перебор и добавление
        line = re.sub('\n', ' ', line.decode('utf8'))
        totalhtml.append(line)  # список для сообщений из html-файла
    totalhtml = " ".join(totalhtml)
    totalhtml = re.split(' date details" title="', totalhtml.lower())  # разделение строки по дате событий
    print(len(totalhtml))
    df = pd.DataFrame(columns=['date', 'invited', 'message', 'media', 'get', 'give', 'text'])
    pd.set_option('display.max_columns', None)
    for index_i, i in enumerate(totalhtml):
        i = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', i)
        i = i.strip()
        if re.search(' utc\+0', i):
            soup = BeautifulSoup(i[39:], 'html.parser')
            text = soup.get_text()
            text = re.sub('\s+', ' ', text).strip()
            date_message = i[:19]
            matches_get = 1 if len(re.findall(patterns_get, text)) > 0 else 0
            matches_give = 1 if len(re.findall(patterns_give, text)) > 0 else 0
            print(datetime.strptime(date_message, "%d.%m.%Y %H:%M:%S"), len(re.findall('invited', i)),
                  len(re.findall('class="text"', i)), len(re.findall('class="media', i)), matches_get, matches_give,
                  text)
            new_row = pd.Series(
                {'date': datetime.strptime(date_message, "%d.%m.%Y %H:%M:%S"), 'invited': len(re.findall('invited', i)),
                 'message': len(re.findall('class="text"', i)), 'media': len(re.findall('class="media', i)),
                 'get': matches_get, 'give': matches_give, 'text': text})
            df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), 'files/data.csv'), index=False)
    print(df[:10])
create_dataframe(patterns_get, patterns_give)

# создание сгруппированного по дате датафрейма - W - неделя, m - месяц, D - день
def create_group_dataframe(period):  # W - неделя, m - месяц, D - день
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "files/data.csv"))
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
    # add a bar chart using the 'invited' column of the dataframe
    bar_column = 'invited'
    bar_width = 0.5
    ax.bar(df.index, df[bar_column], width=bar_width, alpha=0.5, color='green',
           label='Количество новых участников в чате')
    ax.set_xlim(df.index[0], df.index[-1])
    # set the legend
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc='upper right', fontsize=6)
    # ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    # add a title to the graph
    plt.title('Статистика чата - Отпускай вещи - по неделям')
    # display the graph
    plt.savefig(os.path.join(os.path.dirname(__file__), 'files/my_plot.png'), dpi=300)
bild_graph(df, name_time)
