import * as tf from '@tensorflow/tfjs';

/**
 * ML-based post-processing effects for the IFC viewer
 * Uses TensorFlow.js for GPU-accelerated image processing
 */
export class MLPostProcessor {
  constructor(renderer) {
    this.renderer = renderer;
    this.canvas = null;
    this.outputCanvas = null;
    this.ctx = null;
    this.outputCtx = null;
    this.isInitialized = false;
    this.activeEffects = new Set();
    this.models = {};
    this.backend = 'webgl';

    // Effect parameters
    this.params = {
      denoise: { strength: 0.5 },
      sharpen: { amount: 0.3 },
      ssao: { radius: 16, intensity: 1.0 },
      upscale: { factor: 2 },
      edgeEnhance: { strength: 0.5 },
      colorGrading: {
        exposure: 1.0,
        contrast: 1.0,
        saturation: 1.0
      }
    };
  }

  async init() {
    if (this.isInitialized) return;

    try {
      // Try WebGPU first, fallback to WebGL
      try {
        await tf.setBackend('webgpu');
        this.backend = 'webgpu';
        console.log('ML PostProcessor: Using WebGPU backend');
      } catch {
        await tf.setBackend('webgl');
        this.backend = 'webgl';
        console.log('ML PostProcessor: Using WebGL backend');
      }

      await tf.ready();

      // Create off-screen canvases for processing
      this.canvas = document.createElement('canvas');
      this.ctx = this.canvas.getContext('2d');

      this.outputCanvas = document.createElement('canvas');
      this.outputCtx = this.outputCanvas.getContext('2d');

      this.isInitialized = true;
      console.log('ML PostProcessor initialized');

      return { success: true, backend: this.backend };
    } catch (error) {
      console.error('Failed to initialize ML PostProcessor:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Capture frame from Three.js renderer
   */
  captureFrame() {
    const rendererCanvas = this.renderer.domElement;
    this.canvas.width = rendererCanvas.width;
    this.canvas.height = rendererCanvas.height;
    this.ctx.drawImage(rendererCanvas, 0, 0);
    return this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
  }

  /**
   * Apply ML-based denoising using a simple autoencoder-style filter
   */
  async applyDenoise(imageTensor) {
    const strength = this.params.denoise.strength;

    return tf.tidy(() => {
      // Gaussian-like blur using convolution for noise reduction
      const kernel = tf.tensor4d([
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]
      ].map(row => row.map(v => v / 16)), [3, 3, 1, 1]);

      // Apply per channel
      const channels = tf.split(imageTensor, 3, 2);
      const blurred = channels.map(channel => {
        const expanded = channel.expandDims(0).expandDims(-1);
        const convolved = tf.conv2d(expanded, kernel, 1, 'same');
        return convolved.squeeze([0, 3]);
      });

      const blurredImage = tf.stack(blurred, 2);

      // Blend original with blurred based on strength
      return tf.add(
        tf.mul(imageTensor, 1 - strength),
        tf.mul(blurredImage, strength)
      );
    });
  }

  /**
   * Apply ML-based sharpening using unsharp mask
   */
  async applySharpen(imageTensor) {
    const amount = this.params.sharpen.amount;

    return tf.tidy(() => {
      // Laplacian kernel for edge detection
      const kernel = tf.tensor4d([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
      ], [3, 3, 1, 1]);

      const channels = tf.split(imageTensor, 3, 2);
      const sharpened = channels.map(channel => {
        const expanded = channel.expandDims(0).expandDims(-1);
        const convolved = tf.conv2d(expanded, kernel, 1, 'same');
        return convolved.squeeze([0, 3]);
      });

      const sharpenedImage = tf.stack(sharpened, 2);

      // Blend
      return tf.add(
        tf.mul(imageTensor, 1 - amount),
        tf.mul(tf.clipByValue(sharpenedImage, 0, 1), amount)
      );
    });
  }

  /**
   * Apply Screen Space Ambient Occlusion (SSAO) approximation
   */
  async applySSAO(imageTensor) {
    const { radius, intensity } = this.params.ssao;

    return tf.tidy(() => {
      // Convert to grayscale for depth approximation
      const weights = tf.tensor1d([0.299, 0.587, 0.114]);
      const grayscale = tf.sum(tf.mul(imageTensor, weights), 2, true);

      // Create blur kernel for AO sampling
      const kernelSize = Math.min(radius, 7);
      const sigma = kernelSize / 3;
      const kernel1D = [];

      for (let i = 0; i < kernelSize; i++) {
        const x = i - Math.floor(kernelSize / 2);
        kernel1D.push(Math.exp(-(x * x) / (2 * sigma * sigma)));
      }

      const sum = kernel1D.reduce((a, b) => a + b, 0);
      const normalizedKernel = kernel1D.map(v => v / sum);

      // Horizontal blur
      const hKernel = tf.tensor4d(
        normalizedKernel.map(v => [[[[v]]]]).flat(2),
        [1, kernelSize, 1, 1]
      );

      // Vertical blur
      const vKernel = tf.tensor4d(
        normalizedKernel.map(v => [[[[v]]]]),
        [kernelSize, 1, 1, 1]
      );

      let aoMap = grayscale.expandDims(0);
      aoMap = tf.conv2d(aoMap, hKernel, 1, 'same');
      aoMap = tf.conv2d(aoMap, vKernel, 1, 'same');
      aoMap = aoMap.squeeze([0]);

      // Calculate AO factor
      const aoFactor = tf.sub(grayscale, aoMap);
      const aoMultiplier = tf.sub(1, tf.mul(tf.clipByValue(aoFactor, 0, 1), intensity));

      // Apply AO to original image
      return tf.mul(imageTensor, aoMultiplier);
    });
  }

  /**
   * Apply edge enhancement for architectural clarity
   */
  async applyEdgeEnhance(imageTensor) {
    const strength = this.params.edgeEnhance.strength;

    return tf.tidy(() => {
      // Sobel kernels for edge detection
      const sobelX = tf.tensor4d([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
      ], [3, 3, 1, 1]);

      const sobelY = tf.tensor4d([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
      ], [3, 3, 1, 1]);

      // Convert to grayscale
      const weights = tf.tensor1d([0.299, 0.587, 0.114]);
      const grayscale = tf.sum(tf.mul(imageTensor, weights), 2);
      const expanded = grayscale.expandDims(0).expandDims(-1);

      // Apply Sobel filters
      const edgesX = tf.conv2d(expanded, sobelX, 1, 'same');
      const edgesY = tf.conv2d(expanded, sobelY, 1, 'same');

      // Compute gradient magnitude
      const edges = tf.sqrt(tf.add(tf.square(edgesX), tf.square(edgesY)));
      const edgesNormalized = tf.div(edges, tf.max(edges)).squeeze([0, 3]);

      // Enhance edges in original image
      const edgeOverlay = tf.stack([edgesNormalized, edgesNormalized, edgesNormalized], 2);

      return tf.add(
        imageTensor,
        tf.mul(edgeOverlay, strength * 0.3)
      ).clipByValue(0, 1);
    });
  }

  /**
   * Apply color grading adjustments
   */
  async applyColorGrading(imageTensor) {
    const { exposure, contrast, saturation } = this.params.colorGrading;

    return tf.tidy(() => {
      let result = imageTensor;

      // Exposure adjustment
      if (exposure !== 1.0) {
        result = tf.mul(result, exposure);
      }

      // Contrast adjustment
      if (contrast !== 1.0) {
        const mean = tf.mean(result);
        result = tf.add(tf.mul(tf.sub(result, mean), contrast), mean);
      }

      // Saturation adjustment
      if (saturation !== 1.0) {
        const weights = tf.tensor1d([0.299, 0.587, 0.114]);
        const grayscale = tf.sum(tf.mul(result, weights), 2, true);
        result = tf.add(
          tf.mul(grayscale, 1 - saturation),
          tf.mul(result, saturation)
        );
      }

      return tf.clipByValue(result, 0, 1);
    });
  }

  /**
   * Apply super-resolution upscaling
   */
  async applyUpscale(imageTensor) {
    const factor = this.params.upscale.factor;

    return tf.tidy(() => {
      const [height, width] = imageTensor.shape;
      const newHeight = height * factor;
      const newWidth = width * factor;

      // Bilinear upscale with sharpening
      let upscaled = tf.image.resizeBilinear(
        imageTensor.expandDims(0),
        [newHeight, newWidth]
      ).squeeze(0);

      // Apply light sharpening to upscaled image
      const sharpenKernel = tf.tensor4d([
        [0, -0.5, 0],
        [-0.5, 3, -0.5],
        [0, -0.5, 0]
      ], [3, 3, 1, 1]);

      const channels = tf.split(upscaled, 3, 2);
      const sharpened = channels.map(channel => {
        const expanded = channel.expandDims(0).expandDims(-1);
        const convolved = tf.conv2d(expanded, sharpenKernel, 1, 'same');
        return convolved.squeeze([0, 3]);
      });

      return tf.clipByValue(tf.stack(sharpened, 2), 0, 1);
    });
  }

  /**
   * Process frame with all active effects
   */
  async processFrame() {
    if (!this.isInitialized || this.activeEffects.size === 0) {
      return null;
    }

    const imageData = this.captureFrame();

    // Convert to tensor
    let tensor = tf.tidy(() => {
      return tf.browser.fromPixels(imageData).toFloat().div(255);
    });

    try {
      // Apply effects in order
      const effectOrder = ['denoise', 'ssao', 'sharpen', 'edgeEnhance', 'colorGrading', 'upscale'];

      for (const effect of effectOrder) {
        if (this.activeEffects.has(effect)) {
          const newTensor = await this.applyEffect(effect, tensor);
          tensor.dispose();
          tensor = newTensor;
        }
      }

      // Convert back to image data
      const [height, width] = tensor.shape;
      this.outputCanvas.width = width;
      this.outputCanvas.height = height;

      const outputData = await tf.browser.toPixels(tensor, this.outputCanvas);
      tensor.dispose();

      return this.outputCanvas;
    } catch (error) {
      console.error('Error processing frame:', error);
      tensor.dispose();
      return null;
    }
  }

  async applyEffect(effect, tensor) {
    switch (effect) {
      case 'denoise':
        return this.applyDenoise(tensor);
      case 'sharpen':
        return this.applySharpen(tensor);
      case 'ssao':
        return this.applySSAO(tensor);
      case 'edgeEnhance':
        return this.applyEdgeEnhance(tensor);
      case 'colorGrading':
        return this.applyColorGrading(tensor);
      case 'upscale':
        return this.applyUpscale(tensor);
      default:
        return tensor;
    }
  }

  /**
   * Enable an effect
   */
  enableEffect(effect) {
    this.activeEffects.add(effect);
  }

  /**
   * Disable an effect
   */
  disableEffect(effect) {
    this.activeEffects.delete(effect);
  }

  /**
   * Toggle an effect
   */
  toggleEffect(effect) {
    if (this.activeEffects.has(effect)) {
      this.activeEffects.delete(effect);
      return false;
    } else {
      this.activeEffects.add(effect);
      return true;
    }
  }

  /**
   * Update effect parameters
   */
  setParams(effect, params) {
    if (this.params[effect]) {
      this.params[effect] = { ...this.params[effect], ...params };
    }
  }

  /**
   * Get current memory info
   */
  getMemoryInfo() {
    return tf.memory();
  }

  /**
   * Dispose of all resources
   */
  dispose() {
    this.activeEffects.clear();
    tf.disposeVariables();
    this.isInitialized = false;
  }
}

export default MLPostProcessor;
