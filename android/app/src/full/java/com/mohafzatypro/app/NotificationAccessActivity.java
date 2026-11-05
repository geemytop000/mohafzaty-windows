package com.mohafzatypro.app;

import android.Manifest;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Toast;

public class NotificationAccessActivity extends Activity {
    private static final int REQUEST_NOTIFICATIONS = 2417;
    private boolean waitingForListenerSettings = false;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        if (hasListenerAccess()) {
            requestNotificationPermissionOrFinish();
        } else {
            openListenerSettings();
        }
    }

    @Override protected void onResume() {
        super.onResume();
        if (!waitingForListenerSettings) return;
        waitingForListenerSettings = false;
        if (hasListenerAccess()) {
            requestNotificationPermissionOrFinish();
        } else {
            Toast.makeText(this, "لم يتم تفعيل وصول الإشعارات بعد", Toast.LENGTH_LONG).show();
            returnToApp();
        }
    }

    private boolean hasListenerAccess() {
        String enabled = Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");
        String component = new ComponentName(this, TransferNotificationListener.class).flattenToString();
        return enabled != null && (":" + enabled + ":").contains(":" + component + ":");
    }

    private void openListenerSettings() {
        try {
            waitingForListenerSettings = true;
            startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
        } catch (Exception error) {
            waitingForListenerSettings = false;
            Toast.makeText(this, "افتح إعدادات أندرويد ثم الوصول إلى الإشعارات وفعّل محفظتي برو", Toast.LENGTH_LONG).show();
            returnToApp();
        }
    }

    private void requestNotificationPermissionOrFinish() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[] { Manifest.permission.POST_NOTIFICATIONS }, REQUEST_NOTIFICATIONS);
        } else {
            returnToApp();
        }
    }

    private void returnToApp() {
        boolean listenerEnabled = hasListenerAccess();
        boolean appNotificationsEnabled = Build.VERSION.SDK_INT < 33
                || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED;
        String url = BuildConfig.WEB_BASE_URL + "/app/?section=review"
                + "&notificationAccess=" + (listenerEnabled ? "on" : "off")
                + "&appNotifications=" + (appNotificationsEnabled ? "on" : "off");
        Intent open = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
        open.setClassName(this, "com.google.androidbrowserhelper.trusted.LauncherActivity");
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        try {
            startActivity(open);
        } catch (Exception error) {
            Toast.makeText(this, "ارجع لمحفظتي برو لمراجعة حالة الإشعارات", Toast.LENGTH_LONG).show();
        }
        finish();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_NOTIFICATIONS) returnToApp();
    }
}
