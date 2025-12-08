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

  late TextEditingController _searchController;
  List<Map<String, dynamic>> _filteredSessions = [];

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();

    _filteredSessions = List.from(_chatSessions);

    _searchController.addListener(() {
      final keyword = _searchController.text.toLowerCase();
      setState(() {
        _filteredSessions = _chatSessions.where((session) {
          final title = (session["title"] ?? "").toString().toLowerCase();
          return title.contains(keyword);
        }).toList();
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

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

      final keyword = _searchController.text.toLowerCase();
      _filteredSessions = _chatSessions.where((session) {
        final t = (session["title"] ?? "").toString().toLowerCase();
        return t.contains(keyword);
      }).toList();
    });
  }

  void _deleteSession(Map<String, dynamic> session) {
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
                final String id = session['id'] as String;

                _chatSessions.removeWhere((s) => s['id'] == id);

                final keyword = _searchController.text.toLowerCase();
                _filteredSessions = _chatSessions.where((s) {
                  final t = (s["title"] ?? "").toString().toLowerCase();
                  return t.contains(keyword);
                }).toList();
              });
              Navigator.pop(ctx);
            },
            child: const Text("Xóa"),
          ),
        ],
      ),
    );
  }

  void _renameSession(Map<String, dynamic> session) {
    final TextEditingController renameController =
        TextEditingController(text: session['title'] as String? ?? "");

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
                  final String id = session['id'] as String;

                  // Cập nhật trong danh sách gốc
                  final masterIndex =
                      _chatSessions.indexWhere((s) => s['id'] == id);
                  if (masterIndex != -1) {
                    _chatSessions[masterIndex]['title'] =
                        renameController.text.trim();
                  }

                  // Cập nhật lại danh sách đã lọc theo search hiện tại
                  final keyword = _searchController.text.toLowerCase();
                  _filteredSessions = _chatSessions.where((s) {
                    final t = (s["title"] ?? "").toString().toLowerCase();
                    return t.contains(keyword);
                  }).toList();
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
      body: Column(
        children: [
          // Thanh tìm kiếm
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: "Tìm kiếm cuộc trò chuyện",
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                contentPadding:
                    const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          Expanded(
            child: _filteredSessions.isEmpty
                ? const Center(
                    child: Text("Không tìm thấy cuộc trò chuyện nào"),
                  )
                : ListView.builder(
                    itemCount: _filteredSessions.length,
                    itemBuilder: (context, index) {
                      final session = _filteredSessions[index];

                      return HistoryCard(
                        title: session['title'] as String,
                        onTap: () async {
                          // Lấy danh sách tin nhắn hiện tại
                          final List<ChatMessage> currentMsgs =
                              (session['messages'] as List<ChatMessage>?) ?? [];

                          final result = await Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => ChatScreen(
                                title: session['title'] as String,
                                conversationId: session['id'] as String,
                                initialMessages: currentMsgs,
                              ),
                            ),
                          );

                          // Nếu có dữ liệu trả về, cập nhật lại vào bộ nhớ
                          if (result != null &&
                              result is List<ChatMessage>) {
                            setState(() {
                              final String id = session['id'] as String;

                              // cập nhật trong danh sách gốc
                              final masterIndex = _chatSessions
                                  .indexWhere((s) => s['id'] == id);
                              if (masterIndex != -1) {
                                _chatSessions[masterIndex]['messages'] = result;
                              }

                              // cập nhật trong danh sách đã lọc
                              _filteredSessions[index]['messages'] = result;
                            });
                          }
                        },
                        onEdit: () => _renameSession(session),
                        onDelete: () => _deleteSession(session),
                      );
                    },
                  ),
          ),
        ],
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
