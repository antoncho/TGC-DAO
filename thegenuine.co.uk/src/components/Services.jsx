import React from "react";
import SectionIntro from "./SectionIntro";
import Container from "./Container";
import FadeIn from "./FadeIn";
import StylizedImage from "./StylizedImage";
import imageLaptop from "../images/laptop.jpg";
import List, { ListItem } from "./List";

const Services = () => {
  return (
    <>
      <SectionIntro
        eyebrow="What we do"
        title="We design, build and scale real-world solutions."
        className="mt-24 sm:mt-32 lg:mt-40"
      >
        <p>
          From pure and frank conversation, through business and digital transformations, and to advanced tech and AI automation to secure distributed systems.
          We partner with you to uncover opportunities, validate ideas, and deliver products that create measurable impact.
        </p>
      </SectionIntro>
      <Container className="mt-16">
        <div className="lg:flex lg:items-center  lg:justify-end vertical-align: middle;">
         
          {/* List item */}
          <List className="mt-16 lg:mt-0 lg:w-1/2 lg:min-w-[33rem] lg:pl-4 grid grid-cols-1 md:grid-cols-2 gap-8">
            <ListItem title="AI Automation">
              We leverage cutting-edge emerging technology stack to automate complex business processes, 
              enhancing efficiency and decision-making across your organization.
            </ListItem>
            <ListItem title="Big Data & Data Intelligence">
              Our advanced analytics solutions transform vast datasets into actionable insights, driving strategic growth and innovation.
            </ListItem>
            <ListItem title="Blockchain Development">
              We create secure, transparent, and decentralised blockchain solutions, revolutionizing transactions and data management.
            </ListItem>
            <ListItem title="Dapps & Smart Contracts">
              Our team develops robust decentralized applications and smart contracts, enabling trustless and automated business operations.
            </ListItem>
            <ListItem title="Decentralized & Distributed Systems">
              We design and implement scalable distributed systems, ensuring high availability and fault tolerance for critical applications.
            </ListItem>
            <ListItem title="Cybersecurity">
              Our comprehensive security solutions protect your digital assets, safeguarding against evolving threats and ensuring data integrity.
            </ListItem>
            <ListItem title="Information Management Systems">
              We develop tailored information systems that streamline data flow, enhancing organizational efficiency and decision-making processes.
            </ListItem>
            <ListItem title="Infrastructure Planning & Management">
              Our experts design and manage robust IT infrastructures, optimizing performance and scalability for your growing business needs.
            </ListItem>
          </List>

         
          <div className="flex justify-center lg:w-1/2 lg:justify-end lg:pr-12">
            <FadeIn className="w-[33.75rem] flex-none lg:w-[45rem]">
              <StylizedImage
                src={imageLaptop}
                sizes="(min-width: 1024px) 41rem, 31rem"
                className="justify-center lg:justify-end"
              />
            </FadeIn>
          </div>
         
        </div>
      </Container>
    </>
  );
};

export default Services;
