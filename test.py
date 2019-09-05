# import asyncio
# import time
#
# import aiohttp
from tabdoc import PDFWriter, ExcelWriter


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


# async def main():
#     async with aiohttp.ClientSession() as session:
#         html = await fetch(session, 'http://127.0.0.1:8686/api/order/put')
#         print(html)
# ts = time.time()
# tasks = []
# for i in range(2000):
#     tasks.append(asyncio.ensure_future(main()))
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.wait(tasks))
# print(time.time() - ts)

# 线程模式
# import requests
# import threading
#
# def fetch(url):
#     response = requests.get(url)
#     print(response.text)
#
# for i in range(2000):
#     threading.Thread(target=fetch, args=('http://127.0.0.1:8686/api/order/put',)).start()


if __name__ == '__main__':
    data1 = [['日期', '付费', '消费', '签到', '', '', '', '', '', '', '', '', ' 单位：个'],
             ['2019-08-09', '', '编号', '合计', '初中', '', '', '', '', '高中', '', '', ''],
             ['', '', '', '', '计', '一年级', '二年级', '三年级', '四年级', '计', '一年级', '二年级', '三年级'],
             ['甲', '', '乙', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
             ['总计', '', '01', '', '', '', '', '', '', '', '', '', ''],
             ['其中：四年制初中', '', '02', '', '', None, None, None, None, '', '', '', ''],
             ['班\n额\n', '25人及以下', '03', '', '', None, None, None, None, '', None, None, None],
             ['', '26-30人', '04', '', '', None, None, None, None, '', None, None, None],
             ['', '31-35人', '05', '', '', None, None, None, None, '', None, None, None],
             ['', '36-40人', '06', '', '', None, None, None, None, '', None, None, None],
             ['', '41-45人', '07', '', '', None, None, None, None, '', None, None, None],
             ['', '46-50人', '08', '', '', None, None, None, None, '', None, None, None],
             ['', '51-55人', '09', '', '', None, None, None, None, '', None, None, None],
             ['', '56-60人', '10', '', '', None, None, None, None, '', None, None, None],
             ['', '61-65人', '11', '', '', None, None, None, None, '', None, None, None],
             ['', '66人及以上', '12', '', '', None, None, None, None, '', None, None, None]]
    data2 = [
        ["6", None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
         None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
         None, None, None, None],
        ['学校（机构）标识码', None, None, None, None, None, None, None, None, None, '学校（机构）名称（章）', None, None, None,
         None, None, None, None, None, None, None, None, None, None, '学校（机构）英文名称', None, None, None, None, None,
         None, None, None, None, None, None, None]]

    with ExcelWriter("test") as ex:
        ex.add_sheet("test", data1)
        ex.save()
        # for data in [data1, data2]:
        #     pdf.add_table(data, table_name="test")