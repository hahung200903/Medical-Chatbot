import 'package:flutter/material.dart';
import 'package:dash_chat_2/dash_chat_2.dart';
import '../../core/widgets/history_card.dart';
import '../chat/chat_screen.dart';
import '../auth/login_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final List<Map<String, dynamic>> _chatSessions = [
    {
      "title": "Tư vấn đau đầu (10:30 AM)",
      "id": "session_001",
      "messages": <ChatMessage>[],
    },
    {
      "title": "Đau dạ dày cấp (Hôm qua)",
      "id": "session_002",
      "messages": <ChatMessage>[],
    },
    {
      "title": "Hỏi về vắc xin cúm (20/11)",
      "id": "session_003",
      "messages": <ChatMessage>[],
    },
  ];

  // Thêm session mới
  void _addNewSession(String title, String id, List<ChatMessage> messages) {
    setState(() {
      _chatSessions.insert(
        0,
        {
          "title": title,
          "id": id,
          "messages": messages,
        },
      );
    });
  }

  void _deleteSession(int index) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Xác nhận xóa"),
        content:
            const Text("Bạn có chắc chắn muốn xóa cuộc trò chuyện này không?"),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("Hủy"),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _chatSessions.removeAt(index);
              });
              Navigator.pop(ctx);
            },
            child: const Text("Xóa"),
          ),
        ],
      ),
    );
  }

  void _renameSession(int index) {
    final TextEditingController renameController =
        TextEditingController(text: _chatSessions[index]['title']);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Đổi tên cuộc trò chuyện"),
        content: TextField(
          controller: renameController,
          autofocus: true,
          decoration: const InputDecoration(hintText: "Nhập tên mới"),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("Hủy"),
          ),
          ElevatedButton(
            onPressed: () {
              if (renameController.text.trim().isNotEmpty) {
                setState(() {
                  _chatSessions[index]['title'] = renameController.text.trim();
                });
                Navigator.pop(ctx);
              }
            },
            child: const Text("Lưu"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Lịch sử tư vấn"),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => const LoginScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: ListView.builder(
        itemCount: _chatSessions.length,
        itemBuilder: (context, index) {
          final session = _chatSessions[index];

          return HistoryCard(
            title: session['title']!,
            onTap: () async {
              // Lấy danh sách tin nhắn hiện tại
              final List<ChatMessage> currentMsgs =
                  (session['messages'] as List<ChatMessage>?) ?? [];

              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ChatScreen(
                    title: session['title']!,
                    conversationId: session['id']!,
                    initialMessages: currentMsgs,
                  ),
                ),
              );

              // Nếu có dữ liệu trả về, cập nhật lại vào bộ nhớ
              if (result != null && result is List<ChatMessage>) {
                setState(() {
                  _chatSessions[index]['messages'] = result;
                });
              }
            },
            onEdit: () => _renameSession(index),
            onDelete: () => _deleteSession(index),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Colors.teal,
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () async {
          // Tạo ID mới
          final String newId =
              "session_${DateTime.now().millisecondsSinceEpoch}";
          final now = TimeOfDay.now();
          final String newTitle = "Cuộc tư vấn lúc ${now.format(context)}";

          // Mở ChatScreen mới
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ChatScreen(
                title: newTitle,
                conversationId: newId,
              ),
            ),
          );

          if (result != null && result is List<ChatMessage>) {
            _addNewSession(newTitle, newId, result);
          }
        },
      ),
    );
  }
}
