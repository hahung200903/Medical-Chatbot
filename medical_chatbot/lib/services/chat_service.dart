import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  static const String baseUrl = "http://34.205.252.57";

  Future<String?> sendMessage({
    required String text,
    required String conversationId,
  }) async {
    try {
      final url = Uri.parse('$baseUrl/chat');

      final Map<String, dynamic> body = {
        "query": text,
        "conversation_id": conversationId,
        "use_cache": false,
      };

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));

        return data['answer'] as String? ?? "Máy chủ không gửi câu trả lời.";
      } else {
        // Lỗi từ server (500, 422, 404, ...)
        print("Server Error: ${response.statusCode} - ${response.body}");
        return "Xin lỗi, hệ thống đang gặp sự cố. (Mã lỗi: ${response.statusCode})";
      }
    } catch (e) {
      // Không kết nối được (mạng, DNS, server down, ...)
      print("Connection Error: $e");
      return "Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại Backend.";
    }
  }
}
