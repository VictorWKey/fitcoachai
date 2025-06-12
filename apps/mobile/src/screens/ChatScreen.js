import React, { useState } from 'react';
import {
  View,
  TextInput,
  FlatList,
  ActivityIndicator,
  TouchableOpacity,
  Text,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  Dimensions,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useChat } from '../hooks/useChat';
import { ChatBubble } from '../components';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';

const screenWidth = Dimensions.get('window').width;

const ChatScreen = () => {
  const [message, setMessage] = useState('');
  const { messages, isLoading, handleSendMessage, flatListRef } = useChat();
  const insets = useSafeAreaInsets();

  const onSend = () => {
    if (!message.trim()) return;
    handleSendMessage(message);
    setMessage('');
  };

  const renderMessage = ({ item }) => (
    <ChatBubble message={item.content} isUser={item.role === 'user'} />
  );

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.inner}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.header}>
          <Text style={styles.headerText}>Chat with AI</Text>
        </View>

        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item, idx) => (item.id ? item.id.toString() : idx.toString())}
          renderItem={renderMessage}
          contentContainerStyle={styles.listContent}
          inverted={false} // Removed inverted so that messages appear from the bottom
          onContentSizeChange={() => flatListRef.current.scrollToEnd({ animated: true })} // Auto-scroll to bottom
        />

        {isLoading && <ActivityIndicator size="small" style={styles.loading} />}

        <View style={[styles.inputContainer, { paddingBottom: insets.bottom || 10 }]}>
          <TextInput
            style={styles.input}
            placeholder="Escribe un mensaje..."
            value={message}
            onChangeText={setMessage}
            onSubmitEditing={onSend}
            returnKeyType="send"
            placeholderTextColor={COLORS.textLight}
          />
          <TouchableOpacity onPress={onSend} style={styles.sendButton}>
            <Text style={styles.sendText}>Enviar</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  inner: {
    flex: 1,
    justifyContent: 'space-between',
  },
  header: {
    paddingTop: SPACING.md,
    paddingBottom: SPACING.sm,
    backgroundColor: COLORS.primary,
    borderBottomLeftRadius: BORDER_RADIUS.lg,
    borderBottomRightRadius: BORDER_RADIUS.lg,
    alignItems: 'center',
  },
  headerText: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: '#fff',
  },
  listContent: {
    padding: SPACING.md,
  },
  loading: {
    marginVertical: SPACING.sm,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderColor: '#eee',
    padding: SPACING.md,
    backgroundColor: COLORS.background,
  },
  input: {
    flex: 1,
    backgroundColor: COLORS.input,
    borderRadius: BORDER_RADIUS.lg,
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.sm,
    fontSize: FONT_SIZE.md,
    color: COLORS.textDark,
    marginRight: SPACING.sm,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 1,
  },
  sendButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    borderRadius: BORDER_RADIUS.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: FONT_SIZE.md + 1,
  },
});

export default ChatScreen;
