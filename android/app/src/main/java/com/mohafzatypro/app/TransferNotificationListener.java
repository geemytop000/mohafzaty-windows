package com.mohafzatypro.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.util.Base64;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;

public class TransferNotificationListener extends NotificationListenerService {
    private static final String CHANNEL = "transfer_review";
    private String lastFingerprint = "";
    private long lastAlertAt = 0;
    private static final Pattern NUMBER = Pattern.compile("[0-9٠-٩۰-۹][0-9٠-٩۰-۹,.٬٫]{1,}");
    private static final Pattern SIGNAL = Pattern.compile("(تحويل|استلام|استلمت|مبلغ|إيداع|ايداع|سحب|رصيد|خصم|إضافة|اضافة|جنيه|ج\\.م|transfer|received|deposit|withdraw|credited|debited|egp)", Pattern.CASE_INSENSITIVE);

    @Override public void onNotificationPosted(StatusBarNotification sbn) {
        if (sbn == null || sbn.getNotification() == null || sbn.isOngoing()) return;
        CharSequence title = sbn.getNotification().extras.getCharSequence(Notification.EXTRA_TITLE);
        CharSequence body = sbn.getNotification().extras.getCharSequence(Notification.EXTRA_BIG_TEXT);
        if (body == null) body = sbn.getNotification().extras.getCharSequence(Notification.EXTRA_TEXT);
        String text = ((title == null ? "" : title.toString() + ". ") + (body == null ? "" : body.toString())).trim();
        if (text.length() < 10 || text.length() > 4000 || !SIGNAL.matcher(text).find() || !NUMBER.matcher(text).find()) return;
        String fingerprint = sbn.getKey() + "|" + text;
        long now = System.currentTimeMillis();
        if (fingerprint.equals(lastFingerprint) && now - lastAlertAt < 60000) return;
        lastFingerprint = fingerprint;
        lastAlertAt = now;
        postReviewNotification(text);
    }

    private void postReviewNotification(String text) {
        NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager == null) return;
        if (Build.VERSION.SDK_INT >= 26) manager.createNotificationChannel(new NotificationChannel(CHANNEL, "مراجعة التحويلات", NotificationManager.IMPORTANCE_DEFAULT));
        String encoded = Base64.encodeToString(text.getBytes(StandardCharsets.UTF_8), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
        Intent open = new Intent(Intent.ACTION_VIEW, Uri.parse(BuildConfig.WEB_BASE_URL + "/app/#incoming=" + encoded));
        open.setClassName(this, "com.google.androidbrowserhelper.trusted.LauncherActivity");
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        PendingIntent pending = PendingIntent.getActivity(this, (int) (System.currentTimeMillis() & 0x7fffffff), open, flags);
        Notification.Builder builder = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(this, CHANNEL) : new Notification.Builder(this);
        builder.setSmallIcon(com.mohafzatypro.app.R.drawable.ic_stat_wallet)
            .setContentTitle("تحويل محتمل — راجعه في محفظتي برو")
            .setContentText("اضغط لمراجعة المبلغ والنوع قبل تسجيله")
            .setContentIntent(pending).setAutoCancel(true);
        try { manager.notify((int) (System.currentTimeMillis() & 0x7fffffff), builder.build()); } catch (SecurityException ignored) { }
    }
}
