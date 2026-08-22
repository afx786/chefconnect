import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius } from '@/constants/spacing';
import { useAuthContext } from '@/context/AuthContext';
import Button from '@/components/Button';

export default function ProfileScreen() {
  const { user, logout } = useAuthContext();

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headline}>Profile</Text>
        </View>
        <View style={styles.avatarSection}>
          <View style={styles.avatar}>
            <MaterialIcons name="person" size={48} color={Colors.onPrimary} />
          </View>
          <Text style={styles.name}>{user?.name || 'ChefConnect User'}</Text>
          <Text style={styles.email}>{user?.email || ''}</Text>
        </View>
        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <MaterialIcons name="person" size={20} color={Colors.onSurfaceVariant} />
            <Text style={styles.infoLabel}>User ID</Text>
            <Text style={styles.infoValue}>{user?.id || '-'}</Text>
          </View>
        </View>
        <View style={styles.logoutSection}>
          <Button
            title="Sign Out"
            onPress={logout}
            variant="secondary"
          />
        </View>
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
  avatarSection: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  name: {
    ...Typography.headlineMd,
    color: Colors.onSurface,
    marginBottom: Spacing.xs,
  },
  email: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  infoCard: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm + 2,
    gap: Spacing.sm,
  },
  infoLabel: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    width: 70,
  },
  infoValue: {
    ...Typography.bodyMd,
    color: Colors.onSurface,
    flex: 1,
    textAlign: 'right',
  },
  logoutSection: {
    marginTop: Spacing.xl,
  },
});
