import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING } from '../constants/theme';

/**
 * Componente de barra de navegación inferior personalizada
 * Maneja correctamente los insets de seguridad para evitar superposición con la barra de gestos
 */
const CustomTabBar = ({ state, descriptors, navigation }) => {
  const insets = useSafeAreaInsets();

  return (
    <View style={[
      styles.container,
      { paddingBottom: Math.max(SPACING.sm, insets.bottom), height: 60 + insets.bottom }
    ]}>
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];
        const label = options.tabBarLabel || options.title || route.name;

        const isFocused = state.index === index;

        let iconName;
        if (route.name === 'index') {
          iconName = isFocused ? 'chatbubble' : 'chatbubble-outline';
        } else if (route.name === 'workouts') {
          iconName = isFocused ? 'barbell' : 'barbell-outline';
        } else if (route.name === 'profile') {
          iconName = isFocused ? 'person' : 'person-outline';
        }

        const onPress = () => {
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            navigation.navigate(route.name);
          }
        };

        return (
          <TouchableOpacity
            key={route.key}
            accessibilityRole="button"
            accessibilityState={isFocused ? { selected: true } : {}}
            accessibilityLabel={options.tabBarAccessibilityLabel}
            testID={options.tabBarTestID}
            onPress={onPress}
            style={styles.tabButton}
          >
            <Ionicons
              name={iconName}
              size={24}
              color={isFocused ? COLORS.primary : COLORS.textLight}
            />
            <Text style={[
              styles.tabLabel,
              { color: isFocused ? COLORS.primary : COLORS.textLight }
            ]}>
              {label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: COLORS.card,
    borderTopWidth: 1,
    borderTopColor: COLORS.cardLight,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: SPACING.sm,
  },
  tabLabel: {
    fontSize: FONT_SIZE.xs,
    marginTop: 2,
  },
});

export default CustomTabBar; 