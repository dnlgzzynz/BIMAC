/**
 * IFC Tree Navigator - Hierarchical model structure browser
 * Displays the spatial structure of IFC models (Site > Building > Storey > Space > Elements)
 */
export class IFCTreeNavigator {
  constructor(components, fragmentsManager) {
    this.components = components;
    this.fragmentsManager = fragmentsManager;
    this.treeContainer = null;
    this.model = null;
    this.treeData = null;
    this.expandedNodes = new Set();
    this.selectedNode = null;
    this.onSelectCallback = null;

    // IFC entity type icons
    this.typeIcons = {
      'IFCPROJECT': '📋',
      'IFCSITE': '🌍',
      'IFCBUILDING': '🏢',
      'IFCBUILDINGSTOREY': '🏗️',
      'IFCSPACE': '📦',
      'IFCWALL': '🧱',
      'IFCWALLSTANDARDCASE': '🧱',
      'IFCSLAB': '⬛',
      'IFCROOF': '🏠',
      'IFCCOLUMN': '🔲',
      'IFCBEAM': '📏',
      'IFCDOOR': '🚪',
      'IFCWINDOW': '🪟',
      'IFCSTAIR': '🪜',
      'IFCSTAIRFLIGHT': '🪜',
      'IFCRAILING': '🚧',
      'IFCFURNISHINGELEMENT': '🪑',
      'IFCCOVERING': '🎨',
      'IFCCURTAINWALL': '🔳',
      'IFCPLATE': '▫️',
      'IFCMEMBER': '➖',
      'IFCFOOTING': '🧊',
      'IFCPILE': '📍',
      'IFCBUILDINGELEMENTPROXY': '🔷',
      'IFCOPENINGELEMENT': '⭕',
      'IFCFLOWSEGMENT': '🔧',
      'IFCFLOWTERMINAL': '💡',
      'IFCDISTRIBUTIONELEMENT': '⚡',
      'DEFAULT': '📄'
    };

    // Category groupings
    this.categories = {
      'Structure': ['IFCWALL', 'IFCWALLSTANDARDCASE', 'IFCSLAB', 'IFCCOLUMN', 'IFCBEAM', 'IFCFOOTING', 'IFCPILE'],
      'Architecture': ['IFCDOOR', 'IFCWINDOW', 'IFCSTAIR', 'IFCSTAIRFLIGHT', 'IFCRAILING', 'IFCROOF', 'IFCCURTAINWALL'],
      'Furniture': ['IFCFURNISHINGELEMENT'],
      'MEP': ['IFCFLOWSEGMENT', 'IFCFLOWTERMINAL', 'IFCDISTRIBUTIONELEMENT'],
      'Other': []
    };
  }

  /**
   * Initialize the tree navigator
   */
  init(containerId) {
    this.treeContainer = document.getElementById(containerId);
    if (!this.treeContainer) {
      console.error('Tree container not found:', containerId);
      return false;
    }
    return true;
  }

  /**
   * Set callback for element selection
   */
  onSelect(callback) {
    this.onSelectCallback = callback;
  }

  /**
   * Build tree from loaded IFC model
   */
  async buildTree(model) {
    if (!model || !this.treeContainer) return;

    this.model = model;
    this.treeContainer.innerHTML = '<div class="tree-loading">Analizando estructura...</div>';

    try {
      // Get all properties from the model
      const properties = await this.extractModelProperties(model);

      // Build hierarchical structure
      this.treeData = this.buildHierarchy(properties);

      // Render the tree
      this.render();

    } catch (error) {
      console.error('Error building tree:', error);
      this.treeContainer.innerHTML = '<div class="tree-error">Error al cargar estructura</div>';
    }
  }

  /**
   * Extract properties from model fragments
   */
  async extractModelProperties(model) {
    const properties = {};
    const typeCount = {};

    // Iterate through all fragments
    for (const [fragmentId, fragment] of this.fragmentsManager.list) {
      if (fragment.group !== model) continue;

      const localProps = fragment.group.getLocalProperties();
      if (!localProps) continue;

      for (const [expressId, props] of Object.entries(localProps)) {
        if (!props || !props.type) continue;

        const type = props.type.toUpperCase();
        typeCount[type] = (typeCount[type] || 0) + 1;

        properties[expressId] = {
          expressId: parseInt(expressId),
          fragmentId,
          type: type,
          name: props.Name?.value || `${type.replace('IFC', '')} ${typeCount[type]}`,
          description: props.Description?.value || '',
          globalId: props.GlobalId?.value || '',
          objectType: props.ObjectType?.value || '',
          parent: null,
          children: []
        };
      }
    }

    return properties;
  }

  /**
   * Build hierarchical tree structure
   */
  buildHierarchy(properties) {
    const root = {
      id: 'root',
      name: this.model?.name || 'Modelo IFC',
      type: 'ROOT',
      icon: '📁',
      children: [],
      expanded: true
    };

    // Group by spatial structure first
    const spatial = {
      projects: [],
      sites: [],
      buildings: [],
      storeys: [],
      spaces: []
    };

    // Group by element type
    const elementsByType = {};

    for (const [id, prop] of Object.entries(properties)) {
      const type = prop.type;

      if (type === 'IFCPROJECT') {
        spatial.projects.push(prop);
      } else if (type === 'IFCSITE') {
        spatial.sites.push(prop);
      } else if (type === 'IFCBUILDING') {
        spatial.buildings.push(prop);
      } else if (type === 'IFCBUILDINGSTOREY') {
        spatial.storeys.push(prop);
      } else if (type === 'IFCSPACE') {
        spatial.spaces.push(prop);
      } else {
        // Group other elements by type
        if (!elementsByType[type]) {
          elementsByType[type] = [];
        }
        elementsByType[type].push(prop);
      }
    }

    // Build spatial hierarchy
    const spatialNode = this.buildSpatialNode(spatial);
    if (spatialNode.children.length > 0) {
      root.children.push(spatialNode);
    }

    // Build category nodes
    const categoriesNode = this.buildCategoriesNode(elementsByType);
    if (categoriesNode.children.length > 0) {
      root.children.push(categoriesNode);
    }

    // Add type-based grouping
    const typesNode = this.buildTypesNode(elementsByType);
    if (typesNode.children.length > 0) {
      root.children.push(typesNode);
    }

    return root;
  }

  /**
   * Build spatial structure node
   */
  buildSpatialNode(spatial) {
    const node = {
      id: 'spatial',
      name: 'Estructura Espacial',
      type: 'CATEGORY',
      icon: '🏛️',
      children: [],
      expanded: true
    };

    // Add projects
    for (const project of spatial.projects) {
      const projectNode = this.createElementNode(project);
      projectNode.expanded = true;

      // Add sites to project
      for (const site of spatial.sites) {
        const siteNode = this.createElementNode(site);
        siteNode.expanded = true;

        // Add buildings to site
        for (const building of spatial.buildings) {
          const buildingNode = this.createElementNode(building);
          buildingNode.expanded = true;

          // Add storeys to building
          for (const storey of spatial.storeys) {
            const storeyNode = this.createElementNode(storey);

            // Add spaces to storey
            for (const space of spatial.spaces) {
              storeyNode.children.push(this.createElementNode(space));
            }

            buildingNode.children.push(storeyNode);
          }

          siteNode.children.push(buildingNode);
        }

        projectNode.children.push(siteNode);
      }

      node.children.push(projectNode);
    }

    // If no project, add buildings directly
    if (spatial.projects.length === 0 && spatial.buildings.length > 0) {
      for (const building of spatial.buildings) {
        const buildingNode = this.createElementNode(building);
        buildingNode.expanded = true;

        for (const storey of spatial.storeys) {
          buildingNode.children.push(this.createElementNode(storey));
        }

        node.children.push(buildingNode);
      }
    }

    return node;
  }

  /**
   * Build categories node
   */
  buildCategoriesNode(elementsByType) {
    const node = {
      id: 'categories',
      name: 'Categorías',
      type: 'CATEGORY',
      icon: '📂',
      children: [],
      expanded: false
    };

    const categoryIcons = {
      'Structure': '🏗️',
      'Architecture': '🏠',
      'Furniture': '🪑',
      'MEP': '⚡',
      'Other': '📦'
    };

    for (const [category, types] of Object.entries(this.categories)) {
      const elements = [];

      for (const type of types) {
        if (elementsByType[type]) {
          elements.push(...elementsByType[type]);
        }
      }

      if (elements.length > 0) {
        const categoryNode = {
          id: `category-${category}`,
          name: `${category} (${elements.length})`,
          type: 'CATEGORY',
          icon: categoryIcons[category] || '📁',
          children: elements.map(e => this.createElementNode(e)),
          expanded: false
        };
        node.children.push(categoryNode);
      }
    }

    return node;
  }

  /**
   * Build types node
   */
  buildTypesNode(elementsByType) {
    const node = {
      id: 'types',
      name: 'Por Tipo',
      type: 'CATEGORY',
      icon: '🏷️',
      children: [],
      expanded: false
    };

    // Sort types by count
    const sortedTypes = Object.entries(elementsByType)
      .sort((a, b) => b[1].length - a[1].length);

    for (const [type, elements] of sortedTypes) {
      const typeName = type.replace('IFC', '').replace(/([A-Z])/g, ' $1').trim();
      const typeNode = {
        id: `type-${type}`,
        name: `${typeName} (${elements.length})`,
        type: type,
        icon: this.getIcon(type),
        children: elements.map(e => this.createElementNode(e)),
        expanded: false
      };
      node.children.push(typeNode);
    }

    return node;
  }

  /**
   * Create element node
   */
  createElementNode(element) {
    return {
      id: `element-${element.expressId}`,
      expressId: element.expressId,
      fragmentId: element.fragmentId,
      name: element.name,
      type: element.type,
      icon: this.getIcon(element.type),
      children: [],
      expanded: false
    };
  }

  /**
   * Get icon for element type
   */
  getIcon(type) {
    return this.typeIcons[type] || this.typeIcons['DEFAULT'];
  }

  /**
   * Render the tree
   */
  render() {
    if (!this.treeData || !this.treeContainer) return;

    this.treeContainer.innerHTML = '';

    const treeWrapper = document.createElement('div');
    treeWrapper.className = 'tree-wrapper';

    // Add search box
    const searchBox = this.createSearchBox();
    treeWrapper.appendChild(searchBox);

    // Add tree content
    const treeContent = document.createElement('div');
    treeContent.className = 'tree-content';
    treeContent.appendChild(this.renderNode(this.treeData, 0));
    treeWrapper.appendChild(treeContent);

    // Add stats
    const stats = this.createStatsBar();
    treeWrapper.appendChild(stats);

    this.treeContainer.appendChild(treeWrapper);
  }

  /**
   * Create search box
   */
  createSearchBox() {
    const searchWrapper = document.createElement('div');
    searchWrapper.className = 'tree-search';

    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Buscar elementos...';
    searchInput.className = 'tree-search-input';

    searchInput.addEventListener('input', (e) => {
      this.filterTree(e.target.value);
    });

    searchWrapper.appendChild(searchInput);
    return searchWrapper;
  }

  /**
   * Create stats bar
   */
  createStatsBar() {
    const stats = document.createElement('div');
    stats.className = 'tree-stats';

    const elementCount = this.countElements(this.treeData);
    stats.textContent = `${elementCount} elementos`;

    return stats;
  }

  /**
   * Count total elements
   */
  countElements(node) {
    let count = node.expressId ? 1 : 0;
    for (const child of node.children || []) {
      count += this.countElements(child);
    }
    return count;
  }

  /**
   * Render a single node
   */
  renderNode(node, depth) {
    const nodeEl = document.createElement('div');
    nodeEl.className = 'tree-node';
    nodeEl.dataset.id = node.id;
    nodeEl.dataset.depth = depth;

    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = node.expanded || this.expandedNodes.has(node.id);

    // Node header
    const header = document.createElement('div');
    header.className = 'tree-node-header';
    header.style.paddingLeft = `${depth * 16 + 8}px`;

    if (this.selectedNode === node.id) {
      header.classList.add('selected');
    }

    // Toggle button
    const toggle = document.createElement('span');
    toggle.className = 'tree-toggle';
    if (hasChildren) {
      toggle.textContent = isExpanded ? '▼' : '▶';
      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleNode(node.id);
      });
    }
    header.appendChild(toggle);

    // Icon
    const icon = document.createElement('span');
    icon.className = 'tree-icon';
    icon.textContent = node.icon;
    header.appendChild(icon);

    // Name
    const name = document.createElement('span');
    name.className = 'tree-name';
    name.textContent = node.name;
    header.appendChild(name);

    // Count badge for category nodes
    if (hasChildren && !node.expressId) {
      const count = document.createElement('span');
      count.className = 'tree-count';
      count.textContent = node.children.length;
      header.appendChild(count);
    }

    // Click handler for selection
    header.addEventListener('click', () => {
      this.selectNode(node);
    });

    // Double-click to expand/collapse
    header.addEventListener('dblclick', () => {
      if (hasChildren) {
        this.toggleNode(node.id);
      }
    });

    nodeEl.appendChild(header);

    // Children container
    if (hasChildren) {
      const childrenContainer = document.createElement('div');
      childrenContainer.className = 'tree-children';
      childrenContainer.style.display = isExpanded ? 'block' : 'none';

      for (const child of node.children) {
        childrenContainer.appendChild(this.renderNode(child, depth + 1));
      }

      nodeEl.appendChild(childrenContainer);
    }

    return nodeEl;
  }

  /**
   * Toggle node expansion
   */
  toggleNode(nodeId) {
    if (this.expandedNodes.has(nodeId)) {
      this.expandedNodes.delete(nodeId);
    } else {
      this.expandedNodes.add(nodeId);
    }

    // Find and update the node in DOM
    const nodeEl = this.treeContainer.querySelector(`[data-id="${nodeId}"]`);
    if (nodeEl) {
      const toggle = nodeEl.querySelector('.tree-toggle');
      const children = nodeEl.querySelector('.tree-children');

      if (children) {
        const isExpanded = this.expandedNodes.has(nodeId);
        children.style.display = isExpanded ? 'block' : 'none';
        toggle.textContent = isExpanded ? '▼' : '▶';
      }
    }
  }

  /**
   * Select a node
   */
  selectNode(node) {
    // Update selection state
    const previousSelected = this.treeContainer.querySelector('.tree-node-header.selected');
    if (previousSelected) {
      previousSelected.classList.remove('selected');
    }

    this.selectedNode = node.id;

    const nodeEl = this.treeContainer.querySelector(`[data-id="${node.id}"]`);
    if (nodeEl) {
      const header = nodeEl.querySelector('.tree-node-header');
      header.classList.add('selected');
    }

    // Trigger callback for element nodes
    if (node.expressId && this.onSelectCallback) {
      this.onSelectCallback({
        expressId: node.expressId,
        fragmentId: node.fragmentId,
        type: node.type,
        name: node.name
      });
    }
  }

  /**
   * Filter tree by search term
   */
  filterTree(searchTerm) {
    const term = searchTerm.toLowerCase().trim();
    const nodes = this.treeContainer.querySelectorAll('.tree-node');

    if (!term) {
      // Show all nodes
      nodes.forEach(node => {
        node.style.display = 'block';
      });
      return;
    }

    // Hide/show nodes based on search
    nodes.forEach(node => {
      const name = node.querySelector('.tree-name')?.textContent.toLowerCase() || '';
      const matches = name.includes(term);

      if (matches) {
        node.style.display = 'block';
        // Expand parent nodes
        this.expandParents(node);
      } else {
        // Check if any children match
        const childMatches = Array.from(node.querySelectorAll('.tree-name'))
          .some(n => n.textContent.toLowerCase().includes(term));

        node.style.display = childMatches ? 'block' : 'none';
      }
    });
  }

  /**
   * Expand parent nodes
   */
  expandParents(node) {
    let parent = node.parentElement;
    while (parent) {
      if (parent.classList.contains('tree-children')) {
        parent.style.display = 'block';
        const parentNode = parent.parentElement;
        if (parentNode) {
          const toggle = parentNode.querySelector('.tree-toggle');
          if (toggle) toggle.textContent = '▼';
          const nodeId = parentNode.dataset.id;
          if (nodeId) this.expandedNodes.add(nodeId);
        }
      }
      parent = parent.parentElement;
    }
  }

  /**
   * Highlight element by expressId
   */
  highlightElement(expressId) {
    const nodeId = `element-${expressId}`;
    const nodeEl = this.treeContainer.querySelector(`[data-id="${nodeId}"]`);

    if (nodeEl) {
      // Expand parents
      this.expandParents(nodeEl);

      // Scroll into view
      nodeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // Select the node
      const node = this.findNode(this.treeData, nodeId);
      if (node) {
        this.selectNode(node);
      }
    }
  }

  /**
   * Find node by ID
   */
  findNode(root, nodeId) {
    if (root.id === nodeId) return root;

    for (const child of root.children || []) {
      const found = this.findNode(child, nodeId);
      if (found) return found;
    }

    return null;
  }

  /**
   * Clear the tree
   */
  clear() {
    this.model = null;
    this.treeData = null;
    this.expandedNodes.clear();
    this.selectedNode = null;

    if (this.treeContainer) {
      this.treeContainer.innerHTML = '<p class="placeholder">Carga un modelo para ver su estructura</p>';
    }
  }
}

export default IFCTreeNavigator;
