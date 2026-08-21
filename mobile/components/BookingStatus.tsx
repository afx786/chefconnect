import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius } from '@/constants/spacing';
import { Booking } from '@/types/booking';
import { formatDate } from '@/utils/formatDate';
import { MealSlotLabels, BookingStatusLabels } from '@/constants/booking';
import Button from './Button';

interface BookingStatusProps {
  booking: Booking;
  chefName: string;
  onClose: () => void;
}

export default function BookingStatus({ booking, chefName, onClose }: BookingStatusProps) {
  const statusColor =
    booking.status === 'CONFIRMED'
      ? Colors.tertiary
      : booking.status === 'CHEF_EN_ROUTE'
        ? Colors.primary
        : Colors.outline;

  return (
    <View style={styles.container}>
      <View style={styles.successIcon}>
        <MaterialIcons name="check-circle" size={56} color={Colors.tertiary} />
      </View>
      <Text style={styles.title}>Booking Confirmed</Text>
      <Text style={styles.subtitle}>Your booking with {chefName} has been submitted.</Text>

      <View style={styles.card}>
        <View style={styles.row}>
          <MaterialIcons name="person" size={18} color={Colors.onSurfaceVariant} />
          <Text style={styles.rowLabel}>Chef</Text>
          <Text style={styles.rowValue}>{chefName}</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.row}>
          <MaterialIcons name="calendar-today" size={18} color={Colors.onSurfaceVariant} />
          <Text style={styles.rowLabel}>Date</Text>
          <Text style={styles.rowValue}>{formatDate(booking.booking_date)}</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.row}>
          <MaterialIcons name="restaurant" size={18} color={Colors.onSurfaceVariant} />
          <Text style={styles.rowLabel}>Meal</Text>
          <Text style={styles.rowValue}>{MealSlotLabels[booking.meal_slot]}</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.row}>
          <MaterialIcons name="info-outline" size={18} color={statusColor} />
          <Text style={styles.rowLabel}>Status</Text>
          <Text style={[styles.rowValue, { color: statusColor }]}>
            {BookingStatusLabels[booking.status]}
          </Text>
        </View>
      </View>

      <Button title="Done" onPress={onClose} style={styles.doneButton} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: Spacing.lg,
  },
  successIcon: {
    marginBottom: Spacing.md,
  },
  title: {
    ...Typography.headlineMd,
    color: Colors.onSurface,
    marginBottom: Spacing.xs,
  },
  subtitle: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: Spacing.lg,
  },
  card: {
    width: '100%',
    backgroundColor: Colors.surfaceContainerLow,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.lg,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    gap: Spacing.sm,
  },
  rowLabel: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    width: 50,
  },
  rowValue: {
    ...Typography.bodyMd,
    color: Colors.onSurface,
    flex: 1,
    textAlign: 'right',
  },
  divider: {
    height: 1,
    backgroundColor: Colors.divider,
  },
  doneButton: {
    width: '100%',
  },
});
