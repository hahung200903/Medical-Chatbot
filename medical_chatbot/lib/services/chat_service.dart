import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  static const String baseUrl = "http://34.205.252.57";

  /// Gửi câu hỏi lần đầu
  Future<Map<String, dynamic>> sendMessage({
    required String text,
    required String conversationId,
  }) async {
    try {
      print(
          "➡️ Sending message: '$text' with conversation_id: $conversationId");

      final url = Uri.parse('$baseUrl/chat');

      final body = {
        "query": text,
        "conversation_id": conversationId,
        "use_cache": false,
      };

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(body),
      );

      final decoded = jsonDecode(utf8.decode(response.bodyBytes));

      return {
        "success": response.statusCode == 200,
        "answer": decoded["answer"] ?? "",
        "needs_feedback": decoded["needs_feedback"] ?? false,
      };
    } catch (e) {
      print("Connection Error: $e");

      return {
        "success": false,
        "answer": "Không thể kết nối đến máy chủ.",
        "needs_feedback": false,
      };
    }
  }

  /// Gửi phản hồi clarification (feedback)
  Future<Map<String, dynamic>> sendFeedback({
    required String feedback,
    required String conversationId,
  }) async {
    try {
      print(
          "➡️ Sending FEEDBACK '$feedback' for conversation_id: $conversationId");

      final url = Uri.parse('$baseUrl/chat/feedback');

      final body = {
        "conversation_id": conversationId,
        "user_feedback": feedback,
      };

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(body),
      );

      final decoded = jsonDecode(utf8.decode(response.bodyBytes));

      return {
        "success": response.statusCode == 200,
        "answer": decoded["answer"] ?? "",
        "needs_feedback": decoded["needs_feedback"] ?? false,
      };
    } catch (e) {
      print("Connection Error FEEDBACK: $e");

      return {
        "success": false,
        "answer": "Không thể kết nối đến máy chủ.",
        "needs_feedback": false,
      };
    }
  }
}
