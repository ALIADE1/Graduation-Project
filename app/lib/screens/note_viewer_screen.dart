import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../services/api_service.dart';

class NoteViewerScreen extends StatelessWidget {
  final int noteId;
  final String title;

  const NoteViewerScreen({super.key, required this.noteId, required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: FutureBuilder<String>(
        future: ApiService.getNoteContent(noteId),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          } else {
            return Markdown(
              data: snapshot.data ?? "",
              styleSheet: MarkdownStyleSheet(
                h1: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.blue),
                h2: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black87),
                p: const TextStyle(fontSize: 16),
              ),
            );
          }
        },
      ),
    );
  }
}