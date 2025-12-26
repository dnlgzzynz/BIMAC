/**
 * Node Editor - Visual canvas for creating and connecting nodes
 */

import { NodeGraph, PortType } from './NodeGraph.js';
import { NodeRegistry, NodeCategories } from './NodeTypes.js';

export class NodeEditor {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.canvas = null;
    this.ctx = null;
    this.graph = new NodeGraph();

    // View state
    this.offsetX = 0;
    this.offsetY = 0;
    this.scale = 1;

    // Interaction state
    this.isDragging = false;
    this.isPanning = false;
    this.isConnecting = false;
    this.draggedNode = null;
    this.dragOffsetX = 0;
    this.dragOffsetY = 0;
    this.selectedNodes = new Set();
    this.connectionStart = null;
    this.mouseX = 0;
    this.mouseY = 0;

    // Callbacks
    this.onEvaluate = null;

    this.init();
  }

  init() {
    if (!this.container) {
      console.error('Node editor container not found');
      return;
    }

    // Create canvas
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'node-canvas';
    this.container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    // Create toolbar
    this.createToolbar();

    // Create context menu
    this.createContextMenu();

    // Create node panel
    this.createNodePanel();

    // Setup events
    this.setupEvents();

    // Initial resize
    this.resize();

    // Start render loop
    this.render();
  }

  createToolbar() {
    const toolbar = document.createElement('div');
    toolbar.className = 'node-toolbar';
    toolbar.innerHTML = `
      <button id="node-btn-add" class="node-btn" title="Agregar nodo">
        <span>➕</span> Agregar
      </button>
      <button id="node-btn-evaluate" class="node-btn node-btn-primary" title="Evaluar grafo">
        <span>▶️</span> Ejecutar
      </button>
      <button id="node-btn-clear" class="node-btn" title="Limpiar todo">
        <span>🗑️</span> Limpiar
      </button>
      <button id="node-btn-fit" class="node-btn" title="Ajustar vista">
        <span>🎯</span> Centrar
      </button>
      <div class="node-toolbar-spacer"></div>
      <span class="node-status" id="node-status">Listo</span>
    `;
    this.container.appendChild(toolbar);
  }

  createContextMenu() {
    this.contextMenu = document.createElement('div');
    this.contextMenu.className = 'node-context-menu hidden';
    this.contextMenu.innerHTML = this.buildContextMenuHTML();
    this.container.appendChild(this.contextMenu);
  }

  buildContextMenuHTML() {
    let html = '<div class="context-menu-search"><input type="text" placeholder="Buscar nodo..." id="node-search"></div>';

    for (const [category, nodes] of Object.entries(NodeCategories)) {
      html += `<div class="context-menu-category">${category}</div>`;
      for (const nodeType of nodes) {
        const NodeClass = NodeRegistry[nodeType];
        const tempNode = new NodeClass('temp');
        html += `<div class="context-menu-item" data-type="${nodeType}">${tempNode.title}</div>`;
      }
    }

    return html;
  }

  createNodePanel() {
    this.nodePanel = document.createElement('div');
    this.nodePanel.className = 'node-properties-panel hidden';
    this.nodePanel.innerHTML = `
      <div class="node-panel-header">
        <span id="panel-title">Propiedades</span>
        <button id="node-panel-close" class="node-btn-close">&times;</button>
      </div>
      <div id="node-panel-content" class="node-panel-content"></div>
    `;
    this.container.appendChild(this.nodePanel);
  }

  setupEvents() {
    // Canvas events
    this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
    this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
    this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
    this.canvas.addEventListener('wheel', (e) => this.onWheel(e));
    this.canvas.addEventListener('contextmenu', (e) => this.onContextMenu(e));
    this.canvas.addEventListener('dblclick', (e) => this.onDoubleClick(e));

    // Toolbar events
    document.getElementById('node-btn-add').addEventListener('click', (e) => {
      this.showContextMenu(e.clientX, e.clientY);
    });
    document.getElementById('node-btn-evaluate').addEventListener('click', () => this.evaluate());
    document.getElementById('node-btn-clear').addEventListener('click', () => this.clear());
    document.getElementById('node-btn-fit').addEventListener('click', () => this.fitView());

    // Context menu events
    this.contextMenu.addEventListener('click', (e) => {
      const item = e.target.closest('.context-menu-item');
      if (item) {
        const nodeType = item.dataset.type;
        this.addNode(nodeType, this.menuX, this.menuY);
        this.hideContextMenu();
      }
    });

    // Search in context menu
    const searchInput = document.getElementById('node-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterContextMenu(e.target.value);
      });
    }

    // Close context menu on click outside
    document.addEventListener('click', (e) => {
      if (!this.contextMenu.contains(e.target) && !e.target.matches('#node-btn-add')) {
        this.hideContextMenu();
      }
    });

    // Panel close
    document.getElementById('node-panel-close')?.addEventListener('click', () => {
      this.nodePanel.classList.add('hidden');
    });

    // Window resize
    window.addEventListener('resize', () => this.resize());

    // Keyboard
    document.addEventListener('keydown', (e) => this.onKeyDown(e));
  }

  resize() {
    const rect = this.container.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height - 48; // Account for toolbar
  }

  // ============================================
  // MOUSE EVENTS
  // ============================================

  onMouseDown(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - this.offsetX) / this.scale;
    const y = (e.clientY - rect.top - this.offsetY) / this.scale;

    this.mouseX = e.clientX - rect.left;
    this.mouseY = e.clientY - rect.top;

    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      // Middle click or Alt+click: pan
      this.isPanning = true;
      this.canvas.style.cursor = 'grabbing';
      return;
    }

    // Check if clicking on a port
    const portHit = this.hitTestPort(x, y);
    if (portHit) {
      this.isConnecting = true;
      this.connectionStart = portHit;
      return;
    }

    // Check if clicking on a node
    const node = this.hitTestNode(x, y);
    if (node) {
      if (!e.shiftKey) {
        this.selectedNodes.clear();
      }
      this.selectedNodes.add(node.id);
      node.isSelected = true;

      this.isDragging = true;
      this.draggedNode = node;
      this.dragOffsetX = x - node.x;
      this.dragOffsetY = y - node.y;

      // Show properties panel
      this.showNodeProperties(node);
    } else {
      // Clicked on empty space
      this.selectedNodes.clear();
      for (const n of this.graph.nodes.values()) {
        n.isSelected = false;
      }
      this.nodePanel.classList.add('hidden');
    }
  }

  onMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;
    const x = (screenX - this.offsetX) / this.scale;
    const y = (screenY - this.offsetY) / this.scale;

    this.mouseX = screenX;
    this.mouseY = screenY;

    if (this.isPanning) {
      this.offsetX += e.movementX;
      this.offsetY += e.movementY;
    } else if (this.isDragging && this.draggedNode) {
      this.draggedNode.x = x - this.dragOffsetX;
      this.draggedNode.y = y - this.dragOffsetY;
    }
  }

  onMouseUp(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - this.offsetX) / this.scale;
    const y = (e.clientY - rect.top - this.offsetY) / this.scale;

    if (this.isConnecting && this.connectionStart) {
      const portHit = this.hitTestPort(x, y);
      if (portHit && this.canConnect(this.connectionStart, portHit)) {
        // Create connection
        if (this.connectionStart.direction === 'output') {
          this.graph.connect(
            this.connectionStart.node.id,
            this.connectionStart.port.name,
            portHit.node.id,
            portHit.port.name
          );
        } else {
          this.graph.connect(
            portHit.node.id,
            portHit.port.name,
            this.connectionStart.node.id,
            this.connectionStart.port.name
          );
        }
      }
    }

    this.isPanning = false;
    this.isDragging = false;
    this.isConnecting = false;
    this.draggedNode = null;
    this.connectionStart = null;
    this.canvas.style.cursor = 'default';
  }

  onWheel(e) {
    e.preventDefault();
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const zoom = e.deltaY < 0 ? 1.1 : 0.9;
    const newScale = Math.max(0.25, Math.min(2, this.scale * zoom));

    // Zoom towards mouse position
    this.offsetX = mouseX - (mouseX - this.offsetX) * (newScale / this.scale);
    this.offsetY = mouseY - (mouseY - this.offsetY) * (newScale / this.scale);
    this.scale = newScale;
  }

  onContextMenu(e) {
    e.preventDefault();
    this.showContextMenu(e.clientX, e.clientY);
  }

  onDoubleClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - this.offsetX) / this.scale;
    const y = (e.clientY - rect.top - this.offsetY) / this.scale;

    const node = this.hitTestNode(x, y);
    if (node) {
      this.showNodeProperties(node);
    }
  }

  onKeyDown(e) {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      for (const nodeId of this.selectedNodes) {
        this.graph.removeNode(nodeId);
      }
      this.selectedNodes.clear();
    }
  }

  // ============================================
  // HIT TESTING
  // ============================================

  hitTestNode(x, y) {
    for (const node of this.graph.nodes.values()) {
      if (x >= node.x && x <= node.x + node.width &&
          y >= node.y && y <= node.y + node.height) {
        return node;
      }
    }
    return null;
  }

  hitTestPort(x, y) {
    const portRadius = 8;

    for (const node of this.graph.nodes.values()) {
      // Check input ports
      for (let i = 0; i < node.inputs.length; i++) {
        const portY = node.y + 35 + i * 24;
        const portX = node.x;
        if (Math.hypot(x - portX, y - portY) < portRadius) {
          return { node, port: node.inputs[i], direction: 'input', index: i };
        }
      }

      // Check output ports
      for (let i = 0; i < node.outputs.length; i++) {
        const portY = node.y + 35 + i * 24;
        const portX = node.x + node.width;
        if (Math.hypot(x - portX, y - portY) < portRadius) {
          return { node, port: node.outputs[i], direction: 'output', index: i };
        }
      }
    }

    return null;
  }

  canConnect(start, end) {
    // Can't connect to same node
    if (start.node === end.node) return false;

    // Must be different directions
    if (start.direction === end.direction) return false;

    // Check type compatibility
    const output = start.direction === 'output' ? start.port : end.port;
    const input = start.direction === 'input' ? start.port : end.port;

    return output.type === input.type ||
           output.type === PortType.ANY ||
           input.type === PortType.ANY;
  }

  // ============================================
  // CONTEXT MENU
  // ============================================

  showContextMenu(clientX, clientY) {
    const rect = this.container.getBoundingClientRect();
    this.menuX = (clientX - rect.left - this.offsetX) / this.scale;
    this.menuY = (clientY - rect.top - 48 - this.offsetY) / this.scale;

    this.contextMenu.style.left = `${clientX - rect.left}px`;
    this.contextMenu.style.top = `${clientY - rect.top}px`;
    this.contextMenu.classList.remove('hidden');

    const searchInput = document.getElementById('node-search');
    if (searchInput) {
      searchInput.value = '';
      searchInput.focus();
      this.filterContextMenu('');
    }
  }

  hideContextMenu() {
    this.contextMenu.classList.add('hidden');
  }

  filterContextMenu(search) {
    const items = this.contextMenu.querySelectorAll('.context-menu-item');
    const categories = this.contextMenu.querySelectorAll('.context-menu-category');
    const term = search.toLowerCase();

    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(term) ? 'block' : 'none';
    });

    categories.forEach(cat => {
      cat.style.display = term ? 'none' : 'block';
    });
  }

  // ============================================
  // NODE OPERATIONS
  // ============================================

  addNode(nodeType, x = 100, y = 100) {
    const NodeClass = NodeRegistry[nodeType];
    if (!NodeClass) {
      console.error('Unknown node type:', nodeType);
      return null;
    }

    const node = this.graph.createNode(NodeClass, x, y);
    this.updateStatus(`Nodo "${node.title}" agregado`);
    return node;
  }

  showNodeProperties(node) {
    const panel = this.nodePanel;
    const title = document.getElementById('panel-title');
    const content = document.getElementById('node-panel-content');

    title.textContent = node.title;
    content.innerHTML = this.buildNodePropertiesHTML(node);

    // Setup event listeners for inputs
    this.setupPropertyEvents(node, content);

    panel.classList.remove('hidden');
  }

  buildNodePropertiesHTML(node) {
    let html = '';

    // Node values (editable parameters)
    for (const [key, value] of Object.entries(node.values)) {
      html += this.buildPropertyInput(node, key, value);
    }

    // Input ports with no connections (editable)
    for (const input of node.inputs) {
      if (!input.connection && input.value !== null) {
        html += `
          <div class="property-row">
            <label>${input.name}</label>
            <input type="number" class="property-input" data-input="${input.name}"
                   value="${input.value}" step="0.1">
          </div>
        `;
      }
    }

    return html || '<p class="property-empty">Sin propiedades editables</p>';
  }

  buildPropertyInput(node, key, value) {
    if (typeof value === 'number') {
      return `
        <div class="property-row">
          <label>${key}</label>
          <input type="number" class="property-input" data-value="${key}"
                 value="${value}" step="0.1">
        </div>
      `;
    } else if (typeof value === 'string') {
      // Check if it's a select option
      const options = this.getOptionsForProperty(node, key);
      if (options) {
        let optionsHtml = options.map(opt =>
          `<option value="${opt}" ${opt === value ? 'selected' : ''}>${opt}</option>`
        ).join('');
        return `
          <div class="property-row">
            <label>${key}</label>
            <select class="property-select" data-value="${key}">${optionsHtml}</select>
          </div>
        `;
      }
      return `
        <div class="property-row">
          <label>${key}</label>
          <input type="text" class="property-input" data-value="${key}" value="${value}">
        </div>
      `;
    } else if (typeof value === 'boolean') {
      return `
        <div class="property-row">
          <label>${key}</label>
          <input type="checkbox" class="property-checkbox" data-value="${key}"
                 ${value ? 'checked' : ''}>
        </div>
      `;
    }
    return '';
  }

  getOptionsForProperty(node, key) {
    const optionMaps = {
      'operation': ['add', 'subtract', 'multiply', 'divide', 'power', 'modulo', 'min', 'max'],
      'function': ['sin', 'cos', 'tan', 'asin', 'acos', 'atan'],
      'axis': ['X', 'Y', 'Z'],
      'material': ['standard', 'phong', 'basic', 'wireframe']
    };
    return optionMaps[key] || null;
  }

  setupPropertyEvents(node, content) {
    // Number and text inputs
    content.querySelectorAll('.property-input').forEach(input => {
      input.addEventListener('change', (e) => {
        const valueKey = e.target.dataset.value;
        const inputKey = e.target.dataset.input;

        if (valueKey) {
          node.values[valueKey] = e.target.type === 'number'
            ? parseFloat(e.target.value)
            : e.target.value;
        } else if (inputKey) {
          node.setInputValue(inputKey, parseFloat(e.target.value));
        }

        node.markDirty();
      });
    });

    // Select inputs
    content.querySelectorAll('.property-select').forEach(select => {
      select.addEventListener('change', (e) => {
        const valueKey = e.target.dataset.value;
        if (valueKey) {
          node.values[valueKey] = e.target.value;
          node.markDirty();
        }
      });
    });

    // Checkbox inputs
    content.querySelectorAll('.property-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const valueKey = e.target.dataset.value;
        if (valueKey) {
          node.values[valueKey] = e.target.checked;
          node.markDirty();
        }
      });
    });
  }

  // ============================================
  // GRAPH OPERATIONS
  // ============================================

  evaluate() {
    this.updateStatus('Evaluando...');

    try {
      const results = this.graph.evaluate();

      if (this.onEvaluate) {
        this.onEvaluate(results);
      }

      this.updateStatus('Evaluación completada');
    } catch (error) {
      console.error('Evaluation error:', error);
      this.updateStatus('Error en evaluación', true);
    }
  }

  clear() {
    if (confirm('¿Limpiar todo el grafo de nodos?')) {
      this.graph.clear();
      this.selectedNodes.clear();
      this.nodePanel.classList.add('hidden');
      this.updateStatus('Grafo limpiado');
    }
  }

  fitView() {
    if (this.graph.nodes.size === 0) {
      this.offsetX = this.canvas.width / 2;
      this.offsetY = this.canvas.height / 2;
      this.scale = 1;
      return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    for (const node of this.graph.nodes.values()) {
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + node.width);
      maxY = Math.max(maxY, node.y + node.height);
    }

    const padding = 50;
    const graphWidth = maxX - minX + padding * 2;
    const graphHeight = maxY - minY + padding * 2;

    this.scale = Math.min(
      this.canvas.width / graphWidth,
      this.canvas.height / graphHeight,
      1
    );

    this.offsetX = (this.canvas.width - graphWidth * this.scale) / 2 - minX * this.scale + padding * this.scale;
    this.offsetY = (this.canvas.height - graphHeight * this.scale) / 2 - minY * this.scale + padding * this.scale;
  }

  updateStatus(message, isError = false) {
    const status = document.getElementById('node-status');
    if (status) {
      status.textContent = message;
      status.style.color = isError ? '#ef4444' : '#94a3b8';
    }
  }

  // ============================================
  // RENDERING
  // ============================================

  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Background grid
    this.drawGrid();

    this.ctx.save();
    this.ctx.translate(this.offsetX, this.offsetY);
    this.ctx.scale(this.scale, this.scale);

    // Draw connections
    this.drawConnections();

    // Draw connection being made
    if (this.isConnecting && this.connectionStart) {
      this.drawPendingConnection();
    }

    // Draw nodes
    for (const node of this.graph.nodes.values()) {
      this.drawNode(node);
    }

    this.ctx.restore();

    requestAnimationFrame(() => this.render());
  }

  drawGrid() {
    const ctx = this.ctx;
    const gridSize = 20 * this.scale;
    const offsetX = this.offsetX % gridSize;
    const offsetY = this.offsetY % gridSize;

    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    ctx.beginPath();

    for (let x = offsetX; x < this.canvas.width; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.canvas.height);
    }

    for (let y = offsetY; y < this.canvas.height; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(this.canvas.width, y);
    }

    ctx.stroke();
  }

  drawNode(node) {
    const ctx = this.ctx;
    const x = node.x;
    const y = node.y;
    const w = node.width;
    const h = node.height;

    // Shadow
    ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetY = 4;

    // Node body
    ctx.fillStyle = '#1e293b';
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 8);
    ctx.fill();

    ctx.shadowColor = 'transparent';

    // Header
    ctx.fillStyle = node.color;
    ctx.beginPath();
    ctx.roundRect(x, y, w, 28, [8, 8, 0, 0]);
    ctx.fill();

    // Selection border
    if (node.isSelected) {
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 8);
      ctx.stroke();
    }

    // Title
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText(node.title, x + w / 2, y + 18);

    // Draw ports
    this.drawPorts(node);
  }

  drawPorts(node) {
    const ctx = this.ctx;
    const portRadius = 6;

    // Input ports
    for (let i = 0; i < node.inputs.length; i++) {
      const port = node.inputs[i];
      const portY = node.y + 35 + i * 24;
      const portX = node.x;

      // Port circle
      ctx.fillStyle = port.connection ? '#22c55e' : this.getPortColor(port.type);
      ctx.beginPath();
      ctx.arc(portX, portY, portRadius, 0, Math.PI * 2);
      ctx.fill();

      // Port border
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Port label
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px system-ui';
      ctx.textAlign = 'left';
      ctx.fillText(port.name, portX + 12, portY + 4);
    }

    // Output ports
    for (let i = 0; i < node.outputs.length; i++) {
      const port = node.outputs[i];
      const portY = node.y + 35 + i * 24;
      const portX = node.x + node.width;

      // Port circle
      ctx.fillStyle = port.connections.length > 0 ? '#22c55e' : this.getPortColor(port.type);
      ctx.beginPath();
      ctx.arc(portX, portY, portRadius, 0, Math.PI * 2);
      ctx.fill();

      // Port border
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Port label
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px system-ui';
      ctx.textAlign = 'right';
      ctx.fillText(port.name, portX - 12, portY + 4);
    }
  }

  getPortColor(type) {
    const colors = {
      [PortType.NUMBER]: '#22c55e',
      [PortType.VECTOR]: '#8b5cf6',
      [PortType.GEOMETRY]: '#3b82f6',
      [PortType.BOOLEAN]: '#ef4444',
      [PortType.STRING]: '#f59e0b',
      [PortType.ANY]: '#94a3b8'
    };
    return colors[type] || '#94a3b8';
  }

  drawConnections() {
    const ctx = this.ctx;

    for (const conn of this.graph.connections) {
      const sourceNode = conn.sourceNode;
      const targetNode = conn.targetNode;

      const outputIndex = sourceNode.outputs.findIndex(o => o.name === conn.sourceOutput);
      const inputIndex = targetNode.inputs.findIndex(i => i.name === conn.targetInput);

      const x1 = sourceNode.x + sourceNode.width;
      const y1 = sourceNode.y + 35 + outputIndex * 24;
      const x2 = targetNode.x;
      const y2 = targetNode.y + 35 + inputIndex * 24;

      this.drawBezierConnection(x1, y1, x2, y2, '#22c55e');
    }
  }

  drawPendingConnection() {
    const startNode = this.connectionStart.node;
    const isOutput = this.connectionStart.direction === 'output';
    const index = this.connectionStart.index;

    const x1 = isOutput ? startNode.x + startNode.width : startNode.x;
    const y1 = startNode.y + 35 + index * 24;
    const x2 = (this.mouseX - this.offsetX) / this.scale;
    const y2 = (this.mouseY - this.offsetY) / this.scale;

    if (isOutput) {
      this.drawBezierConnection(x1, y1, x2, y2, '#60a5fa');
    } else {
      this.drawBezierConnection(x2, y2, x1, y1, '#60a5fa');
    }
  }

  drawBezierConnection(x1, y1, x2, y2, color) {
    const ctx = this.ctx;
    const dx = Math.abs(x2 - x1) * 0.5;

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.bezierCurveTo(x1 + dx, y1, x2 - dx, y2, x2, y2);
    ctx.stroke();
  }
}

export default NodeEditor;
