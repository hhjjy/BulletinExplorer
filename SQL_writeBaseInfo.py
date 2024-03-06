import os
import requests

test_case_bulletinraw = [{'publisher': '台科大語言中心', 'title': '【語言中心】外語學習坊各種諮詢服務已開始', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122322,r1391.php?Lang=zh-tw', 'content': '學期外語學習坊將於星期一(3/4)開放使用喔!欲了解本學期外語學習坊開放的時間外語學習坊(IB-203)不僅提供各類語言的諮詢服務(英文及華語教師諮詢、英文小老師諮詢、日文小老師諮詢、華語小老師諮詢) ，也提供英文小書借閱喔!知道本學期校內有哪些英語學習相關的活動可參加呢?英文教師諮詢採預約制，開放七天前線上做申請英文小老師諮詢則不需要預約，可依照以下時間前往做諮詢其他語言(日文及華語諮詢)，可點閱此連結:https://lc.ntust.edu.tw/p/412-1070-11164.php?Lang=zh-tw'}, {'publisher': '台科大體育室', 'title': '112學年度精誠盃籃球、排球、桌球、滾球、木球錦標賽-報名簡章', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122351,r1391.php?Lang=zh-tw', 'content': '1.報名簡章如附件，即日起至03月15日(五)止。附件:國立臺灣科技大學 112 學年度 精誠盃籃球、排球、桌球、滾球、木球錦標賽競賽規程2.抽籤日期113年3月22日(星期五)中午12時30分，於體育室抽籤(木球項目無須抽籤)。如未出席者由主辦單位代抽，不得異議。賽程於4月1日（星期一）通知並公佈於體育室網頁、全校性公佈欄。3.本學期新增:報名截止日前至網頁https://register-sport.ntust.edu.tw/連結精誠盃報名系統線上報名。(1)學生組所有比賽項目皆需透過系學會報名，系學會負責體育活動者請至體育室找周宗豪老師開啟權限。報名完成請將報名表列印並加蓋系所或系學會章後繳交紙本至體育室完成報名。凡完成報名手續後一律不得更改名單。(2)教職員工組負責報名各項運動賽事者，請至體育室找周宗豪老師開啟權限。(3)如需組成聯隊請直接至體育室找周宗豪老師協助報名。若有相關問題請洽體育室競賽活動組周宗豪老師，分機7004'}, {'publisher': '台科大通識教育中心', 'title': '【誠徵】「臺科大城南學院STREAM沉浸式夏校」工作人員招募中！', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122350,r1391.php?Lang=zh-tw', 'content': '加入我們，你將可以…..※與通識教育中心教授群、台科大實驗室團隊、跨校跨域的團隊夥伴合作※提升各項能力，包含領導統御、團隊協作、專案管理、企畫執行、跨界溝通、複雜問題解決、危機處理等等※把這個經歷寫在履歷表上超加分※直接申請社會實踐1學分！※以此為題進行「跨領域實務專題」，再拿2學分！(跨領域實務專題選課、修讀辦法)'}, {'publisher': '台科大推廣教育中心', 'title': '勞動部ESG永續發展人才培育據點計畫說明會 暨永續管理師人才養成班就業媒合會', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122349,r1391.php?Lang=zh-tw', 'content': '歡迎全校師生踴躍參加~'}, {'publisher': '台科大圖書館', 'title': '【快搶!! 再度開放名額】3/5 (二)10:00圖書特展開幕 (摸彩、茶點、導覽)，加碼抽500元禮券~ 先搶先贏！', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-121970,r1391.php?Lang=zh-tw', 'content': '網路報名一開放就秒殺你的心聲我們聽到了!!3/5 圖書特展開幕抽500元禮券,報名名額增加20名！！還不快搶！！傳送門👉https://activity.lib.ntust.edu.tw/signup/458報名只到3/2(六)16:00止!!圖書館「2024年春季名人推薦圖書」圖書特展開幕儀式◆◆3/5(二) 上午10:00\xa0 圖書館後棟一樓B庫學習中心◆◆🎁🎁現場抽出幸運兒可獲100元禮券!(須9:55前報到!)📢加碼: 慶祝49週年,邁向50週年校慶，於網路報名再抽出特別獎1名，可獲超商禮券500元!!先搶先嬴https://activity.lib.ntust.edu.tw/signup/458🎁🎁沒抽到7-11禮券？ 接下來還可以參加「選愛書,抽禮券」活動!!開幕典禮結束至10:40前，於學習中心圖書特展區挑選一本「最喜歡的書」，領取摸彩券後填寫書名；再到二樓視聽區享用免費茶點，10:40於二樓視聽區現場抽出21名幸運兒，可獲得禮券100元及200元(各10名)!!（限抽獎時在場者才可領獎哦）📢\xa0📢再加碼: 抽出特別獎1名，可獲超商禮券500元!!'}, {'publisher': '台科大圖書館', 'title': '【電影欣賞活動】圖書館電影欣賞《奧本海默》3月7日(三) 18:30-21:30，歡迎踴躍參與！/Library to invite you to see a movie " Oppenheimer " at 18:30 p.m. on Mar. 07 (Thu.), 2024 at IB-101', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122238,r1391.php?Lang=zh-tw', 'content': '【活動】免費電影欣賞，歡迎參加！※可登錄公務人員及約用人員終身學習時數※【電影】奧本海默【片長】180分鐘【時間】2024/03/07(四)18:30-21:30(18:10開放進場，自由入座)【地點】IB-101(場內禁止飲食)【主辦單位】圖書館【簡介】一起與全球各地觀眾體驗令人讚嘆的現象級傑作，由導演克里斯多夫諾蘭執導，【奧本海默】帶領觀眾進入物理學家羅伯特奧本海默(席尼墨菲飾)，在二次大戰期間主持的曼哈頓計畫中寫下科學史上的里程碑，並研發第一顆原子彈…。本片由席尼墨菲、艾蜜莉布朗主演，參與演出陣容豪華，包括奧斯卡提名麥特戴蒙、小勞勃道尼、佛蘿倫絲普伊以及奧斯卡得主凱西艾佛列克、雷米馬利克和肯尼斯布萊納等巨星共同主演。(摘自博客來)預告片https://youtu.be/cnc8mDAB7QI全程出席者，電影結束後現場抽出30名幸運得主，中獎者可得7-11禮券！（限本校在校師生，領獎需配合填寫基本資料；非本國籍者，領獎需帶居留證，按中獎價值預先扣繳20%稅款）◆Film：Oppenheimer◆Language：English◆Subtitle：Chinese◆Run Time：180 minutes◆Date：Thursday, Mar. 07, 2024◆Time：18:30-21:30 (Admission from 18:10)◆Venue：IB-101 (International Building at NTUST Campus)(No eat or drink in the room!)◆Organizer：NTUST Library◆Overview：Barbie suffers a crisis that leads her to question her world and her existence. (Source: IMDb; IMDb: 8.4)Movie Trailerhttps://youtu.be/uYPbbksJxIgAfter the movie, 30 lucky participants will win 7-11 coupon! (Only for teachers and students of NTUST.For those who of foreign nation, the Alien Residence Certificate(ARC) is required when receiving the prize, and 20% tax will be withheld in advance based on the value of the prize.)'}, {'publisher': '台科大通識教育中心', 'title': '【學程推薦】想成為專業技術、跨域整合力兼具的π型人才嗎？通識教育中心設置「STEM/STREAM 跨域微學程」，歡迎本校大學部學生申請修讀。', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122123,r1391.php?Lang=zh-tw', 'content': '各位同學大家好：為培育學生更多元的跨域整合能力，通識教育中心設置「STEM/STREAM跨域微學程」，歡迎本校大學部學生申請修讀。一、STEM/STREAM跨域微學程簡介：本學程涉及「數位人文」、「體驗學習」與「知識傳承」等三種向度，同步規劃培養理論知識的「帶狀課程」，以及建構實作知識的「塊狀課程」，以體現「科技導入人文」、「做中學」與「知識扎根」。本學程亦提供一個良好平台，讓科學、科技、工程、數學、識讀與藝術等專業領域的學生進行跨域交流、跨界學習，提供問題導向的跨領域統整教學方式，讓同學有機會針對特定社會議題進行探究並構思解決方案。強化跨域合作能力、創新專業實務能力與問題解決能力。二、本學期申請修讀期限：2/2（五）～3/1（五）三、有興趣的同學請上網申請https://cour01.ntust.edu.tw/DMP_student/，並於3/1（五）下午4時前，將修讀申請書印出、送達通識教育中心辦公室(醫揚大樓5樓IA-505-1)，才算完成申請。四、注意事項：1.學程僅提供大學部學生申請修讀，修讀辦法詳：https://www.academic.ntust.edu.tw/var/file/48/1048/img/2550/765403956.pdf2.必修跨領域實務專題，選課方法詳：https://cla.ntust.edu.tw/p/412-1076-8605.php?Lang=zh-tw「臺科大城南學院STREAM沉浸式夏校」工作人員招募中，參與籌備夏校(以高中/職學生為學員的營隊式課程)，可以作為「跨領域實務專題」內容唷！點擊了解詳細夏校資訊3.修畢規定學分後，最遲應於「畢業當學期」主動提出「修業證明」申請（申請期間：每學期本校行事曆「第二次退選」起、迄時間）。若您畢業當學期已修完或預計可修完規定課程（即使當學期還剩一科目正在修讀，也需此規定期限內提出修業證明申請）。4..若主修系無特殊規定，所修讀之相同課名且相同學分的課程，可同時認列於畢業學分及本學程學分。5.申請修讀後，即使畢業時未修完規定學分，也無需來中心申請放棄。（沒修完，僅無法領到修業證明）；惟未於事先申請修讀，雖畢業時已修完本學程規定學分，將無法核發修業證明。（依規定必須事先提出「申請修讀」，才能於修讀完成時，由學生主動提出「修業證明」申請）6.若有其他問題，歡迎來中心洽詢。電話02-2730-1099；通識教育中心辦公室：醫揚大樓5樓IA-505-1。通識教育中心敬啟'}, {'publisher': '台科大通識教育中心', 'title': '【校內工作坊】113.03.07 「形象改造工作坊：挖掘台科潛力股」找出個人皮膚基因色彩魅力，歡迎報名~', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122280,r1391.php?Lang=zh-tw', 'content': '活動簡介：每次出門約會的時候，常不知道自己要穿哪套顏色的服裝？是否今天穿這件顏色適不適合這個面試工作場所？透過有系統的教學與學習分辨方式，讓您輕鬆快樂學習皮膚色彩屬性！「皮膚基因色彩屬性」是每個人與生俱來的皮膚基因色調，以各種不同的比例組合所得出的結果。當你了解人天生就有一個皮膚基因色調後，在選擇服飾的顏色時，選擇適合的顏色來「搭配」我們的「臉色」！臉是主角，選擇可以讓這個主角美麗、放射光芒的顏色！讓你：✨找到屬於自己的皮膚基因色彩屬性✨氣色看起來很好✨搭配適合的配飾✨搭配適合的彩妝顏色✨搭配適合的頭髮顏色🌟🌟🌟🌟🌟🌟🌟🌟🌟鄒老師淺顯易懂、生動活潑的工作坊，千萬不要錯過！🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟◆活動時間：2023/3/7(四)13:00-16:00◆活動地點：RB-102 (12:30開放報到)◆活動對象：台科大同學們◆活動人數：30人◆報名流程：點我報名，或是拉到頁面最下方有報名表單唷！依報名先後次序錄取◆個人準備事項：1.素顏(可在現場卸妝)2.穿著白色衣服(可帶來現場換)3.帶鏡子4.帶筆記本5.手機帶著🌟找好朋友一起來參與，可以互相協助。又可以拿飲料券唷！🌟🎁攜帶異性同學一起來參與，可以獲得飲料券唷！（數量有限，把握雙人組的報名唷！）🎁全程參與本活動並於活動後填寫問卷者，即可參與超商100元禮券抽獎！※ 主辦單位保有調整、更改或取消活動之權利；如有課程異動或相關事宜，將以Email通知。講者介紹：鄒家鈺\xa0 \xa0Chia-Yu TSOU \xa0老師鄒老師個人簡介國立臺灣科技大學\xa0通識教育中心\xa0助理教授級專業技術人員Chia-Yu TSOU\xa0品牌\xa0主理人\xa0與\xa0設計總監勞動部＜時尚服飾畫＞課程 講師文化部＜時裝週＞ 品牌服裝設計師聯絡窗口：通識教育中心-曾小姐電話：(02)2730-1148信箱：yijie@mail.ntust.edu.tw指導單位: 教育部\xa0 \xa0 主辦單位：國立臺灣科技大學 高教深耕計畫、通識教育中心'}, {'publisher': '台科大學務處', 'title': '【學務處生輔組】112-2新增【校外】、【自辦】獎助學金，詳見獎學金網頁/最新消息。', 'url': 'https://sa.ntust.edu.tw/Scholarship/', 'content': '© Copyright (c) NTUST 2020© 學務處生活輔導組電話：(02)2730-3760© 系統開發及維護：電子計算機中心'}, {'publisher': '台科大研究發展處計畫業務服務中心', 'title': '【活動公告】2024年功能性材料研討會暨國科會專題研究計畫成果發表會', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122336,r1391.php?Lang=zh-tw', 'content': '說明：相關資訊：來文電子檔如有任何疑問或需協助之處，惠請不吝來電或來信洽詢，謝謝您！臺灣科技大學 研究發展處計畫業務服務中心 莊雯茹(電話:02-2730-3227，國際大樓九樓)敬上'}, {'publisher': '台科大產學處創新育成中心', 'title': '🔥The 3rd Global Talent Entrepreneurship Program Orientation 🔥 第三屆GTEP說明會開放報名囉', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122332,r1391.php?Lang=zh-tw', 'content': '為激勵在台外籍生，培養創新創業知能，國立臺灣科技大學將於113年3月20日(三)辦理「第三屆外籍人才創新創業培訓計畫GTEP」線上說明會，本計畫開放全國大專院校外籍生及本國學生參加，歡迎對創業有興趣、已創業或準備創業的學生參與。The 3rd Global Talent Entrepreneurship Program targets foreign students in Taiwan, providing entrepreneurial training,cultivating talented foreign entrepreneurial teams, and making Taiwan’s entrepreneurial environment more complete and internationalized.A 5-month entrepreneurship program with professional training, all university students are welcome. Join the online orientation to learn more!✨courses + startup base visit + demo day✨1-on-1 consulting & counseling from market experts✨Access to various external entrepreneurial resources✨Free usage of co-working space📍Time: 10:30 AM, March 20th(Wed.), 2024Event Type:OnlineSign Up:https://pse.is/5mwfk2📍More Information:https://pse.is/4tgubfContact Person:\xa0Melia Tsai(meliatsai@mail.ntust.edu.tw)'}, {'publisher': '台科大國際事務處', 'title': '【轉知】HUNGKUANG UNIVERSITY CHINESE LANGUAGE "CENTER CPR+AED" Training Course', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122333,r1391.php?Lang=zh-tw', 'content': ''}, {'publisher': '台科大教務處教學發展中心', 'title': '【免費軟體申請】VisLab AI 圖像檢測軟體免費線上申請 (目前僅剩餘1套，將依申請表登記順序為標準，申請完即截止)', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-116653,r1391.php?Lang=zh-tw', 'content': '各位師長您好：智泰科技股份有限公司贈與台科大50套VisLab AI圖像檢測軟體 (目前僅剩餘1套，將依申請表登記順序為標準，申請完即截止)歡迎各位老師申請領取，領取之老師將獲贈此軟體序號作為該財產之新保管人，待財產轉移流程完畢將提供軟體序號卡，請各位老師妥善保管您的序號卡。財產移動單將會送到申請表中您填寫的收件地點給您，待您蓋完保管人與單位主管章後至保管組，等保管組蓋章完將第2聯送回教發中心始提供序號卡，屆時將會寄信通知您前來領取序號卡。如有意願申請的老師請填寫線上申請表：https://reurl.cc/OVmjv7軟體介紹及下載區：http://www.3dfamily.com/web/product/product_in.jsp?pd_no=PD1605515183338&lang=tw軟體操作教學請參考下列網址：http://www.3dfamily.com/web/product/product_in.jsp?pd_no=PD1611906028527&lang=tw軟體申請問題請聯繫：教務處教發中心業務承辦人：劉玉雯小姐，02-2730-1021，yuwen@mail.ntust.edu.tw軟體使用問題可洽詢：智泰科技\xa002-2267-2688'}, {'publisher': '台科大教務處教學發展中心', 'title': '【轉知】國立中山大學檢送「113年度教育部教學實踐研究計畫南區區域基地跨校教師社群申請辦法」延長徵件資訊，歡迎教師申請。', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122330,r1391.php?Lang=zh-tw', 'content': '一、依據「教育部113年教學實踐研究計畫區域基地計畫」辦理。二、旨揭辦法係透過區域基地模式邀請各區域學校共構教學實踐教師支持網絡，形成區域型的跨校教師社群，透過更廣泛與多元的交流，以提升教師教學實踐研究能量。三、社群成立以自由組成為原則，需含2校以上專任教師組成，相關規定請依循申請辦法及申請表之規範。四、檢附113年度教學實踐研究計畫南區區域基地「跨校教師社群申請辦法」、「申請表」及「經費核銷說明」各1份供參。五、相關計畫申請書收件時間延長至113年3月7日(四)下午11: 59前，請將申請表電子檔寄送至承辦人信箱(shinghua@mail.nsysu.edu.tw)，內容不全或格式不符者恕不予受理。六、聯絡人：國立中山大學教務處教發中心柯小姐，電話07-5252000分機2166。'}, {'publisher': '台科大教務處教學發展中心', 'title': '【活動轉知】國立臺北護理健康大學與國立臺北科技大學苗圃分區資源中心合作舉辦之「112學年度下學期實用中文寫作教學工作坊」(第二十一屆)，歡迎教職員生參加。', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122327,r1391.php?Lang=zh-tw', 'content': '一、國立臺北護理健康大學通識教育中心與國立臺北科技大學苗圃分區資源中心預定於113年04月19日舉辦「112學年度下學期實用中文寫作教學工作坊」(第二十一屆)，敬邀貴校教職員生參加並惠予公差假。二、活動時間：113年04月19日(五)早上八點四十五分至下午四點十五分，中午敬備餐盒。三、活動地點：國立臺北科技大學「宏裕科技大樓B1國際會議廳」(臺北市忠孝東路三段一號，近捷運「忠孝新生站」)。四、本次主題：「AI科技與國文教學創新」。本次活動特別邀請兩位專家分享如何利用AI科技推動國文教學創新，並透過現場實作帶領大家體驗，AI科技能為國文教學帶來哪些多元可能性。五、公告及報名網址如下(報名前請詳讀公告內容)：https://www.beclass.com/rid=284d75865cf8333d8d51六、如本活動臨時調整舉辦方式，將盡速以E-mail通知報名師長及嘉賓。'}, {'publisher': '台科大人事室', 'title': '轉知「第14屆台達企業環境倫理研究獎助」教師國外研究進修徵選計畫，請參考內容。', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122325,r1391.php?Lang=zh-tw', 'content': ''}, {'publisher': '台科大國際產學聯盟推動辦公室', 'title': '【活動敬邀】HPE x NTUST 年度企業參訪，歡迎電機工程系/資訊工程系的大三/大四/碩士生踴躍參與！', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-121945,r1391.php?Lang=zh-tw', 'content': 'HPE (Hewlett Packard Enterprise)是一家全球性的邊緣到雲端、平台即服務的公司，提供包括伺服器、儲存設備、無線網路設備、雲端服務與各種IT服務，協助各組織和企業快速、順利地完成數位轉型。這次將帶領同學參觀HPE位於南港的辦公室一探究竟，歡迎有實習、求職需求的同學們，請不要猶豫，趕緊手刀報名~【活動資訊】【報名須知】【參訪議程】TimeSubject14:00-14:10Greeting/Opening14:10-14:30HPE Welcome Speech14:30-14:40HPE Insight14:40-15:00Unboxing HPE Server15:00-15:30Life in HPE15:30-15:40Break Time15:40-16:30Explore HPE16:30-16:45HPE Career Spotlight16:45-17:00Closing & Group Picture【備註】【聯絡窗口】國際產學聯盟推動辦公室葉小姐 02-2733-3141分機5127Email：gloria@mail.ntust.edu.tw'}, {'publisher': '台科大語言中心', 'title': '【語言中心集點活動】112-2 第一場電影之夜「摩天大樓」開放報名囉~', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122321,r1391.php?Lang=zh-tw', 'content': '活動時間：113年3月22日(五)17:30~20:30活動地點：未定(報名成功後將公告)撥放電影：摩天大樓 Skyscraper報名網址：https://forms.gle/cfNatTUfShvjb3b99【備註】活動當日備有餐點(報名前40名)；電影以英文字幕播放；全程參與可獲得英文自學點數１點。📌本活動與學務處築夢踏實合作，全程參與皆可獲得課外成長獎助金A項申請門檻1場，需現場取得認證章。'}, {'publisher': '台科大學生事務處', 'title': '【2024 春季校園徵才說明會熱烈開跑囉！】', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122320,r1391.php?Lang=zh-tw', 'content': '【2024 春季校園徵才說明會熱烈開跑囉！】時間：3/01～3/26 （週一至週五） 12:20～16:20地點：國際大樓二樓 IB-2022024 校園徵才說明會第一、二週活動內容如下，無論是尋找未來就業廠商還是實習機會，都歡迎同學們踴躍參加，聽聽各家企業對於招募員工的第一手訊息！All information sessions are held in Chinese language.說明會場次報名：https://career.ntust.edu.tw/#/news/2058原訂 3/01 (五) 第四場次【士林電機廠】因廠商內部臨時會議延期至 3/11 (一) 第四場次舉辦！請同學特別注意！[說明]每場說明會廠商若未提供餐點，學務處就輔組將加碼贈送：第一場（午餐）提供便當給前 30 位入場同學（會後發放）第二、三、四場提供點心給前 30 位入場同學（會後發放）歡迎同學們踴躍報名參加！本活動可採計高教深耕築夢踏實助學金職涯活動項目，詳情請見報名網址：https://career.ntust.edu.tw/#/lectures/recruitment集滿 9 點可兌換精美禮品之外，還可參加總價值高昂的抽獎活動！（其餘抽獎規則請詳閱：https://career.ntust.edu.tw/#/news/2084）※注意事項網路報名之正備取皆不影響入場與集點抽獎資格（僅供主辦方預抓人數）會場內禁止飲食，離開時記得檢查有無遺漏物品All information sessions are held in Chinese language.'}, {'publisher': '台科大教務處教學發展中心', 'title': '【校內實體講座】113.06.13(四) 教學引導力─引導團隊思考與討論的流程設計(工作坊型態)', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122002,r1391.php?Lang=zh-tw', 'content': '本次教發中心特別邀請國際引導者協會專業引導師林依瑋，演講內容為講者會以學習者為中心，在教學法中融入討論流程，透過提問引導學生思考與討論。除了照顧考試所需要的記憶與理解的層次，同時協助學生進行思考討論。探討教師們在教室內教學的教學引導能力，協助老師設計流程，引導團隊思考與討論。活動時間：113年06月13日(星期四) 下午14:00~17:00活動地點：綜合研究大樓RB-101會議室暨PBL教室演 講 者：國際引導者協會專業引導師林依瑋參加對象：僅提供教師\xa0 \xa0 \xa0 \xa0 \xa0 \xa0 \xa0 \xa0 \xa0 \xa0 \xa0 \xa0 (開放三校教師報名，將於6/3(一)開始報名)報名網址：https://reurl.cc/N4nkbn(將於6/07(五)中午12點截止報名或到達報名人數截止)報名人數：限制30人(因工作坊型態限制)連絡窗口：周小姐\xa0 02-2737-6982yiying88@mail.ntust.edu.tw經費來源：國立臺灣科技大學高教深耕計畫其他說明：1.活動開始13:40分開始辦理報到，於14:20分停止簽到，敬請準時出席。2.本活動可提供本校教師之研習時數，需全程參與講座，如需研習證明，請於簽到表中註明，將提供電子檔研習認證。3.本活動會將提供餐點，現場報名恕無法提供餐點。4.本講座無提供築夢踏實認證。活動議程：06/13(星期四) 14:00~17:00時間活動主持人/主講者14:00-14:05引言教務處陳副教務長秀玲14:05-17:00教學引導力─引導團隊思考與討論的流程設計國際引導者協會專業引導師林依瑋'}, {'publisher': '台科大教務處教學發展中心', 'title': '【校內實體講座】113.05.16(四) 問世間創意為何物？執教人生使相許：創意教學創意', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-121992,r1391.php?Lang=zh-tw', 'content': '教務處教發中心特別邀請創新教學專家師範大學張雨霖老師，本演講旨在探討創造力的培養與教師創新教學，期能提升學生的創造力與學習，以面對未來人生。內容包含：簡介創造性思考的關鍵指標、要素，以及創造力教學的類型；體驗多種創意教學方法：如腦力激盪技巧、創造性問題解決、設計思考原則；最後反思教師如何透過教育創新應對未來挑戰。活動時間：113年05月16日(星期四) 下午14:00~16:00活動地點：國際大樓3樓301會議室演 講 者：臺灣師範大學教育心理與輔導學系助理教授張雨霖參加對象：教師、職員、學生、教學助理報名網址：https://reurl.cc/54aOWn(將於05/14(二)中午12點截止報名或到達報名人數截止報名)連絡窗口：周小姐\xa0 02-2737-6982yiying88@mail.ntust.edu.tw經費來源：國立臺灣科技大學高教深耕計畫其他說明：1.本研習可提供本校教師及教學助理相關之研習時數，需全程參與講座，如需研習證明，請於簽到表中註明，將提供電子檔研習認證。【築夢生如何取得認證章】1.活動13:40分開始辦理報到，於14:20分停止簽到，未簽到者無法蓋築夢踏實之研習認證章，且需全程參與研習會，敬請準時出席。2.本研習可提供築夢踏實之研習認證章，如需核章者請於活動結束後，於簽到桌給櫃檯人員出示填完滿意度問卷畫面始得核章，而且蓋認證章時，會確認是否有完成簽到，若造成排隊人潮，請耐心等候。依據築夢踏實助學金計畫規定(五、申請流程之第二步)，須當場改蓋章，無法事後補蓋認證章。(備註：研習活動集點卡，第1個蓋認證章時會發放，聽1場講座蓋1個認證章，需集滿4個認證章，才會再發第2張集點卡)活動議程：05/16(星期四) 14:00~16:00時間活動主持人/主講者14:00-14:05引言教務處陳副教務長秀玲14:05-15:50問世間創意為何物？執教人生使相許：創意教學創意臺灣師範大學教育心理與輔導學系助理教授張雨霖15:50-16:00綜合座談與交流時間'}, {'publisher': '台科大教務處教學發展中心', 'title': '【校內實體講座】113.05.03(五)PBL在大學教學上的應用', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122194,r1391.php?Lang=zh-tw', 'content': '教務處教發中心特別邀請PBL專家中原大學楊坤原教授，以現今趨勢而言，應用PBL（Problem-Based Learning，問題導向學習）於大學教學是當前高教發展的重要趨勢之一。運用PBL可提升學生的學習動機，有效培育具備核心專業知能的學生，達成高教深耕的目標。本次演講的內容主要分為下列幾個部分。首先透過「前言」簡介應用PBL於大學教學的理由，並扼要說明PBL的定義與教學原理。在第二部分「PBL課程單元設計」項下，除針對國內外文獻中關於設計PBL課程單元的具體作法加以闡述外，並輔以個人在中原大學帶動教師社群進行PBL課程單元設計為例，進一步說明設計PBL課程單元的細節及注意事項。第三部分「PBL的教學實務」將提供個人在中原大學實施PBL教學的課堂經驗分享，藉以拋磚引玉，激發教師們未來設計與執行PBL教學的巧思。最後，則從教學心得、教師專業成長活動（SOTL）和學校行政等方面，提出結論與建議。活動時間：113年05月03日(星期五) 下午14:00~16:00活動地點：國際大樓2樓202會議室演 講 者：中原大學教育研究所暨師資培育中心楊坤原教授參加對象：教師、職員、學生、教學助理報名網址：https://reurl.cc/RWE7Yr(將於04/30(二)中午12點截止報名或到達報名人數截止報名)連絡窗口：周小姐\xa0 02-2737-6982yiying88@mail.ntust.edu.tw經費來源：國立臺灣科技大學高教深耕計畫其他說明：1.本研習可提供本校教師及教學助理相關之研習時數，需全程參與講座，如需研習證明，請於簽到表中註明，將提供電子檔研習認證。【築夢生如何取得認證章】1.活動13:40分開始辦理報到，於14:20分停止簽到，未簽到者無法蓋築夢踏實之研習認證章，且需全程參與研習會，敬請準時出席。2.本研習可提供築夢踏實之研習認證章，如需核章者請於活動結束後，於簽到桌給櫃檯人員出示填完滿意度問卷畫面始得核章，而且蓋認證章時，會確認是否有完成簽到，若造成排隊人潮，請耐心等候。依據築夢踏實助學金計畫規定(五、申請流程之第二步)，須當場改蓋章，無法事後補蓋認證章。(備註：研習活動集點卡，第1個蓋認證章時會發放，聽1場講座蓋1個認證章，需集滿4個認證章，才會再發第2張集點卡)活動議程：05/03(星期五) 14:00~16:00時間活動主持人/主講者14:00-14:05引言教務處陳副教務長秀玲14:05-15:50PBL在大學教學上的應用中原大學教育研究所暨師資培育中心楊坤原教授15:50-16:00綜合座談與交流時間'}, {'publisher': '台科大教務處教學發展中心', 'title': '【校內實體講座】113.04.17(三)從審查角度談教學實踐與教學創新之搶分訣竅與申請秘笈', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122001,r1391.php?Lang=zh-tw', 'content': '教務處教發中心特別邀請教學實踐專家國立臺南大學數位學習科技系林豪鏘教授兼系主任，講者榮獲入選世界頂尖資訊領域台灣百大科學家，屢獲獎勵，包括工程教育傑出研究獎、渴望資訊文化獎、國科會研究獎勵傑出人才獎及薪傳學者榮譽，演講次數高達567次，發表著述達466篇。在過去五年中，主講者於全國大學及區域基地進行了超過200場的教學實踐專題演講，並主講多場兩天一夜實作工作坊，分享教學實踐經驗。本次講座內容：主講者將審查角度，分享教學實踐計畫申請策略，介紹如何撰寫計畫主持人介紹章節以增加通過機率，計畫成果的公開發表與共享方法，以及學習成效評量的設計。此外，還會探討教學實踐計畫的審查評分機制和搶分技巧，依變項在研究中的關鍵角色，實驗流程和研究架構的設計，並結合審查案例與教學創新的學理基礎，協助老師們快速汲取經驗，寫出高品質計畫書。誠摯邀請對教學實踐研究計畫有興趣教師們踴躍參加。活動時間：113年04月17日(星期三) 15:30\xa0~17:30活動地點：國際大樓2樓202會議室(IB-202)演 講 者：國立臺南大學數位學習科技系林豪鏘教授兼系主任參加對象：教師、協助教師的助理報名網址：https://reurl.cc/g4x3R7(將於4/15(一)中午12點截止報名或到達報名人數截止報名)連絡窗口：周小姐\xa0 02-2737-6982yiying88@mail.ntust.edu.tw經費來源：國立臺灣科技大學高教深耕計畫其他說明：1.活動開始15:10分開始辦理報到，於15:50分停止簽到，敬請準時出席。2.本活動可提供本校教師及教學助理相關之研習時數，需全程參與講座，如需研習證明，請於簽到表中註明，將提供電子檔研習認證。3.本活動會將提供餐點，現場報名恕無法提供便當。4.本講座無提供築夢踏實認證。活動議程：04/17(星期三) 15:30~17:30時間活動主持人/主講者15:30-15:35引言陳副教務長秀玲15:35-17:25從審查角度談教學實踐與教學創新之搶分訣竅與申請秘笈國立臺南大學數位學習科技系林豪鏘教授兼系主任17:25-17:30綜合討論------'}, {'publisher': '台科大教務處教學發展中心', 'title': '【校內實體講座】113.03.19(二) 精準簡報', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122031,r1391.php?Lang=zh-tw', 'content': '教務處教發中心特別邀請簡報專家簡報藝術烘焙坊SlideArt 的社群長暨設計師謝天璦老師，本次講座將帶你剖析簡報背後的觀念與邏輯，並以實際的簡報案例，帶你一步步解析如何落地應用核心觀念，並帶你瞭解各種實用的簡報設計手法、線上工具資源，幫助你聚焦目的、引導邏輯，更有效地將你的想法傳達給聽眾。活動時間：113年03月19日(星期二) 上午10:00~12:00活動地點：國際大樓2樓201會議室演 講 者：簡報藝術烘焙坊SlideArt 社群長暨設計師謝天璦老師參加對象：教師、職員、學生、教學助理報名網址：https://reurl.cc/A4D5b8(將於03/14\xa0(四)下午17點截止報名或到達報名人數截止報名)連絡窗口：周小姐\xa0 02-2737-6982yiying88@mail.ntust.edu.tw經費來源：國立臺灣科技大學高教深耕計畫其他說明：1.本研習可提供本校教師及教學助理相關之研習時數，需全程參與講座，如需研習證明，請於簽到表中註明，將提供電子檔研習認證。2.本活動會後將提供便當，現場報名恕無法提供便當。3.本次講師天璦老師，為了更能貼近每次受眾的實際簡報使用情境，請本次講座聽眾可以自由上傳平常使用的簡報到以下的雲端連結：https://drive.google.com/drive/folders/1Dwx84mU9ZecmcN2RMo32e7lZ0sF21nsD，講師會根據大家上傳的簡報類型，挑選最適合的過往案例作為課程素材，上傳截止日為 3/11。*備註：1.上傳檔案名稱範例，如下：(1)教師身分：系(所)+姓名，如：化工系王O明老師(2)學生身分：學號+系(所)+姓名，如：M11200000數位所陳O華2.上傳者上傳格式以PDF檔、PPT檔為主，上傳時請不要刪除其他參與者的檔案3.因上傳雲端空間，上傳者請確定檔案內容可公開，也可供講者做為案例進行討論若同意以上的備註事項，可將檔案上傳至雲端空間。【築夢生如何取得認證章】1.活動09:40分開始辦理報到，於10:20分停止簽到，未簽到者無法蓋築夢踏實之研習認證章，且需全程參與研習會，敬請準時出席。2.本研習可提供築夢踏實之研習認證章，如需核章者請於活動結束後，於簽到桌給櫃檯人員出示填完滿意度問卷畫面始得核章，而且蓋認證章時，會確認是否有完成簽到，若造成排隊人潮，請耐心等候。依據築夢踏實助學金計畫規定(五、申請流程之第二步)，須當場改蓋章，無法事後補蓋認證章。(備註：研習活動集點卡，第1個蓋認證章時會發放，聽1場講座蓋1個認證章，需集滿4個認證章，才會再發第2張集點卡)活動議程：03/19(星期二) 10:00~12:00時間活動主持人/主講者10:00-10:05引言教務處陳副教務長秀玲10:05-11:50精準簡報簡報藝術烘焙坊SlideArt的社群長暨設計師謝天璦老師11:50-12:00綜合座談與交流時間'}, {'publisher': '台科大教務處教學發展中心', 'title': '【校內實體講座】113.03.15(五)112學年度第2學期『一般課程』教學助理研習會(本研習會全程中文講述)', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-121994,r1391.php?Lang=zh-tw', 'content': '為提升教學助理之職能與品質，落實培育教學助理專業技能，強化學生學習能力，教發中心於每學期初辦理教學助理研習會，其中教學助理經驗分享環節，本次特邀連續2屆獲獎教學助理營建工程系李仁傑同學，進行教學經驗分享(一般性課程)為例，再者，專題演講的部分，邀請衍聲說藝坊-曾莉婷老師，講授生動的說話技巧主題，在課堂講授以及錄製教材時都需要大量使用到聲音，如何長時間說話也不會不舒服，讓聽眾專注地聽你說話，並依照課程內容調整說話方式，達到良好的教學效果。 一起來學習有效的發聲方式和語調，提升聽眾的注意力。本次研習會主題精彩紛呈，歡迎有興趣的師生一同共襄盛舉。活動時間：113年03月15日(星期五) 15:10~17:05活動地點：國際大樓2樓201會議室(IB-201)演講者：1.連續2屆獲獎教學助理(一般課程)：營建工程系李仁傑同學2.專業課程講者：【衍聲說藝坊】曾莉婷老師參加對象：全校教職員工生報名網址：https://reurl.cc/80zxmb(將於3/12(二)中午12點截止報名或到達報名人數截止報名)連絡窗口：周小姐\xa0 02-2737-6982yiying88@mail.ntust.edu.tw其他說明：1.本研習可提供本校教師及教學助理相關之研習時數，需全程參與講座，如需研習證明，請於簽到表中註明，將提供電子檔研習認證。2.本活動會後將提供餐盒，現場報名恕無法提供餐盒。3.教學助理可參與教發中心於本學期辦理任2場講座，等同完成教學助理培訓，若需教學助理研習證明，請來信通知承辦人說明參與2場次講座，經中心核對確認出席，提供教學助理研習認證。若想參加傑出及優良TA遴選，參選資格為擁有教學助理研習認證，需額外參加本學期教發中心所辦理的一場講座。【築夢生如何取得認證章】1.活動14:50分開始辦理報到，於15:30分停止簽到，未簽到者無法蓋築夢踏實之研習認證章，且需全程參與研習會，敬請準時出席。2.本研習可提供築夢踏實之研習認證章，如需核章者請於活動結束後，於簽到桌櫃台人員出示填完問卷畫面始得核章，而且蓋認證章時，會確認是否有完成簽到，若造成排隊人潮，請耐心等候。依據築夢踏實助學金計畫規定(五、申請流程之第二步)，須當場改蓋章，無法事後補蓋認證章。(備註：研習活動集點卡，第1個蓋認證章時會發放，聽1場講座蓋1個認證章，需集滿4個認證章，才會再發第2張集點卡)活動議程：'}, {'publisher': '台科大教務處教學發展中心', 'title': '【伴讀輔導制度】伴讀員熱烈招募中，歡迎符合條件的同學踴躍申請~', 'url': 'https://ctld.ntust.edu.tw/p/426-1051-6.php?Lang=zh-tw', 'content': '學習伴讀制度為達到有效解決學生課業疑難、提升學習成效之目的，並鼓勵學業成績優異學生協助輔導同儕課業，特此本校訂定了「國立臺灣科技大學伴讀實施辦法」，歡迎各位同學利用此伴讀制度減輕在課業上所遇到的困難。提供伴讀之科目分為院系所專業課程及大學部一、二年級數理課程。伴讀申請流程：可參照伴讀申請作業流程(如下圖)欲申請伴讀之同學請繳交伴讀申請表至各所屬單位；欲申請協助輔導之伴讀員，請繳交伴讀員申請表至各所屬單位以利媒合作業。媒合成功後，伴讀員需每月需繳交伴讀教學紀錄表，伴讀學生需繳交回饋意見表給媒合單位留存。伴讀相關申請表下載網址：https://ctld.ntust.edu.tw/p/426-1051-18.php?Lang=zh-tw如有對伴讀制度有疑問之處，請聯繫伴讀承辦人：劉玉雯小姐、電話：(02)2730-1021\xa0、信箱：yuwen@mail.ntust.edu.tw'}, {'publisher': '台科大研究發展處計畫業務服務中心', 'title': '【NSTC計畫徵求】國科會徵件一覽表', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-110660,r1391.php?Lang=zh-tw', 'content': '國科會徵件一覽表【連結】【研發處網站/計畫徵求/國科會計畫徵求/國科會徵件一覽表https://www.rd.ntust.edu.tw/p/406-1055-81503,r83.php?Lang=zh-tw】The calls for the proposals by the National Science and Technology Council\xa0(NSTC) are summarized\xa0on the ORD website. The link is as follows:https://www.rd.ntust.edu.tw/p/406-1055-81503,r83.php?Lang=zh-tw'}, {'publisher': '台科大人事室', 'title': '113年3月人事服務簡訊已出刊，歡迎下載參閱。“Personnel Office Newsletter/ March 2024 Issue released:  Enjoy reading, stay informed!”', 'url': 'https://www.personnel.ntust.edu.tw/p/412-1066-8.php?Lang=zh-tw', 'content': '2024年人事快訊(03/01/2024出刊)人事快訊(02/01/2024出刊)人事快訊(01/01/2024出刊)2023年人事快訊(12/01/2023出刊)人事快訊(11/01/2023出刊)人事快訊(10/01/2023出刊)人事快訊(09/01/2023出刊)人事快訊(08/01/2023出刊)人事快訊(07/01/2023出刊)人事快訊(06/01/2023出刊)人事快訊(05/01/2023出刊)人事快訊(04/01/2023出刊)人事快訊(03/01/2023出刊)人事快訊(02/01/2023出刊)人事快訊(01/01/2023出刊)2022年人事快訊(12/01/2022出刊)人事快訊(11/01/2022出刊)人事快訊(10/01/2022出刊)人事快訊(09/01/2022出刊)人事快訊(08/01/2022出刊)人事快訊(07/01/2022出刊)人事快訊(06/01/2022出刊)人事快訊(05/01/2022出刊)人事快訊(04/01/2022出刊)人事快訊(03/01/2022出刊)人事快訊(02/01/2022出刊)人事快訊(01/01/2022出刊)2021年人事快訊(12/01/2021出刊)人事快訊(11/01/2021出刊)人事快訊(10/01/2021出刊)人事快訊(09/01/2021出刊)人事快訊(08/01/2021出刊)人事快訊(07/01/2021出刊)人事快訊(06/01/2021出刊)人事快訊(05/01/2021出刊)人事快訊(04/01/2021出刊)人事快訊(03/01/2021出刊)人事快訊(02/01/2021出刊)人事快訊(01/01/2021出刊)2020年人事快訊(12/01/2020出刊)人事快訊(11/01/2020出刊)人事快訊(10/01/2020出刊)人事快訊(09/01/2020出刊)人事快訊(08/01/2020出刊)人事快訊(07/01/2020出刊)人事快訊(06/01/2020出刊)人事快訊(05/01/2020出刊)人事快訊(04/01/2020出刊)人事快訊(03/01/2020出刊)人事快訊(02/01/2020出刊)人事快訊(01/01/2020出刊)2019年人事快訊(12/01/2019出刊)人事快訊(11/01/2019出刊)人事快訊(10/01/2019出刊)人事快訊(09/01/2019出刊)人事快訊(08/01/2019出刊)人事快訊(07/01/2019出刊)人事快訊(06/01/2019出刊)人事快訊(05/01/2019出刊)人事快訊(04/15/2019出刊)人事快訊(03/15/2019出刊)人事快訊(02/15/2019出刊)人事快訊(01/15/2019出刊)2018年人事快訊(12/15/2018出刊)人事快訊(11/15/2018出刊)人事快訊(10/15/2018出刊)人事快訊(09/15/2018出刊)人事快訊(08/15/2018出刊)人事快訊(07/15/2018出刊)人事快訊(06/15/2018出刊)人事快訊(05/15/2018出刊)人事快訊(04/16/2018出刊)人事快訊(03/15/2018出刊)人事快訊(02/13/2018出刊)人事快訊(01/15/2018出刊)2017年人事快訊(12/15/2017出刊)人事快訊(11/15/2017出刊)'}, {'publisher': '台科大體育室', 'title': '轉知 113年運動大會領隊會議開會通知', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122312,r1391.php?Lang=zh-tw', 'content': '說明：一、依據113年運動大會競賽規程舉行。二、領隊會議時間：3月1號中午12：30。三、領隊會議地點：S101（衛保組對面教室）四、請有報名參賽的系所派員參加。'}, {'publisher': '台科大體育室', 'title': '游泳池於3月9、10日辦理場地租借及運動績優學生單獨招生考試，暫停開放使用。 The swimming pool will be closed for venue rental and hosting individual recruitment exams for outstanding athletes on March 9th and 10th.', 'url': 'https://bulletin.ntust.edu.tw/p/406-1045-122309,r1391.php?Lang=zh-tw', 'content': 'The swimming pool will be closed for venue rental from 08:00 to 16:00 on 3/9.13:00~17:00辦理場地租借，暫停使用。The swimming pool will host individual recruitment exams for outstanding athletes from 08:00 to 12:00 on 3/10, and will be closed for venue rental from 13:00 to 17:00.'}]
if __name__ == "__main__":
    # 1. test case for bulletinraw 
    # 注意: 測試範例再上面
    data = [] 
    for row in test_case_bulletinraw:
        result = requests.post(url="http://127.0.0.1:8000/scraper/save_bulletin", json=row)
        print(result.text)
    # 2. test case for bulletinprocessed

    # 3. test case for label  

    # 4. test case for subscription S

    # 5. test case for bulletinraw 

    # 6. test case for test 





        