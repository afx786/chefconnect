import React, { useRef, useEffect } from 'react';
import { Animated, StyleSheet, TouchableOpacity, Text, View } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius, Shadow } from '@/constants/spacing';
import { Chef } from '@/types/chef';
import { formatCurrency } from '@/utils/formatCurrency';

interface ChefCardProps {
  chef: Chef;
  onBook: (chef: Chef) => void;
  onPress: (chef: Chef) => void;
  index?: number;
}

export default function ChefCard({ chef, onBook, onPress, index = 0 }: ChefCardProps) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(24)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 350,
        delay: index * 80,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 350,
        delay: index * 80,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <Animated.View style={{ opacity, transform: [{ translateY }] }}>
      <TouchableOpacity
        style={styles.card}
        activeOpacity={0.9}
        onPress={() => onPress(chef)}
      >
        <View style={styles.imagePlaceholder}>
          <MaterialIcons name="restaurant" size={48} color={Colors.outlineVariant} />
          <View style={styles.ratingBadge}>
            <MaterialIcons name="star" size={14} color={Colors.star} />
            <Text style={styles.ratingText}>{chef.rating}</Text>
          </View>
        </View>

        <View style={styles.body}>
          <View style={styles.headerRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.chefName}>{chef.name}</Text>
              <View style={styles.metaRow}>
                <MaterialIcons name="restaurant" size={14} color={Colors.onSurfaceVariant} />
                <Text style={styles.metaText}>{chef.cuisine}</Text>
                <Text style={styles.metaDot}> · </Text>
                <MaterialIcons name="location-on" size={14} color={Colors.onSurfaceVariant} />
                <Text style={styles.metaText}>{chef.locality}</Text>
              </View>
            </View>
          </View>

          <View style={styles.dishBox}>
            <Text style={styles.dishLabel}>SIGNATURE DISH</Text>
            <Text style={styles.dishName}>{chef.signature_dish}</Text>
          </View>

          <View style={styles.footer}>
            <View>
              <Text style={styles.price}>{formatCurrency(chef.price_per_meal)}</Text>
              <Text style={styles.priceUnit}> / meal</Text>
            </View>
            <TouchableOpacity
              style={styles.bookButton}
              activeOpacity={0.85}
              onPress={() => onBook(chef)}
            >
              <Text style={styles.bookButtonText}>Book Chef</Text>
            </TouchableOpacity>
          </View>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
    ...Shadow.card,
  },
  imagePlaceholder: {
    height: 192,
    backgroundColor: Colors.surfaceContainerHigh,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ratingBadge: {
    position: 'absolute',
    top: Spacing.md,
    right: Spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.9)',
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
    gap: 4,
  },
  ratingText: {
    ...Typography.labelMd,
    color: Colors.onSurface,
  },
  body: {
    padding: Spacing.lg,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.sm,
  },
  chefName: {
    ...Typography.headlineMd,
    color: Colors.onSurface,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.xs,
  },
  metaText: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  metaDot: {
    ...Typography.bodyMd,
    color: Colors.outlineVariant,
    marginHorizontal: 2,
  },
  dishBox: {
    backgroundColor: Colors.surfaceContainerLow,
    borderRadius: BorderRadius.default,
    padding: Spacing.sm,
    marginBottom: Spacing.md,
  },
  dishLabel: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  dishName: {
    ...Typography.bodyMd,
    fontWeight: '500',
    color: Colors.onSurface,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingTop: Spacing.md,
  },
  price: {
    ...Typography.headlineMd,
    color: Colors.primary,
  },
  priceUnit: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  bookButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.lg,
    borderRadius: BorderRadius.md,
  },
  bookButtonText: {
    ...Typography.labelMd,
    color: Colors.onPrimary,
  },
});
