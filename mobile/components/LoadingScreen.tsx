import React, { useEffect, useRef } from 'react';
import { View, Animated, StyleSheet } from 'react-native';
import { Colors } from '@/constants/colors';
import { Spacing, BorderRadius } from '@/constants/spacing';

function SkeletonBar({ width, height = 16 }: { width: number | string; height?: number }) {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ]),
    ).start();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        styles.skeletonBar,
        { width: width as any, height, opacity },
      ]}
    />
  );
}

export function SkeletonChefCard() {
  return (
    <View style={styles.card}>
      <SkeletonBar width="100%" height={192} />
      <View style={styles.cardBody}>
        <SkeletonBar width="60%" height={20} />
        <View style={{ height: Spacing.xs }} />
        <SkeletonBar width="40%" height={14} />
        <View style={{ height: Spacing.sm }} />
        <View style={styles.dishRow}>
          <SkeletonBar width={48} height={48} />
          <View style={{ flex: 1, marginLeft: Spacing.sm }}>
            <SkeletonBar width="70%" height={12} />
            <View style={{ height: 4 }} />
            <SkeletonBar width="50%" height={14} />
          </View>
        </View>
        <View style={{ height: Spacing.md }} />
        <View style={styles.priceRow}>
          <SkeletonBar width={80} height={24} />
          <SkeletonBar width={100} height={40} />
        </View>
      </View>
    </View>
  );
}

export default function LoadingScreen() {
  return (
    <View style={styles.container}>
      <SkeletonChefCard />
      <SkeletonChefCard />
      <SkeletonChefCard />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: Spacing.containerMargin,
    paddingTop: Spacing.md,
    gap: Spacing.lg,
  },
  card: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  cardBody: {
    padding: Spacing.lg,
  },
  dishRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceContainerLow,
    borderRadius: BorderRadius.default,
    padding: Spacing.sm,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingTop: Spacing.md,
  },
  skeletonBar: {
    backgroundColor: Colors.skeletonBase,
    borderRadius: BorderRadius.sm,
  },
});
