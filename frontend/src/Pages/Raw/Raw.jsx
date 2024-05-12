import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { DateRangePicker } from 'rsuite';
import 'rsuite/DateRangePicker/styles/index.css';
import isAfter from 'date-fns/isAfter';
import './Raw.css';
const env = import.meta.env;

function Raw() {
    const HOST = env.VITE_DEV_OR_MAIN === 'dev' ? env.VITE_DEV_HOST : env.VITE_MAIN_HOST;
    const PORT = env.VITE_DEV_OR_MAIN === 'dev' ? env.VITE_DEV_PORT : env.VITE_MAIN_PORT;
    const apiUrl = `http://${HOST}:${PORT}/frontend/get_bulletin`;

    const location = useLocation();
    useEffect(() => {
        document.title = "Raw Page";
    }, [location]);

    const [Data, setData] = useState([]); // 顯示在頁面上的資料
    const [KeywordsSearch, setKeywordsSearch] = useState(''); // 儲存搜尋內文關鍵字欄位的資料
    const [ShowContext, setShowContext] = useState([]); // 顯示表格的內文欄位
    const [DataTotalNumber, setDataTotalNumber] = useState(2); // 儲存搜尋比數
    const [DateRange, setDateRange] = useState([null, null]); // 儲存搜尋日期範圍
    const [SelecteOption, setSelecteOption] = useState(''); // 下拉式選單資料

    // 定義選項列表
    const options = ['ALL', '發布單位', '內文'];

    // 處理選項變更事件
    const handleSelecteOption = (event) => {
        setSelecteOption(event.target.value);
    };

    // Search 欄位
    const handleDataSearch = (e) => {
        setKeywordsSearch(e.target.value);
    };

    // 每次抓取幾筆資料
    const handleDataTotalNumber = (e) => {
        const value = parseInt(e.target.value, 10);
        setDataTotalNumber(value);
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
        if (DataTotalNumber === 0 || DataTotalNumber > 200) {
            alert('數量需在 1 ~ 200 之間');
            return;
        }

        let jsonData;
        let formattedStartDate = '';
        let formattedEndDate = '';

        if (DateRange && DateRange[0] && DateRange[1]) {
            formattedStartDate = formatDate(DateRange[0]);
            formattedEndDate = formatDate(DateRange[1]);
        }

        const requestData = {
            publisher: null,
            keywords: KeywordsSearch || null,
            start_date: formattedStartDate || null,
            end_date: formattedEndDate || null,
            numbers: DataTotalNumber
        };

        jsonData = await FetchAPI(requestData);

        if (jsonData.length === 0) {
            alert('查無資料');
            return;
        }

        setData(jsonData);
        setShowContext([]);
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

    // 收起/展開 表格的內文欄位
    const handleShowContext = (index) => {
        const newShowContext = [...ShowContext];
        if (newShowContext.includes(index)) { // 如果已經展開，則收起
            const indexToRemove = newShowContext.indexOf(index);
            newShowContext.splice(indexToRemove, 1);
        } else { // 如果尚未展開，則展開
            newShowContext.push(index);
        }
        setShowContext(newShowContext);
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
                    numbers: 2
                };

                const jsonData = await FetchAPI(requestData);
                setData(jsonData);
            } catch (error) {
                // console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    return (
        <div>
            <div className="navigation">
                <div className="NTUST">NTUST</div>
                <div className="searh">
                    <label htmlFor="SelecteOption">搜尋位置:</label>
                    <select value={SelecteOption} onChange={handleSelecteOption} className="SelecteOption">
                        {options.map((option, index) => (
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

                    <label htmlFor="DataTotalNumber">數量:</label>
                    <input
                        type="number"
                        className="DataTotalNumber"
                        value={DataTotalNumber}
                        onChange={handleDataTotalNumber}
                    />

                    <button className="button_search" onClick={handleDataSearchResult}>搜尋</button>
                </div>
            </div>

            <table className='raw_table'>
                <thead className='raw_thead'>
                    <tr>
                        <th className="raw_th_number">排序</th>
                        <th className="raw_th_addtime">日期</th>
                        <th className="raw_th_publisher">發布單位</th>
                        <th className="raw_th_title">主旨</th>
                    </tr>
                </thead>
                <tbody className='raw_tbody'>
                    {Data.map((item, index) => (
                        <React.Fragment key={index}>
                            <tr>
                                <td>{item.rawid}</td>
                                <td>{formatDateTime(item.addtime)}</td>
                                <td>{item.publisher}</td>
                                <td>
                                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                                        {item.title}
                                    </a>
                                    <button className="button_context" onClick={() => handleShowContext(index)}>
                                        {ShowContext.includes(index) ? '收起內文' : '展開內文'}
                                    </button>
                                </td>
                            </tr>
                            {ShowContext.includes(index) && (
                                <tr>
                                    <td></td>
                                    <td>內文</td>
                                    <td colSpan={2}>
                                        {item.content}
                                    </td>
                                </tr>
                            )}
                        </React.Fragment>
                    ))}
                </tbody>
            </table>

        </div>
    );
};

export default Raw;