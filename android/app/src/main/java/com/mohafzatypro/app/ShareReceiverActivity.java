package com.mohafzatypro.app;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import java.nio.charset.StandardCharsets;

public class ShareReceiverActivity extends Activity {
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        String text = getIntent().getStringExtra(Intent.EXTRA_TEXT);
        if (text == null || text.trim().isEmpty()) { finish(); return; }
        if (text.length() > 4000) text = text.substring(0, 4000);
        String encoded = Base64.encodeToString(text.getBytes(StandardCharsets.UTF_8), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
        Intent open = new Intent(Intent.ACTION_VIEW, Uri.parse(BuildConfig.WEB_BASE_URL + "/app/#incoming=" + encoded));
        open.setClassName(this, "com.google.androidbrowserhelper.trusted.LauncherActivity");
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        try { startActivity(open); } finally { finish(); }
    }
}
