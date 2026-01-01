import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';

class NodeModel {
  final String id;
  final String hostname;
  final String? ipAddress;
  final String status;
  final List<String> tags;
  final DateTime? lastSeen;
  final String? detectorStatus;
  final double? cpuUsage;
  final double? memoryUsage;
  final String? os;
  final String? version;
  final List<String>? capabilities;
  final Map<String, dynamic>? metadata;

  NodeModel({
    required this.id,
    required this.hostname,
    this.ipAddress,
    required this.status,
    required this.tags,
    this.lastSeen,
    this.detectorStatus,
    this.cpuUsage,
    this.memoryUsage,
    this.os,
    this.version,
    this.capabilities,
    this.metadata,
  });

  factory NodeModel.fromJson(Map<String, dynamic> json) {
    return NodeModel(
      id: json['id'],
      hostname: json['hostname'],
      ipAddress: json['ipAddress'],
      status: json['status'],
      tags: List<String>.from(json['tags'] ?? []),
      lastSeen: json['lastSeen'] != null ? DateTime.parse(json['lastSeen']) : null,
      detectorStatus: json['detectorStatus'],
      cpuUsage: json['cpuUsage']?.toDouble(),
      memoryUsage: json['memoryUsage']?.toDouble(),
      os: json['os'],
      version: json['version'],
      capabilities: json['capabilities'] != null 
          ? List<String>.from(json['capabilities']) 
          : null,
      metadata: json['metadata'],
    );
  }

  bool get isOnline => status == 'ONLINE';
}

class TopologyData {
  final TopologySummary summary;
  final List<TagCount> byTag;

  TopologyData({required this.summary, required this.byTag});

  factory TopologyData.fromJson(Map<String, dynamic> json) {
    return TopologyData(
      summary: TopologySummary.fromJson(json['summary']),
      byTag: (json['byTag'] as List)
          .map((t) => TagCount.fromJson(t))
          .toList(),
    );
  }
}

class TopologySummary {
  final int total;
  final int online;
  final int offline;
  final int degraded;

  TopologySummary({
    required this.total,
    required this.online,
    required this.offline,
    required this.degraded,
  });

  factory TopologySummary.fromJson(Map<String, dynamic> json) {
    return TopologySummary(
      total: json['total'] ?? 0,
      online: json['online'] ?? 0,
      offline: json['offline'] ?? 0,
      degraded: json['degraded'] ?? 0,
    );
  }
}

class TagCount {
  final String tag;
  final int total;
  final int online;

  TagCount({required this.tag, required this.total, required this.online});

  factory TagCount.fromJson(Map<String, dynamic> json) {
    return TagCount(
      tag: json['tag'],
      total: json['total'],
      online: json['online'],
    );
  }
}

final nodesServiceProvider = Provider<NodesService>((ref) {
  return NodesService(ref.watch(dioProvider));
});

class NodesService {
  final Dio _dio;

  NodesService(this._dio);

  Future<List<NodeModel>> getNodes({String? status, String? tag}) async {
    final response = await _dio.get(
      ApiConstants.nodes,
      queryParameters: {
        if (status != null) 'status': status,
        if (tag != null) 'tag': tag,
      },
    );
    
    final nodes = (response.data['data'] as List)
        .map((n) => NodeModel.fromJson(n))
        .toList();
    return nodes;
  }

  Future<NodeModel> getNodeDetail(String id) async {
    final response = await _dio.get(ApiConstants.nodeDetail(id));
    return NodeModel.fromJson(response.data['data']);
  }

  Future<TopologyData> getTopology() async {
    final response = await _dio.get(ApiConstants.nodesTopology);
    return TopologyData.fromJson(response.data['data']);
  }

  Future<void> sendCommand(String nodeId, String commandType, Map<String, dynamic>? params) async {
    await _dio.post(
      ApiConstants.nodeCommands(nodeId),
      data: {
        'commandType': commandType,
        if (params != null) 'params': params,
      },
    );
  }
}

final nodesListProvider = FutureProvider<List<NodeModel>>((ref) async {
  final service = ref.watch(nodesServiceProvider);
  return service.getNodes();
});

final topologyProvider = FutureProvider<TopologyData>((ref) async {
  final service = ref.watch(nodesServiceProvider);
  return service.getTopology();
});

final nodeDetailProvider = FutureProvider.family<NodeModel, String>((ref, id) async {
  final service = ref.watch(nodesServiceProvider);
  return service.getNodeDetail(id);
});
