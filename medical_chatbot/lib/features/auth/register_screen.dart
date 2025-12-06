import 'package:flutter/material.dart';
import '../../core/widgets/custom_text_field.dart';
import '../../core/widgets/primary_button.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passController = TextEditingController();
  final TextEditingController _confirmPassController = TextEditingController();

  void _handleRegister() {
    final name = _nameController.text.trim();
    final email = _emailController.text.trim();
    final pass = _passController.text;
    final confirmPass = _confirmPassController.text;

    if (name.isEmpty || email.isEmpty || pass.isEmpty || confirmPass.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Vui lòng nhập đầy đủ thông tin!')),
      );
      return;
    }

    if (pass != confirmPass) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Mật khẩu nhập lại không khớp!')),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Đăng ký thành công! Vui lòng đăng nhập.'),
        backgroundColor: Colors.teal,
      ),
    );

    Navigator.pop(context);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passController.dispose();
    _confirmPassController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal[50],
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.person_add_alt_1, size: 80, color: Colors.teal),
              const SizedBox(height: 20),
              const Text(
                "Tạo tài khoản mới",
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.teal,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                "Điền thông tin để tham gia cùng chúng tôi",
                style: TextStyle(color: Colors.grey, fontSize: 16),
              ),
              const SizedBox(height: 40),

              CustomTextField(
                label: "Họ và tên",
                icon: Icons.person,
                controller: _nameController,
              ),
              const SizedBox(height: 15),
              CustomTextField(
                label: "Email",
                icon: Icons.email,
                keyboardType: TextInputType.emailAddress,
                controller: _emailController,
              ),
              const SizedBox(height: 15),
              CustomTextField(
                label: "Mật khẩu",
                icon: Icons.lock,
                isPassword: true,
                controller: _passController,
              ),
              const SizedBox(height: 15),
              CustomTextField(
                label: "Nhập lại mật khẩu",
                icon: Icons.lock_outline,
                isPassword: true,
                textInputAction: TextInputAction.done,
                controller: _confirmPassController,
              ),
              const SizedBox(height: 30),

              PrimaryButton(
                text: "Đăng ký",
                onPressed: _handleRegister,
              ),

              const SizedBox(height: 20),

              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text("Đã có tài khoản?"),
                  TextButton(
                    onPressed: () {
                      Navigator.pop(context); // Quay lại màn hình trước
                    },
                    child: const Text(
                      "Đăng nhập ngay",
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
