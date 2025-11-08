import requests
from bs4 import BeautifulSoup
import re
import json


def get_meta_tag_content(url, meta_name):
    """
    从网页源代码中查找指定name的meta标签的content值

    参数:
    url (str): 要检查的网页URL
    meta_name (str): meta标签的name属性值

    返回:
    str: 找到的content值，如果未找到则返回None
    """
    try:
        # 获取网页源代码
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找指定name的meta标签
        meta_tag = soup.find('meta', attrs={'name': meta_name})

        if meta_tag:
            content = meta_tag.get('content')
            print(f"找到 '{meta_name}': {content}")
            return content
        else:
            print(f"未找到 '{meta_name}' meta标签")
            return None

    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None


def find_event_trace_lines(url):
    """
    从网页中找出以 eventTrace: 开头的行并打印

    参数:
    url (str): 网页URL
    """
    try:
        # 获取网页源代码
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # 按行分割源代码
        lines = response.text.split('\n')

        # 查找以 eventTrace: 开头的行
        event_trace_lines = []
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            if stripped_line.startswith('eventTrace:'):
                event_trace_lines.append((i, stripped_line))
        result = ""
        # 打印结果
        if event_trace_lines:
            #print(f"找到 {len(event_trace_lines)} 行以 eventTrace: 开头的行:")
            for line_num, line_content in event_trace_lines:
                # print(f"第 {line_num} 行: {line_content}")
                result = line_content
        else:
            print("未找到以 eventTrace: 开头的行")

        # 去掉开头的 'eventTrace:'
        if result.startswith('eventTrace:'):
            processed_str = result[len('eventTrace:'):]
        else:
            processed_str = result

        # 去掉最后一个字符（如果字符串长度大于0）
        if len(processed_str) > 0:
            processed_str = processed_str[:-1]
        return processed_str
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except Exception as e:
        print(f"其他错误: {e}")
        return []

def main():
    url = "https://panxiaojietestfeed2.myshoplinestg.com"  # 替换为你要检查的网址
    facebook_content = get_meta_tag_content(url, "facebook-domain-verification")
    print(facebook_content)
    ads_channel = find_event_trace_lines(url)
    body = json.loads(ads_channel)
    print(body['extra'][8]['toolName'])

if __name__ == '__main__':
    main()



