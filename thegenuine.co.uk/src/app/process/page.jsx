import Build from "@/components/Build";
import ContactSection from "@/components/ContactSection";
import Deliver from "@/components/Deliver";
import Discover from "@/components/Discover";
import PageIntro from "@/components/PageIntro";
import Values from "@/components/Values";
import React from "react";

export const metadata = {
  title: "Process",
  description: "Our outcome‑driven process from discovery through delivery.",
};

const ProcessPage = () => {
  return (
    <>
      <PageIntro eyebrow="Our process" title="How we work">
        <p>
          A clear, outcome‑driven process from discovery through delivery. Small
          batches, rapid feedback, and continuous improvement keep us moving
          fast without breaking trust.
        </p>
      </PageIntro>
      <div className="mt-24 space-y-24 [counter-reset:section] sm:mt-32 sm:space-y-32 lg:mt-40 lg:space-y-40">
        {/* Discover */}
        <Discover />
        {/* Build */}
        <Build />
        {/* Deliver */}
        <Deliver />
      </div>
      {/* Values */}
      <Values />
      <ContactSection />
    </>
  );
};

export default ProcessPage;
