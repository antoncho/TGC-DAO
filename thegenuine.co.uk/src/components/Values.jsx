import React from "react";
import GridPattern from "./GridPattern";
import SectionIntro from "./SectionIntro";
import Container from "./Container";
import { GridList, GridListItem } from "./GridList";

const Values = () => {
  return (
    <div className="relative mt-24 pt-24 sm:mt-32 sm:pt-32 lg:mt-40 lg:pt-40">
      <div className="absolute inset-x-0 top-0 -z-10 h-[884px] overflow-hidden rounded-t-4xl bg-gradient-to-b from-neutral-50">
        <GridPattern
          className="absolute inset-0 h-full w-full fill-neutral-100 stroke-neutral-950/5 [mask-image:linear-gradient(to_bottom_left,white_40%,transparent_50%)]"
          yOffset={-270}
        />
      </div>
  <SectionIntro
        eyebrow="Our values"
        title="Genuine by design"
      >
        <p>
          We believe authenticity drives trust, and trust drives outcomes. Our
          work blends thoughtful strategy, careful execution, and continuous
          learning to deliver lasting results.
        </p>
      </SectionIntro>
      <Container className="mt-24">
        <GridList>
          <GridListItem title="Authentic">
            We build with clarity and honesty, aligning solutions to real needs
            and clear outcomes.
          </GridListItem>
          <GridListItem title="Crafted">
            Details matter. We sweat the fundamentals to ensure quality,
            reliability, and maintainability.
          </GridListItem>
          <GridListItem title="Pragmatic">
            We prioritise the right thing at the right time to move you forward with confidence.
          </GridListItem>
          <GridListItem title="Collaborative">
            We partner closely with your team, transferring knowledge and building lasting capability.
          </GridListItem>
          <GridListItem title="Secure">
            Security and privacy are foundational — not an afterthought.
          </GridListItem>
          <GridListItem title="Curious">
            We learn continuously and adapt quickly as technologies and markets
            evolve.
          </GridListItem>
        </GridList>
      </Container>
    </div>
  );
};

export default Values;
