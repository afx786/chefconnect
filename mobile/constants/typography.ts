import { TextStyle } from 'react-native';

const FONT_FAMILY = 'HankenGrotesk';

export const Typography: Record<string, TextStyle> = {
  displayLg: {
    fontFamily: FONT_FAMILY,
    fontSize: 48,
    fontWeight: '700',
    lineHeight: 56,
    letterSpacing: -0.02,
  },
  headlineLg: {
    fontFamily: FONT_FAMILY,
    fontSize: 32,
    fontWeight: '600',
    lineHeight: 40,
    letterSpacing: -0.01,
  },
  headlineLgMobile: {
    fontFamily: FONT_FAMILY,
    fontSize: 28,
    fontWeight: '600',
    lineHeight: 36,
  },
  headlineMd: {
    fontFamily: FONT_FAMILY,
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
  },
  bodyLg: {
    fontFamily: FONT_FAMILY,
    fontSize: 18,
    fontWeight: '400',
    lineHeight: 28,
  },
  bodyMd: {
    fontFamily: FONT_FAMILY,
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
  },
  labelMd: {
    fontFamily: FONT_FAMILY,
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 20,
    letterSpacing: 0.02,
  },
  labelSm: {
    fontFamily: FONT_FAMILY,
    fontSize: 12,
    fontWeight: '500',
    lineHeight: 16,
    letterSpacing: 0.05,
  },
};
