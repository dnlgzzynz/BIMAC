import * as THREE from 'three';
import * as OBC from '@thatopen/components';
import * as OBCF from '@thatopen/components-front';

// Initialize the IFC Viewer Application
class IFCViewerApp {
  constructor() {
    this.components = null;
    this.world = null;
    this.fragmentsManager = null;
    this.ifcLoader = null;
    this.highlighter = null;
    this.culler = null;
    this.model = null;
    this.isTransparent = false;
    this.isWireframe = false;
    this.isOrtho = false;

    this.init();
  }

  async init() {
    try {
      await this.setupScene();
      this.setupEventListeners();
      this.updateStatus('Listo - Carga un modelo IFC para comenzar');
    } catch (error) {
      console.error('Error initializing viewer:', error);
      this.updateStatus('Error al inicializar el visor', true);
    }
  }

  async setupScene() {
    const container = document.getElementById('viewer-container');

    // Initialize components
    this.components = new OBC.Components();

    // Create worlds component
    const worlds = this.components.get(OBC.Worlds);

    // Create a simple 3D world
    this.world = worlds.create();

    // Setup scene
    this.world.scene = new OBC.SimpleScene(this.components);
    this.world.scene.setup();
    this.world.scene.three.background = new THREE.Color(0x0f172a);

    // Setup renderer
    this.world.renderer = new OBC.SimpleRenderer(this.components, container);

    // Setup camera
    this.world.camera = new OBC.SimpleCamera(this.components);
    this.world.camera.controls.setLookAt(15, 15, 15, 0, 0, 0);

    // Initialize the components
    this.components.init();

    // Setup grids
    const grids = this.components.get(OBC.Grids);
    const grid = grids.create(this.world);
    grid.material.uniforms.uColor.value = new THREE.Color(0x334155);
    grid.material.uniforms.uSize1.value = 1;
    grid.material.uniforms.uSize2.value = 10;

    // Setup fragments manager for IFC
    this.fragmentsManager = this.components.get(OBC.FragmentsManager);

    // Setup IFC loader
    this.ifcLoader = this.components.get(OBC.IfcLoader);
    await this.ifcLoader.setup();

    // Configure WASM path for web-ifc
    this.ifcLoader.settings.wasm = {
      path: 'https://unpkg.com/web-ifc@0.0.57/',
      absolute: true,
    };

    // Setup highlighter for selection
    this.highlighter = this.components.get(OBCF.Highlighter);
    this.highlighter.setup({ world: this.world });

    // Selection highlight color
    this.highlighter.colors.set('select', new THREE.Color(0x2563eb));

    // Add lights
    this.addLights();

    // Enable raycaster
    const raycasters = this.components.get(OBC.Raycasters);
    raycasters.get(this.world);
  }

  addLights() {
    const scene = this.world.scene.three;

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    // Directional lights
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(50, 50, 50);
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-50, 50, -50);
    scene.add(directionalLight2);

    // Hemisphere light for ambient variation
    const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.3);
    scene.add(hemisphereLight);
  }

  setupEventListeners() {
    // File input
    const fileInput = document.getElementById('file-input');
    const btnLoad = document.getElementById('btn-load');

    btnLoad.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

    // Drag and drop
    const dropZone = document.getElementById('drop-zone');
    const viewerContainer = document.getElementById('viewer-container');

    viewerContainer.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });

    viewerContainer.addEventListener('dragleave', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
    });

    viewerContainer.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.loadIFCFile(files[0]);
      }
    });

    // Toolbar buttons
    document.getElementById('btn-fit').addEventListener('click', () => this.fitToView());
    document.getElementById('btn-ortho').addEventListener('click', () => this.toggleOrthographic());
    document.getElementById('btn-wireframe').addEventListener('click', () => this.toggleWireframe());
    document.getElementById('btn-transparent').addEventListener('click', () => this.toggleTransparency());
    document.getElementById('btn-measure').addEventListener('click', () => this.toggleMeasure());
    document.getElementById('btn-section').addEventListener('click', () => this.toggleSection());

    // Panel close buttons
    document.getElementById('btn-close-panel').addEventListener('click', () => {
      document.getElementById('properties-panel').classList.add('hidden');
    });
    document.getElementById('btn-close-tree').addEventListener('click', () => {
      document.getElementById('tree-panel').classList.add('hidden');
    });

    // Selection handling
    if (this.highlighter) {
      this.highlighter.events.select.onHighlight.add((fragmentIdMap) => {
        this.onElementSelected(fragmentIdMap);
      });

      this.highlighter.events.select.onClear.add(() => {
        this.onSelectionCleared();
      });
    }

    // Window resize
    window.addEventListener('resize', () => {
      if (this.world?.renderer) {
        this.world.renderer.resize();
      }
    });
  }

  async handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
      await this.loadIFCFile(file);
    }
    event.target.value = '';
  }

  async loadIFCFile(file) {
    if (!file.name.toLowerCase().endsWith('.ifc')) {
      this.updateStatus('Error: Por favor selecciona un archivo IFC', true);
      return;
    }

    // Show loading
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const dropZone = document.getElementById('drop-zone');

    loadingOverlay.classList.remove('hidden');
    dropZone.classList.add('hidden');
    loadingText.textContent = 'Cargando modelo...';
    this.updateStatus('Cargando modelo IFC...');

    try {
      // Clear previous model
      if (this.model) {
        this.fragmentsManager.dispose();
      }

      // Read file as ArrayBuffer
      const buffer = await file.arrayBuffer();
      const data = new Uint8Array(buffer);

      loadingText.textContent = 'Procesando geometría...';

      // Load IFC
      this.model = await this.ifcLoader.load(data);
      this.model.name = file.name;

      // Add to scene
      this.world.scene.three.add(this.model);

      // Fit camera to model
      await this.fitToView();

      // Update UI
      loadingOverlay.classList.add('hidden');
      this.updateStatus(`Modelo cargado: ${file.name}`);
      this.updateModelInfo();

    } catch (error) {
      console.error('Error loading IFC:', error);
      loadingOverlay.classList.add('hidden');
      dropZone.classList.remove('hidden');
      this.updateStatus('Error al cargar el modelo IFC', true);
    }
  }

  async fitToView() {
    if (!this.model) return;

    try {
      // Get bounding box of the model
      const bbox = new THREE.Box3().setFromObject(this.model);
      const center = bbox.getCenter(new THREE.Vector3());
      const size = bbox.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      const distance = maxDim * 2;

      await this.world.camera.controls.setLookAt(
        center.x + distance,
        center.y + distance,
        center.z + distance,
        center.x,
        center.y,
        center.z,
        true
      );
    } catch (error) {
      console.error('Error fitting to view:', error);
    }
  }

  toggleOrthographic() {
    const btn = document.getElementById('btn-ortho');
    this.isOrtho = !this.isOrtho;

    if (this.world.camera?.three) {
      // Toggle between perspective and orthographic
      // Note: Full implementation would require camera switching
      btn.classList.toggle('active', this.isOrtho);
    }
  }

  toggleWireframe() {
    const btn = document.getElementById('btn-wireframe');
    this.isWireframe = !this.isWireframe;
    btn.classList.toggle('active', this.isWireframe);

    if (this.model) {
      this.model.traverse((child) => {
        if (child.isMesh && child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach((mat) => {
              mat.wireframe = this.isWireframe;
            });
          } else {
            child.material.wireframe = this.isWireframe;
          }
        }
      });
    }
  }

  toggleTransparency() {
    const btn = document.getElementById('btn-transparent');
    this.isTransparent = !this.isTransparent;
    btn.classList.toggle('active', this.isTransparent);

    if (this.model) {
      this.model.traverse((child) => {
        if (child.isMesh && child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach((mat) => {
              mat.transparent = this.isTransparent;
              mat.opacity = this.isTransparent ? 0.5 : 1.0;
            });
          } else {
            child.material.transparent = this.isTransparent;
            child.material.opacity = this.isTransparent ? 0.5 : 1.0;
          }
        }
      });
    }
  }

  toggleMeasure() {
    const btn = document.getElementById('btn-measure');
    btn.classList.toggle('active');
    this.updateStatus('Herramienta de medición: En desarrollo');
  }

  toggleSection() {
    const btn = document.getElementById('btn-section');
    btn.classList.toggle('active');
    this.updateStatus('Plano de corte: En desarrollo');
  }

  async onElementSelected(fragmentIdMap) {
    const panel = document.getElementById('properties-panel');
    const content = document.getElementById('properties-content');

    // Get properties for selected elements
    try {
      const indexer = this.components.get(OBC.IfcRelationsIndexer);
      let propertiesHtml = '';

      for (const [fragmentId, expressIds] of fragmentIdMap) {
        for (const expressId of expressIds) {
          const fragment = this.fragmentsManager.list.get(fragmentId);
          if (fragment?.group) {
            const properties = fragment.group.getLocalProperties()?.[expressId];
            if (properties) {
              propertiesHtml += this.renderProperties(properties);
            }
          }
        }
      }

      if (propertiesHtml) {
        content.innerHTML = propertiesHtml;
      } else {
        content.innerHTML = '<p class="placeholder">No hay propiedades disponibles</p>';
      }

      panel.classList.remove('hidden');
    } catch (error) {
      console.error('Error getting properties:', error);
      content.innerHTML = '<p class="placeholder">Error al obtener propiedades</p>';
    }
  }

  renderProperties(properties) {
    let html = '<div class="property-group">';
    html += `<div class="property-group-header">${properties.type || 'Elemento IFC'}</div>`;
    html += '<table class="properties-table">';

    // Basic properties
    const basicProps = ['GlobalId', 'Name', 'Description', 'ObjectType'];
    for (const prop of basicProps) {
      if (properties[prop]?.value) {
        html += `<tr><th>${prop}</th><td>${properties[prop].value}</td></tr>`;
      }
    }

    html += '</table></div>';
    return html;
  }

  onSelectionCleared() {
    document.getElementById('properties-panel').classList.add('hidden');
  }

  updateStatus(message, isError = false) {
    const statusText = document.getElementById('status-text');
    statusText.textContent = message;
    statusText.style.color = isError ? 'var(--error-color)' : 'var(--text-secondary)';
  }

  updateModelInfo() {
    const modelInfo = document.getElementById('model-info');
    if (this.model) {
      let meshCount = 0;
      this.model.traverse((child) => {
        if (child.isMesh) meshCount++;
      });
      modelInfo.textContent = `Elementos: ${meshCount}`;
    } else {
      modelInfo.textContent = '';
    }
  }
}

// Initialize the application
const app = new IFCViewerApp();

export default app;
