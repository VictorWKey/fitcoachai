import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const WorkoutsScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Aquí podrás ver tus entrenamientos y exercise logs.</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  text: {
    fontSize: 16,
  },
});

export default WorkoutsScreen;
