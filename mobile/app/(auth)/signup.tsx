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

export default function SignupScreen() {
  const router = useRouter();
  const { signup, isLoading, error, clearError } = useAuthContext();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSignup = async () => {
    if (!name.trim() || !email.trim() || !password) return;
    try {
      await signup({ name: name.trim(), email: email.trim(), password });
      setSuccess(true);
    } catch {
      // error is in context
    }
  };

  if (success) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.successContainer}>
          <View style={styles.successIcon}>
            <MaterialIcons name="check-circle" size={64} color={Colors.tertiary} />
          </View>
          <Text style={styles.successTitle}>Account created</Text>
          <Text style={styles.successSubtitle}>You can now sign in with your credentials</Text>
          <Button
            title="Go to Sign In"
            onPress={() => router.replace('/(auth)/login')}
            style={styles.successButton}
          />
        </View>
      </SafeAreaView>
    );
  }

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
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <MaterialIcons name="arrow-back" size={22} color={Colors.onSurface} />
          </TouchableOpacity>

          <View style={styles.header}>
            <Text style={styles.brand}>ChefConnect</Text>
            <Text style={styles.headline}>Create account</Text>
            <Text style={styles.subtitle}>Join to start booking private chefs</Text>
          </View>

          <View style={styles.form}>
            <Text style={styles.label}>NAME</Text>
            <TextInput
              style={styles.input}
              value={name}
              onChangeText={(t) => { setName(t); clearError(); }}
              placeholder="Your full name"
              placeholderTextColor={Colors.outline}
              autoCapitalize="words"
            />

            <Text style={[styles.label, { marginTop: Spacing.md }]}>EMAIL</Text>
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
                placeholder="Min 8 characters"
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
              title="Create Account"
              onPress={handleSignup}
              loading={isLoading}
              disabled={isLoading || !name.trim() || !email.trim() || !password}
              style={styles.signupButton}
            />
          </View>

          <TouchableOpacity
            style={styles.loginLink}
            onPress={() => router.replace('/(auth)/login')}
          >
            <Text style={styles.loginText}>
              Already have an account? <Text style={styles.loginBold}>Sign in</Text>
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
  scroll: { flexGrow: 1, padding: Spacing.containerMargin },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: Colors.surfaceContainerHigh,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.lg,
  },
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
  signupButton: { marginTop: Spacing.lg },
  loginLink: { alignItems: 'center', paddingVertical: Spacing.md },
  loginText: { ...Typography.bodyMd, color: Colors.onSurfaceVariant },
  loginBold: { color: Colors.primary, fontWeight: '600' },
  successContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.containerMargin,
  },
  successIcon: { marginBottom: Spacing.lg },
  successTitle: {
    ...Typography.headlineMd,
    color: Colors.onSurface,
    marginBottom: Spacing.xs,
  },
  successSubtitle: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: Spacing.xl,
  },
  successButton: { width: 200 },
});
