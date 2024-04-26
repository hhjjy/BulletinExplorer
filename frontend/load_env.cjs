// node load_env.cjs 用來手動更新環境變數

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// 定義 .env 檔案路徑和新 .env 檔案路徑
const parentDir = path.resolve(__dirname, '../');
const envFilePath = path.join(parentDir, '.env');
const newEnvFilePath = path.join(parentDir, 'frontend', '.env');

// 更新 .env 檔案的環境變數格式並保存到新 .env 檔案中
function updateEnvFile() {
  fs.readFile(envFilePath, 'utf8', (err, data) => {
    if (err) {
      console.error('讀取 .env 檔案時發生錯誤:', err);
      return;
    }

    // 新的 .env 檔案中的變數名稱對應
    const updatedEnvVariables = {
      'DEV_OR_MAIN': 'VITE_DEV_OR_MAIN',
      'API_MAIN_HOST': 'VITE_MAIN_HOST',
      'API_MAIN_PORT': 'VITE_MAIN_PORT',
      'API_DEV_HOST': 'VITE_DEV_HOST',
      'API_DEV_PORT': 'VITE_DEV_PORT',
    };

    // 將原始 .env 檔案中的變數格式轉換為新的格式
    let updatedEnvData = '';
    const lines = data.split('\n');
    for (const line of lines) {
      for (const originalVar in updatedEnvVariables) {
        if (line.startsWith(`${originalVar}=`)) {
          updatedEnvData += line.replace(`${originalVar}=`, `${updatedEnvVariables[originalVar]}=`) + '\n';
          break;
        }
      }
    }

    // 將更新後的環境變數保存到新的 .env 檔案中
    fs.writeFile(newEnvFilePath, updatedEnvData, (err) => {
      if (err) {
        console.error('寫入新 .env 檔案時發生錯誤:', err);
        return;
      }
      console.log('新的 .env 檔案已成功保存。');
    });
  });
}

// 監聽 .env 檔案的變化並執行相應操作
fs.watch(envFilePath, (eventType, filename) => {
  if (eventType === 'change') {
    console.log(`檔案 ${filename} 被修改了。`);

    // 執行相應的程式
    exec('node load_env.cjs', (error, stdout, stderr) => {
      if (error) {
        console.error(`執行指令時出錯: ${error}`);
        return;
      }
      console.log(`stdout: ${stdout}`);
      console.error(`stderr: ${stderr}`);
    });
  }
});

// 初始化時更新一次
updateEnvFile();
