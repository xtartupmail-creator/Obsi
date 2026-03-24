import { gql } from '@apollo/client';

/**
 * Canonical observation stream used by new clients.
 */
export const NEW_OBSERVATION_SUBSCRIPTION = gql`
  subscription NewObservation {
    newObservation {
      id
      source
      value
      observedAt
    }
  }
`;

/**
 * Legacy alias retained for transitional clients.
 */
export const LIVE_OBSERVATIONS_SUBSCRIPTION = gql`
  subscription LiveObservations {
    liveObservations {
      id
      source
      value
      observedAt
    }
  }
`;
