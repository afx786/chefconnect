import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius } from '@/constants/spacing';

const CUISINES = ['All', 'Indian', 'Punjabi', 'South Indian', 'Continental'];
const LOCALITIES = ['Indirapuram', 'Vaishali', 'Noida', 'Sector 62'];

interface FilterBarProps {
  selectedCuisine?: string;
  selectedLocality?: string;
  onCuisineChange: (cuisine?: string) => void;
  onLocalityChange: (locality?: string) => void;
}

export default function FilterBar({
  selectedCuisine,
  selectedLocality,
  onCuisineChange,
  onLocalityChange,
}: FilterBarProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.sectionLabel}>CUISINE</Text>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chipRow}
      >
        {CUISINES.map((c) => {
          const active = c === 'All' ? !selectedCuisine : selectedCuisine === c;
          return (
            <TouchableOpacity
              key={c}
              style={[styles.chip, active && styles.chipActive]}
              onPress={() => onCuisineChange(c === 'All' ? undefined : c)}
              activeOpacity={0.7}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {c}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <Text style={[styles.sectionLabel, { marginTop: Spacing.sm }]}>LOCALITY</Text>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chipRow}
      >
        {LOCALITIES.map((loc) => {
          const active = selectedLocality === loc;
          return (
            <TouchableOpacity
              key={loc}
              style={[styles.chip, active && styles.chipActive]}
              onPress={() => onLocalityChange(active ? undefined : loc)}
              activeOpacity={0.7}
            >
              <MaterialIcons
                name="location-on"
                size={14}
                color={active ? Colors.onPrimary : Colors.onSurfaceVariant}
              />
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {loc}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: Spacing.sm,
  },
  sectionLabel: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    textTransform: 'uppercase',
    letterSpacing: 0.05,
    marginBottom: Spacing.xs,
    marginLeft: Spacing.xs,
  },
  chipRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    paddingHorizontal: Spacing.xs,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.secondaryContainer + '4D',
    borderWidth: 1,
    borderColor: Colors.surfaceVariant,
  },
  chipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  chipText: {
    ...Typography.labelMd,
    color: Colors.onSurfaceVariant,
  },
  chipTextActive: {
    color: Colors.onPrimary,
  },
});
