import React, { useEffect, useRef } from 'react';

const HomeThreeScene = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    // Include Three.js library
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
    script.async = true;
    document.body.appendChild(script);

    // Include GSAP library
    const gsapScript = document.createElement('script');
    gsapScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.9.1/gsap.min.js';
    gsapScript.async = true;
    document.body.appendChild(gsapScript);

    script.onload = () => {
      // The rest of your code goes here, starting with:
      const MAIN_IMAGE_URL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/204379/mosaic_main_d.jpg";
      const MOSAIC_IMAGE_URL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/204379/mosaic_sheet_a.jpg";

      const Utils = {
        groupByArray(xs, key) {
          return xs.reduce(function (rv, x) {
            let v = key instanceof Function ? key(x) : x[key];
            let el = rv.find(r => r && r.key === v);
            if (el) {
              el.values.push(x);
            } else {
              rv.push({ key: v, values: [x] });
            }
            return rv;
          }, []);
        },
        getSizeToCover(width, height, maxWidth, maxHeight) {
          var ratio = Math.max(maxWidth / width, maxHeight / height);
          return [width * ratio, height * ratio];
        },
        visibleHeightAtZDepth(camera, depth = 0) {
          const cameraOffset = camera.position.z;
          if (depth < cameraOffset) depth -= cameraOffset;
          else depth += cameraOffset;
          const vFOV = camera.fov * Math.PI / 180;
          return 2 * Math.tan(vFOV / 2) * Math.abs(depth);
        },
        visibleWidthAtZDepth(camera, depth = 0) {
          const height = this.visibleHeightAtZDepth(camera, depth);
          return height * camera.aspect;
        },
        lerp(start, end, amt) {
          return (1 - amt) * start + amt * end;
        }
      };

      class SpriteTexture {
        constructor(texture, tilesHorizontal, tilesVertical, frameCount, frameNum) {
          this.texture = texture;
          this.tiles = { x: tilesHorizontal, y: tilesVertical };
          this.frameCount = frameCount;
          texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
          texture.repeat.set(1 / this.tiles.x, 1 / this.tiles.y);
          this.setFrame(frameNum);
        }

        setFrame(frameIndex) {
          const xIndex = frameIndex % this.tiles.x;
          const yIndex = Math.floor(frameIndex / this.tiles.x);
          const halfX = 1 / this.tiles.x / 2;
          const halfY = 1 / this.tiles.y / 2;
          this.texture.offset.x = xIndex / this.tiles.x + halfX;
          this.texture.offset.y = -(yIndex / this.tiles.y) - halfY;
        }
      }

      class Object3DResizer {
        constructor(camera, obj) {
          this.camera = camera;
          this.obj = obj;
          this.scale = new THREE.Vector2(1, 1);
          this.setSize(1, 1);
        }

        setSize(width, height) {
          this.scale.set(width, height);
          this.update();
        }

        update() {
          const { obj, camera, scale } = this;
          const w = Utils.visibleWidthAtZDepth(camera);
          const h = Utils.visibleHeightAtZDepth(camera);
          obj.scale.x = w * scale.x;
          obj.scale.y = h * scale.y;
        }
      }

      class TextureResizer {
        constructor(texture, obj) {
          this.obj = obj;
          this.texture = texture;
          this.texture.center.set(0.5, 0.5);
          this.texture.wrapS = this.texture.wrapT = THREE.ClampToEdgeWrapping;
          this.scale = new THREE.Vector2(1, 1);
          this.originalSize = new THREE.Vector2(1, 1);
        }

        updateTextureSize() {
          const { originalSize, texture } = this;
          const { naturalWidth: nW, naturalHeight: nH } = texture.image;
          if (nW > nH) {
            originalSize.x = 1;
            originalSize.y = nH / nW;
          } else {
            originalSize.x = nW / nH;
            originalSize.y = 1;
          }
        }

        update() {
          const { scale, texture, obj, originalSize } = this;
          let formFactorX = 1;
          let formFactorY = 1;

          if (texture.image) {
            this.updateTextureSize();
            const [widthCover, heightCover] = Utils.getSizeToCover(
              originalSize.x,
              originalSize.y,
              obj.scale.x,
              obj.scale.y
            );

            formFactorX = widthCover / obj.scale.x;
            formFactorY = heightCover / obj.scale.y;
          }
          const scaleX = 1 / (this.scale.x * formFactorX);
          const scaleY = 1 / (this.scale.y * formFactorY);
          texture.repeat.set(scaleX, scaleY);
        }
      }

      class ImagePlane {
        constructor(textureUrl, camera) {
          this.scale = new THREE.Vector2(1, 1);
          this.texture = new THREE.TextureLoader().load(
            textureUrl,
            this.updateSize.bind(this)
          );

          this.geometry = new THREE.PlaneBufferGeometry(1, 1, 1, 1);
          this.material = new THREE.MeshLambertMaterial({
            map: this.texture,
            wireframe: false
          });

          this.mesh = new THREE.Mesh(this.geometry, this.material);
          this.objectResizer = new Object3DResizer(camera, this.mesh);
          this.textureResizer = new TextureResizer(this.texture, this.mesh);
        }

        updateSize() {
          this.objectResizer.scale.copy(this.scale);
          this.objectResizer.update();
          this.textureResizer.update();
        }
      }

      class HexGrid {
        constructor(camera) {
          this.lastActiveCell = undefined;
          this.activeCells = [];
          this.groupObject = new THREE.Object3D();
          this.texture = new THREE.Texture();
          this.camera = camera;
          this.cells = {};
          this.cellSize = 0.45;
          this.cellShapeGeo = new THREE.CircleGeometry(0.5, 6);
          this.initLayout();
          this.initGrid();
        }

        initLayout() {
          this.generate({ size: 8 });
        }

        generate(options) {
          const size = options.size || 8;
          for (let q = -size; q <= size; q++) {
            for (let r = Math.max(-size, -q - size); r <= Math.min(size, -q + size); r++) {
              const s = -q - r;
              this.cells[`${q},${r},${s}`] = { q, r, s };
            }
          }
        }

        cellToPixel(cell) {
          const x = this.cellSize * (3/2 * cell.q);
          const y = this.cellSize * (Math.sqrt(3)/2 * cell.q + Math.sqrt(3) * cell.r);
          return new THREE.Vector3(x, y, 0);
        }

        getTileMaterial(overlay, frameIndex) {
          const framesCount = 64;
          const tilesX = 8;
          const tilesY = 8;
          const halfX = 1 / tilesX / 2;
          const halfY = 1 / tilesY / 2;
          frameIndex = frameIndex % framesCount;
          const xIndex = frameIndex % tilesX;
          const yIndex = Math.floor(frameIndex / tilesX);
          const x = 1 - xIndex / tilesX - halfX;
          const y = 1 - yIndex / tilesY - halfY;

          const uniforms = {
            texture: { value: this.texture },
            offset: { value: new THREE.Vector2(x, y) },
            repeat: { value: new THREE.Vector2(1 / tilesX, 1 / tilesY) },
            opacity: { value: 1 },
            color: { value: new THREE.Color(0xffffff) }
          };

          const vertexShader = `
            varying vec2 vUv;
            uniform vec2 offset;
            uniform vec2 repeat;
            void main() {
              vUv = uv * repeat + offset;
              gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
          `;

          const fragmentShader = overlay ? `
            varying vec2 vUv;
            uniform sampler2D texture;
            uniform vec3 color;
            void main() {
              vec4 texColor = texture2D(texture, vUv);
              vec3 contrast = texColor.rgb * 0.7;
              float gray = dot(contrast, vec3(0.299, 0.587, 0.114));
              gl_FragColor = vec4(vec3(gray), 0.1) * vec4(color, 1.0);
            }
          ` : `
            varying vec2 vUv;
            uniform sampler2D texture;
            uniform vec3 color;
            uniform float opacity;
            void main() {
              gl_FragColor = texture2D(texture, vUv) * vec4(color, opacity);
            }
          `;

          const mat = new THREE.ShaderMaterial({
            uniforms,
            vertexShader,
            fragmentShader,
            transparent: true
          });

          if (overlay) {
            mat.blending = THREE.CustomBlending;
            mat.blendSrc = THREE.SrcColorFactor;
            mat.blendDst = THREE.DstColorFactor;
            mat.blendEquation = THREE.AddEquation;
          }

          return mat;
        }

        getMeshFromCell(cell, overlayMaterial, frameIndex) {
          const mat = this.getTileMaterial(overlayMaterial, frameIndex);
          const mesh = new THREE.Mesh(this.cellShapeGeo, mat);
          mesh.position.copy(this.cellToPixel(cell));
          mesh.rotateOnAxis(new THREE.Vector3(1, 0, 0), Math.PI / 2);
          mesh.scale.set(0.96, 0.96, 1);
          mesh.userData.cell = cell;
          mesh.userData.frameIndex = frameIndex;
          return mesh;
        }

        initGrid() {
          const cellKeys = Object.keys(this.cells);
          cellKeys.forEach((k, frameIndex) => {
            const cell = this.cells[k];
            const mesh = this.getMeshFromCell(cell, true, frameIndex);
            mesh.userData.isOver = false;
            this.groupObject.add(mesh);
          });

          this.groupObject.rotation.x = -Math.PI / 2;
          this.groupObject.position.z = 2.5;
        }

        setTexture(textureUrl) {
          new THREE.TextureLoader().load(textureUrl, (texture) => {
            this.texture = texture;
            this.groupObject.children.forEach(
              c => c.material.uniforms.texture.value = this.texture
            );
            this.updateSize();
          });
        }

        updateSize() {
          const h = Utils.visibleHeightAtZDepth(this.camera, 1.5);
          const w = Utils.visibleWidthAtZDepth(this.camera, 1.5);
          const aspect = w / h;
          const gridSize = 16 * 0.55;
          this.groupObject.scale.set(w / gridSize, 1, h / gridSize * aspect);
        }

        animateGridTilesIn() {
          const tiles = this.groupObject.children.map(c => {
            const cell = c.userData.cell;
            const d = Math.max(Math.abs(cell.q), Math.abs(cell.r), Math.abs(cell.s));
            return { target: c, d };
          });

          const rings = Utils.groupByArray(tiles, "d");
          rings.forEach(r => {
            r.values.forEach(item => {
              const target = item.target;
              target.scale.set(0.5, 0.5, 1);
              gsap.to(target.scale, {
                x: 0.96,
                y: 0.96,
                duration: item.d * 0.22 + 0.8,
                ease: "power3.out",
                delay: item.d * 0.12
              });
            });
          });

          gsap.from(this.groupObject.position, {
            z: 7,
            duration: 2,
            ease: "power3.out"
          });
        }

        animatePosition(target, endPosition, duration) {
          const startPosition = target.position.clone();
          const startTime = performance.now();

          const updatePosition = (time) => {
            const progress = Math.min((time - startTime) / (duration * 1000), 1);
            target.position.z = Utils.lerp(startPosition.z, endPosition.z, progress);

            if (progress < 1) {
              requestAnimationFrame(updatePosition);
            }
          };

          requestAnimationFrame(updatePosition);
        }
      }

      class App {
        constructor() {
          this.width = 0;
          this.height = 0;
          this.mouse = new THREE.Vector2(0, 0);
          this.raycaster = new THREE.Raycaster();
          this.init();
          this.setupScene();
          this.setupLights();
          this.attachEvents();
          this.setupMosaic();
          this.onResize();
          this.onFrame(0);
          this.loader = THREE.DefaultLoadingManager;
          this.loader.onProgress = (url, itemsLoaded, itemsTotal) => {
            if (itemsLoaded === itemsTotal) {
              this.mosaicAnimationIn();
            }
          };
        }

        init() {
          const { innerWidth: w, innerHeight: h } = window;
          this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            canvas: canvasRef.current
          });
          this.scene = new THREE.Scene();
          this.camera = new THREE.PerspectiveCamera(45, 0, 0.1, 1000);
          this.renderer.setPixelRatio(window.devicePixelRatio);
          this.clock = new THREE.Clock();
        }

        attachEvents() {
          window.addEventListener("resize", this.onResize.bind(this));
          window.addEventListener("mousemove", this.onMouseMove.bind(this));
        }

        onMouseMove(event) {
          this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
          this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        }

        onResize() {
          this.resize();
          this.background.updateSize();
          this.grid.updateSize();
        }

        resize() {
          const { renderer, camera } = this;
          const { innerWidth: w, innerHeight: h } = window;
          renderer.setSize(w, h);
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          this.width = w;
          this.height = h;
        }

        setupScene() {
          const { scene } = this;
          scene.background = new THREE.Color(0xffffff);
          this.camera.position.z = 10;
        }

        setupLights() {
          const { scene } = this;
          const light = new THREE.AmbientLight(0xffffff);
          this.pLight = new THREE.PointLight(0xffffff, 1, 20);
          this.pLight.position.set(0, 0, 9);
          scene.add(this.pLight);
          scene.add(light);
        }

        setupMosaic() {
          const { scene, camera } = this;
          this.background = new ImagePlane(MAIN_IMAGE_URL, camera);
          this.background.scale.set(1.1, 1.1, 1);
          this.grid = new HexGrid(camera);
          this.grid.setTexture(MOSAIC_IMAGE_URL);
        }

        updateGridOver() {
          const { camera, raycaster, mouse, grid } = this;
          if (mouse.x !== 0 && mouse.y !== 0) {
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(
              this.grid.groupObject.children
            );

            if (intersects.length) {
              grid.setActiveCell(intersects[0].object);
            }
          }
        }

        mosaicAnimationIn() {
          const { scene } = this;
          scene.add(this.background.mesh);
          scene.add(this.grid.groupObject);
          this.grid.animateGridTilesIn();

          gsap.to(this.pLight, {
            intensity: 0,
            duration: 1.5
          });

          gsap.from(this.background.scale, {
            x: 1.4,
            y: 1.4,
            duration: 1.8,
            ease: "power4.out",
            onUpdate: () => {
              this.background.updateSize();
            }
          });
        }

        updateMosaicTilt() {
          const { camera, mouse } = this;
          gsap.to(this.camera.position, {
            x: mouse.x * 0.5,
            y: mouse.y * 0.5,
            duration: 1.5
          });
        }

        onFrame(time) {
          const { renderer, scene, camera, clock } = this;
          requestAnimationFrame(this.onFrame.bind(this));
          this.updateGridOver();
          this.updateMosaicTilt();
          camera.lookAt(scene.position);
          renderer.render(scene, camera);
        }
      }

      new App();
    };

    return () => {
      document.body.removeChild(script);
      document.body.removeChild(gsapScript);
    };
  }, []);

  return (
    <>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100vh' }} />
      <style jsx>{`
        body {
          margin: 0;
          padding: 0;
          overflow: hidden;
        }
      `}</style>
    </>
  );
};

export default HomeThreeScene;