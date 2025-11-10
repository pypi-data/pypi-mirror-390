import { Model } from "../model";
import { getDefaultModelTypeForApplication } from "../tree";
import type { ModelConfig } from "../types";
import { DFTModel } from "./dft";

export class ModelFactory {
    static DFTModel = DFTModel;

    static Model = Model;

    static create(config: ModelConfig): Model {
        switch (config.type) {
            case "dft":
                return new this.DFTModel(config);
            default:
                return new this.Model(config);
        }
    }

    static createFromApplication(config: ModelConfig): Model {
        const { application } = config;
        if (!application) {
            throw new Error("ModelFactory.createFromApplication: application is required");
        }
        const type = getDefaultModelTypeForApplication(application);
        if (!type) {
            throw new Error(
                `ModelFactory.createFromApplication: cannot determine model type: ${type}`,
            );
        }
        return this.create({ ...config, type });
    }
}
