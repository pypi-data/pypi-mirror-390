import { ApiClient } from "./api.js";
import { logger } from "./logger.js";

export class Configurator {
  constructor() {
    this.apiClient = new ApiClient();
    this.openApiSchema = null;
    this.currentConfig = {};
    this.configApplyHandler = null;
    this.versionData = null;
    this.configSchemas = new Map();
  }

  async init() {
    await this.loadSchema();
    this.setupEventListeners();
    this.generateUI();
  }

  setApiBase(url) {
    this.apiClient.setBaseUrl(url);
    logger.log(`API базовый URL обновлен: ${url}`);
  }

  async loadSchema() {
    try {
      this.openApiSchema = await this.apiClient.fetchOpenApiSchema();
      this.versionData = await this.apiClient.fetchVersion();
      this.updateStatus("success", `API: ${this.apiClient.baseUrl}`);
      this.updateVersion();
      logger.success("OpenAPI схема загружена");
    } catch (error) {
      this.updateStatus("error", "API: Ошибка подключения");
      logger.error(error.message);
    }
  }

  generateUI() {
    if (!this.openApiSchema) return;

    const sectionsContainer = document.getElementById("configSections");
    sectionsContainer.innerHTML = "";

    // Парсим компоненты схемы
    const components = this.openApiSchema.components?.schemas;

    if (!components) {
      sectionsContainer.innerHTML =
        '<div class="loading-config">Нет доступных конфигураций</div>';
      return;
    }

    // Находим главную схему конфигурации (с g_parser)
    const mainConfigSchema = this.findMainConfigSchema(components);

    if (!mainConfigSchema) {
      sectionsContainer.innerHTML =
        '<div class="loading-config">Нет доступных конфигураций</div>';
      return;
    }

    // Генерируем UI для главной схемы и всех вложенных
    this.generateConfigUI(mainConfigSchema, components, sectionsContainer);
  }

  findMainConfigSchema(components) {
    return Object.entries(components).find(([schemaName, schema]) => {
      return this.shouldDisplaySchema(schemaName, schema);
    });
  }

  shouldDisplaySchema(schemaName, schema) {
    if (!schema || !schema.properties) return false;
    // Ищем схемы с полем g_parser
    const hasGParser = schema.properties && "g_parser" in schema.properties;

    // Исключаем служебные схемы
    const excluded = [
      "Error",
      "Response",
      "Message",
      "HTTPValidationError",
      "ValidationError",
    ];

    return hasGParser && !excluded.includes(schemaName) && schema.properties;
  }

  generateConfigUI(mainSchema, allSchemas, container) {
    const [schemaName, schema] = mainSchema;

    // Рекурсивно собираем все связанные схемы
    const configSchemas = this.collectAllConfigSchemas(
      schemaName,
      schema,
      allSchemas,
    );

    // Генерируем UI для каждой найденной схемы конфигурации
    configSchemas.forEach((configSchema, schemaName) => {
      // Пропускаем главную схему с g_parser, т.к. она содержит только ссылки на вложенные
      if (schemaName === mainSchema[0]) return;

      if (!configSchema || !configSchema.properties) return false;

      const section = this.createConfigSection(schemaName, configSchema);
      container.appendChild(section);
    });
  }

  collectAllConfigSchemas(
    startSchemaName,
    startSchema,
    allSchemas,
    collected = new Map(),
  ) {
    // Добавляем текущую схему
    collected.set(startSchemaName, startSchema);

    // Рекурсивно ищем все вложенные схемы через $ref
    this.findReferencedSchemas(startSchema, allSchemas, collected);

    return collected;
  }

  findReferencedSchemas(schema, allSchemas, collected) {
    if (!schema || typeof schema !== "object") return;

    if (schema.$ref) {
      // Обрабатываем ссылки на другие схемы
      const refName = schema.$ref.split("/").pop();
      if (!collected.has(refName) && allSchemas[refName]) {
        collected.set(refName, allSchemas[refName]);
        this.findReferencedSchemas(allSchemas[refName], allSchemas, collected);
      }
    } else if (schema.properties) {
      // Обрабатываем свойства объектов
      Object.values(schema.properties).forEach((property) => {
        this.findReferencedSchemas(property, allSchemas, collected);
      });
    } else if (Array.isArray(schema)) {
      // Обрабатываем массивы
      schema.forEach((item) =>
        this.findReferencedSchemas(item, allSchemas, collected),
      );
    } else {
      // Обрабатываем вложенные объекты
      Object.values(schema).forEach((value) => {
        if (typeof value === "object") {
          this.findReferencedSchemas(value, allSchemas, collected);
        }
      });
    }
  }

  createConfigSection(schemaName, schema) {
    const section = document.createElement("div");
    section.className = "config-section";

    const title = this.formatSchemaName(schemaName);
    const description = schema.description || "";

    section.innerHTML = `
            <div class="section-header" onclick="this.parentNode.querySelector('.section-content').style.display = this.parentNode.querySelector('.section-content').style.display === 'none' ? 'grid' : 'none'">
                <span>${title}</span>
                <span>▶</span>
            </div>
            <div class="section-content">
                ${description ? `<div class="field-description">${description}</div>` : ""}
                ${this.generateFields(schema.properties, schema.required || [], schemaName)}
            </div>
        `;

    return section;
  }

  generateFields(properties, requiredFields, parentSchemaName = "") {
    let fieldsHTML = "";

    Object.entries(properties).forEach(([fieldName, fieldSchema]) => {
      // Пропускаем поле-маркер g_parser
      if (fieldName === "g_parser") return;

      const isRequired = requiredFields.includes(fieldName);

      // Генерируем поле с учетом родительской схемы для уникальности ID
      fieldsHTML += this.generateField(
        fieldName,
        fieldSchema,
        isRequired,
        parentSchemaName,
      );
    });

    return fieldsHTML;
  }

  generateField(fieldName, fieldSchema, isRequired, parentSchemaName = "") {
    const label = this.formatFieldName(fieldName);
    const description = fieldSchema.description || "";
    // Добавляем родительскую схему к ID для уникальности
    const fieldId = `config_${parentSchemaName}_${fieldName}`.replace(
      /[^a-zA-Z0-9_]/g,
      "_",
    );

    let inputHTML = "";

    // Обрабатываем ссылки на другие схемы (вложенные объекты)
    if (fieldSchema.$ref) {
      // Для вложенных объектов не показываем отдельное поле - они будут в своих секциях
      return "";
    }

    // Генерируем подходящий input на основе типа поля
    switch (fieldSchema.type) {
      case "string":
        if (fieldSchema.enum) {
          inputHTML = this.generateSelect(
            fieldId,
            fieldSchema.enum,
            fieldSchema.default,
          );
        } else {
          inputHTML = `<input type="text" id="${fieldId}" class="field-input"
                        value="${fieldSchema.default || ""}"
                        placeholder="${fieldSchema.example || ""}">`;
        }
        break;

      case "number":
      case "integer":
        if (
          fieldSchema.minimum !== undefined ||
          fieldSchema.maximum !== undefined
        ) {
          inputHTML = this.generateRange(fieldId, fieldSchema);
        } else {
          inputHTML = `<input type="number" id="${fieldId}" class="field-input"
                        value="${fieldSchema.default || 0}"
                        step="${fieldSchema.type === "integer" ? 1 : 0.1}">`;
        }
        break;

      case "boolean":
        inputHTML = this.generateCheckbox(
          fieldId,
          fieldSchema.default || false,
        );
        break;

      case "object":
        // Для объектов без $ref генерируем поля рекурсивно
        if (fieldSchema.properties) {
          inputHTML = this.generateFields(
            fieldSchema.properties,
            fieldSchema.required || [],
            fieldName,
          );
        } else {
          inputHTML = `<div class="field-note">Объект конфигурации</div>`;
        }
        break;

      default:
        inputHTML = `<input type="text" id="${fieldId}" class="field-input"
                    value="${JSON.stringify(fieldSchema.default || "")}">`;
    }

    // Если inputHTML содержит вложенные поля, возвращаем как есть
    if (typeof inputHTML === "string" && inputHTML.includes("config-field")) {
      return inputHTML;
    }

    return `
            <div class="config-field">
                <label class="field-label" for="${fieldId}">
                    ${label} ${isRequired ? '<span style="color: #ff4444">*</span>' : ""}
                </label>
                ${description ? `<div class="field-description">${description}</div>` : ""}
                ${inputHTML}
            </div>
        `;
  }

  generateSelect(fieldId, enumValues, defaultValue) {
    const options = enumValues
      .map(
        (value) =>
          `<option value="${value}" ${value === defaultValue ? "selected" : ""}>${value}</option>`,
      )
      .join("");

    return `<select id="${fieldId}" class="field-select">${options}</select>`;
  }

  generateRange(fieldId, fieldSchema) {
    const min = fieldSchema.minimum || 0;
    const max = fieldSchema.maximum || 100;
    const step = fieldSchema.type === "integer" ? 1 : 0.1;
    const defaultValue = fieldSchema.default || min;

    return `
            <input type="range" id="${fieldId}" class="field-range"
                min="${min}" max="${max}" step="${step}" value="${defaultValue}">
            <div class="range-value" id="${fieldId}_value">${defaultValue}</div>
        `;
  }

  generateCheckbox(fieldId, defaultValue) {
    const checked = defaultValue ? "checked" : "";
    return `
            <div class="field-checkbox">
                <input type="checkbox" id="${fieldId}" ${checked}>
                <label class="checkbox-label" for="${fieldId}">Включено</label>
            </div>
        `;
  }

  // Сбор конфигурации со всех полей
  collectConfiguration() {
    const config = {};
    const fields = document.querySelectorAll('[id^="config_"]');

    fields.forEach((field) => {
      const fullFieldId = field.id.replace("config_", "");
      // Разбираем ID вида "ParentSchema_FieldName"
      const parts = fullFieldId.split("_");
      let value;

      // Определяем значение в зависимости от типа поля
      switch (field.type) {
        case "checkbox":
          value = field.checked;
          break;
        case "range":
        case "number":
          value = parseFloat(field.value);
          break;
        case "select-one":
          value = field.value;
          // Конвертируем числа если нужно
          if (!isNaN(value) && value !== "") {
            value = parseFloat(value);
          }
          break;
        default:
          value = field.value;
          // Конвертируем числа если нужно
          if (!isNaN(value) && value !== "") {
            value = parseFloat(value);
          }
      }

      // Пропускаем пустые значения
      if (value !== "" && value !== null && value !== undefined) {
        // Строим вложенную структуру
        this.setNestedValue(config, parts, value);
      }
    });

    return config;
  }

  // Вспомогательная функция для установки вложенных значений
  setNestedValue(obj, path, value) {
    if (path.length === 1) {
      obj[path[0]] = value;
    } else {
      const current = path[0];
      if (!obj[current]) {
        obj[current] = {};
      }
      this.setNestedValue(obj[current], path.slice(1), value);
    }
  }

  // Применение конфигурации к роверу
  async applyConfiguration() {
    const config = this.collectConfiguration();

    logger.log("⚡ Отправка конфигурации...");

    try {
      if (this.configApplyHandler) {
        // Используем внешний обработчик если есть
        await this.configApplyHandler(config);
      } else {
        // Или применяем напрямую через API
        await this.apiClient.applyConfiguration(config);
        logger.success("Конфигурация применена успешно");
      }
    } catch (error) {
      logger.error(`Ошибка применения: ${error.message}`);
    }
  }

  // Сохранение конфигурации в файл
  saveConfiguration() {
    const config = this.collectConfiguration();
    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `rover-config-${new Date().toISOString().split("T")[0]}.json`;
    a.click();

    URL.revokeObjectURL(url);
    logger.log("Конфигурация сохранена в файл");
  }

  // Загрузка конфигурации из файла
  loadConfigurationFromFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const config = JSON.parse(e.target.result);
        this.populateForm(config);
        logger.log("Конфигурация загружена из файла");
      } catch (error) {
        logger.error(`Ошибка загрузки файла: ${error.message}`);
      }
    };
    reader.readAsText(file);
  }

  // Заполнение формы значениями из конфигурации
  populateForm(config) {
    // Рекурсивно обходим конфигурацию и заполняем поля
    this.populateFormRecursive(config);
  }

  populateFormRecursive(config, prefix = "") {
    Object.entries(config).forEach(([key, value]) => {
      const fieldId = prefix ? `config_${prefix}_${key}` : `config_${key}`;
      const field = document.getElementById(fieldId);

      if (field) {
        if (field.type === "checkbox") {
          field.checked = Boolean(value);
        } else if (field.type === "range") {
          field.value = value;
          const valueDisplay = document.getElementById(`${field.id}_value`);
          if (valueDisplay) {
            valueDisplay.textContent = value;
          }
        } else {
          field.value = value;
        }
      } else if (typeof value === "object" && value !== null) {
        // Рекурсивно обрабатываем вложенные объекты
        const newPrefix = prefix ? `${prefix}_${key}` : key;
        this.populateFormRecursive(value, newPrefix);
      }
    });
  }

  // Вспомогательные методы
  formatSchemaName(name) {
    return name
      .replace(/([A-Z])/g, " $1")
      .replace(/_/g, " ")
      .trim()
      .toUpperCase();
  }

  formatFieldName(name) {
    return name
      .replace(/([A-Z])/g, " $1")
      .replace(/_/g, " ")
      .replace(/^\w/, (c) => c.toUpperCase());
  }

  setupEventListeners() {
    // Кнопка обновления схемы
    const refreshBtn = document.getElementById("refreshConfig");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => {
        this.loadSchema().then(() => this.generateUI());
      });
    }

    // Кнопка применения конфигурации
    const applyBtn = document.getElementById("applyConfig");
    if (applyBtn) {
      applyBtn.addEventListener("click", () => {
        this.applyConfiguration();
      });
    }

    // Кнопка сохранения конфигурации
    const saveBtn = document.getElementById("saveConfig");
    if (saveBtn) {
      saveBtn.addEventListener("click", () => {
        this.saveConfiguration();
      });
    }

    // Кнопка загрузки конфигурации
    const loadBtn = document.getElementById("loadConfig");
    if (loadBtn) {
      const fileInput = document.getElementById("configFileInput");
      if (!fileInput) {
        // Создаем скрытый input для загрузки файлов
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".json";
        input.id = "configFileInput";
        input.style.display = "none";
        document.body.appendChild(input);

        input.addEventListener("change", (e) => {
          if (e.target.files[0]) {
            this.loadConfigurationFromFile(e.target.files[0]);
          }
        });

        loadBtn.addEventListener("click", () => {
          input.click();
        });
      }
    }

    // Обновление значений range
    document.addEventListener("input", (e) => {
      if (e.target.type === "range") {
        const valueDisplay = document.getElementById(`${e.target.id}_value`);
        if (valueDisplay) {
          valueDisplay.textContent = e.target.value;
        }
      }
    });
  }

  updateVersion() {
    let software_version = this.versionData.software;
    const versionElement = document.getElementById("configVersion");
    if (versionElement) {
      versionElement.textContent = `Версия: ${software_version}`;
    }
  }

  updateStatus(type, message) {
    const endpointElement = document.getElementById("apiEndpoint");
    if (endpointElement) {
      endpointElement.textContent = message;
      endpointElement.className = `api-endpoint ${type}`;
    }
  }

  onConfigApply(handler) {
    this.configApplyHandler = handler;
  }

  // Дополнительные методы для удобства
  async getCurrentConfig() {
    try {
      return await this.apiClient.getCurrentConfig();
    } catch (error) {
      logger.error(`Ошибка получения текущей конфигурации: ${error.message}`);
      return null;
    }
  }

  async refreshCurrentConfig() {
    const config = await this.getCurrentConfig();
    if (config) {
      this.populateForm(config);
      logger.log("Текущая конфигурация загружена");
    }
  }
}
