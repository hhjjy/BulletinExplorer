from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os,asyncio,json,re,requests
from dotenv import load_dotenv
from log_config import setup_logger
import logging,traceback

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量。")
logger = setup_logger("llm_service", log_level=logging.DEBUG)

# label table的所有資料
label_table = None
def get_label_table():
    response = requests.post("http://localhost:8000/llm/get_label_table")
    label_table = response.json()  # 將 JSON 格式的回應轉換為 dict
    return label_table

class LLMService:
    def __init__(self,api_endpoint):
        self.llm = ChatOpenAI(temperature=0.3, model_name="gpt-4-0613")
        self.api_endpoint = api_endpoint

    async def classify_content_by_llm(self, title: str, content: str) -> dict:
        """異步分類內容並返回標籤字典"""
        logger.info(f"輸入標題: {title}, 內容: {content}")
        # 創建提示模板（此處假設這一步不需要異步操作）
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
        prompt = PromptTemplate.from_template(templates_classify)
        formatted_prompt = prompt.format(title=title, content=content)
        logger.info(f"格式化提示: {formatted_prompt}")
        
        # 假設 ChatOpenAI 的 invoke 方法支持異步調用
        response = await self.llm.invoke(formatted_prompt)
        logger.info(f"輸出: {response}")
        
        tags_dict = self.extract_json_from_response(response)
        return tags_dict

    async def classify_content_by_regex(self, title: str, content: str) -> dict:
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
        result = {'tags': []}
        result['tags'] = regex_labels.get('tags', []) + voting_result.get('tags', [])
        return result

    async def aggregate_tags_from_models(self, rawid, title, content):
        # 假设 BulletinInfo 包含了 rawid, title, content
        bulletin_info = {"rawid": rawid, "title": title, "content": content}
        
        # 对 BulletinInfo 进行处理，这里 LLM1, LLM2, LLM3 是示例处理函数
        # 你需要根据实际情况定义这些函数或者处理逻辑
        results_llm1 = self.LLM1(bulletin_info)
        results_llm2 = self.LLM2(bulletin_info)
        results_llm3 = self.LLM3(bulletin_info)
        
        # 将结果提交给投票系统，这里的 voting 是一个示例函数
        # 你需要根据实际情况定义投票或聚合逻辑
        final_tags = self.voting([results_llm1, results_llm2, results_llm3])
        
        # 返回最终的标签
        return {"tags": final_tags}        
    async def execute(self):
        # Fetch unprocessed bulletins
        bulletins_response = requests.post(f"{self.api_endpoint}/llm/get_unprocessed_bulletin")
        bulletins = bulletins_response.json()
        for bulletin in bulletins:
            rawid = bulletin['rawid']
            title = bulletin['title']
            content = bulletin['content']

            # Classify content using three different LLMs and perform voting
            llm1_labels = await self.classify_content_by_llm(title, content)
            llm2_labels = await self.classify_content_by_llm(title, content)
            llm3_labels = await self.classify_content_by_llm(title, content)
            llm_voting_result = self.voting(llm1_labels, llm2_labels, llm3_labels)

            # Classify content using regex
            labels_regex = await self.classify_content_by_regex(title, content)

            # Combine results
            result_label = await self.combine(labels_regex, llm_voting_result)

            # Post labels back to the API
            for tag in result_label['tags']:
                
                label_response = await requests.post(f"{self.api_endpoint}/llm/get_label_id", json={'labelname': tag})
                label_id = label_response.json()['labelid']
                response_dict = {'rawid': rawid, 'labelid': label_id}
                await requests.post(f"{self.api_endpoint}/llm/save_label", json=response_dict)

        # Report finishing
        requests.post(f"{self.api_endpoint}/llm/report_finishing")

    @staticmethod
    def extract_json_from_response(response: str) -> dict:
        """從字符串中提取 JSON 並返回字典"""
        logger.info(f"輸入: {response}")
        pattern = r'```json\n(.*?\n*?)```'
        matches = re.search(pattern, response, re.DOTALL)
        
        json_content_str = matches.group(1) if matches else '{"tags": ["其他"]}'
        logger.info(f"提取的 JSON 字串: {json_content_str}")
        
        response_dict = json.loads(json_content_str)
        logger.info(f"輸出: {response_dict}")
        return response_dict

if __name__ == '__main__':
    # llm_classify("【學務處生輔組】112-2新增【校外】、【自辦】獎助學金，詳見獎學金網頁/最新消息。","© Copyright (c) NTUST 2020© 學務處生活輔導組電話：(02)2730-3760© 系統開發及維護：電子計算機中心")

    # content='### 指令操作：\n\n#### 段落分割：\n- 段落1：【學務處生輔組】112-2新增【校外】、【自辦】獎助學金，詳見獎學金網頁/最新消息。\n- 段落2：© Copyright (c) NTUST 2020© 學務處生活輔導組電話：(02)2730-3760© 系統開發及維護：電子計算機中心\n\n#### 主旨分析：\n- 段落1主旨：學務處生輔組在112-2學期新增了校外和自辦的獎助學金，詳細信息可以在獎學金網頁的最新消息中查看。\n- 段落2主旨：版權所有，學務處生活輔導組的聯絡電話和系統開發及維護單位的信息。\n\n#### 摘要提取：\n- 段落1摘要：112-2學期新增校外和自辦的獎助學金，詳情請查看獎學金網頁的最新消息。\n- 段落2摘要：學務處生活輔導組的聯絡電話為(02)2730-3760，系統由電子計算機中心開發及維護。\n\n#### 標籤匹配：\n- 段落1標籤：學校舉辦活動\n- 段落2標籤：其他\n\n### 指令操作：\n\n#### 標籤合併：\n- 學校舉辦活動、其他\n\n#### JSON格式輸出：\n```json\n{\n    "tags": ["學校舉辦活動", "其他"]\n}\n```'
    # print(get_dict_from_str(content))
    LLM = LLMService("http://127.0.0.1:8000")
    
    # import os
    # import asyncio
    # from openai import AsyncOpenAI

    # client = AsyncOpenAI(
    #     # This is the default and can be omitted
    #     api_key=os.environ.get("OPENAI_API_KEY"),
    # )

    # async def llm(title,content) -> None:
    #     response = await client.chat.completions.create(
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": "Say this is a test",
    #             }
    #         ],
    #         model="gpt-3.5-turbo",
    #     )
    #     print(response)
    #     return response

        
        # chat_completion = await client.chat.completions.create(
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": "i am leo who are u ",
        #         }
        #     ],
        #     model="gpt-3.5-turbo",
        # )


    asyncio.run(llm(1,2))