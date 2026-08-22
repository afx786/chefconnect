import React, { useState } from 'react';
import {
  View,
  Text,
  Modal,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Colors } from '@/constants/colors';
import { Typography } from '@/constants/typography';
import { Spacing, BorderRadius } from '@/constants/spacing';
import { Chef } from '@/types/chef';
import { MealSlot } from '@/types/booking';
import { useBooking } from '@/hooks/useBooking';
import { formatDate } from '@/utils/formatDate';
import Button from './Button';
import BookingStatus from './BookingStatus';

interface BookingModalProps {
  visible: boolean;
  chef: Chef | null;
  onClose: () => void;
}

const MEAL_SLOTS: { value: MealSlot; label: string }[] = [
  { value: 'BREAKFAST', label: 'Breakfast' },
  { value: 'LUNCH', label: 'Lunch' },
  { value: 'DINNER', label: 'Dinner' },
];

export default function BookingModal({ visible, chef, onClose }: BookingModalProps) {
  const [date, setDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [mealSlot, setMealSlot] = useState<MealSlot>('DINNER');
  const [specialRequests, setSpecialRequests] = useState('');
  const { loading, error, success, submit, reset } = useBooking();

  const handleClose = () => {
    reset();
    setDate(new Date());
    setMealSlot('DINNER');
    setSpecialRequests('');
    onClose();
  };

  const handleSubmit = async () => {
    if (!chef) return;
    const dateStr = date.toISOString().split('T')[0];
    await submit({
      chef_id: chef.id,
      booking_date: dateStr,
      meal_slot: mealSlot,
      special_requests: specialRequests || null,
    });
  };

  if (!chef) return null;

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={handleClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.overlay}
      >
        <TouchableOpacity style={styles.backdrop} onPress={handleClose} activeOpacity={1} />
        <View style={styles.sheet}>
          <View style={styles.handle} />
          <ScrollView showsVerticalScrollIndicator={false}>
            {success ? (
              <BookingStatus booking={success} chefName={chef.name} onClose={handleClose} />
            ) : (
              <>
                <Text style={styles.title}>Book {chef.name}</Text>
                <Text style={styles.subtitle}>{chef.cuisine} · {chef.signature_dish}</Text>

                <Text style={styles.label}>DATE</Text>
                <TouchableOpacity
                  style={styles.dateButton}
                  onPress={() => setShowDatePicker(true)}
                >
                  <MaterialIcons name="calendar-today" size={18} color={Colors.onSurfaceVariant} />
                  <Text style={styles.dateText}>{formatDate(date.toISOString().split('T')[0])}</Text>
                </TouchableOpacity>
                {showDatePicker && (
                  <DateTimePicker
                    value={date}
                    mode="date"
                    display="default"
                    minimumDate={new Date()}
                    onChange={(_, selected) => {
                      setShowDatePicker(false);
                      if (selected) setDate(selected);
                    }}
                  />
                )}

                <Text style={[styles.label, { marginTop: Spacing.md }]}>MEAL SLOT</Text>
                <View style={styles.slotRow}>
                  {MEAL_SLOTS.map((s) => (
                    <TouchableOpacity
                      key={s.value}
                      style={[styles.slotChip, mealSlot === s.value && styles.slotChipActive]}
                      onPress={() => setMealSlot(s.value)}
                    >
                      <Text
                        style={[
                          styles.slotText,
                          mealSlot === s.value && styles.slotTextActive,
                        ]}
                      >
                        {s.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>

                <Text style={[styles.label, { marginTop: Spacing.md }]}>SPECIAL REQUESTS</Text>
                <TextInput
                  style={styles.input}
                  value={specialRequests}
                  onChangeText={setSpecialRequests}
                  placeholder="Any dietary preferences or special instructions..."
                  placeholderTextColor={Colors.outline}
                  multiline
                  numberOfLines={3}
                  textAlignVertical="top"
                />

                {error ? (
                  <View style={styles.errorBox}>
                    <MaterialIcons name="error-outline" size={18} color={Colors.error} />
                    <Text style={styles.errorText}>{error}</Text>
                  </View>
                ) : null}

                <Button
                  title="Request Booking"
                  onPress={handleSubmit}
                  loading={loading}
                  disabled={loading}
                  style={styles.submitButton}
                />
              </>
            )}
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  sheet: {
    backgroundColor: Colors.surfaceContainerLowest,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    paddingHorizontal: Spacing.containerMargin,
    paddingBottom: Spacing.xl,
    paddingTop: Spacing.sm,
    maxHeight: '85%',
  },
  handle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: Colors.outlineVariant,
    alignSelf: 'center',
    marginBottom: Spacing.md,
  },
  title: {
    ...Typography.headlineMd,
    color: Colors.onSurface,
    marginBottom: Spacing.xs,
  },
  subtitle: {
    ...Typography.bodyMd,
    color: Colors.onSurfaceVariant,
    marginBottom: Spacing.lg,
  },
  label: {
    ...Typography.labelSm,
    color: Colors.onSurfaceVariant,
    textTransform: 'uppercase',
    letterSpacing: 0.05,
    marginBottom: Spacing.sm,
  },
  dateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.surfaceContainerLow,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
  },
  dateText: {
    ...Typography.bodyMd,
    color: Colors.onSurface,
  },
  slotRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
  },
  slotChip: {
    flex: 1,
    paddingVertical: Spacing.sm + 2,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.surfaceContainerLow,
    alignItems: 'center',
  },
  slotChipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  slotText: {
    ...Typography.labelMd,
    color: Colors.onSurfaceVariant,
  },
  slotTextActive: {
    color: Colors.onPrimary,
  },
  input: {
    backgroundColor: Colors.surfaceContainerLow,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    ...Typography.bodyMd,
    color: Colors.onSurface,
    minHeight: 80,
  },
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
  submitButton: {
    marginTop: Spacing.lg,
  },
});
