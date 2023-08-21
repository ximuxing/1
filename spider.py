import time
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sql_models import engine, KrNews

# 创建一个 Chrome 浏览器实例
driver = webdriver.Chrome()

# 打开滚动加载页面
scroll_url = "https://36kr.com/information/technology/"
driver.get(scroll_url)

scroll_times = 5
for _ in range(scroll_times):
    # 执行 JavaScript 操作，滚动到页面底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # 等待页面加载

# 使用 XPath 定位并点击按钮
click_count = 0
max_clicks = 20

while click_count < max_clicks:
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait = WebDriverWait(driver, 10)
        view_more_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]/div[3]/div/div/div[1]/div/div/div[3]')))
        view_more_button.click()
    except Exception as e:
        print("Button not found or clickable:", e)
        break

# 获取完整页面内容
scroll_html = driver.page_source

# 关闭浏览器
driver.quit()

# 解析滚动加载页面内容
soup = BeautifulSoup(scroll_html, 'html.parser')
soup_p = soup.find(class_='information-flow-list')
soup_t = soup_p.find_all(class_='title-wrapper ellipsis-2')
print(len(soup_t))

# 解析文章列表，获取每篇文章的链接
# 创建一个 Chrome 浏览器实例
driver = webdriver.Chrome()
for i in range(len(soup_t)):
    l = soup_t[i]
    # print(l)
    path = l.findChild("a")['href']
    url = "https://36kr.com"
    link = url + path

    # 打开文章页面
    driver.get(link)

    # 等待一段时间，让页面完成动态加载
    driver.implicitly_wait(10)  # 等待 10 秒

    # 获取页面内容
    article_html = driver.page_source

    # 关闭浏览器
    # driver.quit()

    # 解析文章内容页
    soup = BeautifulSoup(article_html, 'html.parser')

    # 标题
    title = soup.find('h1', class_='article-title margin-bottom-20 common-width').get_text()
    # print(title)

    # 正文
    content_j = soup.find(class_='common-width content articleDetailContent kr-rich-text-wrapper')
    content_p = content_j.find_all('p')
    content = ''.join([p.get_text() for p in content_p])
    # print(content)

    # 来源
    source = soup.find('a', class_='title-icon-item item-a').get_text()

    # 发布日期
    publish = soup.find('span', class_='title-icon-item item-time').get_text()

    # 输出文章信息
    print("标题:", title)
    print("链接:", link)
    print("正文:", content)
    print("来源:", source)
    print("发布时间:", publish)
    print("-" * 50)

    data_new = dict(
        title=title,
        link=link,
        content=content,
        source=source,
        publish_date=publish,
    )

    print('to_save', data_new['title'], data_new['link'], len(str(data_new['content'])))
    kwargs = dict(
        title=data_new['title'],
        link=data_new['link'],
        content=data_new['content'],
        source=data_new['source'],
        publish_date=data_new['publish_date'],

    )

    # 插入数据
    new_ = KrNews(**kwargs)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(new_)
    session.commit()
