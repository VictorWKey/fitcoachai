import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { COLORS, BORDER_RADIUS, FONT_SIZE, SHADOWS } from '../constants/theme';

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
    borderRadius: BORDER_RADIUS.lg,
    padding: 12,
    marginVertical: 5,
    ...SHADOWS.light,
  },
  userBubble: {
    backgroundColor: COLORS.userBubble,
    alignSelf: 'flex-end',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    backgroundColor: COLORS.aiBubble,
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 4,
  },
  chatText: {
    fontSize: FONT_SIZE.md,
    lineHeight: 22,
  },
  userChatText: {
    color: COLORS.userText,
    fontWeight: '500',
  },
  aiChatText: {
    color: COLORS.aiText,
  },
});

export default ChatBubble; 