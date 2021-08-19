import requests
import datetime
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import parse_qs
import urllib.parse as urlparse
import time 
import os

# https://www.ambassador.com.tw/home/TheaterList      #影城頁面
# theaterInfos = [ # init data structure
#     {
#         'crawler_theater_name': '國賓大戲院', 
#         'crawler_theater_id': '84b87b82-b936-4a39-b91f-e88328d33b4e', 
#         'address': '台北市成都路88號', 
#         'tel': '02-2361-1223', 
#         'datesTable': []
#     }
# ]

# 匯出到指定資料夾的 function, 還需測試 
# def write_json(target_path, target_file, data): 
#     if not os.path.exists(target_path):
#         try:
#             os.makedirs(target_path)
#         except Exception as e:
#             print(e)
#             raise
#     with open(os.path.join(target_path, target_file), 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False,  indent = 2)


"""
取得影城資訊及 ID
Return:
    array: array of theater infos
"""
def getTheaterInfos():
    theaterInfos = []
    r_theater = requests.get('https://www.ambassador.com.tw/home/TheaterList')
    soup_theater = BeautifulSoup(r_theater.text, "html.parser")
    theater_cells = soup_theater.select('div.theater > div.cell')
    for cell in theater_cells:
        theater_info_block = cell.find('div', class_="theater-info")
        a_tag_href = cell.find("a").get('href')
        parsed_url = urlparse.urlparse(a_tag_href)
        theater_ID = parse_qs(parsed_url.query)['ID'][0]
        theater_name = theater_info_block.find('h6').text
        theater_address = theater_info_block.find('p').text
        theater_phone = theater_info_block.find('p').find_next_sibling('p').text
        theaterInfos.append({
            'crawler_theater_name': theater_name,
            'crawler_theater_id': theater_ID,
            'address': theater_address,
            'tel': theater_phone,
            'datesTable': []
        })
    return theaterInfos

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
    today_date = time.strftime("%Y/%m/%d", time.localtime())
    today_after_6_days.append(today_date)
    # n = 5  #選擇後 5 天, 將日期存成 ary
    for x in range(n):
        d = x + 1
        date = datetime.datetime(int(t_year), int(t_month), int(t_day)) + datetime.timedelta(days=d)	# 2015-10-29 00:00:00
        time_format = date.strftime('%Y/%m/%d')	# '2021/08/18'
        today_after_6_days.append(time_format)
    return today_after_6_days


#https://www.ambassador.com.tw/home/Showtime?ID=84b87b82-b936-4a39-b91f-e88328d33b4e&DT=2021/08/13
#取得包含今日之後的 6 天日期 ex: 2021/08/13
# for loop theaters
    #for loop dates
theaterInfos = getTheaterInfos()
dates = getDates(5) # 取得包含今日的六天日期
today = dates[0]
print(dates)
print(theaterInfos)
for theater in theaterInfos:
    print(f"======================================= {theater['crawler_theater_name']} ==============================================")
    for d in dates:
        r = requests.get(f"https://www.ambassador.com.tw/home/Showtime?ID={theater['crawler_theater_id']}&DT={d}")
        soup = BeautifulSoup(r.text, "html.parser")
        movies = soup.find_all('div', class_='showtime-item')
        # print(movies)
        if(len(movies) == 0): # 若當日無電影則繼續下一天
            print(theater['crawler_theater_name'] + ', ' + str(d) + '無電影' )
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

print('Crawler finished! Well Done')
# write_json('/json', 'Ambassador.json', theaterInfos) #未測試
with open('Ambassador.json', 'w', encoding='utf-8') as f:
    json.dump(theaterInfos, f, ensure_ascii=False,  indent = 2)
print('JSON dump finished')
################################################################