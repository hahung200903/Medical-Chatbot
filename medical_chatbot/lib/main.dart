import 'package:flutter/material.dart';
import 'package:medical_chatbot/features/auth/login_screen.dart';

void main() {
  runApp(const MedicalChatbotApp());
}

class MedicalChatbotApp extends StatelessWidget {
  const MedicalChatbotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Medical Chatbot',
      debugShowCheckedModeBanner: false,

      // --- CẤU HÌNH GIAO DIỆN CHUNG (THEME) ---
      theme: ThemeData(
        // 1. Màu chủ đạo toàn app
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.teal,
          primary: Colors.teal,
        ),
        useMaterial3: true,

        // 2. AppBar mặc định
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
          centerTitle: true,
        ),

        // 3. Nút ElevatedButton
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.teal,
            foregroundColor: Colors.white,
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(10)),
            ),
          ),
        ),
      ),

      home: const LoginScreen(),
    );
  }
}
