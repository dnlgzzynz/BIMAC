/**
 * Node Editor Core - Graph-based parametric design system
 * Inspired by Grasshopper, Dynamo, and Blender Geometry Nodes
 */

// Node port types
export const PortType = {
  NUMBER: 'number',
  VECTOR: 'vector',
  GEOMETRY: 'geometry',
  BOOLEAN: 'boolean',
  STRING: 'string',
  ANY: 'any'
};

// Port direction
export const PortDirection = {
  INPUT: 'input',
  OUTPUT: 'output'
};

/**
 * Base class for all nodes
 */
export class BaseNode {
  constructor(id, type, title) {
    this.id = id;
    this.type = type;
    this.title = title;
    this.x = 0;
    this.y = 0;
    this.width = 180;
    this.height = 100;
    this.inputs = [];
    this.outputs = [];
    this.values = {};
    this.isSelected = false;
    this.isDirty = true;
    this.cachedOutput = null;
    this.color = '#3b82f6';
  }

  addInput(name, type, defaultValue = null) {
    this.inputs.push({
      name,
      type,
      value: defaultValue,
      connection: null,
      node: this
    });
    this.updateHeight();
    return this;
  }

  addOutput(name, type) {
    this.outputs.push({
      name,
      type,
      connections: [],
      node: this
    });
    this.updateHeight();
    return this;
  }

  updateHeight() {
    const portCount = Math.max(this.inputs.length, this.outputs.length);
    this.height = Math.max(80, 50 + portCount * 28);
  }

  getInputValue(name) {
    const input = this.inputs.find(i => i.name === name);
    if (!input) return null;

    if (input.connection) {
      const sourceNode = input.connection.sourceNode;
      const sourceOutput = input.connection.sourceOutput;
      const outputData = sourceNode.evaluate();
      return outputData?.[sourceOutput];
    }

    return input.value;
  }

  setInputValue(name, value) {
    const input = this.inputs.find(i => i.name === name);
    if (input) {
      input.value = value;
      this.markDirty();
    }
  }

  markDirty() {
    this.isDirty = true;
    // Propagate dirty flag to connected nodes
    for (const output of this.outputs) {
      for (const conn of output.connections) {
        conn.targetNode.markDirty();
      }
    }
  }

  evaluate() {
    if (!this.isDirty && this.cachedOutput) {
      return this.cachedOutput;
    }

    this.cachedOutput = this.process();
    this.isDirty = false;
    return this.cachedOutput;
  }

  process() {
    // Override in subclasses
    return {};
  }

  toJSON() {
    return {
      id: this.id,
      type: this.type,
      title: this.title,
      x: this.x,
      y: this.y,
      values: this.values,
      inputs: this.inputs.map(i => ({
        name: i.name,
        value: i.value
      }))
    };
  }
}

/**
 * Connection between nodes
 */
export class Connection {
  constructor(sourceNode, sourceOutput, targetNode, targetInput) {
    this.sourceNode = sourceNode;
    this.sourceOutput = sourceOutput;
    this.targetNode = targetNode;
    this.targetInput = targetInput;
    this.id = `${sourceNode.id}:${sourceOutput}->${targetNode.id}:${targetInput}`;
  }
}

/**
 * Node Graph - Manages all nodes and connections
 */
export class NodeGraph {
  constructor() {
    this.nodes = new Map();
    this.connections = [];
    this.nodeIdCounter = 0;
    this.onChangeCallbacks = [];
  }

  createNode(NodeClass, x = 0, y = 0) {
    const id = `node_${++this.nodeIdCounter}`;
    const node = new NodeClass(id);
    node.x = x;
    node.y = y;
    this.nodes.set(id, node);
    this.notifyChange();
    return node;
  }

  removeNode(nodeId) {
    const node = this.nodes.get(nodeId);
    if (!node) return;

    // Remove all connections involving this node
    this.connections = this.connections.filter(conn => {
      if (conn.sourceNode.id === nodeId || conn.targetNode.id === nodeId) {
        // Clear connection references
        if (conn.targetNode.id !== nodeId) {
          const input = conn.targetNode.inputs.find(i => i.name === conn.targetInput);
          if (input) input.connection = null;
        }
        if (conn.sourceNode.id !== nodeId) {
          const output = conn.sourceNode.outputs.find(o => o.name === conn.sourceOutput);
          if (output) {
            output.connections = output.connections.filter(c => c !== conn);
          }
        }
        return false;
      }
      return true;
    });

    this.nodes.delete(nodeId);
    this.notifyChange();
  }

  connect(sourceNodeId, sourceOutput, targetNodeId, targetInput) {
    const sourceNode = this.nodes.get(sourceNodeId);
    const targetNode = this.nodes.get(targetNodeId);

    if (!sourceNode || !targetNode) return null;

    const output = sourceNode.outputs.find(o => o.name === sourceOutput);
    const input = targetNode.inputs.find(i => i.name === targetInput);

    if (!output || !input) return null;

    // Check type compatibility
    if (output.type !== input.type && output.type !== PortType.ANY && input.type !== PortType.ANY) {
      console.warn('Incompatible port types:', output.type, input.type);
      return null;
    }

    // Remove existing connection to this input
    if (input.connection) {
      this.disconnect(input.connection);
    }

    const connection = new Connection(sourceNode, sourceOutput, targetNode, targetInput);
    this.connections.push(connection);

    output.connections.push(connection);
    input.connection = connection;

    targetNode.markDirty();
    this.notifyChange();

    return connection;
  }

  disconnect(connection) {
    const index = this.connections.indexOf(connection);
    if (index === -1) return;

    const output = connection.sourceNode.outputs.find(o => o.name === connection.sourceOutput);
    const input = connection.targetNode.inputs.find(i => i.name === connection.targetInput);

    if (output) {
      output.connections = output.connections.filter(c => c !== connection);
    }
    if (input) {
      input.connection = null;
    }

    this.connections.splice(index, 1);
    connection.targetNode.markDirty();
    this.notifyChange();
  }

  evaluate() {
    // Find output nodes and evaluate them
    const results = [];
    for (const node of this.nodes.values()) {
      if (node.type === 'output' || node.type === 'geometry-output') {
        results.push({
          nodeId: node.id,
          data: node.evaluate()
        });
      }
    }
    return results;
  }

  onChange(callback) {
    this.onChangeCallbacks.push(callback);
  }

  notifyChange() {
    for (const callback of this.onChangeCallbacks) {
      callback(this);
    }
  }

  toJSON() {
    return {
      nodes: Array.from(this.nodes.values()).map(n => n.toJSON()),
      connections: this.connections.map(c => ({
        sourceNode: c.sourceNode.id,
        sourceOutput: c.sourceOutput,
        targetNode: c.targetNode.id,
        targetInput: c.targetInput
      }))
    };
  }

  clear() {
    this.nodes.clear();
    this.connections = [];
    this.nodeIdCounter = 0;
    this.notifyChange();
  }
}

export default NodeGraph;
