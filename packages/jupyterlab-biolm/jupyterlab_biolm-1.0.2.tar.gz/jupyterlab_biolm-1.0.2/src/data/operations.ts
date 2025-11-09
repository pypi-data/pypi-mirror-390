/**
 * Static operations data for the Operations tab
 * Based on BioLM API documentation: https://docs.biolm.ai/latest/python-client/usage.html
 */

export interface Operation {
  title: string;
  description: string;
  category: string;
  code: string;
  parameters?: string[];
}

export const operations: Operation[] = [
  {
    title: 'Import BioLM',
    description: 'Import the BioLM library (run this once at the top of your notebook)',
    category: 'Setup',
    code: `from biolmai import biolm`,
    parameters: [],
  },
  {
    title: 'Encode Sequence',
    description: 'Encode a single sequence into embeddings using ESM2-8M',
    category: 'Encoding',
    code: `result = biolm(entity="esm2-8m", action="encode", type="sequence", items="MSILVTRPSPAGEEL")

print(result)`,
    parameters: ['entity', 'action', 'type', 'items'],
  },
  {
    title: 'Encode Batch',
    description: 'Encode multiple sequences in a batch',
    category: 'Encoding',
    code: `result = biolm(entity="esm2-8m", action="encode", type="sequence", items=["SEQ1", "SEQ2"])

print(result)`,
    parameters: ['entity', 'action', 'type', 'items'],
  },
  {
    title: 'Predict Structure',
    description: 'Predict protein structure from sequence using ESMFold',
    category: 'Prediction',
    code: `result = biolm(entity="esmfold", action="predict", type="sequence", items="MDNELE")

print(result)`,
    parameters: ['entity', 'action', 'type', 'items'],
  },
  {
    title: 'Predict Batch',
    description: 'Predict structures for multiple sequences',
    category: 'Prediction',
    code: `result = biolm(entity="esmfold", action="predict", type="sequence", items=["MDNELE", "MENDEL"])

print(result)`,
    parameters: ['entity', 'action', 'type', 'items'],
  },
  {
    title: 'Generate Sequence',
    description: 'Generate new sequences from a context using ProGen2-OAS',
    category: 'Generation',
    code: `result = biolm(
    entity="progen2-oas",
    action="generate",
    type="context",
    items="M",
    params={"temperature": 0.7, "top_p": 0.6, "num_samples": 2, "max_length": 17}
)

print(result)`,
    parameters: ['entity', 'action', 'type', 'items', 'params'],
  },
  {
    title: 'Write to Disk',
    description: 'Save results directly to a file',
    category: 'Output',
    code: `result = biolm(
    entity="esmfold",
    action="predict",
    type="sequence",
    items=["SEQ1", "SEQ2"],
    output='disk',
    file_path="results.jsonl"
)`,
    parameters: ['entity', 'action', 'type', 'items', 'output', 'file_path'],
  },
  {
    title: 'Classify Sequence',
    description: 'Classify a sequence',
    category: 'Classification',
    code: `result = biolm(entity="your-model-id", action="classify", type="sequence", items="YOUR_SEQUENCE")

print(result)`,
    parameters: ['entity', 'action', 'type', 'items'],
  },
  {
    title: 'Similarity Search',
    description: 'Find similar sequences',
    category: 'Similarity',
    code: `result = biolm(entity="your-model-id", action="similarity", type="sequence", items="YOUR_SEQUENCE")

print(result)`,
    parameters: ['entity', 'action', 'type', 'items'],
  },
];
