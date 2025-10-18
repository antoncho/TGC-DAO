import ContactSection from "@/components/ContactSection";

export const metadata = {
  title: "About",
  description: "About The Genuine Collective — who we are and how we work.",
};
import Container from "@/components/Container";
import Cultures from "@/components/Cultures";
import PageIntro from "@/components/PageIntro";
import { StatList, StatListItem } from "@/components/StatList";
import React from "react";

const AboutPage = () => {
  return (
    <>
      <PageIntro eyebrow="About us" title="Our strength is collaboration">
        <p>
         TheGenuine Collective (TGC) is a new form of business organisation
         that aims to provide a platform for businesses to collaborate,
         and thrive collectively along with their customers and suppliers.
         We’re a remote‑first collective of professionals and organisations. 
         We partner closely with teams to shape strategy, design great experiences, and ship reliable software.
        </p>
        <div className="mt-10 max-w-2xl space-y-6 text-base">
          <p>
            The Genuine Collective began with a belief: authenticity wins. We
            focus on genuine problems and measurable impact, bringing a blend of
            product thinking, technical excellence, and honest communication to
            every engagement.
          </p>
          <p>
            Despite the current centralised state and physical organisation anchoring the entire venture, 
            TGC aims to elevate the governance structure of the business to a decentralised model, 
            once the foundation platform is launched.
          </p>
          <p>
            We keep teams small, feedback loops tight, and delivery continuous.
            You’ll work directly with the people designing and building your
            product — no layers, no theatre, just good work together.
          </p>
        </div>
      </PageIntro>
      <Container className="mt-16">
        <StatList>
          <StatListItem value="10+" label="Years combined experience" />
          <StatListItem value="20+" label="Projects delivered" />
          <StatListItem value=">95%" label="On-time milestones" />
        </StatList>
      </Container>
      <Cultures />
      <ContactSection />
    </>
  );
};

export default AboutPage;
