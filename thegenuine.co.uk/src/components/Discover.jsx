import React from "react";
import Section from "./Section";
import imageWhiteboard from "@/images/whiteboard.jpg";
import { TagList, TagListItem } from "./TagList";

const Discover = () => {
  return (
    <Section title="Discover" image={{ src: imageWhiteboard, shape: 1 }}>
      <div className="space-y-6 text-base text-neutral-600">
        <p>
          We immerse ourselves in your context to understand goals, constraints,
          risks, and opportunities. Together we clarify the problem space and
          align on success.
        </p>
        <p>
          Through stakeholder interviews, technical audits, and rapid
          prototyping, we de‑risk assumptions and validate direction before we
          commit engineering effort.
        </p>
        <p>
          The outcome is a clear plan, realistic roadmap, and shared
          understanding that keeps delivery focused and measurable.
        </p>
      </div>
      <h3 className="mt-12 font-display text-base font-semibold text-neutral-950">
        Included in this phase
      </h3>
      <TagList className="mt-4">
        <TagListItem>Stakeholder interviews</TagListItem>
        <TagListItem>Technical audit</TagListItem>
        <TagListItem>Data discovery</TagListItem>
        <TagListItem>Risk assessment</TagListItem>
        <TagListItem>Prototyping & validation</TagListItem>
        <TagListItem>Roadmapping</TagListItem>
      </TagList>
    </Section>
  );
};

export default Discover;
