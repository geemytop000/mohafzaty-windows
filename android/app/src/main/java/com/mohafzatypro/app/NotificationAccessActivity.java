package com.mohafzatypro.app;

import android.Manifest;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
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
            Toast.makeText(this, "فعّل محفظتي برو من قائمة الوصول للإشعارات ثم ارجع للتطبيق", Toast.LENGTH_LONG).show();
            finish();
        }
    }

    private boolean hasListenerAccess() {
        String enabled = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_NOTIFICATION_LISTENERS);
        String component = new ComponentName(this, TransferNotificationListener.class).flattenToString();
        return enabled != null && (":" + enabled + ":").contains(":" + component + ":");
    }

    private void openListenerSettings() {
        try {
            waitingForListenerSettings = true;
            startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
        } catch (Exception error) {
            waitingForListenerSettings = false;
            Toast.makeText(this, "افتح إعدادات أندرويد ثم الوصول للإشعارات وفعّل محفظتي برو", Toast.LENGTH_LONG).show();
            finish();
        }
    }

    private void requestNotificationPermissionOrFinish() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[] { Manifest.permission.POST_NOTIFICATIONS }, REQUEST_NOTIFICATIONS);
        } else {
            Toast.makeText(this, "تم تفعيل وصول محفظتي برو للإشعارات", Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQUEST_NOTIFICATIONS) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            Toast.makeText(this, "تم تفعيل التنبيهات", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "وصول الإشعارات مفعّل، لكن اسمح لمحفظتي برو بعرض التنبيهات لتصلك المراجعات", Toast.LENGTH_LONG).show();
        }
        finish();
    }
}
