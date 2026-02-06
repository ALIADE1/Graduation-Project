import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import '../theme.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  List<dynamic> _recommendations = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchRecommendations();
  }

  Future<void> _fetchRecommendations() async {
    setState(() => _isLoading = true);
    final recs = await ApiService.getRecommendations();
    if (mounted) {
      setState(() {
        _recommendations = recs;
        _isLoading = false;
      });
    }
  }

  Future<void> _launchUrl(String url) async {
    final Uri uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not launch $url')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: CustomScrollView(
        slivers: [
          // Elegant Header
          SliverAppBar(
            expandedHeight: 120,
            floating: false,
            pinned: true,
            backgroundColor: AppTheme.primaryColor,
            elevation: 0,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text(
                'Discovery',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: -0.5,
                ),
              ),
              centerTitle: false,
              titlePadding: const EdgeInsets.only(left: 20, bottom: 16),
              background: Container(
                decoration: BoxDecoration(
                  gradient: AppTheme.appBarGradient,
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.refresh_rounded),
                onPressed: _fetchRecommendations,
              ),
              const SizedBox(width: 8),
            ],
          ),

          if (_isLoading)
            const SliverFillRemaining(
              child: Center(child: CircularProgressIndicator()),
            )
          else if (_recommendations.isEmpty)
            SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.ondemand_video_rounded, size: 64, color: Colors.grey[300]),
                    const SizedBox(height: 16),
                    const Text('No recommendations yet. Start studying!'),
                  ],
                ),
              ),
            )
          else ...[
            // Section Title: Featured for You
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Featured for You',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    Text(
                      'BASED ON YOUR INTERESTS',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor.withOpacity(0.7),
                        letterSpacing: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Video Cards List
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final rec = _recommendations[index];
                    return _buildDiscoveryCard(rec);
                  },
                  childCount: _recommendations.length,
                ),
              ),
            ),
            
            const SliverToBoxAdapter(child: SizedBox(height: 32)),
          ],
        ],
      ),
    );
  }

  Widget _buildDiscoveryCard(dynamic rec) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Video Thumbnail with Play Overlay
          Stack(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.network(
                    rec['thumbnail'] ?? '',
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Container(
                      color: Colors.grey[100],
                      child: const Icon(Icons.broken_image_rounded, size: 40),
                    ),
                  ),
                ),
              ),
              Positioned.fill(
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () => _launchUrl(rec['url']),
                    child: Center(
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.9),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.play_arrow_rounded,
                          color: Colors.red,
                          size: 32,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          
          // Video Info
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  rec['title'] ?? 'No Title',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: AppTheme.textPrimary,
                    height: 1.3,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    CircleAvatar(
                      radius: 12,
                      backgroundColor: Colors.red.withOpacity(0.1),
                      child: const Icon(Icons.tv_rounded, size: 12, color: Colors.red),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        rec['channelTitle'] ?? 'YouTube Channel',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                if (rec['description'] != null && (rec['description'] as String).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    rec['description'],
                    style: TextStyle(
                      color: AppTheme.textLight,
                      fontSize: 12,
                      height: 1.4,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
                const SizedBox(height: 16),
                Divider(color: Colors.grey.withOpacity(0.1)),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.auto_awesome_rounded, size: 16, color: AppTheme.primaryColor.withOpacity(0.7)),
                        const SizedBox(width: 6),
                        Text(
                          'Recommended',
                          style: TextStyle(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    ActionChip(
                      onPressed: () => _launchUrl(rec['url']),
                      backgroundColor: AppTheme.primaryColor.withOpacity(0.05),
                      side: BorderSide.none,
                      padding: EdgeInsets.zero,
                      label: const Text('WATCH NOW'),
                      labelStyle: TextStyle(
                        color: AppTheme.primaryColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

