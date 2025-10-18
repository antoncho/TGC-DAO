import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { SimplexNoise } from 'three/examples/jsm/math/SimplexNoise';
import { useColorModeValue, Text } from '@chakra-ui/react';
import { motion, useScroll, useTransform } from 'framer-motion';

const HomeHero = () => {
  const canvasRef = useRef(null);
  const sceneRef = useRef(null);
  const [scrollProgress, setScrollProgress] = useState(0);

  // Define responsive colors
  const backgroundColor = useColorModeValue('rgb(249, 250, 251)', 'linear-gradient(to bottom, #1A202C, #000000)');
  const particleColor = useColorModeValue('rgb(55, 65, 81)', 'rgb(55, 65, 81)');
  const textColor = useColorModeValue('black', 'white');
  const subTextColor = useColorModeValue('gray.600', 'gray.300');

  const { scrollYProgress } = useScroll();
  const scale = useTransform(scrollYProgress, [0, 1], [1, 1.5]);
  const yPos = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 0.5, 0]);

  useEffect(() => {
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    const camera = new THREE.PerspectiveCamera(30, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(4, 2, 8);
    camera.lookAt(scene.position);

    const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Set scene background to transparent
    scene.background = null;

    const geometry = new THREE.PlaneGeometry(12, 8, 150, 100);
    const pos = geometry.getAttribute('position');
    const simplex = new SimplexNoise();

    // Create a color attribute for the particles
    const colors = new Float32Array(pos.count * 3);
    for (let i = 0; i < pos.count; i++) {
      colors[i * 3] = colors[i * 3 + 1] = colors[i * 3 + 2] = 1; // Default color (white)
    }

    // Choose a random particle to be red
    const specialIndex = Math.floor(Math.random() * pos.count);
    colors[specialIndex * 3] = 1;     // Red
    colors[specialIndex * 3 + 1] = 0; // Green
    colors[specialIndex * 3 + 2] = 0; // Blue

    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const waves = new THREE.Points(
      geometry,
      new THREE.PointsMaterial({ 
        size: 0.03, 
        vertexColors: true,
        color: new THREE.Color(particleColor),
        transparent: true,
        opacity: 1
      })
    );
    waves.rotation.x = -Math.PI / 2;
    scene.add(waves);

    const animationLoop = (t) => {
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        const y = pos.getY(i);
        const z = 0.5 * simplex.noise3d(x / 2, y / 2, t / 2000 + scrollProgress);
        pos.setZ(i, z);
      }
      pos.needsUpdate = true;

      waves.material.opacity = 1 - scrollProgress;

      renderer.render(scene, camera);
      requestAnimationFrame(animationLoop);
    };

    animationLoop(0);

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      geometry.dispose();
      waves.material.dispose();
    };
  }, [particleColor]);

  useEffect(() => {
    const unsubscribe = scrollYProgress.onChange(v => {
      setScrollProgress(v);
      if (sceneRef.current) {
        sceneRef.current.scale.set(1 + v * 0.5, 1 + v * 0.5, 1 + v * 0.5);
        sceneRef.current.position.y = v * 2; // Move content up
      }
    });
    return () => unsubscribe();
  }, [scrollYProgress]);

  return (
    <motion.div className="relative" style={{ scale, y: yPos, opacity }}>
      <div style={{ 
        position: 'relative', 
        inset: 0, 
        background: backgroundColor 
      }} />
      <canvas 
        ref={canvasRef} 
        style={{ 
          position: 'absolute', 
          inset: 0,
          width: '100%', 
          height: '100%'
        }} 
      />
      <div className="relative z-10 pt-20 pb-16 md:pt-32 md:pb-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl">
          <Text
            as="h1"
            fontSize={['5xl', null, '7xl']}
            fontWeight="medium"
            letterSpacing="tight"
            color={textColor}
            lineHeight="tight"
            className="font-display [text-wrap:balance]"
          >
            Crafting genuine technology solutions for authentic brands
          </Text>
          <Text
            mt={6}
            fontSize="xl"
            color={subTextColor}
          >
            We are a collective of creative minds with backgrounds in design, engineering and business, dedicated to bringing authenticity to the
            forefront of our work. Our passion lies in creating meaningful connections between human capital and technology at their hands.
          </Text>
        </div>
      </div>
    </motion.div>
  );
};

export default HomeHero;