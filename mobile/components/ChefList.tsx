import React from 'react';
import { FlatList, StyleSheet } from 'react-native';
import { Chef } from '@/types/chef';
import { Spacing } from '@/constants/spacing';
import ChefCard from './ChefCard';

interface ChefListProps {
  chefs: Chef[];
  onBook: (chef: Chef) => void;
  onPress: (chef: Chef) => void;
}

export default function ChefList({ chefs, onBook, onPress }: ChefListProps) {
  return (
    <FlatList
      data={chefs}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item, index }) => (
        <ChefCard chef={item} onBook={onBook} onPress={onPress} index={index} />
      )}
      contentContainerStyle={styles.list}
      showsVerticalScrollIndicator={false}
    />
  );
}

const styles = StyleSheet.create({
  list: {
    gap: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
});
