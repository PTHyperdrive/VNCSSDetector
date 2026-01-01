import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';

class NotificationModel {
  final String id;
  final String title;
  final String body;
  final String type;
  final Map<String, dynamic>? data;
  final bool isRead;
  final DateTime sentAt;

  NotificationModel({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    this.data,
    required this.isRead,
    required this.sentAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'].toString(),
      title: json['title'],
      body: json['body'],
      type: json['type'],
      data: json['data'],
      isRead: json['isRead'] ?? false,
      sentAt: DateTime.parse(json['sentAt']),
    );
  }

  String? get targetScreen => data?['screen'];
  String? get targetNodeId => data?['node_id'];
}

final notificationsServiceProvider = Provider<NotificationsService>((ref) {
  return NotificationsService(ref.watch(dioProvider));
});

class NotificationsService {
  final Dio _dio;

  NotificationsService(this._dio);

  Future<void> registerDevice(String fcmToken, String? deviceInfo) async {
    await _dio.post(
      ApiConstants.deviceTokens,
      data: {
        'fcmToken': fcmToken,
        if (deviceInfo != null) 'deviceInfo': deviceInfo,
      },
    );
  }

  Future<List<NotificationModel>> getNotifications({bool? isRead}) async {
    final response = await _dio.get(
      ApiConstants.notifications,
      queryParameters: {
        if (isRead != null) 'isRead': isRead,
      },
    );
    
    final notifications = (response.data['data']['notifications'] as List)
        .map((n) => NotificationModel.fromJson(n))
        .toList();
    return notifications;
  }

  Future<void> markAsRead(String id) async {
    await _dio.patch(ApiConstants.notificationRead(id));
  }
}

final notificationsListProvider = FutureProvider<List<NotificationModel>>((ref) async {
  final service = ref.watch(notificationsServiceProvider);
  return service.getNotifications();
});
