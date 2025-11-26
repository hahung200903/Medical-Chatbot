import 'package:flutter/material.dart';
import 'package:dash_chat_2/dash_chat_2.dart';

class ChatScreen extends StatefulWidget {
  final String title;
  const ChatScreen({super.key, required this.title});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  ChatUser user = ChatUser(id: '1', firstName: 'Tôi');
  ChatUser bot = ChatUser(
    id: '2',
    firstName: 'Bác sĩ AI',
    profileImage: "https://cdn-icons-png.flaticon.com/512/3774/3774299.png",
  );

  List<ChatMessage> messages = [];

  @override
  void initState() {
    super.initState();
    messages = [
      ChatMessage(
        text:
            "Chào bạn, tôi là trợ lý y tế ảo. Bạn đang gặp vấn đề gì về sức khỏe?",
        user: bot,
        createdAt: DateTime.now(),
      ),
    ];
  }

  void onSend(ChatMessage message) {
    setState(() {
      messages.insert(0, message);
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) {
          setState(() {
            messages.insert(
              0,
              ChatMessage(
                text: "Triệu chứng '${message.text}' cần theo dõi thêm.",
                user: bot,
                createdAt: DateTime.now(),
              ),
            );
          });
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: DashChat(
        currentUser: user,
        onSend: onSend,
        messages: messages,
        inputOptions: const InputOptions(
          inputDecoration: InputDecoration(
            hintText: "Nhập triệu chứng...",
            border: InputBorder.none,
            isDense: true,
          ),
          sendButtonBuilder: null,
        ),
        messageOptions: const MessageOptions(
          currentUserContainerColor: Colors.teal,
          containerColor: Colors.grey,
          textColor: Colors.white,
        ),
      ),
    );
  }
}
