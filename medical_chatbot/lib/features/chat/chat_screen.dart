import 'package:flutter/material.dart';
import 'package:dash_chat_2/dash_chat_2.dart';
import '../../services/chat_service.dart';

class ChatScreen extends StatefulWidget {
  final String title;
  final String conversationId;
  final List<ChatMessage> initialMessages;

  const ChatScreen({
    super.key,
    required this.title,
    required this.conversationId,
    this.initialMessages = const [], // Mặc định là rỗng
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatService _chatService = ChatService();

  final ChatUser _user = ChatUser(
    id: 'user',
    firstName: 'Bạn',
  );

  final ChatUser _bot = ChatUser(
    id: 'bot',
    firstName: 'Bác sĩ AI',
  );

  final TextEditingController _inputController = TextEditingController();
  final FocusNode _inputFocus = FocusNode();

  List<ChatMessage> _messages = [];
  bool _isTyping = false;

  @override
  void initState() {
    super.initState();
    // Nếu có tin nhắn cũ được truyền vào, load nó.
    // Nếu không cuộc chat mới, thì hiển thị mặc định.
    if (widget.initialMessages.isNotEmpty) {
      _messages = List.from(widget.initialMessages);
    } else {
      _messages = [
        ChatMessage(
          text:
              'Chào bạn, tôi là trợ lý y tế ảo. Tôi có thể giúp gì cho bạn hôm nay?',
          user: _bot,
          createdAt: DateTime.now(),
        ),
      ];
    }
  }

  @override
  void dispose() {
    _inputController.dispose();
    _inputFocus.dispose();
    super.dispose();
  }

  // Hàm xử lý khi nhấn nút Back trên AppBar
  void _onBackPress() {
    // Trả về danh sách tin nhắn hiện tại cho HistoryScreen
    Navigator.pop(context, _messages);
  }

  Future<void> _sendFromInput() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;

    _inputController.clear();

    final msg = ChatMessage(
      text: text,
      user: _user,
      createdAt: DateTime.now(),
    );

    await _handleSend(msg);
  }

  Future<void> _handleSend(ChatMessage message) async {
    setState(() {
      _messages.insert(0, message);
      _isTyping = true;
    });

    try {
      final String? replyText = await _chatService.sendMessage(
        text: message.text,
        conversationId: widget.conversationId,
      );

      final String safeReplyText =
          replyText ?? 'Xin lỗi, hiện không nhận được phản hồi từ máy chủ.';

      final botReply = ChatMessage(
        text: safeReplyText,
        user: _bot,
        createdAt: DateTime.now(),
      );

      setState(() {
        _messages.insert(0, botReply);
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Có lỗi xảy ra, vui lòng thử lại.'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isTyping = false;
        });
      }
    }

    _inputFocus.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvoked: (didPop) {
        if (didPop) return;
        _onBackPress();
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.title),
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: _onBackPress, // Gọi hàm trả dữ liệu về
          ),
        ),
        body: Column(
          children: [
            Expanded(
              child: DashChat(
                currentUser: _user,
                messages: _messages,
                onSend: (_) {},
                readOnly: true,
                typingUsers: _isTyping ? [_bot] : const [],
                messageOptions: const MessageOptions(
                  currentUserContainerColor: Colors.teal,
                  containerColor: Colors.grey,
                  textColor: Colors.white,
                  showOtherUsersAvatar: true,
                  showTime: true,
                ),
              ),
            ),
            SafeArea(
              top: false,
              child: Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _inputController,
                        focusNode: _inputFocus,
                        textInputAction: TextInputAction.send,
                        onSubmitted: (_) => _sendFromInput(),
                        decoration: InputDecoration(
                          hintText: 'Nhập triệu chứng hoặc câu hỏi...',
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 10,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: _sendFromInput,
                      icon: const Icon(Icons.send),
                      color: Colors.teal,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
