import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../../../../core/theme/app_theme.dart';
import '../../data/nodes_service.dart';

class NodeDetailScreen extends ConsumerWidget {
  final String nodeId;

  const NodeDetailScreen({super.key, required this.nodeId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodeAsync = ref.watch(nodeDetailProvider(nodeId));
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Node Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(nodeDetailProvider(nodeId)),
          ),
        ],
      ),
      body: nodeAsync.when(
        data: (node) => _NodeDetailContent(node: node),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 8),
              Text('Failed to load node details'),
              TextButton(
                onPressed: () => ref.invalidate(nodeDetailProvider(nodeId)),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NodeDetailContent extends StatelessWidget {
  final NodeModel node;

  const _NodeDetailContent({required this.node});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final statusColor = _getStatusColor(node.status);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Header card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(Icons.dns, size: 28, color: statusColor),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            node.hostname,
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (node.ipAddress != null)
                            Text(
                              node.ipAddress!,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        node.status,
                        style: TextStyle(
                          color: statusColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                if (node.tags.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    children: node.tags
                        .map((t) => Chip(
                              label: Text(t),
                              visualDensity: VisualDensity.compact,
                            ))
                        .toList(),
                  ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Info cards
        _InfoCard(
          title: 'System Information',
          items: [
            _InfoItem(icon: Icons.computer, label: 'OS', value: node.os ?? 'Unknown'),
            _InfoItem(icon: Icons.info, label: 'Version', value: node.version ?? 'Unknown'),
            _InfoItem(
              icon: Icons.access_time,
              label: 'Last Seen',
              value: node.lastSeen != null
                  ? timeago.format(node.lastSeen!)
                  : 'Never',
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Metrics card
        if (node.cpuUsage != null || node.memoryUsage != null)
          _InfoCard(
            title: 'Current Metrics',
            items: [
              if (node.cpuUsage != null)
                _InfoItem(
                  icon: Icons.memory,
                  label: 'CPU Usage',
                  value: '${node.cpuUsage!.toStringAsFixed(1)}%',
                ),
              if (node.memoryUsage != null)
                _InfoItem(
                  icon: Icons.storage,
                  label: 'Memory Usage',
                  value: '${node.memoryUsage!.toStringAsFixed(1)}%',
                ),
            ],
          ),
        const SizedBox(height: 16),

        // Capabilities
        if (node.capabilities != null && node.capabilities!.isNotEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Capabilities',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: node.capabilities!
                        .map((c) => Chip(
                              avatar: const Icon(Icons.check, size: 16),
                              label: Text(c),
                            ))
                        .toList(),
                  ),
                ],
              ),
            ),
          ),
      ],
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

class _InfoCard extends StatelessWidget {
  final String title;
  final List<_InfoItem> items;

  const _InfoCard({required this.title, required this.items});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...items.map((item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    children: [
                      Icon(
                        item.icon,
                        size: 20,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          item.label,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                      Text(
                        item.value,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}

class _InfoItem {
  final IconData icon;
  final String label;
  final String value;

  const _InfoItem({
    required this.icon,
    required this.label,
    required this.value,
  });
}
