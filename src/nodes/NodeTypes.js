/**
 * Node Types for Parametric Design
 * Collection of nodes for generative design workflows
 */

import { BaseNode, PortType } from './NodeGraph.js';
import * as THREE from 'three';

// ============================================
// INPUT NODES
// ============================================

export class NumberNode extends BaseNode {
  constructor(id) {
    super(id, 'number', 'Number');
    this.color = '#22c55e';
    this.addOutput('value', PortType.NUMBER);
    this.values.number = 0;
  }

  process() {
    return { value: this.values.number };
  }
}

export class SliderNode extends BaseNode {
  constructor(id) {
    super(id, 'slider', 'Slider');
    this.color = '#22c55e';
    this.addOutput('value', PortType.NUMBER);
    this.values.min = 0;
    this.values.max = 100;
    this.values.value = 50;
    this.values.step = 1;
  }

  process() {
    return { value: this.values.value };
  }
}

export class VectorNode extends BaseNode {
  constructor(id) {
    super(id, 'vector', 'Vector');
    this.color = '#8b5cf6';
    this.addInput('X', PortType.NUMBER, 0);
    this.addInput('Y', PortType.NUMBER, 0);
    this.addInput('Z', PortType.NUMBER, 0);
    this.addOutput('vector', PortType.VECTOR);
  }

  process() {
    const x = this.getInputValue('X') ?? 0;
    const y = this.getInputValue('Y') ?? 0;
    const z = this.getInputValue('Z') ?? 0;
    return { vector: new THREE.Vector3(x, y, z) };
  }
}

export class PointNode extends BaseNode {
  constructor(id) {
    super(id, 'point', 'Point');
    this.color = '#8b5cf6';
    this.addOutput('point', PortType.VECTOR);
    this.values.x = 0;
    this.values.y = 0;
    this.values.z = 0;
  }

  process() {
    return { point: new THREE.Vector3(this.values.x, this.values.y, this.values.z) };
  }
}

// ============================================
// MATH NODES
// ============================================

export class MathNode extends BaseNode {
  constructor(id) {
    super(id, 'math', 'Math');
    this.color = '#f59e0b';
    this.addInput('A', PortType.NUMBER, 0);
    this.addInput('B', PortType.NUMBER, 0);
    this.addOutput('result', PortType.NUMBER);
    this.values.operation = 'add';
  }

  process() {
    const a = this.getInputValue('A') ?? 0;
    const b = this.getInputValue('B') ?? 0;
    let result = 0;

    switch (this.values.operation) {
      case 'add': result = a + b; break;
      case 'subtract': result = a - b; break;
      case 'multiply': result = a * b; break;
      case 'divide': result = b !== 0 ? a / b : 0; break;
      case 'power': result = Math.pow(a, b); break;
      case 'modulo': result = a % b; break;
      case 'min': result = Math.min(a, b); break;
      case 'max': result = Math.max(a, b); break;
    }

    return { result };
  }
}

export class TrigNode extends BaseNode {
  constructor(id) {
    super(id, 'trig', 'Trigonometry');
    this.color = '#f59e0b';
    this.addInput('angle', PortType.NUMBER, 0);
    this.addOutput('result', PortType.NUMBER);
    this.values.function = 'sin';
    this.values.useDegrees = true;
  }

  process() {
    let angle = this.getInputValue('angle') ?? 0;
    if (this.values.useDegrees) {
      angle = angle * Math.PI / 180;
    }

    let result = 0;
    switch (this.values.function) {
      case 'sin': result = Math.sin(angle); break;
      case 'cos': result = Math.cos(angle); break;
      case 'tan': result = Math.tan(angle); break;
      case 'asin': result = Math.asin(angle); break;
      case 'acos': result = Math.acos(angle); break;
      case 'atan': result = Math.atan(angle); break;
    }

    return { result };
  }
}

export class RangeNode extends BaseNode {
  constructor(id) {
    super(id, 'range', 'Range');
    this.color = '#f59e0b';
    this.addInput('start', PortType.NUMBER, 0);
    this.addInput('end', PortType.NUMBER, 10);
    this.addInput('steps', PortType.NUMBER, 10);
    this.addOutput('values', PortType.ANY);
  }

  process() {
    const start = this.getInputValue('start') ?? 0;
    const end = this.getInputValue('end') ?? 10;
    const steps = Math.max(1, Math.floor(this.getInputValue('steps') ?? 10));

    const values = [];
    for (let i = 0; i <= steps; i++) {
      values.push(start + (end - start) * (i / steps));
    }

    return { values };
  }
}

export class RemapNode extends BaseNode {
  constructor(id) {
    super(id, 'remap', 'Remap');
    this.color = '#f59e0b';
    this.addInput('value', PortType.NUMBER, 0);
    this.addInput('inMin', PortType.NUMBER, 0);
    this.addInput('inMax', PortType.NUMBER, 1);
    this.addInput('outMin', PortType.NUMBER, 0);
    this.addInput('outMax', PortType.NUMBER, 100);
    this.addOutput('result', PortType.NUMBER);
  }

  process() {
    const value = this.getInputValue('value') ?? 0;
    const inMin = this.getInputValue('inMin') ?? 0;
    const inMax = this.getInputValue('inMax') ?? 1;
    const outMin = this.getInputValue('outMin') ?? 0;
    const outMax = this.getInputValue('outMax') ?? 100;

    const t = (value - inMin) / (inMax - inMin);
    const result = outMin + t * (outMax - outMin);

    return { result };
  }
}

// ============================================
// GEOMETRY NODES
// ============================================

export class BoxNode extends BaseNode {
  constructor(id) {
    super(id, 'box', 'Box');
    this.color = '#3b82f6';
    this.addInput('width', PortType.NUMBER, 1);
    this.addInput('height', PortType.NUMBER, 1);
    this.addInput('depth', PortType.NUMBER, 1);
    this.addInput('position', PortType.VECTOR, null);
    this.addOutput('geometry', PortType.GEOMETRY);
  }

  process() {
    const width = this.getInputValue('width') ?? 1;
    const height = this.getInputValue('height') ?? 1;
    const depth = this.getInputValue('depth') ?? 1;
    const position = this.getInputValue('position') ?? new THREE.Vector3(0, 0, 0);

    const geometry = new THREE.BoxGeometry(width, height, depth);
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color: 0x3b82f6 })
    );
    mesh.position.copy(position);

    return { geometry: mesh };
  }
}

export class SphereNode extends BaseNode {
  constructor(id) {
    super(id, 'sphere', 'Sphere');
    this.color = '#3b82f6';
    this.addInput('radius', PortType.NUMBER, 1);
    this.addInput('segments', PortType.NUMBER, 32);
    this.addInput('position', PortType.VECTOR, null);
    this.addOutput('geometry', PortType.GEOMETRY);
  }

  process() {
    const radius = this.getInputValue('radius') ?? 1;
    const segments = Math.max(4, Math.floor(this.getInputValue('segments') ?? 32));
    const position = this.getInputValue('position') ?? new THREE.Vector3(0, 0, 0);

    const geometry = new THREE.SphereGeometry(radius, segments, segments);
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color: 0x3b82f6 })
    );
    mesh.position.copy(position);

    return { geometry: mesh };
  }
}

export class CylinderNode extends BaseNode {
  constructor(id) {
    super(id, 'cylinder', 'Cylinder');
    this.color = '#3b82f6';
    this.addInput('radiusTop', PortType.NUMBER, 1);
    this.addInput('radiusBottom', PortType.NUMBER, 1);
    this.addInput('height', PortType.NUMBER, 2);
    this.addInput('segments', PortType.NUMBER, 32);
    this.addInput('position', PortType.VECTOR, null);
    this.addOutput('geometry', PortType.GEOMETRY);
  }

  process() {
    const radiusTop = this.getInputValue('radiusTop') ?? 1;
    const radiusBottom = this.getInputValue('radiusBottom') ?? 1;
    const height = this.getInputValue('height') ?? 2;
    const segments = Math.max(3, Math.floor(this.getInputValue('segments') ?? 32));
    const position = this.getInputValue('position') ?? new THREE.Vector3(0, 0, 0);

    const geometry = new THREE.CylinderGeometry(radiusTop, radiusBottom, height, segments);
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color: 0x3b82f6 })
    );
    mesh.position.copy(position);

    return { geometry: mesh };
  }
}

export class TorusNode extends BaseNode {
  constructor(id) {
    super(id, 'torus', 'Torus');
    this.color = '#3b82f6';
    this.addInput('radius', PortType.NUMBER, 2);
    this.addInput('tube', PortType.NUMBER, 0.5);
    this.addInput('radialSegments', PortType.NUMBER, 16);
    this.addInput('tubularSegments', PortType.NUMBER, 48);
    this.addInput('position', PortType.VECTOR, null);
    this.addOutput('geometry', PortType.GEOMETRY);
  }

  process() {
    const radius = this.getInputValue('radius') ?? 2;
    const tube = this.getInputValue('tube') ?? 0.5;
    const radialSegments = Math.max(3, Math.floor(this.getInputValue('radialSegments') ?? 16));
    const tubularSegments = Math.max(3, Math.floor(this.getInputValue('tubularSegments') ?? 48));
    const position = this.getInputValue('position') ?? new THREE.Vector3(0, 0, 0);

    const geometry = new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments);
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color: 0x3b82f6 })
    );
    mesh.position.copy(position);

    return { geometry: mesh };
  }
}

export class PlaneNode extends BaseNode {
  constructor(id) {
    super(id, 'plane', 'Plane');
    this.color = '#3b82f6';
    this.addInput('width', PortType.NUMBER, 10);
    this.addInput('height', PortType.NUMBER, 10);
    this.addInput('widthSegments', PortType.NUMBER, 1);
    this.addInput('heightSegments', PortType.NUMBER, 1);
    this.addOutput('geometry', PortType.GEOMETRY);
  }

  process() {
    const width = this.getInputValue('width') ?? 10;
    const height = this.getInputValue('height') ?? 10;
    const widthSegments = Math.max(1, Math.floor(this.getInputValue('widthSegments') ?? 1));
    const heightSegments = Math.max(1, Math.floor(this.getInputValue('heightSegments') ?? 1));

    const geometry = new THREE.PlaneGeometry(width, height, widthSegments, heightSegments);
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color: 0x3b82f6, side: THREE.DoubleSide })
    );
    mesh.rotation.x = -Math.PI / 2;

    return { geometry: mesh };
  }
}

export class GridNode extends BaseNode {
  constructor(id) {
    super(id, 'grid', 'Point Grid');
    this.color = '#ec4899';
    this.addInput('sizeX', PortType.NUMBER, 10);
    this.addInput('sizeY', PortType.NUMBER, 10);
    this.addInput('countX', PortType.NUMBER, 5);
    this.addInput('countY', PortType.NUMBER, 5);
    this.addOutput('points', PortType.ANY);
  }

  process() {
    const sizeX = this.getInputValue('sizeX') ?? 10;
    const sizeY = this.getInputValue('sizeY') ?? 10;
    const countX = Math.max(1, Math.floor(this.getInputValue('countX') ?? 5));
    const countY = Math.max(1, Math.floor(this.getInputValue('countY') ?? 5));

    const points = [];
    const stepX = sizeX / (countX - 1 || 1);
    const stepY = sizeY / (countY - 1 || 1);
    const offsetX = -sizeX / 2;
    const offsetY = -sizeY / 2;

    for (let y = 0; y < countY; y++) {
      for (let x = 0; x < countX; x++) {
        points.push(new THREE.Vector3(
          offsetX + x * stepX,
          0,
          offsetY + y * stepY
        ));
      }
    }

    return { points };
  }
}

// ============================================
// TRANSFORM NODES
// ============================================

export class TransformNode extends BaseNode {
  constructor(id) {
    super(id, 'transform', 'Transform');
    this.color = '#ec4899';
    this.addInput('geometry', PortType.GEOMETRY, null);
    this.addInput('translation', PortType.VECTOR, null);
    this.addInput('rotation', PortType.VECTOR, null);
    this.addInput('scale', PortType.VECTOR, null);
    this.addOutput('geometry', PortType.GEOMETRY);
  }

  process() {
    const geometry = this.getInputValue('geometry');
    if (!geometry) return { geometry: null };

    const translation = this.getInputValue('translation') ?? new THREE.Vector3(0, 0, 0);
    const rotation = this.getInputValue('rotation') ?? new THREE.Vector3(0, 0, 0);
    const scale = this.getInputValue('scale') ?? new THREE.Vector3(1, 1, 1);

    const clone = geometry.clone();
    clone.position.add(translation);
    clone.rotation.x += rotation.x * Math.PI / 180;
    clone.rotation.y += rotation.y * Math.PI / 180;
    clone.rotation.z += rotation.z * Math.PI / 180;
    clone.scale.multiply(scale);

    return { geometry: clone };
  }
}

export class ArrayNode extends BaseNode {
  constructor(id) {
    super(id, 'array', 'Linear Array');
    this.color = '#ec4899';
    this.addInput('geometry', PortType.GEOMETRY, null);
    this.addInput('count', PortType.NUMBER, 5);
    this.addInput('offset', PortType.VECTOR, null);
    this.addOutput('geometries', PortType.ANY);
  }

  process() {
    const geometry = this.getInputValue('geometry');
    if (!geometry) return { geometries: [] };

    const count = Math.max(1, Math.floor(this.getInputValue('count') ?? 5));
    const offset = this.getInputValue('offset') ?? new THREE.Vector3(2, 0, 0);

    const geometries = [];
    for (let i = 0; i < count; i++) {
      const clone = geometry.clone();
      clone.position.add(offset.clone().multiplyScalar(i));
      geometries.push(clone);
    }

    return { geometries };
  }
}

export class RadialArrayNode extends BaseNode {
  constructor(id) {
    super(id, 'radial-array', 'Radial Array');
    this.color = '#ec4899';
    this.addInput('geometry', PortType.GEOMETRY, null);
    this.addInput('count', PortType.NUMBER, 6);
    this.addInput('radius', PortType.NUMBER, 5);
    this.addInput('axis', PortType.STRING, 'Y');
    this.addOutput('geometries', PortType.ANY);
    this.values.axis = 'Y';
  }

  process() {
    const geometry = this.getInputValue('geometry');
    if (!geometry) return { geometries: [] };

    const count = Math.max(1, Math.floor(this.getInputValue('count') ?? 6));
    const radius = this.getInputValue('radius') ?? 5;
    const axis = this.values.axis;

    const geometries = [];
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const clone = geometry.clone();

      switch (axis) {
        case 'X':
          clone.position.y = Math.cos(angle) * radius;
          clone.position.z = Math.sin(angle) * radius;
          break;
        case 'Y':
          clone.position.x = Math.cos(angle) * radius;
          clone.position.z = Math.sin(angle) * radius;
          break;
        case 'Z':
          clone.position.x = Math.cos(angle) * radius;
          clone.position.y = Math.sin(angle) * radius;
          break;
      }

      geometries.push(clone);
    }

    return { geometries };
  }
}

// ============================================
// OUTPUT NODES
// ============================================

export class GeometryOutputNode extends BaseNode {
  constructor(id) {
    super(id, 'geometry-output', 'Geometry Output');
    this.color = '#ef4444';
    this.addInput('geometry', PortType.GEOMETRY, null);
    this.addInput('geometries', PortType.ANY, null);
    this.values.material = 'standard';
    this.values.color = '#3b82f6';
  }

  process() {
    const geometry = this.getInputValue('geometry');
    const geometries = this.getInputValue('geometries') ?? [];

    const outputs = [];

    if (geometry) {
      this.applyMaterial(geometry);
      outputs.push(geometry);
    }

    if (Array.isArray(geometries)) {
      for (const geo of geometries) {
        if (geo) {
          this.applyMaterial(geo);
          outputs.push(geo);
        }
      }
    }

    return { meshes: outputs };
  }

  applyMaterial(mesh) {
    if (!mesh.material) return;

    const color = new THREE.Color(this.values.color);

    switch (this.values.material) {
      case 'standard':
        mesh.material = new THREE.MeshStandardMaterial({ color });
        break;
      case 'phong':
        mesh.material = new THREE.MeshPhongMaterial({ color });
        break;
      case 'basic':
        mesh.material = new THREE.MeshBasicMaterial({ color });
        break;
      case 'wireframe':
        mesh.material = new THREE.MeshBasicMaterial({ color, wireframe: true });
        break;
    }
  }
}

// ============================================
// NODE REGISTRY
// ============================================

export const NodeRegistry = {
  // Inputs
  'number': NumberNode,
  'slider': SliderNode,
  'vector': VectorNode,
  'point': PointNode,

  // Math
  'math': MathNode,
  'trig': TrigNode,
  'range': RangeNode,
  'remap': RemapNode,

  // Geometry
  'box': BoxNode,
  'sphere': SphereNode,
  'cylinder': CylinderNode,
  'torus': TorusNode,
  'plane': PlaneNode,
  'grid': GridNode,

  // Transform
  'transform': TransformNode,
  'array': ArrayNode,
  'radial-array': RadialArrayNode,

  // Output
  'geometry-output': GeometryOutputNode
};

export const NodeCategories = {
  'Input': ['number', 'slider', 'vector', 'point'],
  'Math': ['math', 'trig', 'range', 'remap'],
  'Geometry': ['box', 'sphere', 'cylinder', 'torus', 'plane', 'grid'],
  'Transform': ['transform', 'array', 'radial-array'],
  'Output': ['geometry-output']
};

export default NodeRegistry;
