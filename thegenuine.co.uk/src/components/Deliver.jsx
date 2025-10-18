import React from "react";
import Section from "./Section";
import imageMeeting from "@/images/meeting.jpg";
import List, { ListItem } from "./List";

const Deliver = () => {
  return (
    <Section title="Deliver" image={{ src: imageMeeting, shape: 1 }}>
      <div className="space-y-6 text-base text-neutral-600">
        <p>
          We plan releases to minimise risk and maximise learning. Rollouts are
          monitored with clear SLOs, alerting, and analytics to validate impact.
        </p>
        <p>
          After launch, we review outcomes with your team and prioritise the
          next most valuable increment. Support and iterations are built into
          the plan — not bolted on.
        </p>
      </div>
      <h3 className="mt-12 font-display text-base font-semibold text-neutral-950">
        Included in this phase
      </h3>
      <List className="mt-8">
        <ListItem title="Release planning & rollout">
          Phased releases, feature flags, and clear communication to
          stakeholders.
        </ListItem>
        <ListItem title="Operational excellence">
          Observability, incident response, and blameless reviews that improve
          the system over time.
        </ListItem>
        <ListItem title="Growth & iteration">
          Post‑launch roadmap aligned to outcomes, with continuous delivery and
          measurement.
        </ListItem>
      </List>
    </Section>
  );
};

export default Deliver;
