import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const StudyNotesApp());
}

class StudyNotesApp extends StatelessWidget {
  const StudyNotesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'YouTube Study Notes',
      debugShowCheckedModeBanner: false, // Hides the debug banner
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const LoginScreen(), // Start with Login Screen
    );
  }
}