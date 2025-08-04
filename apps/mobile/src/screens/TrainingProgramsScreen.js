import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  Alert,
  Pressable,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { FontAwesome5, Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS, COMMON_STYLES } from '../constants/theme';
import { useTrainingPrograms } from '../hooks/useTrainingPrograms';
import { LoadingIndicator } from '../components';
import CreateProgramModal from '../components/CreateProgramModal';
import ProgramCard from '../components/ProgramCard';

const TrainingProgramsScreen = () => {
  const router = useRouter();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [showOptionsModal, setShowOptionsModal] = useState(false);

  const {
    programs,
    isLoading,
    error,
    fetchPrograms,
    deleteProgram,
    cloneProgram,
    clearError,
  } = useTrainingPrograms();

  // Función para navegar a las sesiones del programa
  const handleProgramPress = (program) => {
    router.push({
      pathname: '/program-sessions',
      params: { programId: program.id.toString() }
    });
  };

  // Función para manejar la creación de programa
  const handleCreateProgram = () => {
    setShowCreateModal(true);
  };

  // Función para manejar las opciones del programa
  const handleProgramOptions = (program) => {
    setSelectedProgram(program);
    setShowOptionsModal(true);
  };

  // Función para eliminar programa
  const handleDeleteProgram = () => {
    Alert.alert(
      'Eliminar Programa',
      `¿Estás seguro de que deseas eliminar "${selectedProgram.name}"?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            await deleteProgram(selectedProgram.id);
            setShowOptionsModal(false);
            setSelectedProgram(null);
          },
        },
      ]
    );
  };

  // Función para clonar programa
  const handleCloneProgram = async () => {
    await cloneProgram(selectedProgram.id);
    setShowOptionsModal(false);
    setSelectedProgram(null);
  };

  // Renderizar cada programa
  // Función para ver sesiones del programa
  const handleViewSessions = (program) => {
    router.push({
      pathname: '/program-sessions',
      params: { programId: program.id.toString() }
    });
  };

  const renderProgram = ({ item }) => (
    <ProgramCard
      program={item}
      onPress={() => handleProgramPress(item)}
      onOptionsPress={() => handleProgramOptions(item)}
      onViewSessions={() => handleViewSessions(item)}
    />
  );

  // Renderizar mensaje vacío
  const renderEmptyMessage = () => (
    <View style={styles.emptyContainer}>
      <FontAwesome5 name="calendar-alt" size={48} color={COLORS.textLight} />
      <Text style={styles.emptyText}>
        No tienes programas creados.{'\n'}
        ¡Crea tu primer programa de entrenamiento!
      </Text>
    </View>
  );

  if (isLoading && programs.length === 0) {
    return <LoadingIndicator />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Programas de Entrenamiento</Text>
        <TouchableOpacity
          style={styles.createButton}
          onPress={handleCreateProgram}
        >
          <Ionicons name="add" size={24} color={COLORS.background} />
        </TouchableOpacity>
      </View>

      <FlatList
        data={programs}
        renderItem={renderProgram}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={[
          styles.listContainer,
          programs.length === 0 && styles.emptyListContainer,
          { 
            // paddingTop: sessionPadding + SPACING.md,
            // paddingBottom: insets.bottom + SPACING.lg 
          }
        ]}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        showsVerticalScrollIndicator={false}
        refreshing={isLoading}
        onRefresh={fetchPrograms}
        ListEmptyComponent={renderEmptyMessage}
      />

      {/* Modal de Creación */}
      <CreateProgramModal
        visible={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => {
          setShowCreateModal(false);
          fetchPrograms();
        }}
      />

      {/* Modal de Opciones */}
      <Modal
        visible={showOptionsModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowOptionsModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.optionsModal}>
            <Text style={styles.optionsTitle}>
              {selectedProgram?.name}
            </Text>

            <TouchableOpacity
              style={styles.optionButton}
              onPress={handleCloneProgram}
            >
              <Ionicons name="copy" size={20} color={COLORS.textDark} />
              <Text style={styles.optionText}>Clonar</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.optionButton, styles.dangerButton]}
              onPress={handleDeleteProgram}
            >
              <Ionicons name="trash" size={20} color={COLORS.error} />
              <Text style={[styles.optionText, styles.dangerText]}>Eliminar</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => setShowOptionsModal(false)}
            >
              <Text style={styles.cancelText}>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    ...SHADOWS.small,
  },
  title: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
  },
  createButton: {
    backgroundColor: COLORS.primary,
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    ...SHADOWS.small,
  },
  listContainer: {
    paddingHorizontal: SPACING.lg,
    paddingTop: SPACING.md,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
    marginTop: SPACING.sm,
  },
  sectionTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  sectionCount: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    backgroundColor: COLORS.input,
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: BORDER_RADIUS.sm,
  },
  sectionDivider: {
    height: 1,
    backgroundColor: COLORS.input,
    marginVertical: SPACING.lg,
  },
  separator: {
    height: SPACING.md,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: SPACING.xxl,
  },
  emptyText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    marginTop: SPACING.md,
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  optionsModal: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    width: '80%',
    maxWidth: 300,
  },
  optionsTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.lg,
    textAlign: 'center',
  },
  optionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.sm,
    borderRadius: BORDER_RADIUS.sm,
    marginBottom: SPACING.sm,
  },
  optionText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textDark,
    marginLeft: SPACING.sm,
  },
  dangerButton: {
    backgroundColor: 'rgba(255, 82, 82, 0.1)',
  },
  dangerText: {
    color: COLORS.error,
  },
  cancelButton: {
    alignItems: 'center',
    paddingVertical: SPACING.md,
    marginTop: SPACING.md,
    borderTopWidth: 1,
    borderTopColor: COLORS.input,
  },
  cancelText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
  },
});

export default TrainingProgramsScreen;
