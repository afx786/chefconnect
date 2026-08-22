import { Redirect } from 'expo-router';
import { useAuthContext } from '@/context/AuthContext';

export default function Index() {
  const { isAuthenticated } = useAuthContext();
  return <Redirect href={isAuthenticated ? '/(tabs)/explore' : '/(auth)/login'} />;
}
