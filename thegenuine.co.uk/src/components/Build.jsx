import React from "react";
import Section from "./Section";
import imageLaptop from "@/images/laptop.jpg";
import Blockquote from "./Blockquote";

const Build = () => {
  return (
    <Section title="Build" image={{ src: imageLaptop, shape: 2 }}>
      <div className="space-y-6 text-base text-neutral-600">
        <p>
          With a validated roadmap, we design system architecture and iterate on
          the product in small, testable increments. We integrate security,
          observability, and performance from day one.
        </p>
        <p>
          You’ll have a dedicated team, frequent demos, and transparent
          milestones. We co‑create with your stakeholders to keep feedback loops
          tight and momentum high.
        </p>
        <p>
          Delivery is outcome‑driven: shipping value early, reducing risk, and
          maintaining quality as we scale.
        </p>
      </div>
      <Blockquote
        author={{ name: "Debra Fiscal", role: "CEO, Unseal" }}
        className="mt-12"
      >
        The Genuine Collective kept us focused on outcomes. Clear milestones,
        solid engineering, and genuinely collaborative delivery.
      </Blockquote>
    </Section>
  );
};

export default Build;
