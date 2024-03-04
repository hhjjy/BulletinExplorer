from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
# from langchain.prompts.chat import ChatPromptTemplate, SystemMessage, HumanMessage
# from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.chat_models import ChatOpenAI

import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
# 确保环境变量中设置了 OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量。")
from langchain.chat_models import ChatOpenAI


def llm_classify(title,content):
    # 初始化模型
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-4-0613")
    # chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
    templates_classify = """
### 指令內容：
你是一個"對公告欄標題、內文分類成對應的標籤的工作者"。請以"繁體中文"輸出並按照下面的步驟執行：

1. 請依照要求將文章分成不同段落，一步一步將每個段落依序列出該段的主旨，再從中提取摘要，並根據"標籤定義"，列出該段符合的所有標籤。具體操作如下：
    - **段落分割：** 閱讀文章內容，將其分割成不同的段落。每個段落應該集中於一個特定的主題或活動。
    - **主旨分析：** 對每個獨立的段落進行主旨分析，明確該段落主要討論或描述的內容是什麼。
    - **摘要提取：** 從每個段落中提取關鍵信息作為摘要，信息包括活動的時間、地點、參與條件、以及可能的獎勵等。
    - **標籤匹配：** 根據事先定義的標籤類別，將每個段落的主旨和摘要與相應的標籤進行匹配，確定該段落屬於哪一個或哪幾個標籤分類。

2. 從出現過的標籤，把合理的標籤內容合併到一起，並把最終結果以JSON格式輸出。如果最終結果沒有任何標籤，請輸出標籤"其他"，否則不輸出標籤"其他"。具體步驟如下：
    - **標籤合併：** 根據上一步驟中每個段落所匹配的標籤，將合理的標籤進行合併，形成一個包含所有相關標籤的集合。
    - **JSON格式輸出：** 將合併後的標籤集合轉換為JSON格式，這些標籤將包含在tags鍵值下。如果經過分析後，某個公告內容不適合任何預定義的標籤，則為該公告分配一個"其他"標籤。

### 標籤與標籤定義：
"餐點": "提供免費食物或餐點讓大家吃",
"自我認識": "提供心理健康相關服務，如個別諮詢、小團體訓練、心理測驗、生命教育和性平教育，但不包含透過分享引起他人的反饋和討論",
"考試": "用於評估學生學習成果的正式測試，包括書面、口頭或實踐測試，通過後可獲得證照或證書",
"學習技能": "提升個人能力、知識或專業技能",
"體育活動": "指可參加的體育相關競賽",
"學校舉辦活動": "學校為促進學習、社群感及慶祝成就而策劃的事件，包括校慶、電影、文化節等。這些活動旨在支持學生全面發展，如身心健康和社交技巧，並提供展示才能的平台",
"英文學分": "通過完成英語課程或程序獲得的學分",
"付費或繳款": "需要在繳費日期前繳交費用，並且繳費日期在活動日期前，包括學雜費、活動保證金、申請車位等，不包含活動中獲得的獎勵"
### 用戶輸入:
標題:{title}
內文:{content}
"""
    # 创建提示模板
    prompt = PromptTemplate.from_template(templates_classify)
    # 使用提示模板与 LLM 交互
    formated_prompt = prompt.format(title = title,content = content)
    print(formated_prompt)
    response = llm.invoke(formated_prompt)
    print(response)
    
    return response

# llm_classify("""
# "【快搶!! 再度開放名額】3/5 (二)10:00圖書特展開幕 (摸彩、茶點、導覽)，加碼抽500元禮券~ 先搶先贏！"
# """,
# """
# 網路報名一開放就秒殺你的心聲我們聽到了!!3/5 圖書特展開幕抽500元禮券,報名名額增加20名！！還不快搶！！傳送門👉https://activity.lib.ntust.edu.tw/signup/458報名只到3/2(六)16:00止!!圖書館「2024年春季名人推薦圖書」圖書特展開幕儀式◆◆3/5(二) 上午10:00  圖書館後棟一樓B庫學習中心◆◆🎁🎁現場抽出幸運兒可獲100元禮券!(須9:55前報到!)📢加碼: 慶祝49週年,邁向50週年校慶，於網路報名再抽出特別獎1名，可獲超商禮券500元!!先搶先嬴https://activity.lib.ntust.edu.tw/signup/458🎁🎁沒抽到7-11禮券？ 接下來還可以參加「選愛書,抽禮券」活動!!開幕典禮結束至10:40前，於學習中心圖書特展區挑選一本「最喜歡的書」，領取摸彩券後填寫書名；再到二樓視聽區享用免費茶點，10:40於二樓視聽區現場抽出21名幸運兒，可獲得禮券100元及200元(各10名)!!（限抽獎時在場者才可領獎哦）📢 📢再加碼: 抽出特別獎1名，可獲超商禮券500元!!
# """)
llm_classify("""
【學務處生輔組】112-2新增【校外】、【自辦】獎助學金，詳見獎學金網頁/最新消息。
""",
"""
© Copyright (c) NTUST 2020© 學務處生活輔導組電話：(02)2730-3760© 系統開發及維護：電子計算機中心
""")
