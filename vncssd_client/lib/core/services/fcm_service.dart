import 'dart:io';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../features/notifications/data/notifications_service.dart';

// Global background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  debugPrint('[FCM] Background message: ${message.messageId}');
}

final fcmServiceProvider = Provider<FcmService>((ref) {
  return FcmService(ref);
});

class FcmService {
  final Ref _ref;
  static GoRouter? _router;

  FcmService(this._ref);

  static void setRouter(GoRouter router) {
    _router = router;
  }

  Future<void> initialize() async {
    final messaging = FirebaseMessaging.instance;

    // Request permission
    final settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus != AuthorizationStatus.authorized) {
      debugPrint('[FCM] Permission denied');
      return;
    }

    // Get FCM token
    final token = await messaging.getToken();
    if (token != null) {
      await _registerToken(token);
    }

    // Listen for token refresh
    messaging.onTokenRefresh.listen(_registerToken);

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Handle notification tap when app was in background
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

    // Check if app was opened from a notification
    final initialMessage = await messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationTap(initialMessage);
    }
  }

  Future<void> _registerToken(String token) async {
    try {
      final deviceInfo = Platform.isAndroid ? 'Android' : 'iOS';
      final service = _ref.read(notificationsServiceProvider);
      await service.registerDevice(token, deviceInfo);
      debugPrint('[FCM] Token registered');
    } catch (e) {
      debugPrint('[FCM] Failed to register token: $e');
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    debugPrint('[FCM] Foreground message: ${message.notification?.title}');

    // You can show a local notification or snackbar here
    // For now, we just invalidate the notifications provider to refresh
    _ref.invalidate(notificationsListProvider);
  }

  void _handleNotificationTap(RemoteMessage message) {
    debugPrint('[FCM] Notification tap: ${message.data}');

    final screen = message.data['screen'];
    final nodeId = message.data['node_id'];

    if (_router != null && screen != null) {
      if (screen == 'NODE_DETAIL' && nodeId != null) {
        _router!.push('/nodes/$nodeId');
      } else if (screen == 'EVENTS') {
        _router!.go('/events');
      } else if (screen == 'NOTIFICATIONS') {
        _router!.go('/notifications');
      }
    }
  }
}
