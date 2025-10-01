//丸マート商品リクエストページ動作用スクリプト

function doGet() {
  var html = HtmlService.createHtmlOutputFromFile('requests')
    .setTitle('丸PAY')
    .setSandboxMode(HtmlService.SandboxMode.IFRAME)
    .addMetaTag("viewport", "width=device-width, user-scalable=no, initial-scale=1.0");
  return html;
}

function getAppUrl() {
  return ScriptApp.getService().getUrl();
}

function doGet(e) {
  let page = e.parameter.page;
  if (!page) {


    page = 'index';
  }
  var html = HtmlService.createTemplateFromFile(page).evaluate()
    .addMetaTag("viewport", "width=device-width, user-scalable=no, initial-scale=1.0");
  return html;
}

/*リクエストページ用*/
// App Scriptのサーバーサイド処理

/**
 * ウェブアプリとしてデプロイ時のURLを取得する関数
 */
function getAppUrl() {
  return ScriptApp.getService().getUrl();
}

/**
 * スプレッドシートからリクエスト数を取得する関数
 */
function getRequestCount(itemId) {
  try {
    const ss = SpreadsheetApp.openById('YOUR_ID');
    const sheet = ss.getSheetByName('Sheet1');
    
    // B列のitemId+1行目からデータを取得
    // B1からB10に在庫のリクエスト数を格納するという指定に基づく
    const cell = sheet.getRange('B' + (itemId + 1));
    const count = cell.getValue();
    
    // 数値でなければ0を返す
    return isNaN(count) ? 0 : count;
  } catch (e) {
    console.error('リクエスト数取得エラー: ' + e.toString());
    return 0;
  }
}

/**
 * リクエスト数を増加させる関数
 */
function incrementRequestCount(itemId) {
  try {
    const ss = SpreadsheetApp.openById('YOUR_ID');
    const sheet = ss.getSheetByName('Sheet1');
    
    // 現在の値を取得
    const cell = sheet.getRange('B' + (itemId + 1));
    let currentCount = cell.getValue();
    
    // 値が数値でなければ0として扱う
    currentCount = isNaN(currentCount) ? 0 : Number(currentCount);
    
    // カウントを増加して保存
    const newCount = currentCount + 1;
    cell.setValue(newCount);
    
    // 成功レスポンス
    return {
      success: true,
      newCount: newCount
    };
  } catch (e) {
    console.error('リクエスト数更新エラー: ' + e.toString());
    return {
      success: false,
      error: e.toString()
    };
  }
}

/**
 * すべての商品情報とリクエスト数を取得する関数
 * 将来の拡張用
 */
function getAllItems() {
  try {
    const ss = SpreadsheetApp.openById('YOUR_ID');
    const sheet = ss.getSheetByName('Sheet1');
    
    // A1:B10の範囲でデータを取得（商品名とリクエスト数）
    const data = sheet.getRange('A1:B100').getValues();
    
    const items = [];
    for (let i = 0; i < data.length; i++) {
      items.push({
        id: i,
        name: data[i][0] || `商品 ${i+1}`,
        requestCount: isNaN(data[i][1]) ? 0 : Number(data[i][1])
      });
    }
    
    return items;
  } catch (e) {
    console.error('商品情報取得エラー: ' + e.toString());
    return [];
  }
}

/**
 * リクエスト数のリセット（管理者用機能）
 */
function resetAllRequestCounts() {
  try {
    const ss = SpreadsheetApp.openById('YOUR_ID');
    const sheet = ss.getSheetByName('Sheet1');
    
    // B1:B100をすべて0にリセット
    const range = sheet.getRange('B1:B100');
    const values = Array(100).fill([0]);
    range.setValues(values);
    
    return { success: true };
  } catch (e) {
    console.error('リセットエラー: ' + e.toString());
    return { success: false, error: e.toString() };
  }
}
