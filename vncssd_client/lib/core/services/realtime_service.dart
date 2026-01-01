import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import '../constants/api_constants.dart';
import '../../features/auth/data/datasources/auth_local_datasource.dart';

// Node status model for realtime updates
class NodeStatusUpdate {
  final String id;
  final String hostname;
  final String status;
  final double? latitude;
  final double? longitude;
  final String? locationName;
  final DateTime? lastSeen;

  NodeStatusUpdate({
    required this.id,
    required this.hostname,
    required this.status,
    this.latitude,
    this.longitude,
    this.locationName,
    this.lastSeen,
  });

  factory NodeStatusUpdate.fromJson(Map<String, dynamic> json) {
    return NodeStatusUpdate(
      id: json['id'],
      hostname: json['hostname'],
      status: json['status'],
      latitude: json['latitude']?.toDouble(),
      longitude: json['longitude']?.toDouble(),
      locationName: json['locationName'],
      lastSeen:
          json['lastSeen'] != null ? DateTime.parse(json['lastSeen']) : null,
    );
  }

  bool get isOnline => status == 'ONLINE';
  bool get hasLocation => latitude != null && longitude != null;
}

// Status summary
class NodeStatusSummary {
  final int total;
  final int online;
  final int offline;
  final int degraded;
  final int pending;

  NodeStatusSummary({
    required this.total,
    required this.online,
    required this.offline,
    required this.degraded,
    required this.pending,
  });

  factory NodeStatusSummary.fromJson(Map<String, dynamic> json) {
    return NodeStatusSummary(
      total: json['total'] ?? 0,
      online: json['online'] ?? 0,
      offline: json['offline'] ?? 0,
      degraded: json['degraded'] ?? 0,
      pending: json['pending'] ?? 0,
    );
  }
}

// Realtime state
class RealtimeState {
  final bool isConnected;
  final List<NodeStatusUpdate> nodes;
  final NodeStatusSummary? summary;
  final DateTime? lastUpdate;

  const RealtimeState({
    this.isConnected = false,
    this.nodes = const [],
    this.summary,
    this.lastUpdate,
  });

  RealtimeState copyWith({
    bool? isConnected,
    List<NodeStatusUpdate>? nodes,
    NodeStatusSummary? summary,
    DateTime? lastUpdate,
  }) {
    return RealtimeState(
      isConnected: isConnected ?? this.isConnected,
      nodes: nodes ?? this.nodes,
      summary: summary ?? this.summary,
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }
}

// Realtime notifier
class RealtimeNotifier extends StateNotifier<RealtimeState> {
  io.Socket? _socket;
  final Ref _ref;
  String? _workspaceId;

  RealtimeNotifier(this._ref) : super(const RealtimeState());

  void connect(String workspaceId) {
    _workspaceId = workspaceId;

    // Disconnect existing socket
    _socket?.disconnect();

    // Create new socket connection
    final baseUrl = ApiConstants.baseUrl.replaceFirst('/api/v1', '');
    _socket = io.io(
      '$baseUrl/client',
      io.OptionBuilder()
          .setTransports(['websocket'])
          .setQuery({'workspaceId': workspaceId})
          .enableAutoConnect()
          .build(),
    );

    _socket!.onConnect((_) {
      debugPrint('[Realtime] Connected to server');
      state = state.copyWith(isConnected: true);
    });

    _socket!.onDisconnect((_) {
      debugPrint('[Realtime] Disconnected from server');
      state = state.copyWith(isConnected: false);
    });

    _socket!.on('node:status', (data) {
      debugPrint('[Realtime] Received node status update');
      _handleNodeStatus(data);
    });

    _socket!.onError((error) {
      debugPrint('[Realtime] Socket error: $error');
    });

    _socket!.connect();
  }

  void _handleNodeStatus(dynamic data) {
    try {
      final nodesJson = data['nodes'] as List<dynamic>;
      final summaryJson = data['summary'] as Map<String, dynamic>?;

      final nodes = nodesJson
          .map((n) => NodeStatusUpdate.fromJson(n as Map<String, dynamic>))
          .toList();

      final summary =
          summaryJson != null ? NodeStatusSummary.fromJson(summaryJson) : null;

      state = state.copyWith(
        nodes: nodes,
        summary: summary,
        lastUpdate: DateTime.now(),
      );
    } catch (e) {
      debugPrint('[Realtime] Failed to parse node status: $e');
    }
  }

  void disconnect() {
    _socket?.disconnect();
    _socket = null;
    state = const RealtimeState();
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}

// Provider
final realtimeProvider =
    StateNotifierProvider<RealtimeNotifier, RealtimeState>((ref) {
  return RealtimeNotifier(ref);
});
