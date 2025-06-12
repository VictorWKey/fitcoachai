import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';

const ChatBubble = ({ message, isUser }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, translateY]);

  return (
    <Animated.View
      style={[
        styles.chatBubble,
        isUser ? styles.userBubble : styles.aiBubble,
        { opacity: fadeAnim, transform: [{ translateY }] }
      ]}
    >
      <Text style={[
        styles.chatText,
        isUser ? styles.userChatText : styles.aiChatText
      ]}>
        {message}
      </Text>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  chatBubble: {
    maxWidth: '80%',
    borderRadius: 18,
    padding: 12,
    marginVertical: 5,
  },
  userBubble: {
    backgroundColor: '#007AFF',
    alignSelf: 'flex-end',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    backgroundColor: '#e6e6e6',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 4,
  },
  chatText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userChatText: {
    color: '#fff',
  },
  aiChatText: {
    color: '#333',
  },
});

export default ChatBubble; 