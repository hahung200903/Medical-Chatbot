import 'package:flutter/material.dart';

class HistoryCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const HistoryCard({
    super.key,
    required this.title,
    this.subtitle = "Bấm để xem lại...",
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      elevation: 2, 
      child: ListTile(
        leading: const CircleAvatar(
          backgroundColor: Colors.teal,
          child: Icon(Icons.medical_services, color: Colors.white),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}
