import React from 'react';
import { Pressable, Text, StyleSheet, ActivityIndicator } from 'react-native';

const Button = ({ 
  title, 
  onPress, 
  type = 'primary', 
  loading = false,
  disabled = false 
}) => (
  <Pressable
    style={({ pressed }) => [
      styles.button,
      type === 'secondary' ? styles.secondaryButton : styles.primaryButton,
      (loading || disabled) && styles.disabledButton,
      pressed && styles.buttonPressed
    ]}
    onPress={onPress}
    disabled={loading || disabled}
    android_ripple={{ color: type === 'primary' ? '#0056b3' : '#e6f0ff' }}
  >
    {loading ? (
      <ActivityIndicator color={type === 'primary' ? '#fff' : '#007AFF'} size="small" />
    ) : (
      <Text style={[
        styles.buttonText,
        type === 'secondary' ? styles.secondaryButtonText : styles.primaryButtonText
      ]}>
        {title}
      </Text>
    )}
  </Pressable>
);

const styles = StyleSheet.create({
  button: {
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 10,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  disabledButton: {
    opacity: 0.7,
  },
  buttonPressed: {
    opacity: 0.85,
    transform: [{ scale: 0.98 }],
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  primaryButtonText: {
    color: '#fff',
  },
  secondaryButtonText: {
    color: '#007AFF',
  },
});

export default Button; 