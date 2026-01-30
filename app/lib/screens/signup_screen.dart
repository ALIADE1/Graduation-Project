import 'package:flutter/material.dart';
import '../services/api_service.dart'; // Import our API service

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  // Controllers to capture user input
  final _emailController = TextEditingController();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _ageController = TextEditingController();
  String? _selectedGender;
  
  final _formKey = GlobalKey<FormState>(); // Key for form validation
  bool _isLoading = false; // To show loading spinner

  // Function to handle the Signup button press
  Future<void> _handleSignup() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      // Call the API
      bool success = await ApiService.signup(
        _emailController.text,
        _usernameController.text,
        _passwordController.text,
        age: int.tryParse(_ageController.text),
        gender: _selectedGender,
      );

      setState(() {
        _isLoading = false;
      });

      // Show result to the user
      if (!mounted) return; // Check if screen is still visible

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Account Created Successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        // Here we can navigate to Login Screen later
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('❌ Signup Failed. Username or Email might actally exist.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Email Input
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email'),
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Please enter email';
                  if (!value.contains('@')) return 'Invalid email format';
                  return null;
                },
              ),
              const SizedBox(height: 10),

              // Username Input
              TextFormField(
                controller: _usernameController,
                decoration: const InputDecoration(labelText: 'Username'),
                validator: (value) => value!.isEmpty ? 'Please enter username' : null,
              ),
              const SizedBox(height: 10),

              // Password Input
              TextFormField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Password'),
                obscureText: true, // Hide password
                validator: (value) => value!.length < 6 ? 'Password must be 6+ chars' : null,
              ),
              const SizedBox(height: 10),

              // Age Input
              TextFormField(
                controller: _ageController,
                decoration: const InputDecoration(labelText: 'Age'),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    if (int.tryParse(value) == null) return 'Enter a valid number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 10),

              // Gender Input
              DropdownButtonFormField<String>(
                value: _selectedGender,
                decoration: const InputDecoration(labelText: 'Gender'),
                items: ['Male', 'Female', 'Other']
                    .map((label) => DropdownMenuItem(
                          value: label,
                          child: Text(label),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedGender = value;
                  });
                },
              ),
              const SizedBox(height: 20),

              // Signup Button
              _isLoading
                  ? const CircularProgressIndicator()
                  : ElevatedButton(
                      onPressed: _handleSignup,
                      child: const Text('Sign Up'),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}