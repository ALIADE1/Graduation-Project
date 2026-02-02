import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProcessingScreen extends StatefulWidget {
  final String taskId;

  const ProcessingScreen({super.key, required this.taskId});

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  Timer? _timer;
  String _status = 'pending';
  String _message = 'Initializing...';
  int _progress = 0;
  String? _finalNotes; // Store the summary when completed

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  @override
  void dispose() {
    _timer?.cancel(); // Must stop the timer when exiting
    super.dispose();
  }

  // Function that runs every 3 seconds to poll the server
  void _startPolling() {
    _timer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      final data = await ApiService.getTaskStatus(widget.taskId);

      if (data != null && mounted) {
        setState(() {
          _status = data['status'];
          _message = data['message'];
          _progress = data['progress'] ?? 0;
        });

        // If completed, stop the timer and fetch the result
        if (_status == 'completed') {
          timer.cancel();
          _fetchFinalResult();
        } 
        // If failed, stop the timer and show error
        else if (_status == 'failed') {
          timer.cancel();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('❌ Error: $_message'), backgroundColor: Colors.red),
          );
        }
      }
    });
  }

  // Function to load the final result (will be refined later, currently shows success message only)
  Future<void> _fetchFinalResult() async {
    // TODO: Call API to get the full markdown text
    setState(() {
       // This is temporary text until we connect the actual loading function
      _finalNotes = "✅ Notes Generated Successfully!\n\n(We will display the full text here in the next step)";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Generating Notes...')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: _finalNotes != null
            ? _buildSuccessView() // If completed, show result
            : _buildProgressView(), // If still processing, show loading
      ),
    );
  }

  // Loading screen design
  Widget _buildProgressView() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const CircularProgressIndicator(),
        const SizedBox(height: 30),
        Text(
          '$_progress%',
          style: const TextStyle(fontSize: 40, fontWeight: FontWeight.bold, color: Colors.blue),
        ),
        const SizedBox(height: 10),
        Text(
          _message,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 18),
        ),
        const SizedBox(height: 20),
        LinearProgressIndicator(value: _progress / 100),
      ],
    );
  }

  // Success screen design
  Widget _buildSuccessView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.check_circle, color: Colors.green, size: 100),
          const SizedBox(height: 20),
          const Text(
            "Done!",
            style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Return to home screen
            },
            child: const Text("Back to Home"),
          )
        ],
      ),
    );
  }
}