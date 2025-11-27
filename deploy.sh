#!/bin/bash
REPOSITORY_URL="https://github.com/pickle5162/ME2025_Midterm3"
PROJECT_DIR="order-management-system"
VENV_NAME=".venv"
APP_FILE="app.py"
LOG_FILE="deployment.log"
PYTHON_BIN="python3"
install_missing_packages() {
    echo "-> 檢查並安裝缺失的 Python 套件..."
    if [ ! -d "$VENV_NAME" ]; then
        echo "❌ 虛擬環境 $VENV_NAME 不存在，無法安裝套件。" >> ../$LOG_FILE 2>&1
        exit 1
    fi
    source $VENV_NAME/bin/activate
    if pip install -r requirements.txt >> ../$LOG_FILE 2>&1; then
        echo "Python 套件安裝/更新完成。"
    else
        echo "Python 套件安裝失敗，請檢查 ../$LOG_FILE。"
        exit 1
    fi
    deactivate
}
start_application() {
    echo "-> 啟動 $APP_FILE..."
    killall -q $PYTHON_BIN 2>/dev/null
    if [ ! -d "$VENV_NAME" ]; then
        echo "❌ 虛擬環境 $VENV_NAME 不存在，無法啟動應用程式。"
        exit 1
    fi
    source $VENV_NAME/bin/activate
    nohup $PYTHON_BIN $APP_FILE > app.log 2>&1 &
    deactivate
    if [ $? -eq 0 ]; then
        echo "$APP_FILE 已在背景啟動。"
    else
        echo "$APP_FILE 啟動失敗，請檢查 app.log。"
        exit 1
    fi
}
echo "--- 專案部署腳本開始執行 ---"
touch $LOG_FILE
if [ ! -d "$PROJECT_DIR" ]; then
    echo "偵測到首次執行..."
    echo "-> 正在複製儲存庫到 $PROJECT_DIR..."
    git clone $REPOSITORY_URL $PROJECT_DIR >> $LOG_FILE 2>&1
    if [ $? -ne 0 ]; then
        echo "Git Clone 失敗，請檢查 URL 或連線設定。請查看 $LOG_FILE。"
        exit 1
    fi
    cd $PROJECT_DIR
    echo "-> 建立虛擬環境 $VENV_NAME..."
    $PYTHON_BIN -m venv $VENV_NAME >> ../$LOG_FILE 2>&1
    if [ $? -ne 0 ]; then
        echo "虛擬環境建立失敗，請確認已安裝 $PYTHON_BIN 及 venv 模組。"
        exit 1
    fi
    install_missing_packages

else
    echo "偵測到曾經執行..."
    cd $PROJECT_DIR
    echo "-> 執行 Git Pull 更新程式碼..."
    git pull >> ../$LOG_FILE 2>&1
    if [ $? -ne 0 ]; then
        echo "Git Pull 失敗，請查看 ../$LOG_FILE。但繼續執行..."
    else
        echo "程式碼更新完成。"
    fi

    install_missing_packages
fi
start_application

echo "--- 專案部署腳本執行完畢 ---"