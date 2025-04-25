import { Embeddings } from '@langchain/core/embeddings';
import { chunkArray } from '@langchain/core/utils/chunk_array';

export class HuggingFaceTransformersEmbeddings extends Embeddings {
  constructor(fields = {}) {
    super(fields);

    this.modelName = fields.model || fields.modelName || 'Xenova/all-MiniLM-L6-v2';
    this.model = this.modelName;
    this.batchSize = fields.batchSize || 512;
    this.stripNewLines = fields.stripNewLines !== undefined ? fields.stripNewLines : true;
    this.timeout = fields.timeout;
    this.pipelinePromise = null; // Initialize as null
  }

  async embedDocuments(texts) {
    const batches = chunkArray(
      this.stripNewLines ? texts.map(t => t.replace(/\n/g, ' ')) : texts,
      this.batchSize
    );

    const batchRequests = batches.map(batch => this.runEmbedding(batch));
    const batchResponses = await Promise.all(batchRequests);
    const embeddings = [];

    for (let i = 0; i < batchResponses.length; i += 1) {
      const batchResponse = batchResponses[i];
      for (let j = 0; j < batchResponse.length; j += 1) {
        embeddings.push(batchResponse[j]);
      }
    }

    return embeddings;
  }

  async embedQuery(text) {
    const data = await this.runEmbedding([
      this.stripNewLines ? text.replace(/\n/g, ' ') : text,
    ]);
    return data[0];
  }

  async runEmbedding(texts) {
    const { pipeline } = await import('@xenova/transformers');

    const pipe = await (this.pipelinePromise ??= pipeline('feature-extraction', this.model));

    return this.caller.call(async () => {
      const output = await pipe(texts, { pooling: 'mean', normalize: true });
      return output.tolist();
    });
  }
}