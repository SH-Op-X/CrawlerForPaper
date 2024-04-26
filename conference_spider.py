import re
import requests
from lxml import etree

date_pattern1 = '(January|February|March|April|May|June|July|August|September|October|November|December|Decemver),*\s*(3[0-1]|[1-2]\d|0[1-9]|[1-9])\s*-\s*(3[0-1]|[1-2]\d|0[1-9]|[1-9])'
date_pattern2 = '(3[0-1]|[1-2]\d|0[1-9]|[1-9])\s*-\s*(3[0-1]|[1-2]\d|0[1-9]|[1-9])\s*(January|February|March|April|May|June|July|August|September|October|November|December|Decemver)'
date_pattern3 = '(January|February|March|April|May|June|July|August|September|October|November|December|Decemver)\s*(3[0-1]|[1-2]\d|0[1-9]|[1-9])\s*-\s*(January|February|March|April|May|June|July|August|September|October|November|December|Decemver)\s*(3[0-1]|[1-2]\d|0[1-9]|[1-9])'
date_pattern4 = '(3[0-1]|[1-2]\d|0[1-9]|[1-9])\s*(January|February|March|April|May|June|July|August|September|October|November|December|Decemver)\s*-\s*(3[0-1]|[1-2]\d|0[1-9]|[1-9])\s*(January|February|March|April|May|June|July|August|September|October|November|December|Decemver)'
date_pattern5 = 'January|February|March|April|May|June|July|August|September|October|November|December|Decemver'
conference_format = 'Proceeding of the {}{} ({} {}), {},{}, '  # 届数、会议全称、会议简称、年份、地点、日期
usa_state_dict = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Lousiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}
usa_state_dict['D.C.'] = 'DC'   # 特区。。。
can_state_dict = {'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba', 'NL': 'Newfoundland and Labrador', 'NB': 'New Brunswick', 'NS': 'Nova Scotia', 'ON': 'Ontario', 'PE': 'Prince Edward Island', 'QC': 'Quebec', 'SK': 'Saskatchewan'}


def get_date(info):
    info[0] = info[0].replace('Decemver', 'December')  # 错别字。。。
    if len(re.findall(date_pattern1, info[0])) != 0:
        result = re.findall(date_pattern1, info[0])[0]
        month, date1, date2 = result
        date1 = str(int(date1))
        date2 = str(int(date2))
        date = ' ' + month + ' ' + date1 + '-' + date2 + ', ' + year
    elif len(re.findall(date_pattern2, info[0])) != 0:
        result = re.findall(date_pattern2, info[0])[0]
        date1, date2, month = result
        date1 = str(int(date1))
        date2 = str(int(date2))
        date = ' ' + month + ' ' + date1 + '-' + date2 + ', ' + year
    elif len(re.findall(date_pattern3, info[0])) != 0:
        result = re.findall(date_pattern3, info[0])[0]
        month1, date1, month2, date2 = result
        date1 = str(int(date1))
        date2 = str(int(date2))
        date = ' ' + month1 + ' ' + date1 + ' - ' + month2 + ' ' + date2 + ', ' + year
    elif len(re.findall(date_pattern4, info[0])) != 0:
        result = re.findall(date_pattern4, info[0])[0]
        date1, month1, date2, month2 = result
        date1 = str(int(date1))
        date2 = str(int(date2))
        date = ' ' + month1 + ' ' + date1 + ' - ' + month2 + ' ' + date2 + ', ' + year
    elif len(re.findall(date_pattern5, info[0])) != 0:
        month = re.findall(date_pattern5, info[0])[0]
        date = ' ' + month + ', ' + year
    else:
        date = ' ' + year
    return date


def get_jieshu(header):
    jieshu = header.split()[0]
    if not re.findall(r'\d', jieshu):  # 有时候没有提供届数直接赋空值
        jieshu = ''
    else:
        jieshu = int(jieshu[:-2])   # 存在次序有问题的
        if jieshu % 10 == 1 and jieshu % 10 != 11:
            jieshu = str(jieshu) + 'st '
        elif jieshu % 10 == 2 and jieshu % 10 != 12:
            jieshu = str(jieshu) + 'nd '
        elif jieshu % 10 == 3 and jieshu % 10 != 13:
            jieshu = str(jieshu) + 'rd '
        else:
            jieshu = str(jieshu) + 'th '
    return jieshu


def get_place(place):
    place = place.split(', ')
    if place[-1] == 'US' or place[-1] == 'USA':
        place[-1] = 'USA'
        if len(place) == 3:
            for k in usa_state_dict.keys():
                if k == place[-2]:
                    place[-2] = usa_state_dict[k]
    elif place[-1] == 'Canada':
        if len(place) == 3:
            for k in can_state_dict.keys():
                if k == place[-2]:
                    place[-2] = can_state_dict[k]
    elif len(place) == 2:
        for k, v in usa_state_dict.items():
            if k == place[-1] or v == place[-1]:
                place[-1] = usa_state_dict[k]
                place.append('USA')
                break
    place = ', '.join(place)
    return place


if __name__ == '__main__':
    print('Choose how to get conference details: \n(1) By Url (Suggested)\n(2) By name')
    choice = input('Choose number: ')
    assert choice != '1' or choice != '2'
    choice = int(choice)
    if choice == 1:
        url = input('Input URL: ')
        assert 'https://dblp.uni-trier.de/db/' in url
    else:
        name = input('Input conference name: ')
        html = requests.get('https://dblp.uni-trier.de/search', params={'q': name}).content
        html = etree.HTML(html)
        url = html.xpath('//*[@id="completesearch-venues"]/div/ul/li[1]/a/@href')[0]

    # url = 'https://dblp.uni-trier.de/db/conf/uss/index.html'
    html = requests.get(url).content
    html = etree.HTML(html)

    full_name = html.xpath('//*[@id="headline"]/h1/text()')[0]
    if '(' in full_name:
        abbr_name = re.findall(r'(?<=\()(.+?)(?=\))', full_name)[0]
        full_name = full_name.split('(')[0].strip()
    else:
        abbr_name = ' '.join(html.xpath('//*[@id="conf/uss/2023"]/cite/span[3]/text()')[0].split(',')[1].strip().split()[:-1])

    # 遍历每一届会议
    all_header = html.xpath('/html/body/div[2]/header[@class="h2"]')

    for i in range(len(all_header)):
        header = all_header[i].xpath('./h2//text()')
        header = ''.join(header)
        header.replace(' [hybrid]', '')
        if '[virtual]' in header:
            year = header.split()[-2]
            place = 'Virtual'
        else:
            year, place = header.split(': ')
        year = year[-4:]
        place = get_place(place)
        jieshu = get_jieshu(header)

        info = all_header[i].xpath('./following-sibling::ul[1]/li[1]/cite/span[@class="title"]/text()')
        # 匹配日期最麻烦，格式种类有点多
        if len(info) == 0:
            continue
        date = get_date(info)
        print(conference_format.format(jieshu, full_name, abbr_name, year, place, date))
