// Basic Flutter widget test for Study Notes App.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:study_notes_app/main.dart';

void main() {
  testWidgets('App loads successfully', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const StudyNotesApp());

    // Verify that the app title is displayed
    expect(find.text('YouTube Study Notes'), findsAny);
  });
}
