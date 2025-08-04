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
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS, COMMON_STYLES } from '../constants/theme';

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

  // Función mejorada para generar claves únicas
  const keyExtractor = (item, index) => {
    // Si el item tiene un ID, usarlo
    if (item.id) {
      return item.id.toString();
    }
    // Si no tiene ID, usar una combinación de índice y timestamp
    return `msg_${index}_${Date.now()}`;
  };

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
          keyExtractor={keyExtractor}
          renderItem={renderMessage}
          contentContainerStyle={styles.listContent}
          inverted={false}
          onContentSizeChange={() => flatListRef.current.scrollToEnd({ animated: true })}
        />

        {isLoading && <ActivityIndicator size="small" color={COLORS.primary} style={styles.loading} />}

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
    ...SHADOWS.medium,
  },
  headerText: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.background,
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
    borderColor: COLORS.card,
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
    ...SHADOWS.light,
    borderWidth: 1,
    borderColor: COLORS.card,
  },
  sendButton: {
    ...COMMON_STYLES.buttonPrimary,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
  },
  sendText: {
    color: COLORS.background,
    fontWeight: '700',
    fontSize: FONT_SIZE.md,
  },
});

export default ChatScreen;
