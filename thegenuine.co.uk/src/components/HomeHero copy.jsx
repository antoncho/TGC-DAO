import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const HomeHero = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, antialias: true, alpha: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x002764, 1);

    camera.position.z = 50;

    const geometry = new THREE.PlaneGeometry(100, 100, 50, 50);
    const material = new THREE.MeshBasicMaterial({ color: 0x3062ff, wireframe: true });
    const waves = new THREE.Mesh(geometry, material);
    waves.rotation.x = -Math.PI / 4;
    scene.add(waves);

    const animate = () => {
      requestAnimationFrame(animate);

      const time = Date.now() * 0.001;
      const positions = geometry.attributes.position;

      for (let i = 0; i < positions.count; i++) {
        const y = 5 * Math.sin(i / 5 + time);
        positions.setY(i, y);
      }

      positions.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, []);

  return (
    <div className="relative w-full h-screen">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
      <div className="relative z-10 pt-20 pb-16 md:pt-32 md:pb-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl">
          <h1 className="font-display text-5xl font-medium tracking-tight text-white [text-wrap:balance] sm:text-7xl">
            Crafting genuine technology solutions for authentic brands
          </h1>
          <p className="mt-6 text-xl text-gray-300">
            We are a collective of creative minds dedicated to bringing authenticity to the forefront of design and technology. Our passion lies in creating meaningful connections between brands and their audiences.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomeHero;