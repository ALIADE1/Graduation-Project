import 'package:flutter/material.dart';

/// Category configuration for notes
/// Maps category names to their icons and colors
class CategoryConfig {
  static const Map<String, IconData> categoryIcons = {
    // Tech & Science
    'Technology': Icons.computer_rounded,
    'Programming': Icons.code_rounded,
    'Science': Icons.science_rounded,
    'Mathematics': Icons.calculate_rounded,
    'Engineering': Icons.engineering_rounded,
    'AI': Icons.psychology_rounded,
    
    // Education
    'Education': Icons.school_rounded,
    'Tutorial': Icons.play_lesson_rounded,
    'Course': Icons.menu_book_rounded,
    'Lecture': Icons.record_voice_over_rounded,
    'Language': Icons.translate_rounded,
    
    // Business & Finance
    'Business': Icons.business_center_rounded,
    'Finance': Icons.attach_money_rounded,
    'Marketing': Icons.campaign_rounded,
    'Entrepreneurship': Icons.rocket_launch_rounded,
    
    // Creative
    'Music': Icons.music_note_rounded,
    'Art': Icons.palette_rounded,
    'Design': Icons.design_services_rounded,
    'Photography': Icons.camera_alt_rounded,
    'Video': Icons.videocam_rounded,
    
    // Lifestyle
    'Health': Icons.health_and_safety_rounded,
    'Fitness': Icons.fitness_center_rounded,
    'Cooking': Icons.restaurant_rounded,
    'Travel': Icons.flight_rounded,
    'Lifestyle': Icons.self_improvement_rounded,
    
    // Entertainment & Media
    'Entertainment': Icons.movie_rounded,
    'Gaming': Icons.sports_esports_rounded,
    'Sports': Icons.sports_soccer_rounded,
    'News': Icons.newspaper_rounded,
    'Podcast': Icons.podcasts_rounded,
    
    // Default
    'Uncategorized': Icons.article_rounded,
    'Other': Icons.folder_rounded,
  };

  static const Map<String, Color> categoryColors = {
    // Tech & Science - Blues and Cyans
    'Technology': Color(0xFF3B82F6),
    'Programming': Color(0xFF6366F1),
    'Science': Color(0xFF06B6D4),
    'Mathematics': Color(0xFF0EA5E9),
    'Engineering': Color(0xFF0284C7),
    'AI': Color(0xFF8B5CF6),
    
    // Education - Greens and Teals
    'Education': Color(0xFF10B981),
    'Tutorial': Color(0xFF14B8A6),
    'Course': Color(0xFF059669),
    'Lecture': Color(0xFF0D9488),
    'Language': Color(0xFF22C55E),
    
    // Business & Finance - Oranges and Ambers
    'Business': Color(0xFFF59E0B),
    'Finance': Color(0xFF22C55E),
    'Marketing': Color(0xFFF97316),
    'Entrepreneurship': Color(0xFFEAB308),
    
    // Creative - Pinks and Purples
    'Music': Color(0xFFEC4899),
    'Art': Color(0xFFA855F7),
    'Design': Color(0xFFD946EF),
    'Photography': Color(0xFFF472B6),
    'Video': Color(0xFFE11D48),
    
    // Lifestyle - Warm colors
    'Health': Color(0xFFEF4444),
    'Fitness': Color(0xFFF97316),
    'Cooking': Color(0xFFEA580C),
    'Travel': Color(0xFF0EA5E9),
    'Lifestyle': Color(0xFFEC4899),
    
    // Entertainment & Media - Vibrant colors
    'Entertainment': Color(0xFFDC2626),
    'Gaming': Color(0xFF7C3AED),
    'Sports': Color(0xFF16A34A),
    'News': Color(0xFF1D4ED8),
    'Podcast': Color(0xFF9333EA),
    
    // Default
    'Uncategorized': Color(0xFF64748B),
    'Other': Color(0xFF94A3B8),
  };

  /// Get icon for a category, with fallback to default
  static IconData getIcon(String? category) {
    if (category == null) return categoryIcons['Uncategorized']!;
    return categoryIcons[category] ?? categoryIcons['Uncategorized']!;
  }

  /// Get color for a category, with fallback to default
  static Color getColor(String? category) {
    if (category == null) return categoryColors['Uncategorized']!;
    return categoryColors[category] ?? categoryColors['Uncategorized']!;
  }

  /// Get a lighter version of category color (for backgrounds)
  static Color getLightColor(String? category) {
    return getColor(category).withOpacity(0.15);
  }

  /// Get all unique categories
  static List<String> get allCategories => categoryIcons.keys.toList();
  
  /// Common categories for filtering (subset of all)
  static const List<String> filterCategories = [
    'All',
    'Technology',
    'Education',
    'Science',
    'Business',
    'Music',
    'Entertainment',
    'Health',
    'Tutorial',
  ];
}
