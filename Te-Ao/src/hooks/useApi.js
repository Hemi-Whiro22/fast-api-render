import { useMemo } from "react";

export function useApi(baseUrl = "http://localhost:8000") {
  return useMemo(() => {
    async function request(path, options = {}) {
      const response = await fetch(`${baseUrl}${path}`, options);
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      return response.json();
    }
    return { request };
  }, [baseUrl]);
}
