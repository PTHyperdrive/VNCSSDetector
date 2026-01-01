import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/services/realtime_service.dart';

class NodesMapScreen extends ConsumerStatefulWidget {
  const NodesMapScreen({super.key});

  @override
  ConsumerState<NodesMapScreen> createState() => _NodesMapScreenState();
}

class _NodesMapScreenState extends ConsumerState<NodesMapScreen> {
  final MapController _mapController = MapController();

  // Default center (Ho Chi Minh City)
  static const _defaultCenter = LatLng(10.8231, 106.6297);
  static const _defaultZoom = 10.0;

  @override
  Widget build(BuildContext context) {
    final realtimeState = ref.watch(realtimeProvider);
    final theme = Theme.of(context);

    // Filter nodes that have location
    final nodesWithLocation =
        realtimeState.nodes.where((n) => n.hasLocation).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Node Map'),
        actions: [
          // Connection status indicator
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: realtimeState.isConnected
                        ? AppTheme.nodeOnline
                        : AppTheme.nodeOffline,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  realtimeState.isConnected ? 'Live' : 'Offline',
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Map
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: _defaultCenter,
              initialZoom: _defaultZoom,
            ),
            children: [
              // OpenStreetMap tiles
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.vncssd.client',
              ),

              // Node markers
              MarkerLayer(
                markers: nodesWithLocation
                    .map((node) => _buildMarker(node))
                    .toList(),
              ),
            ],
          ),

          // Summary overlay
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: _buildSummaryCard(realtimeState.summary, theme),
          ),

          // Legend
          Positioned(
            bottom: 16,
            left: 16,
            child: _buildLegend(theme),
          ),

          // No location warning
          if (nodesWithLocation.isEmpty && realtimeState.nodes.isNotEmpty)
            Center(
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.location_off, size: 48),
                      const SizedBox(height: 8),
                      Text(
                        'No nodes have location data',
                        style: theme.textTheme.bodyLarge,
                      ),
                      Text(
                        'Update node locations in node settings',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
      floatingActionButton: nodesWithLocation.isNotEmpty
          ? FloatingActionButton(
              onPressed: () => _fitAllMarkers(nodesWithLocation),
              child: const Icon(Icons.center_focus_strong),
            )
          : null,
    );
  }

  Marker _buildMarker(NodeStatusUpdate node) {
    final color = _getStatusColor(node.status);

    return Marker(
      point: LatLng(node.latitude!, node.longitude!),
      width: 40,
      height: 40,
      child: GestureDetector(
        onTap: () => _showNodePopup(node),
        child: Container(
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white, width: 2),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.4),
                blurRadius: 8,
                spreadRadius: 2,
              ),
            ],
          ),
          child: const Icon(Icons.dns, color: Colors.white, size: 20),
        ),
      ),
    );
  }

  Widget _buildSummaryCard(NodeStatusSummary? summary, ThemeData theme) {
    if (summary == null) return const SizedBox();

    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _summaryItem('Online', summary.online, AppTheme.nodeOnline),
            const SizedBox(width: 16),
            _summaryItem('Offline', summary.offline, AppTheme.nodeOffline),
            const SizedBox(width: 16),
            _summaryItem('Degraded', summary.degraded, AppTheme.nodeDegraded),
            const SizedBox(width: 16),
            Text('Total: ${summary.total}', style: theme.textTheme.bodySmall),
          ],
        ),
      ),
    );
  }

  Widget _summaryItem(String label, int count, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text('$count',
            style: TextStyle(color: color, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildLegend(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            _legendItem('Online', AppTheme.nodeOnline),
            _legendItem('Offline', AppTheme.nodeOffline),
            _legendItem('Degraded', AppTheme.nodeDegraded),
            _legendItem('Pending', AppTheme.nodePending),
          ],
        ),
      ),
    );
  }

  Widget _legendItem(String label, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }

  void _showNodePopup(NodeStatusUpdate node) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _getStatusColor(node.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.dns,
                    color: _getStatusColor(node.status),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        node.hostname,
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      Text(
                        node.locationName ?? 'Unknown location',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(node.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    node.status,
                    style: TextStyle(
                      color: _getStatusColor(node.status),
                      fontWeight: FontWeight.w500,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () {
                Navigator.pop(context);
                context.push('/nodes/${node.id}');
              },
              child: const Text('View Details'),
            ),
          ],
        ),
      ),
    );
  }

  void _fitAllMarkers(List<NodeStatusUpdate> nodes) {
    if (nodes.isEmpty) return;

    final points = nodes.map((n) => LatLng(n.latitude!, n.longitude!)).toList();

    final bounds = LatLngBounds.fromPoints(points);
    _mapController.fitCamera(
      CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(50)),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'ONLINE':
        return AppTheme.nodeOnline;
      case 'OFFLINE':
        return AppTheme.nodeOffline;
      case 'DEGRADED':
        return AppTheme.nodeDegraded;
      default:
        return AppTheme.nodePending;
    }
  }
}
