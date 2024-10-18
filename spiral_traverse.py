import aiohttp
import asyncio

async def fetch_data(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Проверяем статус ответа
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Ошибка сервера: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Ошибка соединения: {e}")
        return None

async def process_data(url):
    content = await fetch_data(url)
    if content is None:
        return []

    # Обработка данных
    content = [item for i, item in enumerate(content.splitlines()) if i % 2]

    numb_list = []

    for i in content:
        list_n = ''.join(c if c != ' ' and c != '\n' else '' for c in i).split()
        list_n = [int(item) for i, item in enumerate(list_n) if i % 2]

        numb_list.append(list_n)

    n = len(numb_list)
    left, right = 0, n - 1
    top, bottom = 0, n - 1

    result = []

    while left <= right and top <= bottom:
        for i in range(top, bottom + 1):
            result.append(numb_list[i][left])
        left += 1

        for i in range(left, right + 1):
            result.append(numb_list[bottom][i])
        bottom -= 1

        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(numb_list[i][right])
            right -= 1

        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(numb_list[top][i])
            top += 1

    return result