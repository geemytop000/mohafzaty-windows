// نسخة Windows: بتفتح برنامج محفظتي برو المنشور على الإنترنت في نافذة مستقلة.
// غيّر APP_URL لرابط موقعك بعد النشر (مثال: https://mohafzaty.netlify.app/app/)
const APP_URL = 'https://mohafzatypro.com/app/';
const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
function createWindow() {
  const win = new BrowserWindow({ width: 1200, height: 820, minWidth: 380, minHeight: 600, autoHideMenuBar: true, title: 'محفظتي برو', webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true } });
  Menu.setApplicationMenu(null);
  win.loadURL(APP_URL);
  win.webContents.on('did-fail-load', (e, code, desc, url, isMain) => {
    if (!isMain) return;
    win.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent('<html dir="rtl" style="font-family:Segoe UI,Tahoma;text-align:center;padding:60px;background:#EDE7D8;color:#202B22"><h2>مفيش اتصال بالإنترنت</h2><p>اتأكد من الاتصال وبعدين اضغط الزر.</p><button onclick="location.href=\'' + APP_URL + '\'" style="padding:12px 28px;font-size:16px;border:0;border-radius:12px;background:#2f4a39;color:#fff;cursor:pointer">إعادة المحاولة</button></html>'));
  });
  // الروابط الخارجية تفتح في المتصفح العادي
  win.webContents.setWindowOpenHandler(({ url }) => { if (!url.startsWith(APP_URL.split('/app/')[0])) shell.openExternal(url); return { action: 'deny' }; });
}
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit(); else { app.whenReady().then(createWindow); app.on('window-all-closed', () => app.quit()); }
