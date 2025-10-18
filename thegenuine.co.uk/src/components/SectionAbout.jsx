import React from "react";
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import SectionIntro from "./SectionIntro";
import Container from "./Container";
import FadeIn from "./FadeIn";
import FadeInOut from "./FadeInOut";
import StylizedImage2 from "./StylizedImage2";
import imageAbout from "/public/images/collective-action.jpg";
import List, { ListItem } from "./List";
import GridPattern from "./GridPattern";
const SectionAbout = () => {
	const [ref1, inView1] = useInView({
		triggerOnce: false,
		threshold: 0.5,
	});

	const [ref2, inView2] = useInView({
		triggerOnce: false,
		threshold: 0.2,
	});

	const AboutVariants = {
		hidden: { opacity: 0, y: 40 },
		visible: { opacity: 1, y: 70, transition: { duration: 0.5 } },
		exit: { opacity: 0, y: 90, transition: { duration: 0.5 } },
	};

	const listItemVariants =  {
		hidden: { opacity: 0, y: 40 },
		visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
		exit: { opacity: 0, y: 40, transition: { duration: 0.5 } },
	};

	const imageVariants = {
		hidden: { opacity: 0, x: 40 },
		visible: { opacity: 1, x: 0, transition: { duration: 0.5 } },
	};

	return (
		<>
   
			<motion.div
				ref={ref1}
				initial="hidden"
				animate={inView1 ? "visible" : "exit"}
				variants={AboutVariants}
			>
				<Container className="m-0 w-full items-left max-w-8xl mx-auto relative">
      
                    <SectionIntro
                        eyebrow="What is The Genuine Collective?"
                        title="We help you identify, explore and respond to new opportunities."
                        className="mt-24 sm:mt-32 lg:mt-4 items-right"
                    >
                        <h2 className="text-2xl font-normal">
                            A collective of real humans with expertise aiming to co-create
                            trustworthy, human‑centred solutions and digital products, alongside our clients.
                        </h2>
                    </SectionIntro>
				</Container>
			</motion.div>

			<Container className="mt-0 w-full items-left max-w-8xl mx-auto relative">
				<div className="lg:flex lg:items-center lg:justify-left p-0">
				
        <motion.div
						className="lg:w-1/2 lg:min-w-[33rem] lg:pl-4"
						initial="hidden"
						animate={inView2 ? "visible" : "hidden"}
						variants={{
							visible: {
								transition: { staggerChildren: 0.2 }
							}
						}}
					>
                            <List className="mt-0 lg:mt-0">
                                <motion.div variants={listItemVariants}>
                                    <ListItem title="Who we are">
                                        The Genuine Collective is a group of creators united by a
                                        commitment to authentic design, robust engineering, and
                                        measurable outcomes in real-life value creation.
                                    </ListItem>
                                </motion.div>
                                <motion.div variants={listItemVariants}>
                                    <ListItem title="Our mission & vision">
                                        Elevate your business through genuine, impactful digital solutions.
                                        We connect strategy with craft to build products that are
                                        both beautiful and effective.
                                    </ListItem>
                                </motion.div>
                            </List>
					</motion.div>


          <motion.div
				ref={ref1}
				initial="hidden"
				animate={inView1 ? "visible" : "exit"}
				variants={imageVariants}
			>
						<FadeIn className="w-[33.75rem] flex-none lg:w-[45rem]">
							<StylizedImage2
								src={imageAbout}
								sizes="(min-width: 1024px) 41rem, 31rem"
								className="justify-center lg:justify-end"
							/>

						</FadeIn>
            </motion.div>
       
				</div>
        <GridPattern
        className="absolute inset-0 z-0 h-full w-full fill-neutral-100 stroke-neutral-950/5 [mask-image:linear-gradient(to_bottom_left,white_50%,transparent_60%)] dark:fill-black-900 dark:stroke-neutral-50/5"
        yOffset={-120}
        
      />
			</Container>
		</>
	);
};

export default SectionAbout;
