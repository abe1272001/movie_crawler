import requests
import datetime
import re
import json
from bs4 import BeautifulSoup
import time 
import os

# https://www.ambassador.com.tw/home/TheaterList      #影城頁面
theaterInfos = [ #國賓影城 (全台)
    {
        'name': '國賓大戲院',
        'id': '84b87b82-b936-4a39-b91f-e88328d33b4e',
        'datesTable': []
    },
    {
        'name': '台北微風國賓影城',
        'id': '5c2d4697-7f54-4955-800c-7b3ad782582c',
        'datesTable': []
    },
    {
        'name': '台北長春國賓影城',
        'id': '453b2966-f7c2-44a9-b2eb-687493855d0e',
        'datesTable': []
    },
    {
        'name': '新莊晶冠國賓影城',
        'id': '3301d822-b385-4aa8-a9eb-aa59d58e95c9',
        'datesTable': []
    },
    {
        'name': '林口昕境國賓影城',
        'id': '9383c5fa-b4f3-4ba8-ba7a-c25c7df95fd0',
        'datesTable': []
    },
    {
        'name': '淡水禮萊國賓影城',
        'id': '1e42d235-c3cf-4f75-a382-af60f67a4aad',
        'datesTable': []
    },
    {
        'name': '八德廣豐國賓影城',
        'id': '8fda9934-73d4-4c14-b1c4-386c2b81045c',
        'datesTable': []
    },
    {
        'name': '台中忠孝國賓影城',
        'id': '7008eb95-aa95-4cb1-9530-2551382cf26f',
        'datesTable': []
    },
    {
        'name': '台南國賓影城',
        'id': 'ace1fe19-3d7d-4b7c-8fbe-04897cbed08c',
        'datesTable': []
    },
    {
        'name': '高雄義大國賓影城',
        'id': 'ec07626b-b382-474e-be39-ad45eac5cd1c',
        'datesTable': []
    },
    {
        'name': '高雄草衙道國賓影城',
        'id': 'f760950a-94b6-4e04-9573-831ed7283c5c',
        'datesTable': []
    },
    {
        'name': '屏東環球國賓影城',
        'id': '41aae717-4464-49f4-ac26-fec2d16acbd6',
        'datesTable': []
    },
    {
        'name': '金門昇恆昌國賓影城',
        'id': '65db51ce-3ad5-48d8-8e32-7e872e56aa4a',
        'datesTable': []
    }
]

theater_length = len(theaterInfos)
# print(theater_length)
# today_date = time.strftime("%Y/%m/%d", time.localtime())

"""
This is get next few date function
可控制取得天數  n + 1 天

Param:
    int: how many days
Return:
    array: array of dates. ex: ['2021/08/17', '2021/08/18', '2021/08/19']
"""
def getDates(n):
    today_after_6_days = []
    x = datetime.datetime.now()
    t_year = x.year
    t_month = x.strftime("%m")
    t_day = x.strftime("%d")
    today_date = f"{str(t_year)}/{str(t_month)}/{str(t_day)}"
    today_after_6_days.append(today_date)
    # print(today_after_6_days)
    # n = 5  #選擇後 5 天, 將日期存成 ary
    for x in range(n):
        d = x + 1
        date = datetime.datetime(int(t_year), int(t_month), int(t_day)) + datetime.timedelta(days=d)	# 2015-10-29 00:00:00
        time_format = date.strftime('%Y/%m/%d')	# '2021/08/18'
        today_after_6_days.append(time_format)
    return today_after_6_days

# def write_json(target_path, target_file, data):
#     if not os.path.exists(target_path):
#         try:
#             os.makedirs(target_path)
#         except Exception as e:
#             print(e)
#             raise
#     with open(os.path.join(target_path, target_file), 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False,  indent = 2)

# with open('Ambassador.json', 'w', encoding='utf-8') as f:
#     json.dump(theaterInfos, f, ensure_ascii=False,  indent = 2)

#https://www.ambassador.com.tw/home/Showtime?ID=84b87b82-b936-4a39-b91f-e88328d33b4e&DT=2021/08/13
#取得包含今日之後的 6 天日期 ex: 2021/08/13
# for loop theaters
    #for loop dates

dates = getDates(5) 
today = dates[0]
print(dates)
for theater in theaterInfos:
    print(f"======================================= {theater['name']} ==============================================")
    for d in dates:
        r = requests.get(f"https://www.ambassador.com.tw/home/Showtime?ID={theater['id']}&DT={d}")
        soup = BeautifulSoup(r.text, "html.parser")
        movies = soup.find_all('div', class_='showtime-item')
        # print(movies)
        if(len(movies) == 0): # 若當日無電影則繼續下一天
            print(theater['name'] + ', ' + str(d) + '無電影' )
            continue

        moviesInfo = {
            'date': d,
            'movies' :[]
        }
        print(f"***({d})***")
        for movie in movies:
            movie_title_eng = movie.select_one('h3 a span').getText() # 電影名稱
            movie_title = movie.select_one('h3 a').getText().replace(movie_title_eng, '') # 電影名稱英文
            movie_level = movie.select_one('.info span').getText() # 電影分級
            movie_duration = movie.select_one('.info span').find_next_sibling('span').getText() # 電影時長
            print(f"-----------------------------{movie_title}--------------------------------------------")
            types = movie.find_all('p', class_='tag-seat')
            timeTable = []
            for type in types:
                hall_type = re.findall(r'[(](.*?)[)]', type.getText()) 
                time_doms = type.find_next_siblings('ul')[0].find_all('h6')
                hall_doms = type.find_next_siblings('ul')[0].find_all('span', class_='float-left info') # 影廳節點
                times = []
                
                for index, t in enumerate(time_doms):
                    # try:
                    #     print(hall_doms[index].text.split()[0])
                    # except:
                    #     print(f"https://www.ambassador.com.tw/home/Showtime?ID={theater['id']}&DT={d}")
                    #     break
                    
                    times.append({
                        'time': t.text.strip(),
                        'hall': hall_doms[index].text.split()[0],
                        'capacity': hall_doms[index].text.split()[1]
                    })
                # print(times)
                data = {
                    'type': hall_type[0],
                    'times': times
                }
                timeTable.append(data)
                print(data)
                
            movieData = {
                'title' : movie_title,
                'title_eng': movie_title_eng,
                'level' : movie_level,
                'duration' : movie_duration,
                'timeTable': timeTable
            }
            moviesInfo['movies'].append(movieData)
            
            print('-------------------------------------------------------------------------')
        # 將結果存回 movieTheaterInfos
        theater['datesTable'].append(moviesInfo) 
        # break

print('OVER! Well Done')
# write_json('/json', 'Ambassador.json', theaterInfos)
with open('Ambassador.json', 'w', encoding='utf-8') as f:
    json.dump(theaterInfos, f, ensure_ascii=False,  indent = 2)
print('Write over')
################################################################