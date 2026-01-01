import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';

class ServerStatus {
  final String status;
  final String version;
  final int uptimeSeconds;
  final String database;
  final String redis;
  final int nodesOnline;
  final int nodesTotal;

  ServerStatus({
    required this.status,
    required this.version,
    required this.uptimeSeconds,
    required this.database,
    required this.redis,
    required this.nodesOnline,
    required this.nodesTotal,
  });

  factory ServerStatus.fromJson(Map<String, dynamic> json) {
    return ServerStatus(
      status: json['status'] ?? 'unknown',
      version: json['version'] ?? '0.0.0',
      uptimeSeconds: json['uptimeSeconds'] ?? 0,
      database: json['database'] ?? 'unknown',
      redis: json['redis'] ?? 'unknown',
      nodesOnline: json['nodesOnline'] ?? 0,
      nodesTotal: json['nodesTotal'] ?? 0,
    );
  }

  bool get isHealthy => status == 'healthy';

  String get uptimeFormatted {
    final days = uptimeSeconds ~/ 86400;
    final hours = (uptimeSeconds % 86400) ~/ 3600;
    final minutes = (uptimeSeconds % 3600) ~/ 60;
    
    if (days > 0) return '${days}d ${hours}h';
    if (hours > 0) return '${hours}h ${minutes}m';
    return '${minutes}m';
  }
}

final dashboardServiceProvider = Provider<DashboardService>((ref) {
  return DashboardService(ref.watch(dioProvider));
});

class DashboardService {
  final Dio _dio;

  DashboardService(this._dio);

  Future<ServerStatus> getServerStatus() async {
    final response = await _dio.get(ApiConstants.status);
    return ServerStatus.fromJson(response.data['data']);
  }
}

final serverStatusProvider = FutureProvider<ServerStatus>((ref) async {
  final service = ref.watch(dashboardServiceProvider);
  return service.getServerStatus();
});
