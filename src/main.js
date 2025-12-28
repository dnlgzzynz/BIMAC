import * as THREE from "three";
import * as OBC from "@thatopen/components";
import * as OBCF from "@thatopen/components-front";
import { MLPostProcessor } from "./ml/MLPostProcessor.js";
import { IFCTreeNavigator } from "./components/IFCTreeNavigator.js";
import { NodeEditor } from "./nodes/NodeEditor.js";

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

    // ML Post-processing
    this.mlProcessor = null;
    this.mlEnabled = false;
    this.mlOutputCanvas = null;
    this.isProcessing = false;

    // Tree Navigator
    this.treeNavigator = null;
    this.isTreeVisible = false;

    // Node Editor
    this.nodeEditor = null;
    this.nodePreviewScene = null;
    this.nodePreviewRenderer = null;
    this.nodePreviewCamera = null;
    this.isNodeEditorVisible = false;
    this.generatedMeshes = [];

    this.init();
    this.updateToolbarState(false);
  }

  async init() {
    try {
      await this.setupScene();
      this.setupEventListeners();
      await this.setupMLProcessor();
      this.setupTreeNavigator();
      this.setupNodeEditor();
      this.updateStatus("Listo - Carga un modelo IFC para comenzar");
    } catch (error) {
      console.error("Error initializing viewer:", error);
      this.updateStatus("Error al inicializar el visor", true);
    }
  }

  setupNodeEditor() {
    // Toggle button
    const btnNodes = document.getElementById("btn-nodes");
    const nodeWrapper = document.getElementById("node-editor-wrapper");
    const btnCloseNodes = document.getElementById("btn-close-nodes");

    if (btnNodes) {
      btnNodes.addEventListener("click", () => {
        this.toggleNodeEditor();
      });
    }

    if (btnCloseNodes) {
      btnCloseNodes.addEventListener("click", () => {
        this.hideNodeEditor();
      });
    }
  }

  initNodeEditor() {
    if (this.nodeEditor) return;

    // Create node editor
    this.nodeEditor = new NodeEditor("node-editor");

    // Setup preview renderer
    this.setupNodePreview();

    // Handle evaluation results
    this.nodeEditor.onEvaluate = (results) => {
      this.onNodeGraphEvaluated(results);
    };

    // Add some default nodes
    this.addDefaultNodes();
  }

  setupNodePreview() {
    const previewContainer = document.getElementById("node-preview");
    if (!previewContainer) return;

    // Create scene
    this.nodePreviewScene = new THREE.Scene();
    this.nodePreviewScene.background = new THREE.Color(0x0f172a);

    // Create camera
    this.nodePreviewCamera = new THREE.PerspectiveCamera(
      45,
      previewContainer.clientWidth / previewContainer.clientHeight,
      0.1,
      1000
    );
    this.nodePreviewCamera.position.set(15, 15, 15);
    this.nodePreviewCamera.lookAt(0, 0, 0);

    // Create renderer
    this.nodePreviewRenderer = new THREE.WebGLRenderer({ antialias: true });
    this.nodePreviewRenderer.setSize(
      previewContainer.clientWidth,
      previewContainer.clientHeight
    );
    this.nodePreviewRenderer.setPixelRatio(window.devicePixelRatio);
    previewContainer.appendChild(this.nodePreviewRenderer.domElement);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.nodePreviewScene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    this.nodePreviewScene.add(directionalLight);

    // Add grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x334155, 0x1e293b);
    this.nodePreviewScene.add(gridHelper);

    // Add axes
    const axesHelper = new THREE.AxesHelper(5);
    this.nodePreviewScene.add(axesHelper);

    // OrbitControls for preview
    import("three/examples/jsm/controls/OrbitControls.js").then(
      ({ OrbitControls }) => {
        const controls = new OrbitControls(
          this.nodePreviewCamera,
          this.nodePreviewRenderer.domElement
        );
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Animation loop
        const animate = () => {
          if (!this.isNodeEditorVisible) return;
          requestAnimationFrame(animate);
          controls.update();
          this.nodePreviewRenderer.render(
            this.nodePreviewScene,
            this.nodePreviewCamera
          );
        };
        animate();
      }
    );

    // Handle resize
    window.addEventListener("resize", () => {
      if (!this.isNodeEditorVisible) return;
      const width = previewContainer.clientWidth;
      const height = previewContainer.clientHeight;
      this.nodePreviewCamera.aspect = width / height;
      this.nodePreviewCamera.updateProjectionMatrix();
      this.nodePreviewRenderer.setSize(width, height);
    });
  }

  addDefaultNodes() {
    if (!this.nodeEditor) return;

    // Add a slider node
    const slider = this.nodeEditor.addNode("slider", 50, 100);
    slider.values.min = 0.5;
    slider.values.max = 5;
    slider.values.value = 2;

    // Add a box node
    const box = this.nodeEditor.addNode("box", 300, 100);

    // Add output node
    const output = this.nodeEditor.addNode("geometry-output", 550, 100);

    // Connect slider to box width
    this.nodeEditor.graph.connect(slider.id, "value", box.id, "width");

    // Connect box to output
    this.nodeEditor.graph.connect(box.id, "geometry", output.id, "geometry");
  }

  onNodeGraphEvaluated(results) {
    // Clear previous generated meshes
    for (const mesh of this.generatedMeshes) {
      this.nodePreviewScene.remove(mesh);
      if (mesh.geometry) mesh.geometry.dispose();
      if (mesh.material) mesh.material.dispose();
    }
    this.generatedMeshes = [];

    // Add new meshes to preview scene
    for (const result of results) {
      if (result.data?.meshes) {
        for (const mesh of result.data.meshes) {
          if (mesh) {
            this.nodePreviewScene.add(mesh);
            this.generatedMeshes.push(mesh);
          }
        }
      }
    }
  }

  toggleNodeEditor() {
    this.isNodeEditorVisible = !this.isNodeEditorVisible;
    const wrapper = document.getElementById("node-editor-wrapper");
    const btn = document.getElementById("btn-nodes");

    if (wrapper) {
      wrapper.classList.toggle("hidden", !this.isNodeEditorVisible);
    }

    if (btn) {
      btn.classList.toggle("active", this.isNodeEditorVisible);
    }

    if (this.isNodeEditorVisible) {
      this.initNodeEditor();
      setTimeout(() => {
        this.nodeEditor?.resize();
        this.nodeEditor?.fitView();
      }, 100);
    }
  }

  hideNodeEditor() {
    this.isNodeEditorVisible = false;
    const wrapper = document.getElementById("node-editor-wrapper");
    const btn = document.getElementById("btn-nodes");

    if (wrapper) wrapper.classList.add("hidden");
    if (btn) btn.classList.remove("active");
  }

  setupTreeNavigator() {
    this.treeNavigator = new IFCTreeNavigator(
      this.components,
      this.fragmentsManager
    );
    this.treeNavigator.init("tree-content");

    // Handle element selection from tree
    this.treeNavigator.onSelect((element) => {
      this.onTreeElementSelected(element);
    });

    // Tree toggle button
    const btnTree = document.getElementById("btn-tree");
    const treePanel = document.getElementById("tree-panel");
    const btnCloseTree = document.getElementById("btn-close-tree");

    if (btnTree && treePanel) {
      btnTree.addEventListener("click", () => {
        this.toggleTreePanel();
      });
    }

    if (btnCloseTree && treePanel) {
      btnCloseTree.addEventListener("click", () => {
        this.hideTreePanel();
      });
    }
  }

  toggleTreePanel() {
    const treePanel = document.getElementById("tree-panel");
    const btnTree = document.getElementById("btn-tree");

    this.isTreeVisible = !this.isTreeVisible;

    if (treePanel) {
      treePanel.classList.toggle("hidden", !this.isTreeVisible);
    }

    if (btnTree) {
      btnTree.classList.toggle("active", this.isTreeVisible);
    }
  }

  hideTreePanel() {
    const treePanel = document.getElementById("tree-panel");
    const btnTree = document.getElementById("btn-tree");

    this.isTreeVisible = false;

    if (treePanel) {
      treePanel.classList.add("hidden");
    }

    if (btnTree) {
      btnTree.classList.remove("active");
    }
  }

  async onTreeElementSelected(element) {
    if (!element || !element.expressId) return;

    try {
      // Highlight element in 3D view
      if (this.highlighter && element.fragmentId) {
        const fragmentIdMap = new Map();
        fragmentIdMap.set(element.fragmentId, new Set([element.expressId]));

        await this.highlighter.highlightByID(
          "select",
          fragmentIdMap,
          true,
          true
        );
      }

      // Show properties
      this.showElementProperties(element);

      this.updateStatus(`Seleccionado: ${element.name}`);
    } catch (error) {
      console.error("Error selecting element from tree:", error);
    }
  }

  showElementProperties(element) {
    const panel = document.getElementById("properties-panel");
    const content = document.getElementById("properties-content");

    if (!panel || !content) return;

    let html = '<div class="property-group">';
    html += `<div class="property-group-header">${element.type.replace(
      "IFC",
      ""
    )}</div>`;
    html += '<table class="properties-table">';
    html += `<tr><th>Nombre</th><td>${element.name}</td></tr>`;
    html += `<tr><th>Tipo</th><td>${element.type}</td></tr>`;
    html += `<tr><th>Express ID</th><td>${element.expressId}</td></tr>`;

    if (element.fragmentId) {
      html += `<tr><th>Fragment ID</th><td>${element.fragmentId.substring(
        0,
        8
      )}...</td></tr>`;
    }

    html += "</table></div>";

    content.innerHTML = html;
    panel.classList.remove("hidden");
  }

  async setupMLProcessor() {
    try {
      // Create ML output canvas
      this.mlOutputCanvas = document.createElement("canvas");
      this.mlOutputCanvas.id = "ml-output-canvas";
      this.mlOutputCanvas.className = "hidden";
      document
        .getElementById("viewer-container")
        .appendChild(this.mlOutputCanvas);

      // Create processing indicator
      const indicator = document.createElement("div");
      indicator.id = "processing-indicator";
      indicator.className = "processing-indicator hidden";
      indicator.innerHTML =
        '<span class="processing-dot"></span>Processing ML...';
      document.getElementById("viewer-container").appendChild(indicator);

      // Initialize ML processor after renderer is ready
      const renderer = this.world.renderer.three;
      this.mlProcessor = new MLPostProcessor(renderer);

      const result = await this.mlProcessor.init();

      // Update ML panel status
      const backendEl = document.getElementById("ml-backend");
      if (backendEl) {
        backendEl.textContent = `Backend: ${
          result.success ? result.backend.toUpperCase() : "Failed"
        }`;
      }

      if (result.success) {
        console.log("ML PostProcessor ready with", result.backend);
        this.setupMLEventListeners();
      }
    } catch (error) {
      console.error("Failed to setup ML processor:", error);
    }
  }

  setupMLEventListeners() {
    // Quick toggle buttons
    const mlButtons = {
      "btn-ml-denoise": "denoise",
      "btn-ml-ssao": "ssao",
      "btn-ml-sharpen": "sharpen",
      "btn-ml-edges": "edgeEnhance",
    };

    for (const [btnId, effect] of Object.entries(mlButtons)) {
      const btn = document.getElementById(btnId);
      if (btn) {
        btn.addEventListener("click", () => this.toggleMLEffect(effect, btn));
      }
    }

    // Settings panel toggle
    const btnSettings = document.getElementById("btn-ml-settings");
    const mlPanel = document.getElementById("ml-panel");
    const btnCloseML = document.getElementById("btn-close-ml");

    if (btnSettings && mlPanel) {
      btnSettings.addEventListener("click", () => {
        mlPanel.classList.toggle("hidden");
        this.updateMLMemoryInfo();
      });
    }

    if (btnCloseML && mlPanel) {
      btnCloseML.addEventListener("click", () => {
        mlPanel.classList.add("hidden");
      });
    }

    // Panel toggles
    this.setupMLPanelControls();

    // Apply and Reset buttons
    const btnApply = document.getElementById("btn-ml-apply");
    const btnReset = document.getElementById("btn-ml-reset");

    if (btnApply) {
      btnApply.addEventListener("click", () => this.applyMLEffects());
    }

    if (btnReset) {
      btnReset.addEventListener("click", () => this.resetMLEffects());
    }

    // Range input updates
    this.setupRangeInputs();
  }

  setupMLPanelControls() {
    const toggles = {
      "ml-denoise-toggle": "denoise",
      "ml-ssao-toggle": "ssao",
      "ml-sharpen-toggle": "sharpen",
      "ml-edges-toggle": "edgeEnhance",
      "ml-color-toggle": "colorGrading",
    };

    for (const [toggleId, effect] of Object.entries(toggles)) {
      const toggle = document.getElementById(toggleId);
      if (toggle) {
        toggle.addEventListener("change", (e) => {
          if (e.target.checked) {
            this.mlProcessor.enableEffect(effect);
          } else {
            this.mlProcessor.disableEffect(effect);
          }
          this.syncToolbarButtons();
        });
      }
    }
  }

  setupRangeInputs() {
    // Denoise strength
    this.setupRangeInput("ml-denoise-strength", (value) => {
      this.mlProcessor.setParams("denoise", { strength: value / 100 });
      return `${value}%`;
    });

    // SSAO
    this.setupRangeInput("ml-ssao-radius", (value) => {
      this.mlProcessor.setParams("ssao", { radius: value });
      return value;
    });

    this.setupRangeInput("ml-ssao-intensity", (value) => {
      this.mlProcessor.setParams("ssao", { intensity: value / 100 });
      return (value / 100).toFixed(1);
    });

    // Sharpen
    this.setupRangeInput("ml-sharpen-amount", (value) => {
      this.mlProcessor.setParams("sharpen", { amount: value / 100 });
      return `${value}%`;
    });

    // Edge enhancement
    this.setupRangeInput("ml-edges-strength", (value) => {
      this.mlProcessor.setParams("edgeEnhance", { strength: value / 100 });
      return `${value}%`;
    });

    // Color grading
    this.setupRangeInput("ml-color-exposure", (value) => {
      this.mlProcessor.setParams("colorGrading", { exposure: value / 100 });
      return (value / 100).toFixed(1);
    });

    this.setupRangeInput("ml-color-contrast", (value) => {
      this.mlProcessor.setParams("colorGrading", { contrast: value / 100 });
      return (value / 100).toFixed(1);
    });

    this.setupRangeInput("ml-color-saturation", (value) => {
      this.mlProcessor.setParams("colorGrading", { saturation: value / 100 });
      return (value / 100).toFixed(1);
    });
  }

  setupRangeInput(inputId, updateFn) {
    const input = document.getElementById(inputId);
    if (input) {
      const valueSpan = input.parentElement.querySelector(".range-value");
      input.addEventListener("input", (e) => {
        const value = parseInt(e.target.value);
        if (valueSpan) {
          valueSpan.textContent = updateFn(value);
        }
      });
    }
  }

  toggleMLEffect(effect, button) {
    if (!this.mlProcessor) return;

    const isEnabled = this.mlProcessor.toggleEffect(effect);
    button.classList.toggle("active", isEnabled);

    // Sync panel checkbox
    const toggleMap = {
      denoise: "ml-denoise-toggle",
      ssao: "ml-ssao-toggle",
      sharpen: "ml-sharpen-toggle",
      edgeEnhance: "ml-edges-toggle",
    };

    const checkboxId = toggleMap[effect];
    if (checkboxId) {
      const checkbox = document.getElementById(checkboxId);
      if (checkbox) checkbox.checked = isEnabled;
    }

    this.updateStatus(
      `ML Effect: ${effect} ${isEnabled ? "enabled" : "disabled"}`
    );
  }

  syncToolbarButtons() {
    const buttonMap = {
      denoise: "btn-ml-denoise",
      ssao: "btn-ml-ssao",
      sharpen: "btn-ml-sharpen",
      edgeEnhance: "btn-ml-edges",
    };

    for (const [effect, btnId] of Object.entries(buttonMap)) {
      const btn = document.getElementById(btnId);
      if (btn && this.mlProcessor) {
        btn.classList.toggle(
          "active",
          this.mlProcessor.activeEffects.has(effect)
        );
      }
    }
  }

  async applyMLEffects() {
    if (!this.mlProcessor || this.isProcessing) return;

    if (this.mlProcessor.activeEffects.size === 0) {
      this.updateStatus("No hay efectos ML activos");
      return;
    }

    this.isProcessing = true;
    const indicator = document.getElementById("processing-indicator");
    if (indicator) indicator.classList.remove("hidden");

    this.updateStatus("Procesando efectos ML...");

    try {
      const outputCanvas = await this.mlProcessor.processFrame();

      if (outputCanvas && this.mlOutputCanvas) {
        // Resize output canvas to match
        this.mlOutputCanvas.width = outputCanvas.width;
        this.mlOutputCanvas.height = outputCanvas.height;

        const ctx = this.mlOutputCanvas.getContext("2d");
        ctx.drawImage(outputCanvas, 0, 0);

        this.mlOutputCanvas.classList.remove("hidden");
        this.mlEnabled = true;

        this.updateStatus("Efectos ML aplicados");
        this.updateMLMemoryInfo();
      }
    } catch (error) {
      console.error("Error applying ML effects:", error);
      this.updateStatus("Error al aplicar efectos ML", true);
    } finally {
      this.isProcessing = false;
      if (indicator) indicator.classList.add("hidden");
    }
  }

  resetMLEffects() {
    if (!this.mlProcessor) return;

    // Clear all effects
    this.mlProcessor.activeEffects.clear();

    // Reset checkboxes
    const checkboxes = [
      "ml-denoise-toggle",
      "ml-ssao-toggle",
      "ml-sharpen-toggle",
      "ml-edges-toggle",
      "ml-color-toggle",
    ];

    checkboxes.forEach((id) => {
      const checkbox = document.getElementById(id);
      if (checkbox) checkbox.checked = false;
    });

    // Reset toolbar buttons
    this.syncToolbarButtons();

    // Hide ML output
    if (this.mlOutputCanvas) {
      this.mlOutputCanvas.classList.add("hidden");
    }

    this.mlEnabled = false;
    this.updateStatus("Efectos ML reiniciados");
  }

  updateMLMemoryInfo() {
    if (!this.mlProcessor) return;

    const memInfo = this.mlProcessor.getMemoryInfo();
    const memoryEl = document.getElementById("ml-memory");

    if (memoryEl && memInfo) {
      const mbUsed = (memInfo.numBytes / (1024 * 1024)).toFixed(1);
      memoryEl.textContent = `Memory: ${mbUsed} MB (${memInfo.numTensors} tensors)`;
    }
  }

  async setupScene() {
    const container = document.getElementById("viewer-container");

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
    // Configure WASM path for web-ifc
    this.ifcLoader.settings.wasm = {
      path: "https://unpkg.com/web-ifc@0.0.68/",
      absolute: true,
    };
    await this.ifcLoader.setup();

    // Setup highlighter for selection
    this.highlighter = this.components.get(OBCF.Highlighter);
    this.highlighter.setup({ world: this.world });

    // Selection highlight color
    this.highlighter.colors.set("select", new THREE.Color(0x2563eb));

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
    const fileInput = document.getElementById("file-input");
    const btnLoad = document.getElementById("btn-load");

    btnLoad.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => this.handleFileSelect(e));

    // Drag and drop
    const dropZone = document.getElementById("drop-zone");
    const viewerContainer = document.getElementById("viewer-container");

    viewerContainer.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });

    viewerContainer.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
    });

    viewerContainer.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.loadIFCFile(files[0]);
      }
    });

    // Toolbar buttons
    document
      .getElementById("btn-fit")
      .addEventListener("click", () => this.fitToView());
    document
      .getElementById("btn-ortho")
      .addEventListener("click", () => this.toggleOrthographic());
    document
      .getElementById("btn-wireframe")
      .addEventListener("click", () => this.toggleWireframe());
    document
      .getElementById("btn-transparent")
      .addEventListener("click", () => this.toggleTransparency());
    document
      .getElementById("btn-measure")
      .addEventListener("click", () => this.toggleMeasure());
    document
      .getElementById("btn-section")
      .addEventListener("click", () => this.toggleSection());

    // Panel close buttons
    document.getElementById("btn-close-panel").addEventListener("click", () => {
      document.getElementById("properties-panel").classList.add("hidden");
    });
    document.getElementById("btn-close-tree").addEventListener("click", () => {
      document.getElementById("tree-panel").classList.add("hidden");
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
    window.addEventListener("resize", () => {
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
    event.target.value = "";
  }

  async loadIFCFile(file) {
    if (!file.name.toLowerCase().endsWith(".ifc")) {
      this.updateStatus("Error: Por favor selecciona un archivo IFC", true);
      return;
    }

    // Show loading
    const loadingOverlay = document.getElementById("loading-overlay");
    const loadingText = document.getElementById("loading-text");
    const dropZone = document.getElementById("drop-zone");

    loadingOverlay.classList.remove("hidden");
    dropZone.classList.add("hidden");
    loadingText.textContent = "Cargando modelo...";
    this.updateStatus("Cargando modelo IFC...");

    try {
      // Clear previous model
      if (this.model) {
        this.fragmentsManager.dispose();
      }

      // Read file as ArrayBuffer
      const buffer = await file.arrayBuffer();
      const data = new Uint8Array(buffer);

      loadingText.textContent = "Procesando geometría...";

      // Load IFC
      this.model = await this.ifcLoader.load(data);
      this.model.name = file.name;

      // Add to scene
      this.world.scene.three.add(this.model);

      // Fit camera to model
      await this.fitToView();

      // Build tree navigator
      loadingText.textContent = "Construyendo árbol de navegación...";
      if (this.treeNavigator) {
        await this.treeNavigator.buildTree(this.model);
      }

      // Update UI
      loadingOverlay.classList.add("hidden");
      this.updateStatus(`Modelo cargado: ${file.name}`);
      this.updateModelInfo();
      this.updateToolbarState(true);

      // Auto-show tree panel
      if (!this.isTreeVisible) {
        this.toggleTreePanel();
      }
    } catch (error) {
      console.error("Error loading IFC:", error);
      loadingOverlay.classList.add("hidden");
      dropZone.classList.remove("hidden");
      this.updateStatus("Error al cargar el modelo IFC", true);

      // Clear tree on error
      if (this.treeNavigator) {
        this.treeNavigator.clear();
      }
      this.updateToolbarState(false);
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
      console.error("Error fitting to view:", error);
    }
  }

  toggleOrthographic() {
    const btn = document.getElementById("btn-ortho");
    this.isOrtho = !this.isOrtho;

    if (this.world.camera?.three) {
      // Toggle between perspective and orthographic
      // Note: Full implementation would require camera switching
      btn.classList.toggle("active", this.isOrtho);
    }
  }

  toggleWireframe() {
    const btn = document.getElementById("btn-wireframe");
    this.isWireframe = !this.isWireframe;
    btn.classList.toggle("active", this.isWireframe);

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
    const btn = document.getElementById("btn-transparent");
    this.isTransparent = !this.isTransparent;
    btn.classList.toggle("active", this.isTransparent);

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
    const btn = document.getElementById("btn-measure");
    btn.classList.toggle("active");
    this.updateStatus("Herramienta de medición: En desarrollo");
  }

  toggleSection() {
    const btn = document.getElementById("btn-section");
    btn.classList.toggle("active");
    this.updateStatus("Plano de corte: En desarrollo");
  }

  async onElementSelected(fragmentIdMap) {
    const panel = document.getElementById("properties-panel");
    const content = document.getElementById("properties-content");

    // Get properties for selected elements
    try {
      let propertiesHtml = "";
      let firstExpressId = null;

      for (const [fragmentId, expressIds] of fragmentIdMap) {
        for (const expressId of expressIds) {
          // Store first expressId for tree sync
          if (!firstExpressId) firstExpressId = expressId;

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
        content.innerHTML =
          '<p class="placeholder">No hay propiedades disponibles</p>';
      }

      panel.classList.remove("hidden");

      // Sync with tree navigator
      if (firstExpressId && this.treeNavigator && this.isTreeVisible) {
        this.treeNavigator.highlightElement(firstExpressId);
      }
    } catch (error) {
      console.error("Error getting properties:", error);
      content.innerHTML =
        '<p class="placeholder">Error al obtener propiedades</p>';
    }
  }
    } catch (error) {
      console.error("Error getting properties:", error);
      content.innerHTML =
        '<p class="placeholder">Error al obtener propiedades</p>';
    }
  }

  renderProperties(properties) {
    let html = '<div class="property-group">';
    html += `<div class="property-group-header">${
      properties.type || "Elemento IFC"
    }</div>`;
    html += '<table class="properties-table">';

    // Basic properties
    const basicProps = ["GlobalId", "Name", "Description", "ObjectType"];
    for (const prop of basicProps) {
      if (properties[prop]?.value) {
        html += `<tr><th>${prop}</th><td>${properties[prop].value}</td></tr>`;
      }
    }

    html += "</table></div>";
    return html;
  }

  onSelectionCleared() {
    document.getElementById("properties-panel").classList.add("hidden");
  }

  updateStatus(message, isError = false) {
    const statusText = document.getElementById("status-text");
    statusText.textContent = message;
    statusText.style.color = isError
      ? "var(--error-color)"
      : "var(--text-secondary)";
  }

  updateModelInfo() {
    const modelInfo = document.getElementById("model-info");
    if (this.model) {
      let meshCount = 0;
      this.model.traverse((child) => {
        if (child.isMesh) meshCount++;
      });
      modelInfo.textContent = `Elementos: ${meshCount}`;
    } else {
      modelInfo.textContent = "";
    }
  }

  updateToolbarState(hasModel) {
    const buttons = [
      'btn-tree',
      'btn-fit',
      'btn-wireframe',
      'btn-transparent',
      'btn-measure',
      'btn-section'
    ];

    buttons.forEach(id => {
      const btn = document.getElementById(id);
      if (btn) {
        if (hasModel) {
          btn.classList.remove('disabled');
          btn.removeAttribute('disabled');
        } else {
          btn.classList.add('disabled');
          btn.setAttribute('disabled', 'true');
        }
      }
    });

    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
      if (hasModel) {
        dropZone.classList.add('hidden');
      } else {
        dropZone.classList.remove('hidden');
      }
    }
  }
}

// Initialize the application
const app = new IFCViewerApp();

export default app;
