import { useSubscription } from '@apollo/client';
import {
  LIVE_OBSERVATIONS_SUBSCRIPTION,
  NEW_OBSERVATION_SUBSCRIPTION,
} from '../graphql/subscriptions';

type Observation = {
  id: string;
  source: string;
  value: number;
  observedAt: string;
};

/**
 * Preferred hook using canonical schema field name.
 */
export const useNewObservation = () =>
  useSubscription<{ newObservation: Observation }>(NEW_OBSERVATION_SUBSCRIPTION);

/**
 * Transitional hook for older callers. Prefer `useNewObservation`.
 */
export const useLiveObservations = () =>
  useSubscription<{ liveObservations: Observation }>(LIVE_OBSERVATIONS_SUBSCRIPTION);
