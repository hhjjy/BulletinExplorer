import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(service_name, log_dir="log", max_log_size=1000000, backup_count=5, log_level=logging.DEBUG):
    """
    配置日誌記錄器。

    @param service_name: 服務名稱，用於識別不同的日誌文件。
    @param log_dir: 日誌存儲的目錄。預設為 "log"。
    @param max_log_size: 日誌文件達到該大小時進行滾動（單位：字節）。預設為 1,000,000 字節。
    @param backup_count: 保留的備份文件數量。預設為 5。
    @param log_level: 日誌記錄的級別。預設為 DEBUG。
            DEBUG：最詳細的日誌級別。用於細粒度的事件描述，通常僅在開發或調試時使用。
            INFO：用於常規運行時的信息性消息，如程序啟動、運行狀態或處理進度。
            WARNING：表示潛在的問題，但不妨礙系統的正常運行。
            ERROR：表示較嚴重的問題，影響了某些功能的運行。
            CRITICAL：表示非常嚴重的問題，可能導致程序無法繼續運行。
    @return: 配置好的日誌記錄器。
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"{service_name}.log")
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
    handler.setFormatter(log_formatter)

    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger

if __name__ == "__main__":
    # 範例1:
    # 範例假設我是一個獨立的模組 xxx,下面這句話會自動在log文件夾下創立一個名為xxx_service.log的文件
    # 層級被設成debug 也就是說任何訊息再執行過程中都會印出到xxx.service.log
    logger = setup_logger("xxx_service", log_level=logging.DEBUG)
    logger.info("log config started")
    logger.debug("debug test")

    # 範例2:
    # 最簡單的範例舉例關於如何使用這個函數
    # from log_config import setup_logger
    # import logging
    # logger = setup_logger("xxx_service", log_level=logging.DEBUG)
    # def xxx():
    #     logger.info("xxx started")
    #     logger.error("xxx error ocurred! error is ... ")
    # xxx()


    # 範例＃：
    from logging.handlers import RotatingFileHandler
    import os
    import traceback
    logger = setup_logger("error_example", log_level=logging.DEBUG)

    try:
        result = 10/0
        logger.info("Division result: %s", result)
    except Exception as e:
        error_message = "Error occurred: {}".format(str(e))
        error_traceback = traceback.format_exc()
        logger.error("%s\nTraceback:\n%s", error_message, error_traceback)
