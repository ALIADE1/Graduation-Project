import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import 'processing_screen.dart';
import 'note_viewer_screen.dart'; // هنعمل الملف ده حالاً
import 'recommendations_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _username = '';
  List<dynamic> _notes = []; 
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _fetchNotes(); 
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
        _isLoading = false;
      });
    }
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
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New Study Note'),
        content: TextField(
          controller: urlController,
          decoration: const InputDecoration(
            hintText: 'Paste YouTube URL here...',
            prefixIcon: Icon(Icons.link),
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('🚀 Connecting...')));
              String url = urlController.text.trim();
              if (url.isNotEmpty) {
                String? taskId = await ApiService.generateNotes(url);
                if (!context.mounted) return;
                if (taskId != null) {
                   await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ProcessingScreen(taskId: taskId)),
                  );
                  _fetchNotes();
                }
              }
            },
            child: const Text('Generate'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Notes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.auto_awesome), 
            onPressed: () => Navigator.push(
              context, 
              MaterialPageRoute(builder: (context) => const RecommendationsScreen())
            ),
            tooltip: 'Recommendations',
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _fetchNotes),
          IconButton(icon: const Icon(Icons.logout), onPressed: _logout)
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _notes.isEmpty
              ? const Center(child: Text("No notes yet. Create one! 👇"))
                : ListView.builder(
                    itemCount: _notes.length,
                    padding: const EdgeInsets.all(10),
                    itemBuilder: (context, index) {
                      final note = _notes[index];
                      return Card(
                        elevation: 3,
                        margin: const EdgeInsets.only(bottom: 10),
                        child: ListTile(
                          leading: const Icon(Icons.description, color: Colors.blue, size: 40),
                          title: Text(
                            note['video_title'],
                            style: const TextStyle(fontWeight: FontWeight.bold),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("Created: ${note['created_at'].toString().split('.')[0]}"),
                              if (note['category'] != null)
                                Chip(
                                  label: Text(
                                    note['category'],
                                    style: const TextStyle(fontSize: 10, color: Colors.white),
                                  ),
                                  backgroundColor: Colors.blueAccent,
                                  visualDensity: VisualDensity.compact,
                                  padding: EdgeInsets.zero,
                                ),
                            ],
                          ),
                          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => NoteViewerScreen(
                                  noteId: note['id'],
                                  title: note['video_title'],
                                ),
                              ),
                            );
                          },
                        ),
                      );
                    },
                  ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddNoteDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }
}