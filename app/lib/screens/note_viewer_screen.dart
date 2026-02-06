import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../constants.dart';

class NoteViewerScreen extends StatelessWidget {
  final int noteId;
  final String title;
  final String? category;

  const NoteViewerScreen({
    super.key,
    required this.noteId,
    required this.title,
    this.category,
  });

  @override
  Widget build(BuildContext context) {
    final categoryName = category ?? 'Uncategorized';
    final categoryColor = CategoryConfig.getColor(categoryName);
    final categoryIcon = CategoryConfig.getIcon(categoryName);

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // Custom AppBar with category
          SliverAppBar(
            expandedHeight: 180,
            floating: false,
            pinned: true,
            flexibleSpace: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    categoryColor,
                    categoryColor.withOpacity(0.8),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: FlexibleSpaceBar(
                titlePadding: const EdgeInsets.only(left: 56, right: 16, bottom: 16),
                title: Text(
                  title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        categoryColor,
                        categoryColor.withOpacity(0.7),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: Stack(
                    children: [
                      Positioned(
                        right: 20,
                        bottom: 60,
                        child: Icon(
                          categoryIcon,
                          size: 100,
                          color: Colors.white.withOpacity(0.15),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            leading: IconButton(
              icon: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.arrow_back_rounded, size: 20),
              ),
              onPressed: () => Navigator.pop(context),
            ),
          ),

          // Category Badge
          SliverToBoxAdapter(
            child: Container(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: categoryColor.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          categoryIcon,
                          size: 18,
                          color: categoryColor,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          categoryName,
                          style: TextStyle(
                            color: categoryColor,
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceColor,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.play_circle_outline_rounded,
                          size: 18,
                          color: AppTheme.textSecondary,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'YouTube Video',
                          style: TextStyle(
                            color: AppTheme.textSecondary,
                            fontWeight: FontWeight.w500,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Note Content
          SliverFillRemaining(
            child: FutureBuilder<String>(
              future: ApiService.getNoteContent(noteId),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(
                          color: categoryColor,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Loading notes...',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  );
                } else if (snapshot.hasError) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.red.withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.error_outline_rounded,
                            size: 48,
                            color: Colors.red,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          "Error loading notes",
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: AppTheme.textPrimary,
                              ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          "${snapshot.error}",
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  );
                } else {
                  return Container(
                    color: AppTheme.backgroundColor,
                    child: Markdown(
                      data: snapshot.data ?? "",
                      padding: const EdgeInsets.all(20),
                      styleSheet: MarkdownStyleSheet(
                        h1: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                          color: categoryColor,
                          height: 1.4,
                        ),
                        h2: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textPrimary,
                          height: 1.4,
                        ),
                        h3: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textPrimary,
                          height: 1.4,
                        ),
                        p: const TextStyle(
                          fontSize: 16,
                          color: AppTheme.textPrimary,
                          height: 1.7,
                        ),
                        listBullet: TextStyle(
                          color: categoryColor,
                          fontWeight: FontWeight.bold,
                        ),
                        blockquote: TextStyle(
                          fontSize: 15,
                          fontStyle: FontStyle.italic,
                          color: AppTheme.textSecondary,
                        ),
                        blockquoteDecoration: BoxDecoration(
                          border: Border(
                            left: BorderSide(
                              color: categoryColor.withOpacity(0.5),
                              width: 4,
                            ),
                          ),
                          color: categoryColor.withOpacity(0.05),
                        ),
                        blockquotePadding: const EdgeInsets.all(16),
                        code: TextStyle(
                          fontSize: 14,
                          backgroundColor: AppTheme.surfaceColor,
                          color: categoryColor,
                          fontFamily: 'monospace',
                        ),
                        codeblockDecoration: BoxDecoration(
                          color: const Color(0xFF1E1E1E),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        codeblockPadding: const EdgeInsets.all(16),
                        horizontalRuleDecoration: BoxDecoration(
                          border: Border(
                            top: BorderSide(
                              color: AppTheme.surfaceColor,
                              width: 2,
                            ),
                          ),
                        ),
                        strong: const TextStyle(
                          fontWeight: FontWeight.w700,
                        ),
                        em: const TextStyle(
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  );
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}