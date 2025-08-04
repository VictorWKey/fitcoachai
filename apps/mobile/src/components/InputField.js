import React from 'react';
import { View, TextInput, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../constants/theme';

const InputField = ({ 
  icon, 
  placeholder, 
  value, 
  onChangeText, 
  secureTextEntry = false,
  autoCapitalize = "none",
  keyboardType = "default",
  error = false,
  multiline = false,
  numberOfLines = 1,
  style,
  ...props
}) => (
  <View style={[
    styles.inputContainer, 
    error && styles.inputError, 
    multiline && styles.multilineContainer,
    style
  ]}>
    {icon && <Ionicons name={icon} size={22} color={error ? COLORS.error : COLORS.primary} style={styles.inputIcon} />}
    <TextInput
      style={[styles.input, multiline && styles.textArea]}
      placeholder={placeholder}
      placeholderTextColor={COLORS.textLight}
      value={value}
      onChangeText={onChangeText}
      secureTextEntry={secureTextEntry}
      autoCapitalize={autoCapitalize}
      keyboardType={keyboardType}
      multiline={multiline}
      numberOfLines={numberOfLines}
      {...props}
    />
  </View>
);

const styles = StyleSheet.create({
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
    paddingVertical: 12,
    paddingHorizontal: 15,
  },
  multilineContainer: {
    alignItems: 'flex-start',
  },
  inputError: {
    borderColor: COLORS.error,
    borderWidth: 2,
  },
  inputIcon: {
    marginRight: 10,
    marginTop: 2, // Pequeño ajuste para alineación
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: COLORS.textDark,
  },
  textArea: {
    textAlignVertical: 'top',
    minHeight: 80,
  },
});

export default InputField; 