import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.1.199:8000';

  static final Dio _dio =
      Dio(
          BaseOptions(
            baseUrl: baseUrl,
            connectTimeout: const Duration(seconds: 30),
            receiveTimeout: const Duration(seconds: 30),
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          ),
        )
        ..interceptors.add(
          InterceptorsWrapper(
            onRequest: (options, handler) async {
              final prefs = await SharedPreferences.getInstance();
              final token = prefs.getString('access_token');
              if (token != null) {
                options.headers['Authorization'] = 'Bearer $token';
              }
              return handler.next(options);
            },
          ),
        );

  // Authentication
  static Future<bool> signup(
    String email,
    String username,
    String password, {
    int? age,
    String? gender,
  }) async {
    try {
      final response = await _dio.post(
        '/auth/signup',
        data: {
          'email': email,
          'username': username,
          'password': password,
          'age': age,
          'gender': gender,
        },
      );
      return response.statusCode == 201 || response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> login(String username, String password) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: FormData.fromMap({'username': username, 'password': password}),
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      if (response.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', response.data['access_token']);
        await prefs.setString(
          'username',
          username,
        ); // Store username for display
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // Note Generation
  static Future<String?> generateNotes(String youtubeUrl) async {
    try {
      final response = await _dio.post(
        '/generate',
        data: {'youtube_url': youtubeUrl, 'language': 'en'},
      );
      return response.data['task_id']?.toString();
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>> getTaskStatus(String taskId) async {
    try {
      final response = await _dio.get('/status/$taskId');
      return response.data;
    } catch (e) {
      return {'status': 'error'};
    }
  }

  // Note Retrieval (Using Database Endpoints for isolation)
  static Future<List<dynamic>> getGeneratedNotes() async {
    try {
      // Changed from /notes/generated to /notes
      final response = await _dio.get('/notes');
      return response.data;
    } catch (e) {
      return [];
    }
  }

  static Future<String> getNoteContent(int noteId) async {
    try {
      final response = await _dio.get('/notes/$noteId');
      return response.data['summary_text']?.toString() ?? "No content found";
    } catch (e) {
      return "Error loading content";
    }
  }

  // Recommendations
  static Future<List<dynamic>> getRecommendations() async {
    try {
      final response = await _dio.get('/recommendations');
      return response.data;
    } catch (e) {
      return [];
    }
  }
}
