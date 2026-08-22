import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius, Shadow } from '@/constants/spacing';
import { Chef } from '@/types/chef';
import { fetchChefs } from '@/services/chefService';
import { formatCurrency } from '@/utils/formatCurrency';
import { useAuthContext } from '@/context/AuthContext';
import BookingModal from '@/components/BookingModal';
import ErrorMessage from '@/components/ErrorMessage';
import LoadingScreen from '@/components/LoadingScreen';

export default function ChefDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { isAuthenticated } = useAuthContext();
  const [chef, setChef] = useState<Chef | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bookingVisible, setBookingVisible] = useState(false);
  const [awaitingAuth, setAwaitingAuth] = useState(false);

  useEffect(() => {
    if (isAuthenticated && awaitingAuth) {
      setAwaitingAuth(false);
      setBookingVisible(true);
    }
  }, [isAuthenticated, awaitingAuth]);

  const handleBookPress = () => {
    if (!isAuthenticated) {
      setAwaitingAuth(true);
      router.push('/(auth)/login');
      return;
    }
    setBookingVisible(true);
  };

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchChefs();
        const found = data.chefs.find((c) => c.id === Number(id));
        if (found) {
          setChef(found);
        } else {
          setError('Chef not found');
        }
      } catch (e: any) {
        setError(e?.message || 'Failed to load chef');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingScreen />
      </View>
    );
  }

  if (error || !chef) {
    return (
      <View style={styles.loadingContainer}>
        <ErrorMessage message={error || 'Chef not found'} onRetry={() => router.back()} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.heroImage}>
          <MaterialIcons name="restaurant" size={64} color={Colors.outlineVariant} />
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <MaterialIcons name="arrow-back" size={22} color={Colors.onSurface} />
          </TouchableOpacity>
          <View style={styles.ratingBadge}>
            <MaterialIcons name="star" size={16} color={Colors.star} />
            <Text style={styles.ratingText}>{chef.rating}</Text>
          </View>
        </View>

        <View style={styles.body}>
          <Text style={styles.chefName}>{chef.name}</Text>
          <View style={styles.metaRow}>
            <MaterialIcons name="restaurant" size={16} color={Colors.onSurfaceVariant} />
            <Text style={styles.metaText}>{chef.cuisine}</Text>
            <Text style={styles.metaDot}> · </Text>
            <MaterialIcons name="location-on" size={16} color={Colors.onSurfaceVariant} />
            <Text style={styles.metaText}>{chef.locality}</Text>
          </View>

          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{chef.experience_years} yrs</Text>
              <Text style={styles.statLabel}>Experience</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.stat}>
              <Text style={styles.statValue}>{chef.dishes.length}</Text>
              <Text style={styles.statLabel}>Dishes</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.stat}>
              <Text style={[styles.statValue, { color: Colors.primary }]}>
                {formatCurrency(chef.price_per_meal)}
              </Text>
              <Text style={styles.statLabel}>Per Meal</Text>
            </View>
          </View>

          {chef.bio ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>About</Text>
              <Text style={styles.bioText}>{chef.bio}</Text>
            </View>
          ) : null}

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Signature Dish</Text>
            <View style={styles.dishBox}>
              <Text style={styles.dishName}>{chef.signature_dish}</Text>
            </View>
          </View>

          {chef.dishes.length > 0 ? (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Menu</Text>
              {chef.dishes.map((dish) => (
                <View key={dish.id} style={styles.dishCard}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.dishItemName}>{dish.name}</Text>
                    {dish.description ? (
                      <Text style={styles.dishDesc} numberOfLines={2}>
                        {dish.description}
                      </Text>
                    ) : null}
                  </View>
                  <Text style={styles.dishPrice}>{formatCurrency(dish.price)}</Text>
                </View>
              ))}
            </View>
          ) : null}
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <View>
          <Text style={styles.footerPrice}>{formatCurrency(chef.price_per_meal)}</Text>
          <Text style={styles.footerUnit}>/ meal</Text>
        </View>
        <TouchableOpacity
          style={styles.bookButton}
          onPress={handleBookPress}
          activeOpacity={0.85}
        >
          <Text style={styles.bookButtonText}>Book Chef</Text>
        </TouchableOpacity>
      </View>

      <BookingModal
        visible={bookingVisible}
        chef={chef}
        onClose={() => setBookingVisible(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  heroImage: {
    height: 280,
    backgroundColor: Colors.surfaceContainerHigh,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backButton: {
    position: 'absolute',
    top: Spacing.lg,
    left: Spacing.md,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.9)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  ratingBadge: {
    position: 'absolute',
    top: Spacing.lg,
    right: Spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.9)',
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: Spacing.xs + 2,
    borderRadius: BorderRadius.full,
    gap: 4,
  },
  ratingText: {
    ...Typography.labelMd,
    color: Colors.onSurface,
  },
  body: {
    padding: Spacing.containerMargin,
    paddingBottom: 100,
  },
  chefName: {
    ...Typography.headlineLgMobile,
    color: Colors.onSurface,
    marginBottom: Spacing.xs,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  metaText: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  metaDot: {
    color: Colors.outlineVariant,
    marginHorizontal: 2,
  },
  statsRow: {
    flexDirection: 'row',
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.border,
    ...Shadow.card,
  },
  stat: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    ...Typography.headlineMd,
    color: Colors.onSurface,
    marginBottom: 2,
  },
  statLabel: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
  },
  statDivider: {
    width: 1,
    backgroundColor: Colors.divider,
    marginVertical: Spacing.xs,
  },
  section: {
    marginBottom: Spacing.xl,
  },
  sectionTitle: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    textTransform: 'uppercase',
    letterSpacing: 0.05,
    marginBottom: Spacing.sm,
  },
  bioText: {
    ...Typography.bodyLg,
    color: Colors.onSurface,
    lineHeight: 28,
  },
  dishBox: {
    backgroundColor: Colors.surfaceContainerLow,
    borderRadius: BorderRadius.default,
    padding: Spacing.md,
  },
  dishName: {
    ...Typography.bodyMd,
    fontWeight: '500',
    color: Colors.onSurface,
  },
  dishCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.default,
    padding: Spacing.md,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  dishItemName: {
    ...Typography.bodyMd,
    fontWeight: '500',
    color: Colors.onSurface,
    marginBottom: 2,
  },
  dishDesc: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
  },
  dishPrice: {
    ...Typography.labelMd,
    color: Colors.primary,
    marginLeft: Spacing.sm,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.surfaceContainerLowest,
    paddingHorizontal: Spacing.containerMargin,
    paddingVertical: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    ...Shadow.bottomNav,
  },
  footerPrice: {
    ...Typography.headlineMd,
    color: Colors.primary,
  },
  footerUnit: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  bookButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.sm + 2,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.md,
  },
  bookButtonText: {
    ...Typography.labelMd,
    color: Colors.onPrimary,
  },
});
