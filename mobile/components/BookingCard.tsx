import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius, Shadow } from '@/constants/spacing';
import { Booking } from '@/types/booking';
import { formatBookingDate, mealSlotLabel } from '@/utils/bookingDisplay';

interface BookingCardProps {
  booking: Booking;
  onPress: (booking: Booking) => void;
}

function statusChipStyle(status: Booking['status']) {
  switch (status) {
    case 'CONFIRMED':
      return {
        container: { backgroundColor: Colors.secondaryContainer },
        label: { color: Colors.onSecondaryContainer },
      };
    case 'CHEF_EN_ROUTE':
      return {
        container: { backgroundColor: Colors.tertiaryFixed },
        label: { color: Colors.onTertiaryFixed },
      };
    default:
      return {
        container: { backgroundColor: Colors.surfaceContainerHigh },
        label: { color: Colors.onSurfaceVariant },
      };
  }
}

export default function BookingCard({ booking, onPress }: BookingCardProps) {
  const chip = statusChipStyle(booking.status);

  return (
    <Pressable
      onPress={() => onPress(booking)}
      android_ripple={{ color: Colors.surfaceContainerHigh }}
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    >
      <View style={styles.topRow}>
        <View style={styles.titleBlock}>
          <Text style={styles.chefName}>{booking.chef.name}</Text>
          <Text style={styles.metaLine} numberOfLines={1}>
            {booking.chef.cuisine} · {booking.chef.locality}
          </Text>
        </View>
        <MaterialIcons name="chevron-right" size={22} color={Colors.outlineVariant} />
      </View>

      <View style={styles.detailRow}>
        <MaterialIcons name="calendar-today" size={14} color={Colors.onSurfaceVariant} />
        <Text style={styles.detailText}>{formatBookingDate(booking.booking_date)}</Text>
        <MaterialIcons name="restaurant" size={14} color={Colors.onSurfaceVariant} />
        <Text style={styles.detailText}>{mealSlotLabel(booking.meal_slot)}</Text>
      </View>

      <View style={[styles.bottomRow, styles.divider]}>
        <Text style={styles.bookingId}>#{booking.id}</Text>
        <View style={[styles.statusChip, chip.container]}>
          <Text style={[styles.statusChipLabel, chip.label]}>{booking.status}</Text>
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: Spacing.md,
    ...Shadow.card,
  },
  cardPressed: {
    opacity: 0.9,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
  },
  titleBlock: {
    flex: 1,
    marginRight: Spacing.sm,
  },
  chefName: {
    ...Typography.labelMd,
    fontSize: 16,
    color: Colors.onSurface,
    marginBottom: 2,
  },
  metaLine: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.md,
    gap: Spacing.xs,
  },
  detailText: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    marginRight: Spacing.sm,
  },
  bottomRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.md,
    paddingTop: Spacing.md,
  },
  divider: {
    borderTopWidth: 1,
    borderTopColor: Colors.divider,
  },
  bookingId: {
    ...Typography.labelSm,
    color: Colors.outlineVariant,
  },
  statusChip: {
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.xs + 2,
    paddingHorizontal: Spacing.sm + 4,
  },
  statusChipLabel: {
    ...Typography.labelSm,
    fontWeight: '600',
  },
});
