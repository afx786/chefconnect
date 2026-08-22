import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing } from '@/constants/spacing';
import { useChefs } from '@/hooks/useChefs';
import { Chef } from '@/types/chef';
import { useAuthContext } from '@/context/AuthContext';
import FilterBar from '@/components/FilterBar';
import ChefList from '@/components/ChefList';
import LoadingScreen from '@/components/LoadingScreen';
import ErrorMessage from '@/components/ErrorMessage';
import EmptyState from '@/components/EmptyState';
import BookingModal from '@/components/BookingModal';

export default function ExploreScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuthContext();
  const {
    chefs,
    loading,
    error,
    cuisine,
    locality,
    setCuisine,
    setLocality,
    refetch,
  } = useChefs();

  const [selectedChef, setSelectedChef] = useState<Chef | null>(null);
  const [bookingVisible, setBookingVisible] = useState(false);
  const [awaitingAuth, setAwaitingAuth] = useState(false);

  useEffect(() => {
    if (isAuthenticated && awaitingAuth && selectedChef) {
      setAwaitingAuth(false);
      setBookingVisible(true);
    }
  }, [isAuthenticated, awaitingAuth, selectedChef]);

  useEffect(() => {
    if (!isAuthenticated && bookingVisible) {
      setBookingVisible(false);
      setAwaitingAuth(true);
      router.push('/(auth)/login');
    }
  }, [isAuthenticated, bookingVisible]);

  const handleBook = (chef: Chef) => {
    setSelectedChef(chef);
    if (!isAuthenticated) {
      setAwaitingAuth(true);
      router.push('/(auth)/login');
      return;
    }
    setBookingVisible(true);
  };

  const handlePress = (chef: Chef) => {
    router.push(`/chef/${chef.id}`);
  };

  const hasFilters = !!cuisine || !!locality;

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.container}>
        {loading ? (
          <LoadingScreen />
        ) : error ? (
          <ErrorMessage message={error} onRetry={refetch} />
        ) : (
          <ScrollView
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.scroll}
          >
            <View style={styles.header}>
              <Text style={styles.headline}>Find a chef for your table</Text>
              <Text style={styles.subtitle}>
                Discover culinary experts ready to craft unforgettable meals in your home.
              </Text>
            </View>

            <FilterBar
              selectedCuisine={cuisine}
              selectedLocality={locality}
              onCuisineChange={setCuisine}
              onLocalityChange={setLocality}
            />

            <View style={styles.listSection}>
              {chefs.length === 0 ? (
                <EmptyState
                  title="No chefs found"
                  subtitle="Try adjusting your filters to find available chefs."
                  onAction={() => {
                    setCuisine(undefined);
                    setLocality(undefined);
                  }}
                  actionLabel="Clear Filters"
                />
              ) : (
                <ChefList chefs={chefs} onBook={handleBook} onPress={handlePress} />
              )}
            </View>
          </ScrollView>
        )}
      </View>

      <BookingModal
        visible={bookingVisible}
        chef={selectedChef}
        onClose={() => {
          setBookingVisible(false);
          setSelectedChef(null);
        }}
      />
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
  },
  scroll: {
    paddingHorizontal: Spacing.containerMargin,
    paddingTop: Spacing.md,
  },
  header: {
    marginBottom: Spacing.lg,
  },
  headline: {
    ...Typography.headlineLgMobile,
    color: Colors.onBackground,
    marginBottom: Spacing.sm,
  },
  subtitle: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  listSection: {
    marginTop: Spacing.md,
    minHeight: 300,
  },
});
