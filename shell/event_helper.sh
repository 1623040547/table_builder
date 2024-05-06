#!/bin/bash -l

source /Users/qingdu/.zshrc

PROJECT_PATH="/Users/qingdu/StudioProjects/${APP_NAME}_build"
EVENT_HELPER_PATH="/Users/qingdu/Desktop/event_helper"
JSON_FILE=/Users/qingdu/Desktop/event_helper/shell/app_config.json

echo "APP_NAME: ${APP_NAME}"



CHAT_ROBOT_API=$(cat $JSON_FILE | jq -r ".$APP_NAME.chat_robot_api")
LINK=$(cat $JSON_FILE | jq -r ".$APP_NAME.link")
echo "CHAT_ROBOT_API: ${CHAT_ROBOT_API}"

cd "${PROJECT_PATH}" ||exit

echo "------------------ 更新代码..."
git reset --hard
git checkout -f dev
git pull
git submodule init
git submodule update
git checkout -f dev

cd "${PROJECT_PATH}"/plugin/analyzer_helper || exit

fvm use "$FLUTTER_VERSION"
flutter clean
flutter pub get

echo "------------------ 开始获取打点数据"
echo "$EVENT_HELPER_PATH/data/$APP_NAME"
flutter test  --dart-define="FILE_PATH=$EVENT_HELPER_PATH/data/$APP_NAME" "${PROJECT_PATH}"/plugin/analyzer_helper/test/event_to_json.dart


cd $EVENT_HELPER_PATH || exit
echo "------------------ 开始更新飞书电子表格"

/usr/bin/python3 $EVENT_HELPER_PATH/main.py "$APP_NAME"
echo "------------------ 消息同步至群"
if [ "$APP_ROBOT_NOTIFICATION" = false ]; then
  exit 0
fi

AT_USERS_MSG="" #at指定的人

values=(${AT_USERS//,/ })
for value in ${values[@]}; do
  array=(${value//=/ })
  AT_USERS_MSG="${AT_USERS_MSG}<at id='"${array[1]}"'></at>"
done

curl -X POST -H "Content-Type: application/json" \
  -d '{ 
            "msg_type": "interactive", 
            "card": { 
                "elements": [
                    { 
                    "tag": "div", 
                    "text": {
                        "content": "'"$AT_USERS_MSG"'",
                        "tag": "lark_md"
                    }},
                    { 
                    "tag": "div", 
                    "text": {
                        "content": "'"$LINK"'",
                        "tag": "lark_md"
                    }},
                    { 
                    "tag": "div", 
                    "text": {
                        "content": "更新内容 \n'"$APP_UPDATE_DESCRIPTION"'",
                        "tag": "lark_md"
                    }}
                ]
            }
        }' \
  "$CHAT_ROBOT_API"