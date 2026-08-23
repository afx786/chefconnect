import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Redirect, useRouter } from 'expo-router';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/spacing';
import { useAuthContext } from '@/context/AuthContext';
import { Booking } from '@/types/booking';
import { getBookings } from '@/services/bookingService';
import BookingCard from '@/components/BookingCard';
import LoadingScreen from '@/components/LoadingScreen';
import ErrorMessage from '@/components/ErrorMessage';
import EmptyState from '@/components/EmptyState';

export default function BookingsScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuthContext();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getBookings();
      setBookings(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      load();
    }
  }, [isAuthenticated, load]);

  if (!isAuthenticated) {
    return <Redirect href="/(auth)/login" />;
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headline}>My Bookings</Text>
        </View>
        {loading ? (
          <LoadingScreen />
        ) : error ? (
          <ErrorMessage message={error} onRetry={load} />
        ) : bookings.length === 0 ? (
          <EmptyState
            title="No bookings yet"
            subtitle="When you book a chef, your reservations and their live status will appear here."
            onAction={() => router.push('/(tabs)/explore')}
            actionLabel="Explore Chefs"
          />
        ) : (
          <FlatList
            data={bookings}
            keyExtractor={(item) => String(item.id)}
            renderItem={({ item }) => (
              <BookingCard
                booking={item}
                onPress={(b) => router.push(`/booking/${b.id}`)}
              />
            )}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.list}
          />
        )}
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
    paddingTop: Spacing.md,
    paddingBottom: Spacing.lg,
  },
  headline: {
    ...Typography.headlineLgMobile,
    color: Colors.onBackground,
  },
  list: {
    paddingBottom: Spacing.xl,
  },
});
