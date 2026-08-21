import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';

export default function LoginScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Login (MVP 2)</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' },
  text: { ...Typography.headlineMd, color: Colors.onSurface },
});
