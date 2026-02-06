import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../constants.dart';
import 'login_screen.dart';
import 'processing_screen.dart';
import 'note_viewer_screen.dart';
import 'recommendations_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  String _username = '';
  List<dynamic> _notes = [];
  List<dynamic> _filteredNotes = [];
  bool _isLoading = true;
  String _selectedCategory = 'All';
  late AnimationController _fabController;
  late Animation<double> _fabAnimation;

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _fetchNotes();
    
    _fabController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fabAnimation = CurvedAnimation(
      parent: _fabController,
      curve: Curves.easeOut,
    );
    _fabController.forward();
  }

  @override
  void dispose() {
    _fabController.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _username = prefs.getString('username') ?? 'User';
    });
  }

  Future<void> _fetchNotes() async {
    setState(() => _isLoading = true);
    final notes = await ApiService.getGeneratedNotes();
    if (mounted) {
      setState(() {
        _notes = notes;
        _applyFilter();
        _isLoading = false;
      });
    }
  }

  void _applyFilter() {
    if (_selectedCategory == 'All') {
      _filteredNotes = _notes;
    } else {
      _filteredNotes = _notes.where((note) {
        final category = note['category']?.toString() ?? 'Uncategorized';
        return category == _selectedCategory;
      }).toList();
    }
  }

  void _selectCategory(String category) {
    setState(() {
      _selectedCategory = category;
      _applyFilter();
    });
  }

  List<String> _getAvailableCategories() {
    final categories = <String>{'All'};
    for (var note in _notes) {
      final category = note['category']?.toString() ?? 'Uncategorized';
      categories.add(category);
    }
    return categories.toList();
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  void _showAddNoteDialog(BuildContext context) {
    final urlController = TextEditingController();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Create New Note',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Paste a YouTube URL to generate study notes',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 24),
              TextField(
                controller: urlController,
                decoration: InputDecoration(
                  hintText: 'https://youtube.com/watch?v=...',
                  prefixIcon: Container(
                    margin: const EdgeInsets.all(8),
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.link_rounded, color: AppTheme.primaryColor, size: 20),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    flex: 2,
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: AppTheme.elevatedShadow,
                      ),
                      child: ElevatedButton(
                        onPressed: () async {
                          Navigator.pop(context);
                          String url = urlController.text.trim();
                          if (url.isNotEmpty) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Row(
                                  children: [
                                    SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    ),
                                    const SizedBox(width: 16),
                                    const Text('Connecting to server...'),
                                  ],
                                ),
                                backgroundColor: AppTheme.primaryColor,
                                behavior: SnackBarBehavior.floating,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                            );
                            String? taskId = await ApiService.generateNotes(url);
                            if (!context.mounted) return;
                            if (taskId != null) {
                              await Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => ProcessingScreen(taskId: taskId),
                                ),
                              );
                              _fetchNotes();
                            }
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            Icon(Icons.auto_awesome_rounded, size: 20),
                            SizedBox(width: 8),
                            Text('Generate Notes'),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final availableCategories = _getAvailableCategories();
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // Custom Gradient AppBar
          SliverAppBar(
            expandedHeight: 140,
            floating: false,
            pinned: true,
            flexibleSpace: Container(
              decoration: const BoxDecoration(
                gradient: AppTheme.appBarGradient,
              ),
              child: FlexibleSpaceBar(
                titlePadding: const EdgeInsets.only(left: 20, bottom: 16),
                title: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome back,',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.normal,
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                    Text(
                      _username,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                background: Container(
                  decoration: const BoxDecoration(
                    gradient: AppTheme.appBarGradient,
                  ),
                  child: Align(
                    alignment: Alignment.centerRight,
                    child: Padding(
                      padding: const EdgeInsets.only(right: 20),
                      child: Icon(
                        Icons.auto_stories_rounded,
                        size: 80,
                        color: Colors.white.withOpacity(0.15),
                      ),
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.auto_awesome, size: 20),
                ),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const RecommendationsScreen(),
                  ),
                ),
                tooltip: 'Recommendations',
              ),
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.refresh_rounded, size: 20),
                ),
                onPressed: _fetchNotes,
              ),
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.logout_rounded, size: 20),
                ),
                onPressed: _logout,
              ),
              const SizedBox(width: 8),
            ],
          ),
          
          // Category Filter Chips
          SliverToBoxAdapter(
            child: Container(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'My Notes',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '${_filteredNotes.length} notes',
                          style: TextStyle(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 42,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: availableCategories.length,
                      itemBuilder: (context, index) {
                        final category = availableCategories[index];
                        final isSelected = category == _selectedCategory;
                        final color = category == 'All' 
                            ? AppTheme.primaryColor 
                            : CategoryConfig.getColor(category);
                        
                        return Padding(
                          padding: EdgeInsets.only(
                            right: 8,
                            left: index == 0 ? 0 : 0,
                          ),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 200),
                            child: FilterChip(
                              selected: isSelected,
                              label: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  if (category != 'All') ...[
                                    Icon(
                                      CategoryConfig.getIcon(category),
                                      size: 16,
                                      color: isSelected ? Colors.white : color,
                                    ),
                                    const SizedBox(width: 6),
                                  ],
                                  Text(category),
                                ],
                              ),
                              labelStyle: TextStyle(
                                color: isSelected ? Colors.white : AppTheme.textPrimary,
                                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                              ),
                              backgroundColor: Colors.white,
                              selectedColor: color,
                              checkmarkColor: Colors.white,
                              showCheckmark: false,
                              side: BorderSide(
                                color: isSelected ? color : Colors.grey.shade300,
                              ),
                              onSelected: (_) => _selectCategory(category),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // Notes List
          _isLoading
              ? const SliverFillRemaining(
                  child: Center(
                    child: CircularProgressIndicator(
                      color: AppTheme.primaryColor,
                    ),
                  ),
                )
              : _filteredNotes.isEmpty
                  ? SliverFillRemaining(
                      child: _buildEmptyState(),
                    )
                  : SliverPadding(
                      padding: const EdgeInsets.all(16),
                      sliver: SliverList(
                        delegate: SliverChildBuilderDelegate(
                          (context, index) {
                            final note = _filteredNotes[index];
                            return _buildNoteCard(note, index);
                          },
                          childCount: _filteredNotes.length,
                        ),
                      ),
                    ),
        ],
      ),
      floatingActionButton: ScaleTransition(
        scale: _fabAnimation,
        child: Container(
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            borderRadius: BorderRadius.circular(16),
            boxShadow: AppTheme.elevatedShadow,
          ),
          child: FloatingActionButton.extended(
            onPressed: () => _showAddNoteDialog(context),
            backgroundColor: Colors.transparent,
            elevation: 0,
            icon: const Icon(Icons.add_rounded),
            label: const Text('New Note'),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.note_add_rounded,
                size: 64,
                color: AppTheme.primaryColor.withOpacity(0.7),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              _selectedCategory == 'All'
                  ? 'No notes yet'
                  : 'No $_selectedCategory notes',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Tap the button below to create your first study note from a YouTube video',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textLight,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoteCard(dynamic note, int index) {
    final category = note['category']?.toString() ?? 'Uncategorized';
    final categoryColor = CategoryConfig.getColor(category);
    final categoryIcon = CategoryConfig.getIcon(category);
    
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: Duration(milliseconds: 300 + (index * 50)),
      curve: Curves.easeOut,
      builder: (context, value, child) {
        return Transform.translate(
          offset: Offset(0, 20 * (1 - value)),
          child: Opacity(
            opacity: value,
            child: child,
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: categoryColor.withOpacity(0.08),
              blurRadius: 15,
              offset: const Offset(0, 8),
              spreadRadius: 0,
            ),
            BoxShadow(
              color: Colors.black.withOpacity(0.03),
              blurRadius: 5,
              offset: const Offset(0, 2),
              spreadRadius: 0,
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => NoteViewerScreen(
                    noteId: note['id'],
                    title: note['video_title'],
                    category: category,
                  ),
                ),
              );
            },
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  // Category Icon with Gradient
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          categoryColor.withOpacity(0.15),
                          categoryColor.withOpacity(0.05),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(
                        color: categoryColor.withOpacity(0.1),
                        width: 1,
                      ),
                    ),
                    child: Icon(
                      categoryIcon,
                      color: categoryColor,
                      size: 30,
                    ),
                  ),
                  const SizedBox(width: 18),
                  
                  // Note Details
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          note['video_title'] ?? 'Untitled',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: AppTheme.textPrimary,
                            letterSpacing: -0.2,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 5,
                              ),
                              decoration: BoxDecoration(
                                color: categoryColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    categoryIcon,
                                    size: 12,
                                    color: categoryColor,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    category,
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: categoryColor,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Icon(
                              Icons.history_rounded,
                              size: 14,
                              color: AppTheme.textLight,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              _formatDate(note['created_at']),
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                                color: AppTheme.textLight,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  
                  // Arrow button
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade50,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.chevron_right_rounded,
                      size: 20,
                      color: AppTheme.textSecondary.withOpacity(0.5),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  String _formatDate(dynamic dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr.toString());
      final now = DateTime.now();
      final diff = now.difference(date);
      
      if (diff.inDays == 0) {
        if (diff.inHours == 0) {
          return '${diff.inMinutes}m ago';
        }
        return '${diff.inHours}h ago';
      } else if (diff.inDays < 7) {
        return '${diff.inDays}d ago';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      return dateStr.toString().split('.')[0];
    }
  }
}