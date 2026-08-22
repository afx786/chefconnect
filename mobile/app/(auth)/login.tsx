import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius } from '@/constants/spacing';
import { useAuthContext } from '@/context/AuthContext';
import Button from '@/components/Button';

export default function LoginScreen() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthContext();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!email.trim() || !password) return;
    try {
      await login({ email: email.trim(), password });
      router.back();
    } catch {
      // error is in context
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.header}>
            <Text style={styles.brand}>ChefConnect</Text>
            <Text style={styles.headline}>Welcome back</Text>
            <Text style={styles.subtitle}>Sign in to continue booking chefs</Text>
          </View>

          <View style={styles.form}>
            <Text style={styles.label}>EMAIL</Text>
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={(t) => { setEmail(t); clearError(); }}
              placeholder="you@example.com"
              placeholderTextColor={Colors.outline}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />

            <Text style={[styles.label, { marginTop: Spacing.md }]}>PASSWORD</Text>
            <View style={styles.passwordRow}>
              <TextInput
                style={styles.passwordInput}
                value={password}
                onChangeText={(t) => { setPassword(t); clearError(); }}
                placeholder="Enter your password"
                placeholderTextColor={Colors.outline}
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowPassword(!showPassword)}
              >
                <MaterialIcons
                  name={showPassword ? 'visibility-off' : 'visibility'}
                  size={20}
                  color={Colors.outline}
                />
              </TouchableOpacity>
            </View>

            {error ? (
              <View style={styles.errorBox}>
                <MaterialIcons name="error-outline" size={18} color={Colors.error} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            ) : null}

            <Button
              title="Sign In"
              onPress={handleLogin}
              loading={isLoading}
              disabled={isLoading || !email.trim() || !password}
              style={styles.loginButton}
            />
          </View>

          <TouchableOpacity
            style={styles.signupLink}
            onPress={() => router.replace('/(auth)/signup')}
          >
            <Text style={styles.signupText}>
              Don't have an account? <Text style={styles.signupBold}>Sign up</Text>
            </Text>
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  flex: { flex: 1 },
  scroll: { flexGrow: 1, padding: Spacing.containerMargin, justifyContent: 'center' },
  header: { marginBottom: Spacing.xl },
  brand: {
    ...Typography.labelMd,
    color: Colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 0.1,
    marginBottom: Spacing.lg,
  },
  headline: {
    ...Typography.headlineLgMobile,
    color: Colors.onSurface,
    marginBottom: Spacing.xs,
  },
  subtitle: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
  },
  form: { marginBottom: Spacing.xl },
  label: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    textTransform: 'uppercase',
    letterSpacing: 0.05,
    marginBottom: Spacing.sm,
  },
  input: {
    backgroundColor: Colors.surfaceContainerLow,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    ...Typography.bodyMd,
    color: Colors.onSurface,
    minHeight: 48,
  },
  passwordRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceContainerLow,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
  },
  passwordInput: {
    flex: 1,
    padding: Spacing.md,
    ...Typography.bodyMd,
    color: Colors.onSurface,
    minHeight: 48,
  },
  eyeButton: { padding: Spacing.md },
  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.errorContainer,
    borderRadius: BorderRadius.default,
    padding: Spacing.sm + 2,
    marginTop: Spacing.md,
  },
  errorText: {
    ...Typography.bodyMd,
    color: Colors.onErrorContainer,
    flex: 1,
  },
  loginButton: { marginTop: Spacing.lg },
  signupLink: { alignItems: 'center', paddingVertical: Spacing.md },
  signupText: { ...Typography.bodyMd, color: Colors.onSurfaceVariant },
  signupBold: { color: Colors.primary, fontWeight: '600' },
});
