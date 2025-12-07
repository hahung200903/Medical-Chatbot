import 'package:flutter/material.dart';
import 'package:dash_chat_2/dash_chat_2.dart';
import '../../services/chat_service.dart';

class ChatScreen extends StatefulWidget {
  final String title;
  final String conversationId;
  final List<ChatMessage>? initialMessages;

  const ChatScreen({
    super.key,
    required this.title,
    required this.conversationId,
    this.initialMessages,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatService _chatService = ChatService();

  late final ChatUser user;
  late final ChatUser bot;

  List<ChatMessage> messages = [];
  bool isTyping = false;

  bool waitingForFeedback = false;

  @override
  void initState() {
    super.initState();

    user = ChatUser(id: '1', firstName: 'Tôi');
    bot = ChatUser(
      id: '2',
      firstName: 'Bác sĩ AI',
      profileImage: "https://cdn-icons-png.flaticon.com/512/3774/3774299.png",
    );

    if (widget.initialMessages != null && widget.initialMessages!.isNotEmpty) {
      messages = List<ChatMessage>.from(widget.initialMessages!);
    } else {
      messages = [
        ChatMessage(
          text:
              "Chào bạn, tôi là trợ lý y tế ảo. Tôi có thể giúp gì cho bạn hôm nay?",
          user: bot,
          createdAt: DateTime.now(),
        ),
      ];
    }
  }

  void onSend(ChatMessage message) async {
    setState(() {
      messages.insert(0, message);
      isTyping = true;
    });

    Map<String, dynamic> response;

    /// Nếu đang chờ feedback
    if (waitingForFeedback) {
      response = await _chatService.sendFeedback(
        feedback: message.text,
        conversationId: widget.conversationId,
      );
    }

    else {
      response = await _chatService.sendMessage(
        text: message.text,
        conversationId: widget.conversationId,
      );
    }

    waitingForFeedback = response["needs_feedback"] == true;

    if (!mounted) return;

    setState(() {
      isTyping = false;

      messages.insert(
        0,
        ChatMessage(
          text: response["answer"] ?? "Có lỗi xảy ra, vui lòng thử lại.",
          user: bot,
          createdAt: DateTime.now(),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        Navigator.pop(context, messages);
        return false;
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.title),
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
        ),
        body: DashChat(
          currentUser: user,
          onSend: onSend,
          messages: messages,
          typingUsers: isTyping ? [bot] : [],
          inputOptions: InputOptions(
            inputDecoration: InputDecoration(
              hintText: "Nhập triệu chứng hoặc câu hỏi...",
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(24),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(24),
                borderSide: const BorderSide(
                  color: Colors.teal,
                  width: 1.4,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(24),
                borderSide: const BorderSide(
                  color: Colors.teal,
                  width: 2,
                ),
              ),
            ),
          ),
          messageOptions: const MessageOptions(
            currentUserContainerColor: Colors.teal,
            containerColor: Colors.grey,
            textColor: Colors.white,
            showOtherUsersAvatar: true,
            showTime: true,
          ),
        ),
      ),
    );
  }
}
