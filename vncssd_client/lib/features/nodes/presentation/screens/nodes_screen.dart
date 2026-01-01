import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../../../../core/theme/app_theme.dart';
import '../../data/nodes_service.dart';

class NodesScreen extends ConsumerWidget {
  const NodesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodesAsync = ref.watch(nodesListProvider);
    final topologyAsync = ref.watch(topologyProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Nodes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(nodesListProvider);
              ref.invalidate(topologyProvider);
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(nodesListProvider);
          ref.invalidate(topologyProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Topology summary
            topologyAsync.when(
              data: (topology) => _TopologySummaryCard(topology: topology),
              loading: () => const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Center(child: CircularProgressIndicator()),
                ),
              ),
              error: (_, __) => const SizedBox(),
            ),
            const SizedBox(height: 16),

            // Nodes list
            Text(
              'All Nodes',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),

            nodesAsync.when(
              data: (nodes) {
                if (nodes.isEmpty) {
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        children: [
                          Icon(
                            Icons.dns_outlined,
                            size: 48,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'No nodes registered',
                            style: theme.textTheme.bodyLarge,
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return Column(
                  children: nodes
                      .map((node) => _NodeListItem(
                            node: node,
                            onTap: () => context.push('/nodes/${node.id}'),
                          ))
                      .toList(),
                );
              },
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (e, _) => Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Icon(Icons.error_outline, size: 48, color: Colors.red),
                      const SizedBox(height: 8),
                      Text('Failed to load nodes'),
                      TextButton(
                        onPressed: () => ref.invalidate(nodesListProvider),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TopologySummaryCard extends StatelessWidget {
  final TopologyData topology;

  const _TopologySummaryCard({required this.topology});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final summary = topology.summary;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Topology',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _SummaryChip(
                  label: 'Online',
                  count: summary.online,
                  color: AppTheme.nodeOnline,
                ),
                const SizedBox(width: 8),
                _SummaryChip(
                  label: 'Offline',
                  count: summary.offline,
                  color: AppTheme.nodeOffline,
                ),
                const SizedBox(width: 8),
                _SummaryChip(
                  label: 'Degraded',
                  count: summary.degraded,
                  color: AppTheme.nodeDegraded,
                ),
              ],
            ),
            if (topology.byTag.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: topology.byTag
                    .map((t) => Chip(
                          label: Text('${t.tag}: ${t.online}/${t.total}'),
                          visualDensity: VisualDensity.compact,
                        ))
                    .toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _SummaryChip extends StatelessWidget {
  final String label;
  final int count;
  final Color color;

  const _SummaryChip({
    required this.label,
    required this.count,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            '$label: $count',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _NodeListItem extends StatelessWidget {
  final NodeModel node;
  final VoidCallback onTap;

  const _NodeListItem({required this.node, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final statusColor = _getStatusColor(node.status);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        onTap: onTap,
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(Icons.dns, color: statusColor),
        ),
        title: Text(
          node.hostname,
          style: theme.textTheme.bodyLarge?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (node.ipAddress != null)
              Text(node.ipAddress!),
            if (node.lastSeen != null)
              Text(
                'Last seen: ${timeago.format(node.lastSeen!)}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                node.status,
                style: TextStyle(
                  color: statusColor,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            if (node.cpuUsage != null) ...[
              const SizedBox(height: 4),
              Text(
                'CPU: ${node.cpuUsage!.toStringAsFixed(1)}%',
                style: theme.textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
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
