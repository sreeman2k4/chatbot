import axios from 'axios';

class TextExtractionService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.apiClient = axios.create({
      baseURL: this.baseURL,
      timeout: 120000,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async getAvailableEngines() {
    const res = await this.apiClient.get('/api/extract-text/engines');
    return res.data; // { engines: [...] }
  }

  async getServiceStatus() {
    const res = await this.apiClient.get('/api/extract-text/status');
    return res.data; // status object
  }

  async extractTextFromFile(file, options = { engine: 'auto', preprocess: true, detect_regions: false }) {
    const base64 = await this.fileToBase64(file);
    const payload = {
      image_data: base64.replace(/^data:[^,]+,/, ''),
      engine: options.engine || 'auto',
      preprocess: options.preprocess !== false,
      detect_regions: options.detect_regions === true,
    };

    const res = await this.apiClient.post('/api/extract-text', payload);
    return res.data;
  }

  fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = (err) => reject(err);
      reader.readAsDataURL(file);
    });
  }
}

const textExtractionService = new TextExtractionService();
export default textExtractionService;


