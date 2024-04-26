import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { DateRangePicker } from 'rsuite';
import 'rsuite/DateRangePicker/styles/index.css';
import isAfter from 'date-fns/isAfter';
import './Label.css';
const env = import.meta.env;

function Label() {
    const HOST = env.VITE_DEV_OR_MAIN === 'dev' ? env.VITE_DEV_HOST : env.VITE_APP_MAIN_HOST;
    const PORT = env.VITE_DEV_OR_MAIN === 'dev' ? env.VITE_DEV_PORT : env.VITE_MAIN_PORT;
    const apiUrl = `http://${HOST}:${PORT}/api/frontend/get_processed_table`;

    const location = useLocation();
    useEffect(() => {
        document.title = "Label Page";
    }, [location]);

    const [Data, setData] = useState([]); // 顯示在頁面上的資料
    const [KeywordsSearch, setKeywordsSearch] = useState(''); // 儲存搜尋內文關鍵字欄位的資料
    const [DateRange, setDateRange] = useState([null, null]); // 儲存搜尋日期範圍
    const [SelecteOption, setSelecteOption] = useState(''); // 搜尋位置下拉式選單資料

    const [LabelList, setLabelList] = useState("餐點");

    // 定義選項列表
    const publisher_options = ['ALL', '發布單位', '內文'];
    const label_list_options = ['餐點', '自我認識', '考試', '學習技能', '體育活動', '學校舉辦活動',
                                 '英文學分', '付費或繳款', '社會實踐', '機車車位', '獎助學金', '座談會',
                                 '演講', '工作坊', '選課時間', '行事曆發布', '停水', '停電',
                                 '斷網', '宿舍訊息', '禮卷', '抽獎', '實習機會'];
    // 處理標籤選單變更
    const handleLabelList = (label) => {
        setLabelList(label);
    };

    // 變更標籤選單
    useEffect(() => {
        handleDataSearchResult();
    }, [LabelList]);

    // 處理選項變更事件
    const handleSelecteOption = (event) => {
        setSelecteOption(event.target.value);
    };

    // Search 欄位
    const handleDataSearch = (e) => {
        setKeywordsSearch(e.target.value);
    };

    // 將搜尋欄的日期格式轉換為 'yyyy-MM-dd'
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Result Button 按下後更動顯示資料 Data
    const handleDataSearchResult = async () => {
        let jsonData;
        let formattedStartDate = '';
        let formattedEndDate = '';

        if (DateRange && DateRange[0] && DateRange[1]) {
            formattedStartDate = formatDate(DateRange[0]);
            formattedEndDate = formatDate(DateRange[1]);
        }

        const requestData = {
            search_label: LabelList,
            publisher: null,
            keywords: KeywordsSearch || null,
            start_date: formattedStartDate || null,
            end_date: formattedEndDate || null,
        };

        jsonData = await FetchAPI(requestData);

        if (jsonData.length === 0) {
            alert('查無資料');
            return;
        }

        setData(jsonData);
    };

    // 儲存搜尋日期範圍
    const handleChange = (value) => {
        setDateRange(value);
    };

    // 更改表格的時間欄位
    const formatDateTime = (dateTimeString) => {
        const dateTime = new Date(dateTimeString);
        const year = dateTime.getFullYear();
        const month = String(dateTime.getMonth() + 1).padStart(2, '0');
        const day = String(dateTime.getDate()).padStart(2, '0');
        const hour = String(dateTime.getHours()).padStart(2, '0');
        const minute = String(dateTime.getMinutes()).padStart(2, '0');
        const second = String(dateTime.getSeconds()).padStart(2, '0');

        const formattedDateTime = `${year}-${month}-${day}\n${hour}:${minute}:${second}`;
        return formattedDateTime;
    };

    // 抓取後端 API 資料
    const FetchAPI = async (requestData) => {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const jsonData = await response.json();
            return jsonData;
        } catch (error) {
            // console.error('Error fetching data:', error);
            return [];
        }
    };

    // 初始頁面
    useEffect(() => {
        const fetchData = async () => {
            try {
                const requestData = {
                    search_label: "餐點"
                };

                const jsonData = await FetchAPI(requestData);
                setData(jsonData);
            } catch (error) {
                // console.error('Error fetching data:', error);
            }
        };
    }, []);

    return (
        <div>
            <div className="navigation">
                <div className="NTUST">NTUST</div>
                <div className="searh">
                    <label htmlFor="SelecteOption">搜尋位置:</label>
                    <select value={SelecteOption} onChange={handleSelecteOption} className="SelecteOption">
                        {publisher_options.map((option, index) => (
                            <option key={index} value={option}>
                                {option}
                            </option>
                        ))}
                    </select>

                    <label htmlFor="KeywordsSearch">關鍵字:</label>
                    <input
                        type="text"
                        className="KeywordsSearch"
                        value={KeywordsSearch}
                        onChange={handleDataSearch}
                    />

                    <label htmlFor="DateRange">日期:</label>
                    <DateRangePicker
                        className="DateRange"
                        value={DateRange}
                        onChange={handleChange}
                        format="yyyy-MM-dd"
                        shouldDisableDate={date => isAfter(date, new Date())}
                    />

                    <button className="button_search" onClick={handleDataSearchResult}>搜尋</button>
                </div>
            </div>

            <div className='bulletin_label'>
                <ul className="label_list">
                    {label_list_options.map((option, index) => (
                        <li
                            onClick={() => handleLabelList(option)}
                            key={index}
                            style={{ color: LabelList === option ? 'blue' : 'initial' }}
                        >
                            {option}
                        </li>
                    ))}
                </ul>

                <div className="table_container">
                    <table>
                        <thead>
                            <tr>
                                <th className="th_number">排序</th>
                                <th className="th_addtime">日期</th>
                                <th className="th_publisher">發布單位</th>
                                <th className="th_title">主旨</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Data.map((item, index) => (
                                <React.Fragment key={index}>
                                    <tr className='tr_context'>
                                        <td>{item.rawid}</td>
                                        <td>{formatDateTime(item.addtime)}</td>
                                        <td>{item.publisher}</td>
                                        <td>
                                            <a href={item.url} target="_blank" rel="noopener noreferrer">
                                                {item.title}
                                            </a>
                                        </td>
                                    </tr>
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Label;