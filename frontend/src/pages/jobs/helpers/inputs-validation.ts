import { hfGetRepository } from "../../../helpers"

const isValidName = (value: string) => /^[A-Za-z0-9._-]+$/.test(value)
const isValidRepoName = (text: string, owner?: string) => {
  const pattern = `^${owner ? owner : "[a-zA-Z0-9._-]+"}/[a-zA-Z0-9._-]+$`
  return new RegExp(pattern).test(text)
}
const isValidText = (value: any) => typeof value === "string" && String(value).trim().length > 0
const requiredFieldMessage = "This field is required."
const invalidNameMessage = "Only alphanumeric characters, underscores, hyphens and dots are allowed."
const invalidRepoNameMessage = "Incorrect repository name, should be <owner>/<model_name>"
const repoNotFoundMessage = "Repository not found on HuggingFace."

const validateJobName = (value: string) => {
  if (!isValidText(value)) return requiredFieldMessage
  if (!isValidName(String(value))) return invalidNameMessage
}

const validateModelName = async (value: string) => {
  if (!isValidText(value)) return requiredFieldMessage
  if (!isValidRepoName(value)) {
    return invalidRepoNameMessage
  } else {
    const repo = await hfGetRepository(value, "model").catch(() => undefined)
    if (!repo?.id) return repoNotFoundMessage
  }
}

const validateDatasetName = async (value: string) => {
  if (!isValidText(value)) return requiredFieldMessage
  //TODO: add check on huggingface and ovh
}

const validateHfHub = async (value: string) => {
  if (!isValidText(value)) return requiredFieldMessage
  if (!isValidRepoName(value, "dataesr")) return invalidRepoNameMessage
}

const validateWandbName = (value: string) => {
  if (isValidText(value) && !isValidName(value)) return invalidNameMessage
}

const validateInputMapping = {
  name: validateJobName,
  wandb_name: validateWandbName,
  wandb_project: validateWandbName,
}

const validateDebouncedInputMapping = {
  model_name: validateModelName,
  dataset_name: validateDatasetName,
  hf_hub: validateHfHub,
}

export const validateInput = (name: string, input: string) =>
  name in validateInputMapping ? validateInputMapping[name](input) : ""

export const validateDebouncedInput = async (name: string, input: string) =>
  name in validateDebouncedInputMapping ? await validateDebouncedInputMapping[name](input) : ""
