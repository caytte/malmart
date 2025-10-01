//丸Payチャージ用

function doGet() {
  var html = HtmlService.createHtmlOutputFromFile('login')
    .setTitle('丸PAY')
    .setSandboxMode(HtmlService.SandboxMode.IFRAME)
    .addMetaTag("viewport", "width=device-width, user-scalable=no, initial-scale=1.0")
    .setFaviconUrl('https://drive.google.com/uc?id=ファビコン用ID&.png');
  return html;
}

function processToppingUp(id, password, toppin_value) {
  // スプレッドシート2のデータを取得
  var spreadsheet2 = SpreadsheetApp.openById('SpreadSheetのID');
  var sheet2 = spreadsheet2.getSheetByName('Sheet2');
  var data2 = sheet2.getRange(1, 1, sheet2.getLastRow(), 1).getValues();
  var data2_2 = sheet2.getRange(1, 2, sheet2.getLastRow(), 1).getValues();
  
  // IDとパスワードの組み合わせがスプレッドシート2に存在する場合のみ処理を行う
  var credentialsExist = false;
  for (var i = 0; i < data2.length; i++) {
    if (data2[i][0] === id && data2_2[i][0] === password) {
      credentialsExist = true;
      break;
    }
  }
  
  if (credentialsExist) {
    // スプレッドシート1のデータを取得
    var spreadsheet1 = SpreadsheetApp.openById('SpreadSheetのID');
    var sheet1 = spreadsheet1.getSheetByName('Sheet1');
    var data1 = sheet1.getRange(1, 1, sheet1.getLastRow(), 2).getValues();
  
    //IDに合致するデータを検索して値を更新
    for (var j = 0; j < data1.length; j++) {
      if (data1[j][0] === id) {
        data1[j][1] = data1[j][1] + Number(toppin_value);
        sheet1.getRange(j + 1, 2).setValue(data1[j][1]);
        return 'TOPPING UP SUCCESSFULLY COMPLETED. ' +"(" + data1[j][1] + " yen left)";
      }
    }
    return 'REQUEST DENIED.(invalid ID)'; // IDが存在しない場合のメッセージ
  } else {
    return 'REQUEST DENIED.(invalid ID or PASSWORD)'; // IDとパスワードの組み合わせが存在しない場合のメッセージ
  }
}

function processCheck(id, password) {
  var spreadsheet2 = SpreadsheetApp.openById('SpreadSheetのID');
  var sheet2 = spreadsheet2.getSheetByName('Sheet2');
  var data2 = sheet2.getRange(1, 1, sheet2.getLastRow(), 1).getValues();
  var data2_2 = sheet2.getRange(1, 2, sheet2.getLastRow(), 1).getValues();
  
  // IDとパスワードの組み合わせがスプレッドシート2に存在する場合のみ処理を行う
  var credentialsExist = false;
  for (var i = 0; i < data2.length; i++) {
    if (data2[i][0] === id && data2_2[i][0] === password) {
      credentialsExist = true;
      break;
    }
  }

  if (credentialsExist) {
    // スプレッドシート1のデータを取得
    var spreadsheet1 = SpreadsheetApp.openById('SpreadSheetのID');
    var sheet1 = spreadsheet1.getSheetByName('Sheet1');
    var data1 = sheet1.getRange(1, 1, sheet1.getLastRow(), 2).getValues();

    // IDに合致するデータを検索して値を表示
    for (var j = 0; j < data1.length; j++) {
      if (data1[j][0] === id) {
        return data1[j][1] + " YEN LEFT ON YOUR ACCOUNT.";
      }
    }
    return 'REQUEST DENIED.(invalid ID)'; // IDが存在しない場合のメッセージ
    } else {
    return 'REQUEST DENIED.(invalid ID or PASSWORD)'; // IDとパスワードの組み合わせが存在しない場合のメッセージ
  }
}
