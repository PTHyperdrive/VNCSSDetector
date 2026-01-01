import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';

class EventModel {
  final String id;
  final String nodeId;
  final String nodeHostname;
  final String eventType;
  final String severity;
  final String message;
  final Map<String, dynamic>? data;
  final DateTime occurredAt;

  EventModel({
    required this.id,
    required this.nodeId,
    required this.nodeHostname,
    required this.eventType,
    required this.severity,
    required this.message,
    this.data,
    required this.occurredAt,
  });

  factory EventModel.fromJson(Map<String, dynamic> json) {
    return EventModel(
      id: json['id'].toString(),
      nodeId: json['nodeId'],
      nodeHostname: json['nodeHostname'] ?? 'Unknown',
      eventType: json['eventType'],
      severity: json['severity'],
      message: json['message'],
      data: json['data'],
      occurredAt: DateTime.parse(json['occurredAt']),
    );
  }
}

final eventsServiceProvider = Provider<EventsService>((ref) {
  return EventsService(ref.watch(dioProvider));
});

class EventsService {
  final Dio _dio;

  EventsService(this._dio);

  Future<List<EventModel>> getEvents({
    List<String>? severity,
    String? nodeId,
    DateTime? from,
    DateTime? to,
  }) async {
    final response = await _dio.get(
      ApiConstants.events,
      queryParameters: {
        if (severity != null) 'severity': severity.join(','),
        if (nodeId != null) 'nodeId': nodeId,
        if (from != null) 'from': from.toIso8601String(),
        if (to != null) 'to': to.toIso8601String(),
      },
    );
    
    final events = (response.data['data'] as List)
        .map((e) => EventModel.fromJson(e))
        .toList();
    return events;
  }
}

final eventsListProvider = FutureProvider<List<EventModel>>((ref) async {
  final service = ref.watch(eventsServiceProvider);
  return service.getEvents();
});
