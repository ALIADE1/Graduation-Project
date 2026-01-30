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
  String? _finalNotes; // هنا هنحفظ الملخص لما يخلص

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  @override
  void dispose() {
    _timer?.cancel(); // لازم نوقف التايمر لما نخرج
    super.dispose();
  }

  // دالة بتشتغل كل 3 ثواني تسأل السيرفر
  void _startPolling() {
    _timer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      final data = await ApiService.getTaskStatus(widget.taskId);

      if (data != null && mounted) {
        setState(() {
          _status = data['status'];
          _message = data['message'];
          _progress = data['progress'] ?? 0;
        });

        // لو خلص، وقف التايمر وهات النتيجة
        if (_status == 'completed') {
          timer.cancel();
          _fetchFinalResult();
        } 
        // لو فشل، وقف التايمر واعرض خطأ
        else if (_status == 'failed') {
          timer.cancel();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('❌ Error: $_message'), backgroundColor: Colors.red),
          );
        }
      }
    });
  }

  // دالة لتحميل النتيجة النهائية (لسه هنظبطها، حالياً بتعرض رسالة نجاح بس)
  Future<void> _fetchFinalResult() async {
    // TODO: Call API to get the full markdown text
    setState(() {
       // ده نص مؤقت لحد ما نربط دالة التحميل الحقيقية
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
            ? _buildSuccessView() // لو خلص اعرض النتيجة
            : _buildProgressView(), // لو لسه شغال اعرض التحميل
      ),
    );
  }

  // تصميم شاشة التحميل
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

  // تصميم شاشة النجاح
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
              Navigator.pop(context); // ارجع للشاشة الرئيسية
            },
            child: const Text("Back to Home"),
          )
        ],
      ),
    );
  }
}