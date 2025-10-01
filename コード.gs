//malpay_combined2.py用スクリプト
const MAGICWORD = 'CaLeNdAr'
function doPost(req) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  var total_balance = sheet.getRange(19, 2).getValue();
  return HtmlService.createHtmlOutput(MAGICWORD + JSON.stringify(total_balance) + MAGICWORD);
}

function doGet(e) {
  var value = e.parameter.data1;
  var sheet = SpreadsheetApp.getActiveSheet();

  if (value) {
    // 元の機能を保持：セルの値を取得し、110を引いて更新
    var cellValue = sheet.getRange(value).getValue();
    var updatedValue = cellValue - 110;  決済金額はここから変更
    sheet.getRange(value).setValue(updatedValue);
    Logger.log(updatedValue);

    // 新しい機能：更新後の値を返す
    return HtmlService.createHtmlOutput(MAGICWORD + JSON.stringify(updatedValue) + MAGICWORD);
  } else {
    return HtmlService.createHtmlOutput("Error: No cell specified");
  }
}
