import { deepClone } from "@mat3ra/code/dist/js/utils";
import { ApplicationSchemaBase, SlugifiedEntry } from "@mat3ra/esse/dist/js/types";
import lodash from "lodash";
import _ from "underscore";

import type { ModelTree } from "./types";

// TODO: migrate to use manifest instead

export const METHODS = {
    pseudopotential: "pseudopotential",
    localorbital: "localorbital",
    unknown: "unknown",
} as const;

const methods: Record<string, string[]> = {
    [METHODS.pseudopotential]: ["paw", "nc", "nc-fr", "us"],
    // TODO: Add additional basis set options, once user choice of specific (i.e 3-21G vs cc-pVDZ) is implemented.
    [METHODS.localorbital]: ["pople"],
    [METHODS.unknown]: ["unknown"],
};

export const getPseudopotentialTypesFromTree = (): string[] => methods[METHODS.pseudopotential];

// DFT-specific

const DFTModelRefiners = ["hse", "g0w0"];
const DFTModelModifiers = ["soc", "magn"];

const DFTModelTree = {
    gga: {
        refiners: DFTModelRefiners,
        modifiers: DFTModelModifiers,
        methods,
        functionals: ["pbe", "pbesol", "pw91", "other"],
    },
    lda: {
        refiners: DFTModelRefiners,
        modifiers: DFTModelModifiers,
        methods,
        functionals: ["pz", "pw", "vwn", "other"],
    },
    hybrid: {
        methods,
        functionals: ["b3lyp", "hse06"],
    },
    other: {
        methods,
        functionals: ["other"],
    },
};

export const getDFTFunctionalsFromTree = (): string[] => Object.keys(DFTModelTree);

export const getDFTFunctionalsByApproximation = (approximation: string): string[] | undefined => {
    const branch = DFTModelTree[approximation as keyof typeof DFTModelTree];
    return branch && branch.functionals;
};

// GENERAL

export const MODEL_TREE: ModelTree = {
    dft: DFTModelTree,
    ml: {
        re: {
            methods: {
                linear: ["least_squares", "ridge"],
                kernel_ridge: ["least_squares"],
            },
        },
    },
    unknown: {
        unknown: {
            methods: {
                unknown: ["unknown"],
            },
        },
    },
};

export const MODEL_NAMES: Record<string, string> = {
    dft: "density functional theory",
    lda: "local density approximation",
    gga: "generalized gradient approximation",
    hybrid: "hybrid functional",
    ml: "machine learning",
    re: "regression",
};

export const treeSlugToNamedObject = (modelSlug: string): SlugifiedEntry => {
    return {
        slug: modelSlug,
        name: lodash.get(MODEL_NAMES, modelSlug, modelSlug),
    };
};

// TODO: find a better way to handle application-specific model-method combination
// must be a subset of the MODEL_TREE above
// demonstrate how tree can be modified
// VASP_MODELS_TREE.gga.functionals = _.omit(VASP_MODELS_TREE.gga.functionals);

type DftOnlyTree = { dft: typeof DFTModelTree };

const VASP_MODELS_TREE = deepClone(_.pick(MODEL_TREE, "dft")) as DftOnlyTree;
const ESPRESSO_MODELS_TREE = deepClone(_.pick(MODEL_TREE, "dft")) as DftOnlyTree;
const NWCHEM_MODELS_TREE = deepClone(_.pick(MODEL_TREE, "dft")) as DftOnlyTree;

(["gga", "lda"] as const).forEach((approximation) => {
    // pick "paw" for vasp
    VASP_MODELS_TREE.dft[approximation].methods.pseudopotential = VASP_MODELS_TREE.dft[
        approximation
    ].methods.pseudopotential.splice(0, 1);

    // assert "us" is the first option
    ESPRESSO_MODELS_TREE.dft[approximation].methods.pseudopotential =
        ESPRESSO_MODELS_TREE.dft[approximation].methods.pseudopotential.reverse();
});

const UNKNOWN_MODELS_TREE = _.pick(MODEL_TREE, "unknown") as ModelTree;
// const ML_MODELS_TREE = _.pick(MODEL_TREE, "ml");

const MODELS_TREE_CONFIGS_BY_APPLICATION_NAME_VERSION: Array<{
    name: string;
    tree: ModelTree;
}> = [
    {
        name: "vasp",
        tree: VASP_MODELS_TREE,
    },
    {
        name: "espresso",
        tree: ESPRESSO_MODELS_TREE,
    },
    {
        name: "python",
        tree: UNKNOWN_MODELS_TREE,
    },
    {
        name: "shell",
        tree: UNKNOWN_MODELS_TREE,
    },
    {
        name: "jupyterLab",
        tree: UNKNOWN_MODELS_TREE,
    },
    {
        name: "nwchem",
        tree: NWCHEM_MODELS_TREE,
    },
    {
        name: "deepmd",
        tree: UNKNOWN_MODELS_TREE,
    },
];

export const getTreeByApplicationNameAndVersion = ({
    name,
}: Pick<ApplicationSchemaBase, "name" | "version">): ModelTree => {
    // TODO: add logic to filter by version when necessary
    const cfgs = MODELS_TREE_CONFIGS_BY_APPLICATION_NAME_VERSION.filter(
        (cfg) => cfg.name === name,
    ).map((cfg) => cfg.tree);
    return Object.assign({}, ...cfgs);
};

export const getDefaultModelTypeForApplication = (application: ApplicationSchemaBase): string => {
    return Object.keys(getTreeByApplicationNameAndVersion(application))[0];
};
