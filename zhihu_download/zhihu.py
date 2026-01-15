import requests
import os
import time
import re
import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin

# ====================== 【仅需修改这3个地方 ↓↓↓】 ======================
USER_ID = "mr-dang-77"       # 替换成目标知乎博主的user_id
AUTHOR_NAME = "MR Dang"      # 替换成博主昵称，用于创建本地保存文件夹
MIN_ANSWER_DATE = "2025-01-01"  # 仅下载此日期及之后的回答，格式：YYYY-MM-DD
# =======================================================================

# 初始化请求头 - 防反爬核心配置
# ua = UserAgent()  # 暂时不使用随机UA，使用固定UA更稳定
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.zhihu.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    # 【关键】：请在浏览器登录知乎，按F12打开开发者工具 -> Network -> 刷新页面 -> 找到第一个请求 -> 复制Request Headers中的Cookie值填入下方
    "Cookie": "SESSIONID=iCoussn7NugIg29g6jEwWtCL8PgJCqqaF5TF3KQKqGm; JOID=W1wRB0zqc_wynXtfEYrzYtB8mUkHoQqaSdExLiPWE5d07zwoR_vnl1aedl8S0pzEHVam-GO332WGXwvV71VNvg0=; osd=WlgXC07rd_o-n3pbF4bxY9R6lUsGpQyWS9A1KC_UEpNy4z4pQ_3rlVeacFMQ05jCEVSn_GW73WSCWQfX7lFLsg8=; _xsrf=jEXlaCMbkp6OlTH1i5LD9kYkWNYyDsF0; _zap=db664e23-8200-4346-ac03-7784159d83f5; d_c0=FweUWuHvFRuPTvK5JqO6H92GpsyyU2BtZAw=|1758108637; HMACCOUNT=B4F69BF209DB9E9E; DATE=1758206982575; crystal=U2FsdGVkX1+l2Me1mx5fVEe94CGPCnELMfntmaPXv5XQjsolGZwSpaBzBYMDdvvOdXW0vd2NYlY8pMyUoD0tCNPecyzqRdpYgwm/o1KQBfFCl64+aZgZUG+RVJPcftuU7Yx73O6V/Ga6O/iDMTjrBYQ2JQS+RS33GIDHTR/hwZtS8V5rfRB600u4+3pfP0NEih/yC2ozl3S8GLnPmfSX4soHu0VvJUWGmuParNzXXm7dJ0z8cEo3ahL71R10YrmU; vmce9xdq=U2FsdGVkX19GjFQBruXHIxbFk0ZkASlGs3NMM9AznZ9EoD1X1zrGuY1VMpcaYwSGN82p0js35oy782x67igFPF+BXPvC2odwalA9EThp1s+iugIx4Vz+8EUbHwbF8YAg+S29h+hjDGeI3SfirOCn+5FLzyP6X6J8hnEx0Ce4WZ4=; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1765892192; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1765971228; __snaker__id=3X2uXvk4oUWGxcaj; gdxidpyhxdE=yZVUb8At%2ByEL7qocoLk6OyLPOdLH9cvipLuMtTOmDZchgZtJs%2ByPBvYD%5C8rewEH1E9vDxLcZTH%2FEfaVnPyz9omk6gxUr0sYMh%2BrjxZ2q6sLLrxQ6Bl9yi%5CC9lnmdi9A9yxtDBmokPSSeHbuLpURYanlB%5Ct0Awnsc8bw7wnqQIhh0DMV4%3A1767185225832; captcha_session_v2=2|1:0|10:1767184339|18:captcha_session_v2|88:SnhsRS9WU2lZdnBycWJubzJxNzM3aWNpbWtDUFBxU2U2aVZvLzRFRVhuc1dZRE1YYU5BNWRDV2ZQMEhxZVBsbQ==|6ce458b266ba3d33889ddf3497d7c43bcad3317434e749b20179f24a85dfca6f; cmci9xde=U2FsdGVkX1/KaUewWQp9LX2TECa09SggRMvNquf86WlZBcMohfk1fIH1xZ9mdT9jmJAggwphYCyGAqoI2u7gFg==; pmck9xge=U2FsdGVkX1+0xi4no6I9vhKtqqPUJFHmRFtMcU7Hrps=; assva6=U2FsdGVkX19MkhvUZRVeEUTHCLt6Lg2nM45kvjr8WxY=; assva5=U2FsdGVkX19nE+eYR8AaBz5Ks9ITJYBTgctKsKMqbdc5tJe0gqFhzyL0fi3dA1X4pLihw3O7zSFM7hdleDKquA==; captcha_ticket_v2=2|1:0|10:1767184355|17:captcha_ticket_v2|728:eyJ2YWxpZGF0ZSI6IkNOMzFfT0dBb0xMVEwzOWFWVWhrbGExb2NESXRYcFNJS2hXTF9Da0N2MDRNLlJmbmlGM2REQnRIaExNNHJXMFFyKkNwTE5XbFBtalJUSENVU0t5eGZpbmFXKkZnNFAuVUNtelJHV012SzEqT1VPelI1OFBvR0lQR2FTNm1mSDBxZEU1TG5PSUdHVzZPVUFLNlJxOVByYWg0TVBGZFc4cGhzZUhndm9XdExpTzVnM1RRM0Zod0Z0OWNhWWhqWmJtbDE0Qypja0gua2NwNip4Wm1XVTBCazlMMnR3M09ONV9ZdDB0dk5UVUlnb3dMWVBtU3VkTW9GU3pLbkNTb3g5eWNKcTNSSWUqbjFnVXguYl9FZVRNd25hUlhKdlkwTlpYMW5YUXJicVFDZjNndVRZaEFSUk4xKkhUR3R6Y3ltKmNmdnVsbmFXMTFXeVdJcXB5ZVR5YW1mYl9Wc1pEb0Jua2VDOU14czZqaGFib3MzWXVFWGFmeHVuZDZKUWtNZHQxeE1YZFBsNlpxRnZxNipVNGwzTEhLU0g0RHdxQnduckVhanhUM0RjTWVERS5KOFNzUmpOb3VZMEZ0bnhpemc1bG1jdHk0NEdDZDE1TU9BMnRJNXFicmRCRFZfbGQ1U3BiTXBseDJneVVOcDU2SjBUNXFVODhBdEdWaldka0F4cmRHenNHRzZRY3Ztamc3N192X2lfMSJ9|d33a0cb643a7416baebd976ac730f96e642bed93d76171a5ad3a08b61a80ed1f; z_c0=2|1:0|10:1767200920|4:z_c0|92:Mi4xWURvUUFBQUFBQUFYQjVSYTRlOFZHeVlBQUFCZ0FsVk44V1ZDYWdCRDZHaHVkTnN1b0RPRFB1WGdxcTZYMkgzVG1B|7548f61fc02feaacd33e13d0f70a255dfb4ac7c1c56c02783dcf0bab49c74af2; q_c1=5e01cb87547449eebbc4590a090268cc|1767282754000|1767282754000; SESSIONID=FyfxBGq22mkFqIzVuzODQle23oSRcYP5z5dw0QeCF8A; JOID=V1gQA02oSVELDfzWWMDMwunsFsVD6zUydUy-om-ZIT9IerapCxnIMWcL_NZbIll0rTYAQ4Regw7EwCB8tZsX6Q8=; osd=U1sSAU-sSlMJD_jVWsLOxuruFMdH6Dcwd0i9oG2bJTxKeLStCBvKM2MI_tRZJlp2rzQEQIZcgQrHwiJ-sZgV6w0=; __zse_ck=005_tt0mOpAxNR8PncOPe31NfdVNaAuRipijioE0w4D5MfKUBpyz5LPJuQlHFD=7CcbVY=e3O2bkwtKosB1fEheHdN3L4JuoWmwJji/b6/YV6ZJsGtE588dhMRD1FBWGAvCu-1y43Nwo1f2Sd8gQ/6ujcAavUCiuwnJbaeDDjwuq4KvarW3OriAc54Bg7sCAaKCKH8CfjA+OndIIsQLdEInd8afQt+nD02UiNNtiJhzpLGgig9JM8fsuice5zz1SGZ/U6; BEC=f7bc18b707cd87fca0d61511d015686f"}

# 创建主保存文件夹
main_save_dir = f"知乎_{AUTHOR_NAME}_回答合集(含本地图片)"
if not os.path.exists(main_save_dir):
    os.makedirs(main_save_dir)

def clean_file_name(title):
    """清洗标题/文件名，去除系统非法字符，防止保存失败"""
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '，', '。']
    for char in illegal_chars:
        title = title.replace(char, "")
    # 去除首尾空格和换行
    return title.strip()[:50]  # 标题过长截取前50字符，避免文件名过长

def download_img_and_replace_md_link(md_content, article_title, article_url, date_str):
    """
    核心功能函数：下载文章内所有图片到本地 + 替换markdown中的网络图片链接为本地路径
    :param md_content: 原始markdown文本内容
    :param article_title: 文章标题，用于创建专属图片文件夹
    :param article_url: 文章链接，用于Referer防盗链
    :return: 替换本地路径后的markdown内容
    """
    img_sub_dir = f"{date_str}_{clean_file_name(article_title)}_图片"
    img_save_path = os.path.join(main_save_dir, img_sub_dir)
    if not os.path.exists(img_save_path):
        os.makedirs(img_save_path)

    # 正则匹配markdown中的所有图片链接：![图片描述](图片URL)
    img_pattern = re.compile(r"!\[(.*?)\]\((https?://.*?)\)")
    all_img = img_pattern.findall(md_content)

    if not all_img:
        return md_content  # 无图片则直接返回原内容

    # 遍历所有图片，下载+替换链接
    for img_desc, img_url in all_img:
        try:
            # 生成图片文件名，防止重复/非法字符
            img_suffix = img_url.split(".")[-1].lower()
            if img_suffix not in ["jpg", "png", "gif", "webp", "jpeg"]:
                img_suffix = "jpg"
            img_name = f"{clean_file_name(img_desc)}_{int(time.time())}.{img_suffix}"
            img_file_path = os.path.join(img_save_path, img_name)

            # 图片已存在则跳过下载，避免重复请求
            if not os.path.exists(img_file_path):
                # 关键：设置Referer为文章链接，解决403 Forbidden
                img_headers = headers.copy()
                img_headers["Referer"] = article_url
                
                img_response = requests.get(img_url, headers=img_headers, timeout=10)
                img_response.raise_for_status()
                # 二进制写入图片文件
                with open(img_file_path, "wb") as f:
                    f.write(img_response.content)
                time.sleep(0.2)  # 图片下载间隔，防反爬

            # 关键：将markdown中的【网络URL】替换为【本地相对路径】，保证打开md能直接加载图片
            md_content = md_content.replace(img_url, img_sub_dir + "/" + img_name)
        except Exception as e:
            print(f"⚠️ 图片下载失败: {img_url} | 原因: {str(e)[:20]}")
            continue
    return md_content

def get_zhihu_author_all_answers(user_id, min_answer_date_str=None):
    """获取知乎博主的全部回答列表（标题+链接+日期），分页加载所有内容"""
    answer_list = []

    min_ts = None
    if min_answer_date_str:
        try:
            min_dt = datetime.datetime.strptime(min_answer_date_str, "%Y-%m-%d")
            min_ts = int(min_dt.timestamp())
        except Exception:
            min_ts = None

    offset = 0
    limit = 20
    answer_api = f"https://www.zhihu.com/api/v4/members/{user_id}/answers"
    print("\n🔍 正在获取博主的所有【回答】列表...")
    while True:
        try:
            params = {
                "include": "data[*].id,question.title,url,created_time,updated_time",
                "offset": offset,
                "limit": limit,
                "sort_by": "created"
            }
            res = requests.get(answer_api, headers=headers, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()

            if not data.get("data"):
                break

            for item in data["data"]:
                question_title = item.get("question", {}).get("title", "无标题回答")
                title = clean_file_name(question_title)
                url = f"https://www.zhihu.com/question/{item['question']['id']}/answer/{item['id']}"
                created_ts = item.get("created_time")
                if min_ts and created_ts and created_ts < min_ts:
                    continue
                date_str = datetime.datetime.fromtimestamp(created_ts).strftime('%Y-%m-%d') if created_ts else "0000-00-00"
                answer_list.append((title, url, date_str))

            print(f"   >> 已加载 {len(data['data'])} 个回答，继续加载下一页...")
            if data["paging"]["is_end"]:
                break

            offset += limit
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠️ 获取回答列表异常: {str(e)}")
            break
            
    return answer_list

def parse_zhihu_article_to_markdown(article_url):
    """解析单篇知乎文章，提取正文并转为标准Markdown格式"""
    try:
        res = requests.get(article_url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        # 知乎文章正文的固定核心容器，所有内容都在这里
        content_box = soup.find("div", class_="RichContent-inner")
        if not content_box:
            return "【⚠️ 该文章已被删除/权限不足，无法查看内容】"
        
        # HTML转Markdown，完美保留知乎排版格式
        markdown_content = md(str(content_box), heading_style="ATX")
        # 清理多余空行，让markdown更整洁
        markdown_content = "\n".join([line for line in markdown_content.split("\n") if line.strip()])
        return markdown_content
    except Exception as e:
        return f"【⚠️ 文章解析失败】错误原因: {str(e)[:30]}"

def save_markdown_file(article_title, markdown_content):
    """将处理好的markdown内容（含本地图片链接）保存为.md文件"""
    md_file_name = f"{article_title}.md"
    md_file_path = os.path.join(main_save_dir, md_file_name)
    # 去重：文件已存在则跳过，避免重复下载
    if os.path.exists(md_file_path):
        print(f"✅ 已存在，跳过：{md_file_name}")
        return
    # 写入文件，指定utf-8编码防止中文乱码
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(f"# {article_title}\n\n")  # 标题作为一级标题
        f.write(markdown_content)
    print(f"✅ 保存成功：{md_file_name}")

if __name__ == "__main__":
    print("=" * 50)
    print(f"开始爬取【{AUTHOR_NAME}】的知乎全部回答 + 图片本地化下载")
    print("=" * 50)
    
    all_answers = get_zhihu_author_all_answers(USER_ID, MIN_ANSWER_DATE)
    
    if not all_answers:
        print("❌ 未获取到任何回答，请检查【user_id】是否正确！")
        print("💡 提示：如果遇到401/403错误，请务必更新代码中的【Cookie】！")
    else:
        total = len(all_answers)
        print(f"\n🎉 共获取到 {total} 条回答，开始解析+下载图片+保存...\n")
        
        for index, (title, url, date_str) in enumerate(all_answers, start=1):
            print(f"\n[{index}/{total}] [{date_str}] 正在处理：{title}")
            
            raw_md = parse_zhihu_article_to_markdown(url)
            
            final_md = download_img_and_replace_md_link(raw_md, title, url, date_str)
            
            file_name_prefix = f"{date_str}_{title}"
            save_markdown_file(file_name_prefix, final_md)
            
            time.sleep(1)  # 间隔，防反爬
    
    print("\n" + "=" * 50)
    print("✅ 全部处理完成！所有文章和图片已保存至：", main_save_dir)
    print("=" * 50)
