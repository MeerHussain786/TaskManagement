import { defineConfig } from 'orval';

export default defineConfig({
  api: {
    input: 'http://127.0.0.1:8000/openapi.json',
    output: {
      mode: 'tags-split',
      target: 'src/services/api/generated/api.ts',
      schemas: 'src/services/api/generated/models',
      client: 'react-query',
      httpClient: 'axios',
      mock: false,
      override: {
        mutator: {
          path: './src/services/api/axios-instance.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
