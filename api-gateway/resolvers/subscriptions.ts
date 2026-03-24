import { PubSub } from 'graphql-subscriptions';

const NEW_OBSERVATION_TOPIC = 'NEW_OBSERVATION';

export type Observation = {
  id: string;
  source: string;
  value: number;
  observedAt: string;
};

const pubsub = new PubSub();

const subscribeToNewObservation = () =>
  pubsub.asyncIterator<Observation>([NEW_OBSERVATION_TOPIC]);

export const subscriptionResolvers = {
  Subscription: {
    /** Canonical subscription field used by frontend hooks. */
    newObservation: {
      subscribe: subscribeToNewObservation,
      resolve: (payload: Observation) => payload,
    },
    /**
     * Backward-compatibility alias. Keep until all clients migrate.
     * Uses same event stream to prevent semantic divergence.
     */
    liveObservations: {
      subscribe: subscribeToNewObservation,
      resolve: (payload: Observation) => payload,
    },
  },
};

/**
 * Event publisher used by ingestion pipeline or Hasura action/event bridge.
 */
export const publishNewObservation = (observation: Observation) => {
  return pubsub.publish(NEW_OBSERVATION_TOPIC, observation);
};
