import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, FlatList, TextInput, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import { useStandardExercises } from '../hooks/useStandardExercises';
import LoadingIndicator from './LoadingIndicator';

const StandardExerciseSelector = ({ visible, onClose, onSelect, title = "Seleccionar Ejercicio", exercises: propExercises, isLoadingExercises }) => {
  const {
    exercises: hookExercises,
    isLoading: isLoadingHook,
    error,
    searchExercises,
    getEquipmentTypes,
    getMuscleGroups,
    getExerciseTypes,
    applyFilters,
    clearFilters
  } = useStandardExercises();

  // Use prop exercises if provided, otherwise use hook exercises
  const exercises = propExercises || hookExercises;
  
  // Use the loading state from props if available, otherwise use the hook's loading state
  const isLoading = isLoadingExercises !== undefined ? isLoadingExercises : isLoadingHook;

  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [equipmentTypes, setEquipmentTypes] = useState([]);
  const [muscleGroups, setMuscleGroups] = useState([]);
  const [exerciseTypes, setExerciseTypes] = useState([]);
  const [selectedFilters, setSelectedFilters] = useState({
    equipment: '',
    muscle_group: '',
    exercise_type: ''
  });

  // Cargar opciones de filtros
  useEffect(() => {
    const loadFilterOptions = async () => {
      const [equipment, muscles, types] = await Promise.all([
        getEquipmentTypes(),
        getMuscleGroups(),
        getExerciseTypes()
      ]);
      setEquipmentTypes(equipment);
      setMuscleGroups(muscles);
      setExerciseTypes(types);
    };

    if (visible) {
      loadFilterOptions();
    }
  }, [visible]);

  // Manejar búsqueda con autocompletado
  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length >= 2) {
      const results = await searchExercises(query);
      setSuggestions(results);
    } else {
      setSuggestions([]);
    }
  };

  // Aplicar filtros
  const handleApplyFilters = () => {
    applyFilters(selectedFilters);
    setShowFilters(false);
  };

  // Limpiar filtros
  const handleClearFilters = () => {
    setSelectedFilters({
      equipment: '',
      muscle_group: '',
      exercise_type: ''
    });
    clearFilters();
    setShowFilters(false);
  };

  // Seleccionar ejercicio
  const handleSelectExercise = (exercise) => {
    // Asegurarnos de que el ejercicio tiene una estructura consistente
    const standardizedExercise = {
      id: exercise.id,
      standard_name: exercise.standard_name || exercise.name,
      type: exercise.type || 'strength',
      main_muscle_group: exercise.main_muscle_group || '',
      equipment: exercise.equipment || ''
    };
    
    onSelect(standardizedExercise);
    onClose();
    setSearchQuery('');
    setSuggestions([]);
  };

  // Renderizar ejercicio
  const renderExercise = ({ item }) => (
    <TouchableOpacity
      style={styles.exerciseItem}
      onPress={() => handleSelectExercise(item)}
    >
      <View style={styles.exerciseInfo}>
        <Text style={styles.exerciseName}>{item.standard_name || item.name}</Text>
        <View style={styles.exerciseDetails}>
          {item.main_muscle_group && (
            <>
              <Text style={styles.exerciseDetail}>{item.main_muscle_group}</Text>
              <Text style={styles.exerciseDetail}>•</Text>
            </>
          )}
          {item.equipment && (
            <>
              <Text style={styles.exerciseDetail}>{item.equipment}</Text>
              <Text style={styles.exerciseDetail}>•</Text>
            </>
          )}
          <Text style={styles.exerciseDetail}>{item.type || ''}</Text>
        </View>
      </View>
      <Ionicons name="chevron-forward" size={20} color={COLORS.textMedium} />
    </TouchableOpacity>
  );

  // Renderizar filtros
  const renderFilters = () => (
    <Modal visible={showFilters} animationType="slide" transparent>
      <View style={styles.filterOverlay}>
        <View style={styles.filterContainer}>
          <View style={styles.filterHeader}>
            <Text style={styles.filterTitle}>Filtros</Text>
            <TouchableOpacity onPress={() => setShowFilters(false)}>
              <Ionicons name="close" size={24} color={COLORS.textMedium} />
            </TouchableOpacity>
          </View>

          {/* Filtro por equipamiento */}
          <View style={styles.filterSection}>
            <Text style={styles.filterLabel}>Equipamiento</Text>
            <FlatList
              data={equipmentTypes}
              horizontal
              showsHorizontalScrollIndicator={false}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.filterChip,
                    selectedFilters.equipment === item.value && styles.filterChipSelected
                  ]}
                  onPress={() => setSelectedFilters(prev => ({
                    ...prev,
                    equipment: prev.equipment === item.value ? '' : item.value
                  }))}
                >
                  <Text style={[
                    styles.filterChipText,
                    selectedFilters.equipment === item.value && styles.filterChipTextSelected
                  ]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              )}
              keyExtractor={item => item.value}
            />
          </View>

          {/* Filtro por grupo muscular */}
          <View style={styles.filterSection}>
            <Text style={styles.filterLabel}>Grupo Muscular</Text>
            <FlatList
              data={muscleGroups}
              horizontal
              showsHorizontalScrollIndicator={false}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.filterChip,
                    selectedFilters.muscle_group === item.value && styles.filterChipSelected
                  ]}
                  onPress={() => setSelectedFilters(prev => ({
                    ...prev,
                    muscle_group: prev.muscle_group === item.value ? '' : item.value
                  }))}
                >
                  <Text style={[
                    styles.filterChipText,
                    selectedFilters.muscle_group === item.value && styles.filterChipTextSelected
                  ]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              )}
              keyExtractor={item => item.value}
            />
          </View>

          {/* Filtro por tipo de ejercicio */}
          <View style={styles.filterSection}>
            <Text style={styles.filterLabel}>Tipo de Ejercicio</Text>
            <FlatList
              data={exerciseTypes}
              horizontal
              showsHorizontalScrollIndicator={false}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.filterChip,
                    selectedFilters.exercise_type === item.value && styles.filterChipSelected
                  ]}
                  onPress={() => setSelectedFilters(prev => ({
                    ...prev,
                    exercise_type: prev.exercise_type === item.value ? '' : item.value
                  }))}
                >
                  <Text style={[
                    styles.filterChipText,
                    selectedFilters.exercise_type === item.value && styles.filterChipTextSelected
                  ]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              )}
              keyExtractor={item => item.value}
            />
          </View>

          <View style={styles.filterButtons}>
            <TouchableOpacity
              style={[styles.filterButton, styles.clearButton]}
              onPress={handleClearFilters}
            >
              <Text style={styles.clearButtonText}>Limpiar</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.filterButton, styles.applyButton]}
              onPress={handleApplyFilters}
            >
              <Text style={styles.applyButtonText}>Aplicar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  return (
    <Modal visible={visible} animationType="slide">
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          <TouchableOpacity onPress={onClose}>
            <Ionicons name="close" size={24} color={COLORS.textMedium} />
          </TouchableOpacity>
        </View>

        {/* Barra de búsqueda */}
        <View style={styles.searchContainer}>
          <View style={styles.searchBar}>
            <Ionicons name="search" size={20} color={COLORS.textMedium} />
            <TextInput
              style={styles.searchInput}
              placeholder="Buscar ejercicio..."
              value={searchQuery}
              onChangeText={handleSearch}
            />
          </View>
          <TouchableOpacity
            style={styles.filterButton}
            onPress={() => setShowFilters(true)}
          >
            <Ionicons name="filter" size={20} color={COLORS.primary} />
          </TouchableOpacity>
        </View>

        {/* Mostrar error si existe */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Mostrar cargando */}
        {isLoading && <LoadingIndicator />}

        {/* Lista de sugerencias o ejercicios */}
        <FlatList
          data={searchQuery.length >= 2 ? suggestions.map(name => ({ standard_name: name })) : exercises}
          renderItem={renderExercise}
          keyExtractor={(item, index) => {
            if (item.id) return item.id.toString();
            if (item.standard_name) return `${item.standard_name}-${index}`;
            if (item.name) return `${item.name}-${index}`;
            return `exercise-${index}`;
          }}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContainer}
        />
      </View>

      {renderFilters()}
    </Modal>
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
    paddingHorizontal: SPACING.md,
    paddingTop: SPACING.xl,
    paddingBottom: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  title: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  searchContainer: {
    flexDirection: 'row',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    gap: SPACING.sm,
  },
  searchBar: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.backgroundSecondary,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    gap: SPACING.sm,
  },
  searchInput: {
    flex: 1,
    fontSize: FONT_SIZE.md,
    color: COLORS.textPrimary,
  },
  filterButton: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.backgroundSecondary,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
  },
  errorContainer: {
    backgroundColor: COLORS.error,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
  },
  errorText: {
    color: COLORS.white,
    fontSize: FONT_SIZE.sm,
    textAlign: 'center',
  },
  listContainer: {
    paddingHorizontal: SPACING.md,
    paddingBottom: SPACING.lg,
  },
  exerciseItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.sm,
  },
  exerciseInfo: {
    flex: 1,
  },
  exerciseName: {
    fontSize: FONT_SIZE.md,
    fontWeight: '500',
    color: COLORS.textPrimary,
    marginBottom: SPACING.xs,
  },
  exerciseDetails: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  exerciseDetail: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  separator: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: SPACING.xs,
  },
  // Estilos para filtros
  filterOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  filterContainer: {
    backgroundColor: COLORS.background,
    borderTopLeftRadius: BORDER_RADIUS.lg,
    borderTopRightRadius: BORDER_RADIUS.lg,
    paddingHorizontal: SPACING.md,
    paddingBottom: SPACING.xl,
    maxHeight: '80%',
  },
  filterHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  filterTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  filterSection: {
    marginVertical: SPACING.md,
  },
  filterLabel: {
    fontSize: FONT_SIZE.md,
    fontWeight: '500',
    color: COLORS.textPrimary,
    marginBottom: SPACING.sm,
  },
  filterChip: {
    backgroundColor: COLORS.backgroundSecondary,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.lg,
    marginRight: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  filterChipSelected: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  filterChipText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  filterChipTextSelected: {
    color: COLORS.white,
  },
  filterButtons: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginTop: SPACING.md,
  },
  clearButton: {
    flex: 1,
    backgroundColor: COLORS.backgroundSecondary,
    paddingVertical: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
  },
  applyButton: {
    flex: 1,
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
  },
  clearButtonText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
  },
  applyButtonText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.white,
    fontWeight: '500',
  },
});

export default StandardExerciseSelector;
