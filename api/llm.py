import os,asyncio,json,re,requests
from dotenv import load_dotenv
from log_config import setup_logger
import logging,traceback
from openai import AsyncOpenAI
import atexit

load_dotenv()
mode = os.getenv("DEV_OR_MAIN")  # 默認為開發環境 
if mode == "main" or mode == "MAIN":# dev 
    print("MAIN MODE")
    API_server =  "http://"+os.getenv("API_MAIN_HOST")+":"+os.getenv("API_MAIN_PORT")
    print(f"LLM API SERVER :{API_server}")
else:
    print(f"Defaulting to DEVELOPMENT MODE.")
    print("DEV MODE ")
    API_server =  "http://"+os.getenv("API_DEV_HOST")+":"+os.getenv("API_DEV_PORT")
    print(f"LLM API SERVER :{API_server}")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量。")
logger = setup_logger("llm_service", log_level=logging.DEBUG)
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
# label table的所有資料
label_table = None
def get_label_table():
    response = requests.post(f"{API_server}/llm/get_label_table")
    label_table = response.json()  # 將 JSON 格式的回應轉換為 dict
    return label_table
def find_labelid(label_define, labelname):
    for label in label_define:
        if label['labelname'] == labelname:
            return label['labelid']
    else :
        return 0 #表示其他
class LLMService:
    def __init__(self,api_endpoint):
        self.api_endpoint = api_endpoint
        # openai.api_key = os.getenv("OPENAI_API_KEY")
    def classify_content_by_regex(self, title: str, content: str) -> dict:
        result = {'tags': []}
        global label_table

        if label_table is None:
            label_table = get_label_table()
        
        matched_labels = []  # 用於儲存符合的標籤

        # 正規表達式模式，尋找符合的標籤名稱
        label_names = [label["labelname"] for label in label_table]
        pattern = "|".join(label_names)
        regex = re.compile(pattern)

        # 搜尋標題中的符合標籤
        title_matches = regex.findall(title)
        matched_labels.extend(title_matches)

        # 搜尋內容中的符合標籤
        content_matches = regex.findall(content)
        matched_labels.extend(content_matches)

        # 去除重複的標籤
        matched_labels = list(set(matched_labels))
        
        result['tags'] = matched_labels

        return result
    
    def voting(self, llm1_labels, llm2_labels, llm3_labels) -> dict:
        # 規則：
        #     1. 創立一個集合 計算各個標籤的個數 
        #     2. 只要標籤不是其他 超過兩票就算
        #     3. 針對其他大於兩票 強制把其他標籤結果覆蓋 
        #     4. 或是結果恰好沒有同意的 會被設為其他 表示意見非常繁雜
        logger.info(f"輸入: {llm1_labels},{llm2_labels},{llm3_labels}")
        # Initialize an empty dictionary to store the final result
        result = {'tags': []}
        # Initialize a list to collect all tags
        all_tags = []
        # Extend the all_tags list with tags from each label set
        all_tags.extend(llm1_labels.get('tags', []))
        all_tags.extend(llm2_labels.get('tags', []))
        all_tags.extend(llm3_labels.get('tags', []))

        # Use a set for unique tags and a dictionary to count occurrences
        unique_tags = set(all_tags)
        tag_counts = {tag: all_tags.count(tag) for tag in unique_tags}

        # Determine which tags meet the voting criteria (appearing in at least two label sets)
        agreed_tags = [tag for tag, count in tag_counts.items() if count >= 2 and tag!= "其他"]

        # Handle special case for the tag "其他"
        # If "其他" is the only tag or appears in all three label sets, include it in the result
        if ("其他" in unique_tags and tag_counts["其他"] >= 2) or len(agreed_tags) == 0:
            agreed_tags=["其他"]

        result['tags'] = agreed_tags
        logger.info(f"輸出: {result}")
        return result

    def combine(self, regex_labels, voting_result)->dict:
        # 如果 llm輸出的標籤有其他 ，只有在regex_labe 數量為0的情況下 才會輸出其他 。
        # 否則其他情況 其他都會被覆蓋 。
        result = {'tags': []}
        if "其他" in voting_result.get('tags', []) :
            regex = regex_labels.get('tags', [])
            if len(regex) > 0:
                result['tags'] = regex # 只有在regex長度不為0才會輸出regex 否則就是輸出其他
            else :
                result['tags'] = ["其他"]
        else:
            result['tags'] = voting_result.get('tags', []) + regex_labels.get('tags', []) # 直接輸出串接 
        return result

    async def llm(self,title: str, content: str):
        client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        # 使用提供的模板格式化输入
        system_prompt  = f"""
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
            3. 最後請檢查輸出是否包含大括號 如果沒有請新增。
            ### 標籤與標籤定義：
            "餐點": "提供免費食物、餐點或餐盒、點心",
            "自我認識": "提供心理健康相關服務，如個別諮詢、小團體訓練、心理測驗、生命教育和性平教育，但不包含透過分享引起他人的反饋和討論",
            "考試": "用於評估學生學習成果的正式測試，包括書面、口頭或實踐測試，通過後可獲得證照或證書",
            "學習技能": "提升個人能力、知識或專業技能",
            "體育活動": "指可參加的體育相關競賽",
            "學校舉辦活動": "學校為促進學習、社群感及慶祝成就而策劃的事件，包括校慶、電影、文化節等。這些活動旨在支持學生全面發展，如身心健康和社交技巧，並提供展示才能的平台",
            "英文學分": "通過完成英語課程或程序獲得的學分",
            "付費或繳款": "需要在繳費日期前繳交費用，並且繳費日期在活動日期前，包括學雜費、活動保證金、申請車位等，不包含活動中獲得的獎勵"
            """        
        user_input = f"""###用戶輸入:
            "標題": "{title}",
            "內文": "{content}"
            """
        # logger.info(f"user_input:\n{user_input}\n")
        chat_completion = await client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_input,
                },
                # 根据需要添加更多消息
            ],
        )
        # 从返回的对象中提取消息内容
        if chat_completion.choices:
            message_content = chat_completion.choices[0].message.content  # 注意这里的改动
        else:
            message_content = "No completion choices were returned."
            
        # logger.info(f"gpt response :{message_content}")
        j = self.extract_json_from_response(message_content)
        logger.info(f"Json response :{j}")
        return j
    
 
    async def execute(self,max_data=1):
        # async def execute(self,max_data=1):

        # Fetch unprocessed bulletins
        bulletins_response = requests.post(f"{self.api_endpoint}/llm/get_unprocessed_data")
        bulletins = bulletins_response.json()
        logger.info(f"總共發現{len(bulletins)}筆新資料！！,這次最多可以處理{max_data}筆資料")
        label_define = get_label_table() 
        for i,bulletin in enumerate(bulletins,start=1):
            if max_data - i >=0 :
                # print(bulletin) 
                rawid = bulletin.get('rawid')
                title = bulletin.get('title')
                content = bulletin.get('content')
                logger.info(f"處理第{i}筆資料,rawid:{rawid}")
                # Classify content using three different LLMs and perform voting
                logger.info(f"title:{title}\n\ncontent:{content}\n")
                labels = await self.classify_and_vote(title, content)
                # Post labels back to the API
                for tag in labels.get('tags'):
                    label_id = find_labelid(label_define, tag)
                    response_dict = {'rawid': rawid, 'labelid': label_id}
                    requests.post(f"{API_server}/llm/save_label", json=response_dict)
            else :
                logger.info(f"llm 處完{max_data}筆資料，停止運行！")
                break 
        # delete event 
        # requests.post(f"{self.api_endpoint}/llm/report_finishing")
        
    
    @staticmethod
    def extract_json_from_response(response: str) -> dict:
        try:
            # logger.info(f"input : {response}")
            """从字符串中提取 JSON 并返回字典"""
            # 匹配被 ```json\n 和 ``` 包裹的，或直接以 { 开头直到 } 结尾（考虑嵌套的情况）的 JSON 字符串
            pattern = r'```json\n([\s\S]*?)```'
            match = re.search(pattern, response)
            # 如果匹配到被 ``` 包裹的 JSON，使用第一个匹配组；否则，使用第二个匹配组
            json_content_str = match.group(1) 
            response_dict = json.loads(json_content_str)
            # logger.info(f"output : {response_dict}")
            return response_dict
        except Exception as Error:

            error_message = "無法解析LLM輸出結果！ {}".format(str(Error))
            error_traceback = traceback.format_exc()
            logger.error(f"輸入字串 : {response}")
            logger.error(f"解析字串 : {json_content_str}")
            logger.error("問題 : %s\n%s", error_message, error_traceback)
            
            return {"tags":["其他"]}
    
    async def classify_and_vote(self,title,content):
        # 1. 正則表達式找確定標籤 
        regex_labels = self.classify_content_by_regex(title,content)
        logger.info(f"regex result:{regex_labels}")
        # 2. LLM標籤分類 
        logger.info(f"start llm1, llm2, llm3 concurrently")
        llm1_labels, llm2_labels, llm3_labels = await asyncio.gather(
            self.llm(title, content),
            self.llm(title, content),
            self.llm(title, content)
        )
        logger.info(f"llm1,2,3:{llm1_labels},{llm2_labels},{llm3_labels}")
        # 3. LLM投票決定最終標籤 
        logger.info(f"llm1,2,3:{llm1_labels},{llm2_labels},{llm3_labels}")
        llm_voting_result = self.voting(llm1_labels, llm2_labels, llm3_labels)
        logger.info(f"llm_voting_result:{llm_voting_result}")
        # 4. 合併兩者結果
        combine_labels = self.combine(regex_labels, llm_voting_result)
        logger.info(f"combine_labels:{combine_labels}")
        return combine_labels
import unittest
class TestLLMCombine(unittest.TestCase):
    def test_combine_other_and_scholarship(self):
        llm = {"tags": ["其他"]}
        regex = {"tags": ["獎助學金"]}
        expected = {"tags": ["獎助學金"]}
        self.assertEqual(LLM.combine(regex_labels=regex, voting_result= llm), expected)

    def test_combine_other_and_empty(self):
        llm = {"tags": ["其他"]}
        regex = {"tags": []}
        expected = {"tags": ["其他"]}
        self.assertEqual(LLM.combine(regex_labels=regex, voting_result= llm), expected)

    def test_combine_activity_and_scholarship(self):
        llm = {"tags": ["學校舉辦活動"]}
        regex = {"tags": ["獎助學金"]}
        expected = {"tags": ["學校舉辦活動", "獎助學金"]}
        self.assertEqual(LLM.combine(regex_labels=regex, voting_result= llm), expected)

    def test_combine_activity_and_empty(self):
        llm = {"tags": ["學校舉辦活動"]}
        regex = {"tags": []}
        expected = {"tags": ["學校舉辦活動"]}
        self.assertEqual(LLM.combine(regex_labels=regex, voting_result= llm), expected)
class TestLabelVoter(unittest.TestCase):
    # def setUp(self):
        # self.voter = LabelVoter()  # Initialize your class

    def test_other_condition_met(self):
        llm1_labels = {"tags": ["其他"]}
        llm2_labels = {"tags": ["其他"]}
        llm3_labels = {"tags": ["其他"]}
        expected_result = {"tags": ["其他"]}
        self.assertEqual(LLM.voting(llm1_labels, llm2_labels, llm3_labels), expected_result)

    def test_one_label_agreed(self):
        llm1_labels = {"tags": ["獎助學金"]}
        llm2_labels = {"tags": ["其他"]}
        llm3_labels = {"tags": ["獎助學金"]}
        expected_result = {"tags": ["獎助學金"]}
        self.assertEqual(LLM.voting(llm1_labels, llm2_labels, llm3_labels), expected_result)

    def test_no_agreement(self):
        llm1_labels = {"tags": ["學校舉辦活動"]}
        llm2_labels = {"tags": ["其他"]}
        llm3_labels = {"tags": ["獎助學金"]}
        expected_result = {"tags": ["其他"]}  # Based on your logic, this should actually be "其他" since there's no agreement
        self.assertEqual(LLM.voting(llm1_labels, llm2_labels, llm3_labels), expected_result)

    def test_mixed_labels(self):
        llm1_labels = {"tags": ["學校舉辦活動", "獎助學金"]}
        llm2_labels = {"tags": ["其他"]}
        llm3_labels = {"tags": ["獎助學金"]}
        expected_result = {"tags": ["獎助學金"]}
        self.assertEqual(LLM.voting(llm1_labels, llm2_labels, llm3_labels), expected_result)
    def test_withnoinput(self):
        llm1_labels = {"tags": []}
        llm2_labels = {"tags": []}
        llm3_labels = {"tags": []}
        expected_result = {"tags": ["其他"]}
        self.assertEqual(LLM.voting(llm1_labels, llm2_labels, llm3_labels), expected_result)
class TestAPI(unittest.TestCase):
    def save_label_inital(self):
        api = f"{API_server}/llm/save_label"
        data = {"rawid":1,"labelname":"餐點"}
        expect = {"message":"Label ID INSERT SUCESSFULLY!","detail":""}
        response = requests.post(api,json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expect)
    
    def save_label_same(self):
        api = f"{API_server}/llm/save_label"
        data = {"rawid":1,"labelname":"餐點"}
        expect = {"message":"Label ID INSERT SUCESSFULLY!","detail":""}
        response = requests.post(api,json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expect)
        
def delete_event():
    url = API_server + "/llm/delete_event"
    data = {
        "function": "llm",
        "status": "2"
    }
    response = requests.post(url, json=data)
    logger.info("離開!執行完 delete_event")

if __name__ == '__main__':
    atexit.register(delete_event)

    import argparse
    parser = argparse.ArgumentParser(description='使用指定的執行次數來運行 LLM 服務。')
    parser.add_argument('--max_data', type=int, default=1, help='處理的數據項目的最大數量。')
    args = parser.parse_args()

    LLM = LLMService(f"{API_server}")
    asyncio.run(LLM.execute(max_data=args.max_data))




