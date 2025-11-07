export class ApiClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    setBaseUrl(url) {
        this.baseUrl = url;
    }

    async fetchOpenApiSchema() {
        try {
            const response = await fetch(`${this.baseUrl}/openapi.json`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            throw new Error(`Ошибка загрузки схемы: ${error.message}`);
        }
    }

    async fetchVersion() {
        try {
            const response = await fetch(`${this.baseUrl}/version`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            throw new Error(`Ошибка загрузки версии: ${error.message}`);
        }
    }

    async applyConfiguration(config) {
        const response = await fetch(`${this.baseUrl}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    }

    async getCurrentConfig() {
        const response = await fetch(`${this.baseUrl}/config`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    }

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch {
            return false;
        }
    }
}