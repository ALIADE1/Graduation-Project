import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'theme.dart';

void main() {
  runApp(const StudyNotesApp());
}

class StudyNotesApp extends StatelessWidget {
  const StudyNotesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'YouTube Study Notes',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const LoginScreen(),
    );
  }
}