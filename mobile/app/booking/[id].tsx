import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius } from '@/constants/spacing';
import { useAuthContext } from '@/context/AuthContext';
import { Booking, BookingStatus } from '@/types/booking';
import { getBookings } from '@/services/bookingService';
import { useBookingStatus } from '@/hooks/useBookingStatus';
import { STATUS_ORDER } from '@/utils/bookingStatus';
import { formatBookingDate, mealSlotLabel } from '@/utils/bookingDisplay';
import LoadingScreen from '@/components/LoadingScreen';
import ErrorMessage from '@/components/ErrorMessage';

interface TimelineStep {
  status: BookingStatus;
  title: string;
  description: string;
}

const TIMELINE_STEPS: TimelineStep[] = [
  {
    status: 'PENDING',
    title: 'Booking Requested',
    description: 'Your booking request has been submitted',
  },
  {
    status: 'CONFIRMED',
    title: 'Chef Confirmed',
    description: 'Your chef has confirmed the booking',
  },
  {
    status: 'CHEF_EN_ROUTE',
    title: 'Chef En Route',
    description: 'Your chef is on the way',
  },
];

export default function BookingTrackerScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { isAuthenticated } = useAuthContext();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const displayStatus = useBookingStatus(booking);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setNotFound(false);
    try {
      const bookings = await getBookings();
      const found = bookings.find((b) => String(b.id) === id) ?? null;
      setBooking(found);
      setNotFound(found === null);
    } catch (e: any) {
      setError(e?.message || 'Failed to load booking');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (isAuthenticated) {
      load();
    }
  }, [isAuthenticated, load]);

  if (!isAuthenticated) {
    return null;
  }

  const goBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/(tabs)/bookings');
    }
  };

  let content: React.ReactNode;
  if (loading) {
    content = <LoadingScreen />;
  } else if (error) {
    content = <ErrorMessage message={error} onRetry={load} />;
  } else if (notFound || !booking || !displayStatus) {
    content = (
      <ErrorMessage
        title="Booking not found"
        message="We could not find this booking in your account."
        onRetry={goBack}
      />
    );
  } else {
    content = (
      <View>
        <View style={styles.heroCard}>
          <Text style={styles.chefName}>{booking.chef.name}</Text>
          <Text style={styles.chefMeta}>
            {booking.chef.cuisine} · {booking.chef.locality}
          </Text>
          <View style={styles.detailRow}>
            <MaterialIcons name="calendar-today" size={14} color={Colors.onSurfaceVariant} />
            <Text style={styles.detailText}>
              {formatBookingDate(booking.booking_date)}
            </Text>
            <MaterialIcons name="restaurant" size={14} color={Colors.onSurfaceVariant} />
            <Text style={styles.detailText}>{mealSlotLabel(booking.meal_slot)}</Text>
          </View>
        </View>

        <Text style={styles.trackerHeading}>Booking #{booking.id}</Text>

        <View style={styles.timelineCard}>
          {TIMELINE_STEPS.map((step, index) => {
            const stepOrder = STATUS_ORDER[step.status];
            const currentOrder = STATUS_ORDER[displayStatus];
            const completed = stepOrder < currentOrder;
            const active = stepOrder === currentOrder;
            const isLast = index === TIMELINE_STEPS.length - 1;
            return (
              <View key={step.status} style={styles.stepRow}>
                <View style={styles.nodeColumn}>
                  <MaterialIcons
                    name={completed || active ? 'check-circle' : 'radio-button-unchecked'}
                    size={active ? 26 : 22}
                    color={
                      completed
                        ? Colors.primaryContainer
                        : active
                          ? Colors.primary
                          : Colors.outlineVariant
                    }
                  />
                  {!isLast ? (
                    <View
                      style={[
                        styles.connector,
                        { backgroundColor: completed ? Colors.primaryContainer : Colors.outlineVariant },
                      ]}
                    />
                  ) : null}
                </View>
                <View style={[styles.stepContent, !isLast && styles.stepContentSpaced]}>
                  <Text
                    style={[
                      styles.stepTitle,
                      active && styles.stepTitleActive,
                      completed && styles.stepTitleCompleted,
                    ]}
                  >
                    {step.title}
                  </Text>
                  <Text style={styles.stepDescription}>{step.description}</Text>
                </View>
              </View>
            );
          })}
        </View>

        <Animated.View
          key={displayStatus}
          entering={FadeInDown.duration(350)}
          style={styles.currentStatusCard}
        >
          <Text style={styles.currentStatusLabel}>Current status</Text>
          <View
            style={[
              styles.currentStatusChip,
              displayStatus === 'CHEF_EN_ROUTE' && styles.currentStatusChipEnRoute,
              displayStatus === 'CONFIRMED' && styles.currentStatusChipConfirmed,
            ]}
          >
            <Text style={styles.currentStatusText}>{displayStatus}</Text>
          </View>
        </Animated.View>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Pressable onPress={goBack} hitSlop={12} android_ripple={{ color: Colors.surfaceContainerHigh }}>
            <MaterialIcons name="arrow-back" size={24} color={Colors.onSurface} />
          </Pressable>
          <Text style={styles.headerTitle}>Booking Tracker</Text>
          <View style={styles.headerSpacer} />
        </View>
        {content}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  container: {
    flex: 1,
    paddingHorizontal: Spacing.containerMargin,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.md,
  },
  headerTitle: {
    ...Typography.labelMd,
    fontSize: 16,
    color: Colors.onSurface,
    textAlign: 'center',
    flex: 1,
  },
  headerSpacer: {
    width: 24,
  },
  heroCard: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: Spacing.md,
  },
  chefName: {
    ...Typography.headlineMd,
    fontSize: 22,
    color: Colors.onSurface,
  },
  chefMeta: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
    marginTop: 2,
    marginBottom: Spacing.sm,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    marginTop: Spacing.xs,
  },
  detailText: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    marginRight: Spacing.sm,
  },
  trackerHeading: {
    ...Typography.labelMd,
    color: Colors.onSurfaceVariant,
    marginTop: Spacing.lg,
    marginBottom: Spacing.sm,
  },
  timelineCard: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: Spacing.md,
  },
  stepRow: {
    flexDirection: 'row',
  },
  nodeColumn: {
    alignItems: 'center',
    width: 28,
  },
  connector: {
    width: 2,
    flex: 1,
    marginVertical: 2,
    borderRadius: BorderRadius.full,
  },
  stepContent: {
    flex: 1,
    paddingLeft: Spacing.md,
  },
  stepContentSpaced: {
    paddingBottom: Spacing.lg,
  },
  stepTitle: {
    ...Typography.labelMd,
    color: Colors.outline,
    marginBottom: 2,
  },
  stepTitleActive: {
    fontSize: 16,
    color: Colors.primary,
  },
  stepTitleCompleted: {
    color: Colors.onSurface,
  },
  stepDescription: {
    ...Typography.labelSm,
    lineHeight: 18,
    color: Colors.outline,
  },
  currentStatusCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.lg,
    backgroundColor: Colors.surfaceContainerLow,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.md + 4,
  },
  currentStatusLabel: {
    ...Typography.labelMd,
    color: Colors.onSurfaceVariant,
  },
  currentStatusChip: {
    backgroundColor: Colors.surfaceContainerHigh,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.xs + 2,
    paddingHorizontal: Spacing.sm + 4,
  },
  currentStatusChipConfirmed: {
    backgroundColor: Colors.secondaryFixed,
  },
  currentStatusChipEnRoute: {
    backgroundColor: Colors.tertiaryFixed,
  },
  currentStatusText: {
    ...Typography.labelSm,
    fontWeight: '600',
    color: Colors.onSurface,
  },
});
