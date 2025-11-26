import 'package:flutter/material.dart';
import '../../core/widgets/history_card.dart';
import '../chat/chat_screen.dart';
import '../auth/login_screen.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<String> chatSessions = [
      "Tư vấn đau đầu (10:30 AM)",
      "Đau dạ dày cấp (Hôm qua)",
      "Hỏi về vắc xin cúm (20/11)",
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text("Lịch sử tư vấn"),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: ListView.builder(
        itemCount: chatSessions.length,
        itemBuilder: (context, index) {
          // --- SỬ DỤNG WIDGET TÁI SỬ DỤNG ---
          return HistoryCard(
            title: chatSessions[index],
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ChatScreen(title: chatSessions[index]),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Colors.teal,
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ChatScreen(title: "Cuộc tư vấn mới"),
            ),
          );
        },
      ),
    );
  }
}
